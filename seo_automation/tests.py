from io import BytesIO

from django.test import SimpleTestCase

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None

from seo_automation.services.content_enrichment import (
    compose_rich_seo_article_html,
    inject_game_internal_link,
)
from seo_automation.services.quality_enhancement import (
    _estimate_bottom_banner_risk,
    _reject_image_by_text_or_watermark,
)


class WatermarkFilterTests(SimpleTestCase):
    def _to_bytes(self, image: "Image.Image") -> bytes:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def _build_clean_sample(self) -> "Image.Image":
        if Image is None or ImageDraw is None:
            self.skipTest("Pillow is not available")
        image = Image.new("RGB", (1280, 720), (72, 118, 168))
        draw = ImageDraw.Draw(image)
        for idx in range(9):
            y = 120 + (idx * 42)
            draw.rectangle(
                (88 + (idx * 7), y, 1170 - (idx * 5), y + 18),
                fill=(94 + (idx * 6), 138 + (idx * 4), 186 + (idx * 2)),
            )
        draw.ellipse((420, 180, 860, 620), fill=(220, 166, 102))
        return image

    def _build_logo_banner_sample(self) -> "Image.Image":
        image = self._build_clean_sample().copy()
        draw = ImageDraw.Draw(image)

        for x in range(18, 260):
            for y in range(12, 112):
                color = (245, 245, 245) if (x + y) % 9 < 4 else (22, 28, 34)
                draw.point((x, y), fill=color)

        draw.rectangle((90, 560, 1190, 696), fill=(236, 236, 236))
        for idx in range(26):
            y = 574 + (idx * 4)
            draw.line((120, y, 1160, y), fill=(34, 34, 34), width=1)
        return image

    def _build_gradient_sample(self) -> "Image.Image":
        if Image is None:
            self.skipTest("Pillow is not available")
        image = Image.new("RGB", (1280, 720))
        pixels = image.load()
        for y in range(720):
            for x in range(1280):
                pixels[x, y] = (
                    int(40 + (x / 7)) % 256,
                    int(80 + (y / 3)) % 256,
                    int(110 + ((x + y) / 16)) % 256,
                )
        return image

    def test_clean_image_not_rejected(self) -> None:
        payload = self._to_bytes(self._build_clean_sample())
        rejected, reason = _reject_image_by_text_or_watermark(
            image_bytes=payload,
            image_url="https://example.com/clean-art.png",
        )
        self.assertFalse(rejected, reason)

    def test_logo_and_banner_image_rejected(self) -> None:
        payload = self._to_bytes(self._build_logo_banner_sample())
        rejected, reason = _reject_image_by_text_or_watermark(
            image_bytes=payload,
            image_url="https://example.com/game-art.png",
        )
        self.assertTrue(rejected)
        self.assertIn(
            reason,
            {
                "heuristic_text_overlay",
                "bottom_banner_overlay",
                "overlay_combo",
                "corner_logo_overlay",
            },
        )

    def test_bottom_banner_score_avoids_gradient_false_positive(self) -> None:
        payload = self._to_bytes(self._build_gradient_sample())
        score = _estimate_bottom_banner_risk(payload)
        self.assertLess(score, 0.12)


class RelatedLinksInjectionTests(SimpleTestCase):
    def test_inject_related_links_dedupes_existing_blocks(self) -> None:
        body_html = (
            '<section class="seo-related-links"><h2>old links block</h2></section>'
            "<h2>\u76f8\u95dc\u904a\u6232\u8207\u5b98\u65b9\u9023\u7d50</h2>"
            "<p>legacy intro</p>"
            "<ul><li>legacy item</li></ul>"
            "<p>legacy tail</p>"
            "<p>article body</p>"
        )
        result = inject_game_internal_link(
            body_html=body_html,
            game_id=88,
            game_title="Seven Knights Re:BIRTH",
            google_play_id="com.example.game",
        )

        self.assertEqual(result.count("seo-related-links"), 1)
        self.assertNotIn("old links block", result)
        self.assertNotIn("legacy intro", result)
        self.assertIn("https://apps.apple.com/tw/iphone/search?term=", result)
        self.assertNotIn("https://apps.apple.com/tw/search?term=", result)


class SeoComposeDedupTests(SimpleTestCase):
    def test_compose_rich_article_removes_legacy_duplicate_summary_and_metadata(self) -> None:
        zh_summary = "\u6458\u8981"
        zh_keywords_tc = "\u95dc\u9375\u8a5e"
        zh_keywords_sc = "\u5173\u952e\u8bcd"
        zh_publish_tc = "\u767c\u5e03\u65e5\u671f"
        zh_publish_sc = "\u53d1\u5e03\u65e5\u671f"

        body_html = f"""
        <article class="seo-article-shell">
          <div class="seo-summary"><strong>{zh_summary}</strong>：old-summary-a</div>
          <section class="seo-main-content">
            <p>{zh_summary}：old-summary-b</p>
            <h2>gameplay-focus</h2>
            <p>body paragraph.</p>
          </section>
          <footer class="seo-metadata">
            <p><strong>{zh_keywords_tc}</strong>：old-keywords-a</p>
            <p><strong>{zh_publish_tc}</strong>：2026-02-01</p>
          </footer>
        </article>
        <div>
          <p><strong>{zh_keywords_sc}</strong>：old-keywords-b</p>
          <p><strong>{zh_publish_sc}</strong>：2026-02-02</p>
        </div>
        """

        result = compose_rich_seo_article_html(
            title="test title",
            body_html=body_html,
            game_name="test game",
            summary="new summary",
            keywords=["tag-a", "tag-b"],
        )

        self.assertEqual(result.count('class="seo-summary"'), 1)
        self.assertEqual(result.count('class="seo-metadata"'), 1)
        self.assertEqual(result.count("<strong>摘要</strong>"), 1)
        self.assertEqual(result.count("<strong>關鍵詞</strong>"), 1)
        self.assertEqual(result.count("<strong>發布日期</strong>"), 1)
        self.assertNotIn("old-summary-a", result)
        self.assertNotIn("old-keywords-a", result)
        self.assertNotIn("old-keywords-b", result)
        self.assertIn("<h2>gameplay-focus</h2>", result)
