from __future__ import annotations

from .backfill_i18n import Command as MultiLangBackfillCommand


class Command(MultiLangBackfillCommand):
    help = "Backfill English translations into *_i18n JSON fields for dynamic content."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.set_defaults(langs="en")
