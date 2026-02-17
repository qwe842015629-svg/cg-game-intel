from django.core.management.base import BaseCommand

from main.media_library import dedupe_existing_media_assets


class Command(BaseCommand):
    help = "Dedupe media library by image content hash and normalize asset names."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-duplicates",
            action="store_true",
            help="Keep duplicate rows and only backfill content_hash for auditing.",
        )

    def handle(self, *args, **options):
        result = dedupe_existing_media_assets(
            delete_duplicate_files=not bool(options.get("keep_duplicates")),
        )
        self.stdout.write(
            self.style.SUCCESS(
                "done indexed={indexed} deleted_duplicates={deleted_duplicates} renamed={renamed} skipped={skipped}".format(
                    **result
                )
            )
        )
