import time

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from game_page.models import GamePage
from game_page.scraper import GooglePlayScraper


class Command(BaseCommand):
    help = "Download GamePage.icon_external_url to local media library and bind icon_image."

    def add_arguments(self, parser):
        parser.add_argument(
            "--ids",
            type=str,
            default="",
            help="Process only specific GamePage IDs, comma separated. Example: --ids 12,18,25",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing icon_image when external icon can be downloaded.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview only, do not write to database.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum records to process. 0 means no limit.",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=0.0,
            help="Sleep seconds between each record to reduce request pressure.",
        )

    @staticmethod
    def _parse_ids(raw_ids: str):
        if not raw_ids:
            return []

        parsed = []
        for token in raw_ids.split(","):
            value = token.strip()
            if not value:
                continue
            if not value.isdigit():
                raise CommandError(f"Invalid ID in --ids: {value}")
            parsed.append(int(value))
        return parsed

    def handle(self, *args, **options):
        ids = self._parse_ids(options["ids"])
        overwrite = options["overwrite"]
        dry_run = options["dry_run"]
        limit = max(0, int(options["limit"] or 0))
        sleep_seconds = max(0.0, float(options["sleep"] or 0.0))

        queryset = GamePage.objects.exclude(icon_external_url__isnull=True).exclude(icon_external_url__exact="")

        if ids:
            queryset = queryset.filter(id__in=ids)

        if not overwrite:
            queryset = queryset.filter(Q(icon_image__isnull=True) | Q(icon_image__exact=""))

        queryset = queryset.order_by("id")
        if limit > 0:
            queryset = queryset[:limit]

        pages = list(queryset)
        total = len(pages)
        if total == 0:
            self.stdout.write(self.style.WARNING("No matching records found."))
            return

        mode = "DRY-RUN" if dry_run else "WRITE"
        self.stdout.write(
            f"Start syncing game icons from external URL: total={total}, mode={mode}, overwrite={overwrite}"
        )

        scraper = GooglePlayScraper()
        stats = {
            "updated": 0,
            "would_update": 0,
            "unchanged": 0,
            "failed": 0,
        }

        for index, page in enumerate(pages, start=1):
            label = f"[{index}/{total}] id={page.id} title={page.title}"

            try:
                media = scraper.save_icon_to_media_library(
                    page.icon_external_url,
                    page.title or "",
                    package_id=page.google_play_id or "",
                )
            except Exception as exc:  # noqa: BLE001
                stats["failed"] += 1
                self.stdout.write(self.style.ERROR(f"{label} -> download exception: {exc}"))
                continue

            if not media or not media.file:
                stats["failed"] += 1
                self.stdout.write(self.style.ERROR(f"{label} -> download failed"))
                continue

            media_path = getattr(media.file, "name", "")
            current_path = getattr(page.icon_image, "name", "")
            if current_path and current_path == media_path:
                stats["unchanged"] += 1
                self.stdout.write(f"{label} -> unchanged (already bound)")
                continue

            if dry_run:
                stats["would_update"] += 1
                self.stdout.write(self.style.WARNING(f"{label} -> would bind icon_image={media_path}"))
            else:
                page.icon_image = media.file
                page.save(update_fields=["icon_image", "updated_at"])
                stats["updated"] += 1
                self.stdout.write(self.style.SUCCESS(f"{label} -> icon_image={media_path}"))

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

        self.stdout.write("")
        self.stdout.write("Done:")
        self.stdout.write(f"  updated={stats['updated']}")
        self.stdout.write(f"  would_update={stats['would_update']}")
        self.stdout.write(f"  unchanged={stats['unchanged']}")
        self.stdout.write(f"  failed={stats['failed']}")
