from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from customer_service.models import ContactMethod, CustomerServiceConfig, FAQ
from footer.models import FooterConfig, FooterLink, FooterSection
from game_article.models import Article, ArticleCategory, ArticleTag
from game_page.models import GamePage, GamePageCategory
from main.models import Banner, HomeLayout
from main.i18n_backfill import (
    DEFAULT_BACKFILL_LANGS,
    TranslationBackfiller,
    backfill_instance_fields,
    parse_target_langs,
)


TASKS: list[tuple[str, object, list[tuple[str, str, bool]]]] = [
    (
        "article_categories",
        ArticleCategory.objects.all(),
        [("name", "name_i18n", False), ("description", "description_i18n", False)],
    ),
    (
        "article_tags",
        ArticleTag.objects.all(),
        [("name", "name_i18n", False)],
    ),
    (
        "articles",
        Article.objects.all(),
        [
            ("title", "title_i18n", False),
            ("author_name", "author_name_i18n", False),
            ("excerpt", "excerpt_i18n", False),
            ("summary", "summary_i18n", False),
            ("content", "content_i18n", True),
            ("read_time", "read_time_i18n", False),
        ],
    ),
    (
        "game_categories",
        GamePageCategory.objects.all(),
        [("name", "name_i18n", False), ("description", "description_i18n", False)],
    ),
    (
        "games",
        GamePage.objects.all(),
        [
            ("title", "title_i18n", False),
            ("platform", "platform_i18n", False),
            ("regions", "regions_i18n", False),
            ("description", "description_i18n", False),
            ("content", "content_i18n", False),
            ("topup_info", "topup_info_i18n", False),
        ],
    ),
    (
        "contact_methods",
        ContactMethod.objects.all(),
        [
            ("title", "title_i18n", False),
            ("description", "description_i18n", False),
            ("button_text", "button_text_i18n", False),
        ],
    ),
    (
        "faqs",
        FAQ.objects.all(),
        [
            ("question", "question_i18n", False),
            ("answer", "answer_i18n", False),
            ("category", "category_i18n", False),
        ],
    ),
    (
        "customer_service_config",
        CustomerServiceConfig.objects.all(),
        [
            ("page_title", "page_title_i18n", False),
            ("page_description", "page_description_i18n", False),
            ("faq_title", "faq_title_i18n", False),
        ],
    ),
    (
        "banners",
        Banner.objects.all(),
        [
            ("title", "title_i18n", False),
            ("description", "description_i18n", False),
            ("badge", "badge_i18n", False),
            ("primary_button_text", "primary_button_text_i18n", False),
            ("secondary_button_text", "secondary_button_text_i18n", False),
        ],
    ),
    (
        "home_layouts",
        HomeLayout.objects.all(),
        [
            ("section_name", "section_name_i18n", False),
            ("config", "config_i18n", False),
        ],
    ),
    (
        "footer_sections",
        FooterSection.objects.all(),
        [
            ("title", "title_i18n", False),
            ("description", "description_i18n", False),
        ],
    ),
    (
        "footer_links",
        FooterLink.objects.all(),
        [("title", "title_i18n", False)],
    ),
    (
        "footer_config",
        FooterConfig.objects.all(),
        [("copyright_text", "copyright_text_i18n", False)],
    ),
]
TASK_INDEX = {label: (queryset, mappings) for label, queryset, mappings in TASKS}


class Command(BaseCommand):
    help = "Backfill translations into *_i18n JSON fields for dynamic content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--langs",
            default=",".join(DEFAULT_BACKFILL_LANGS),
            help="Comma-separated locale list. Default: en,ja,ko,th,vi,zh-CN,zh-TW,fr,de",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing translations if already present.",
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

        overwrite = bool(options.get("overwrite"))
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

        backfiller = TranslationBackfiller()

        self.stdout.write(
            self.style.WARNING(
                "Backfilling languages: "
                f"{', '.join(target_langs)} | overwrite={overwrite} | "
                f"targets={','.join(label for label, _, _ in selected_tasks)}"
            )
        )

        total_updated = 0
        for label, queryset, mappings in selected_tasks:
            updated_rows = 0
            for obj in queryset.iterator():
                dirty_fields = backfill_instance_fields(
                    obj,
                    mappings,
                    target_langs,
                    overwrite=overwrite,
                    backfiller=backfiller,
                )
                if dirty_fields:
                    obj.save(update_fields=sorted(set(dirty_fields)))
                    updated_rows += 1

            total_updated += updated_rows
            self.stdout.write(self.style.SUCCESS(f"{label}: updated {updated_rows} rows"))

        self.stdout.write(self.style.SUCCESS(f"Done. Total updated rows: {total_updated}"))
