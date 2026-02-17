import time
from urllib.parse import parse_qs, urlparse

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from game_page.models import GamePage
from game_page.scraper import GooglePlayScraper


class Command(BaseCommand):
    help = "批量回填 GamePage 缺失的 Google Play 简介到 description/content 字段。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            dest="process_all",
            help="处理所有有 google_play_id 的记录（默认仅处理缺失详情的记录）。",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="覆盖已有内容（默认不覆盖）。",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅预览将修改哪些记录，不写入数据库。",
        )
        parser.add_argument(
            "--ids",
            type=str,
            default="",
            help="仅处理指定 ID，逗号分隔，例如: --ids 12,18,25",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="最多处理多少条，0 表示不限制。",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=0.0,
            help="每条处理后的等待秒数，避免请求过快。",
        )
        parser.add_argument(
            "--save-icon",
            action="store_true",
            help="尝试将抓取到的图标保存并绑定到 GamePage.icon_image。",
        )
        parser.add_argument(
            "--no-sync-tw",
            action="store_true",
            help="不回填 description_tw/content_tw。",
        )

    @staticmethod
    def _parse_ids(raw_ids):
        if not raw_ids:
            return []
        result = []
        for token in raw_ids.split(","):
            token = token.strip()
            if not token:
                continue
            if not token.isdigit():
                raise CommandError(f"--ids 包含非法值: {token}")
            result.append(int(token))
        return result

    @staticmethod
    def _build_play_url(raw_value):
        value = (raw_value or "").strip()
        if not value:
            return "", ""

        if value.startswith("http://") or value.startswith("https://"):
            parsed = urlparse(value)
            package_id = parse_qs(parsed.query).get("id", [""])[0].strip()
        else:
            package_id = value

        if not package_id:
            return "", ""

        url = (
            "https://play.google.com/store/apps/details"
            f"?id={package_id}&hl=zh_TW&gl=HK"
        )
        return package_id, url

    def handle(self, *args, **options):
        process_all = options["process_all"]
        overwrite = options["overwrite"]
        dry_run = options["dry_run"]
        limit = max(0, int(options["limit"] or 0))
        sleep_seconds = max(0.0, float(options["sleep"] or 0.0))
        save_icon = options["save_icon"]
        sync_tw = not options["no_sync_tw"]
        ids = self._parse_ids(options["ids"])

        queryset = GamePage.objects.exclude(google_play_id__isnull=True).exclude(google_play_id__exact="")

        if ids:
            queryset = queryset.filter(id__in=ids)

        # Default mode: only fill missing fields.
        # If overwrite is enabled, process selected records directly.
        if not process_all and not overwrite:
            queryset = queryset.filter(
                Q(description__isnull=True)
                | Q(description__exact="")
                | Q(content__isnull=True)
                | Q(content__exact="")
                | Q(description_tw__isnull=True)
                | Q(description_tw__exact="")
                | Q(content_tw__isnull=True)
                | Q(content_tw__exact="")
                | Q(icon_external_url__isnull=True)
                | Q(icon_external_url__exact="")
                | Q(developer__isnull=True)
                | Q(developer__exact="")
            )

        queryset = queryset.order_by("id")
        if limit > 0:
            queryset = queryset[:limit]

        pages = list(queryset)
        total = len(pages)
        if total == 0:
            self.stdout.write(self.style.WARNING("没有符合条件的记录。"))
            return

        mode = "DRY-RUN" if dry_run else "WRITE"
        self.stdout.write(
            f"开始回填: total={total}, mode={mode}, overwrite={overwrite}, sync_tw={sync_tw}, save_icon={save_icon}"
        )

        scraper = GooglePlayScraper()
        stats = {
            "updated": 0,
            "would_update": 0,
            "unchanged": 0,
            "failed": 0,
        }

        for idx, page in enumerate(pages, start=1):
            package_id, play_url = self._build_play_url(page.google_play_id)
            label = f"[{idx}/{total}] id={page.id} title={page.title}"

            if not package_id:
                stats["failed"] += 1
                self.stdout.write(self.style.ERROR(f"{label} -> 跳过，google_play_id 无法解析"))
                continue

            data = scraper.fetch_game_info(play_url)
            if "error" in data:
                stats["failed"] += 1
                self.stdout.write(self.style.ERROR(f"{label} -> 抓取失败: {data['error']}"))
                continue

            description = (data.get("description") or "").strip()
            content = (data.get("content") or "").strip()
            developer = (data.get("developer") or "").strip()
            icon_external_url = (data.get("icon_url") or "").strip()

            if not content and description:
                content = description
            if not description and content:
                description = content[:300]

            update_fields = []

            if package_id and page.google_play_id != package_id:
                page.google_play_id = package_id
                update_fields.append("google_play_id")

            if (overwrite or not page.icon_external_url) and icon_external_url and page.icon_external_url != icon_external_url:
                page.icon_external_url = icon_external_url
                update_fields.append("icon_external_url")

            if (overwrite or not page.description) and description and page.description != description:
                page.description = description
                update_fields.append("description")

            if (overwrite or not page.content) and content and page.content != content:
                page.content = content
                update_fields.append("content")

            if sync_tw:
                if (overwrite or not page.description_tw) and description and page.description_tw != description:
                    page.description_tw = description
                    update_fields.append("description_tw")

                if (overwrite or not page.content_tw) and content and page.content_tw != content:
                    page.content_tw = content
                    update_fields.append("content_tw")

            if (overwrite or not page.developer) and developer and page.developer != developer:
                page.developer = developer
                update_fields.append("developer")

            if save_icon and data.get("icon_url") and not page.icon_image:
                media = scraper.save_icon_to_media_library(
                    data["icon_url"],
                    data.get("title") or page.title,
                    package_id=package_id,
                )
                if media and media.file:
                    page.icon_image = media.file
                    update_fields.append("icon_image")

            unique_fields = sorted(set(update_fields))
            if not unique_fields:
                stats["unchanged"] += 1
                self.stdout.write(f"{label} -> 无变化")
            elif dry_run:
                stats["would_update"] += 1
                self.stdout.write(self.style.WARNING(f"{label} -> 将更新字段: {', '.join(unique_fields)}"))
            else:
                page.save(update_fields=unique_fields + ["updated_at"])
                stats["updated"] += 1
                self.stdout.write(self.style.SUCCESS(f"{label} -> 已更新字段: {', '.join(unique_fields)}"))

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

        self.stdout.write("")
        self.stdout.write("执行完成:")
        self.stdout.write(f"  updated={stats['updated']}")
        self.stdout.write(f"  would_update={stats['would_update']}")
        self.stdout.write(f"  unchanged={stats['unchanged']}")
        self.stdout.write(f"  failed={stats['failed']}")
