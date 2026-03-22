from io import BytesIO

from unittest import mock

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIRequestFactory

from game_article.models import Article
from seo_automation.models import SeoArticle
from seo_automation.views import SeoArticleViewSet

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None

from seo_automation.services.content_enrichment import (
    build_meta_fields,
    compose_rich_seo_article_html,
    inject_game_internal_link,
    sanitize_seo_summary_text,
)
from seo_automation.services.quality_enhancement import (
    _estimate_bottom_banner_risk,
    _reject_image_by_text_or_watermark,
    _score_candidate_relevance,
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

    def test_url_hint_rejected_even_for_clean_image(self) -> None:
        payload = self._to_bytes(self._build_clean_sample())
        rejected, reason = _reject_image_by_text_or_watermark(
            image_bytes=payload,
            image_url="https://example.com/images/giftcode-banner.png",
        )
        self.assertTrue(rejected)
        self.assertEqual(reason, "url_hint")


class RelevanceScoringTests(SimpleTestCase):
    def test_seed_without_game_signal_is_not_high_score(self) -> None:
        score = _score_candidate_relevance(
            candidate={
                "source": "seed",
                "url": "https://cdn.example.com/assets/cover_001.jpg",
                "title": "latest mobile game guide",
                "heading": "\u7248\u672c\u653b\u7565",
                "query": "",
            },
            game_name="honkai star rail",
        )
        self.assertLess(score, 0.34)

    def test_other_game_candidate_is_penalized(self) -> None:
        score = _score_candidate_relevance(
            candidate={
                "source": "bing",
                "url": "https://media.example.com/genshin-impact-4-0-tier-list.jpg",
                "title": "Genshin Impact tier list and gift code",
                "heading": "\u5f00\u5c40\u6280\u5de7",
                "query": "honkai star rail beginner build guide",
            },
            game_name="honkai star rail",
        )
        self.assertLess(score, 0.42)

    def test_target_game_candidate_keeps_high_score(self) -> None:
        score = _score_candidate_relevance(
            candidate={
                "source": "bing",
                "url": "https://assets.game.example.com/honkai-starrail-key-visual-2026.jpg",
                "title": "Honkai Star Rail official key visual wallpaper",
                "heading": "\u89d2\u8272\u57f9\u990a",
                "query": "honkai star rail character build official art",
            },
            game_name="honkai star rail",
        )
        self.assertGreaterEqual(score, 0.6)


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


class SeoSummarySanitizationTests(SimpleTestCase):
    def test_sanitize_summary_removes_links_duplicate_prefix_and_forum_noise(self) -> None:
        raw = (
            "摘要：寒霜啟示錄代儲攻略與實戰技巧分享 摘要："
            "【情報】寒霜啟示錄電玩展舞台活動時間一覽 "
            "FB粉專 https://example.com/post/123"
        )
        cleaned = sanitize_seo_summary_text(raw, game_name="寒霜啟示錄代儲", limit=160)

        self.assertNotIn("https://", cleaned)
        self.assertNotIn("FB", cleaned.upper())
        self.assertEqual(cleaned.count("摘要"), 0)
        self.assertIn("寒霜", cleaned)

    def test_build_meta_fields_uses_cleaned_summary_block(self) -> None:
        body_html = (
            '<article class="seo-article-shell">'
            '<div class="seo-summary"><strong>摘要</strong>：摘要：版本重點整理 https://example.com/foo</div>'
            "<section><p>正文段落 A。</p><p>正文段落 B。</p></section>"
            "</article>"
        )
        meta = build_meta_fields(
            title="測試標題",
            body_html=body_html,
            default_title="測試遊戲",
        )

        self.assertIn("版本重點整理", meta["meta_description"])
        self.assertNotIn("https://", meta["meta_description"])
        self.assertLessEqual(len(meta["meta_description"]), 160)


class SeoArticleViewSetPublishFlowTests(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    @mock.patch("game_article.signals._get_backfiller", return_value=None)
    @mock.patch("seo_automation.views._ensure_article_cover_image", return_value=False)
    def test_partial_update_syncs_linked_published_article(self, _mock_cover, _mock_backfiller) -> None:
        article = Article.objects.create(
            title="旧标题",
            content="<p>旧内容</p>",
            excerpt="旧摘要",
            summary="旧摘要",
            status="published",
        )
        seo_article = SeoArticle.objects.create(
            title="旧SEO标题",
            body_html="<p>旧SEO内容</p>",
            meta_title="旧Meta",
            meta_description="旧描述",
            status="published",
            published_article=article,
        )

        view = SeoArticleViewSet.as_view({"patch": "partial_update"})
        request = self.factory.patch(
            f"/api/seo-automation/articles/{seo_article.id}/",
            {
                "title": "新SEO标题",
                "body_html": '<p>新正文 <img src="new-image.jpg" /></p>',
                "meta_description": "新的描述",
            },
            format="json",
        )
        response = view(request, pk=seo_article.id)

        self.assertEqual(response.status_code, 200)
        article.refresh_from_db()
        self.assertEqual(article.title, "新SEO标题")
        self.assertIn("new-image.jpg", article.content)
        self.assertEqual(article.status, "published")
        self.assertIn("new-image.jpg", (article.content_i18n or {}).get("zh-CN", ""))

    @mock.patch("game_article.signals._get_backfiller", return_value=None)
    @mock.patch("seo_automation.views._ensure_article_cover_image", return_value=False)
    @mock.patch(
        "seo_automation.views._refresh_seo_article_source_and_media",
        side_effect=RuntimeError("step5 boom"),
    )
    def test_publish_step5_failure_non_strict_still_publishes(
        self,
        _mock_step5,
        _mock_cover,
        _mock_backfiller,
    ) -> None:
        seo_article = SeoArticle.objects.create(
            title="待发布草稿",
            body_html="<p>草稿正文</p>",
            meta_title="草稿Meta",
            meta_description="草稿描述",
            status="draft",
        )

        view = SeoArticleViewSet.as_view({"post": "publish"})
        request = self.factory.post(
            f"/api/seo-automation/articles/{seo_article.id}/publish/",
            {"publish_now": True, "run_step5": True},
            format="json",
        )
        response = view(request, pk=seo_article.id)

        self.assertEqual(response.status_code, 200)
        payload = dict(response.data)
        self.assertEqual(payload.get("step5_status"), "failed")
        self.assertIn("step5_failed", str(payload.get("quality_error", "")))

        seo_article.refresh_from_db()
        self.assertEqual(seo_article.status, "published")
        self.assertIsNotNone(seo_article.published_article_id)

    @mock.patch(
        "seo_automation.views._refresh_seo_article_source_and_media",
        side_effect=RuntimeError("step5 boom"),
    )
    def test_publish_step5_failure_strict_returns_400(self, _mock_step5) -> None:
        seo_article = SeoArticle.objects.create(
            title="严格发布草稿",
            body_html="<p>草稿正文</p>",
            meta_title="草稿Meta",
            meta_description="草稿描述",
            status="draft",
        )

        view = SeoArticleViewSet.as_view({"post": "publish"})
        request = self.factory.post(
            f"/api/seo-automation/articles/{seo_article.id}/publish/",
            {"publish_now": True, "run_step5": True, "strict_step5": True},
            format="json",
        )
        response = view(request, pk=seo_article.id)

        self.assertEqual(response.status_code, 400)
        seo_article.refresh_from_db()
        self.assertIsNone(seo_article.published_article_id)
        self.assertNotEqual(seo_article.status, "published")
