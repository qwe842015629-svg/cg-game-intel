import json

from django.core.management.base import BaseCommand

from ops_gateway.auto_runner import run_daily_cycle_now


class Command(BaseCommand):
    help = "Run ops gateway daily robot cycle (Google Play import + SEO daily generation + published recheck)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force run immediately, even if it already ran today.",
        )

    def handle(self, *args, **options):
        force = bool(options.get("force"))
        result = run_daily_cycle_now(force=force, trigger_source="management_command")
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))

