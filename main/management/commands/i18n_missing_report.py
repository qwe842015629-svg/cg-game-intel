from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from main.i18n_backfill import DEFAULT_BACKFILL_LANGS, parse_target_langs
from main.management.commands.backfill_i18n import TASKS, TASK_INDEX


def _is_empty_i18n_value(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) == 0
    return False


class Command(BaseCommand):
    help = "Report missing translation rows in *_i18n JSON fields."

    def add_arguments(self, parser):
        parser.add_argument(
            "--langs",
            default=",".join(DEFAULT_BACKFILL_LANGS),
            help="Comma-separated locale list. Default: en,ja,ko,th,vi,zh-CN,zh-TW,fr,de",
        )
        parser.add_argument(
            "--targets",
            default="all",
            help="Comma-separated task labels. Use 'all' for all tasks.",
        )

    def handle(self, *args, **options):
        try:
            target_langs = parse_target_langs(options.get("langs"))
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        raw_targets = str(options.get("targets") or "all").strip()
        if not raw_targets or raw_targets.lower() == "all":
            selected_tasks = TASKS
        else:
            labels = [item.strip() for item in raw_targets.split(",") if item.strip()]
            invalid = [item for item in labels if item not in TASK_INDEX]
            if invalid:
                raise CommandError(
                    f"Unsupported target(s): {', '.join(invalid)}. Allowed: {', '.join(TASK_INDEX.keys())}"
                )
            selected_tasks = [(label, *TASK_INDEX[label]) for label in labels]

        self.stdout.write(
            self.style.WARNING(
                "Checking missing translations for: "
                f"{', '.join(target_langs)} | targets={','.join(label for label, _, _ in selected_tasks)}"
            )
        )

        missing_total = 0
        for label, queryset, mappings in selected_tasks:
            for source_field, i18n_field, _ in mappings:
                missing_rows = 0
                for obj in queryset.iterator():
                    source_value = getattr(obj, source_field, "")
                    if isinstance(source_value, (dict, list, tuple, set)):
                        if len(source_value) == 0:
                            continue
                    else:
                        source_text = str(source_value or "").strip()
                        if not source_text:
                            continue
                    if source_value is None:
                        continue

                    payload = getattr(obj, i18n_field, {}) or {}
                    if not isinstance(payload, dict):
                        missing_rows += 1
                        continue

                    if any(_is_empty_i18n_value(payload.get(lang)) for lang in target_langs):
                        missing_rows += 1

                if missing_rows > 0:
                    missing_total += missing_rows
                    self.stdout.write(
                        self.style.ERROR(f"{label}.{i18n_field}: missing_rows={missing_rows}")
                    )

        if missing_total == 0:
            self.stdout.write(self.style.SUCCESS("All checked translations are complete."))
        else:
            self.stdout.write(
                self.style.WARNING(f"Found missing translations. Total missing rows: {missing_total}")
            )
