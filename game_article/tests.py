from django.test import TestCase
from rest_framework.test import APIRequestFactory
from unittest import mock

from game_page.models import GamePage
from .models import Article
from .serializers import (
    ArticleDetailSerializer,
    _ensure_related_links_block,
    _normalize_existing_summary_block,
)


class ArticleSerializerFallbackTests(TestCase):
    def _build_article(self) -> Article:
        article = Article(
            title="寒霜启示录代储攻略与实战小技巧分享",
            content="",
        )
        article.game = GamePage(
            id=77,
            title="寒霜启示录代储",
            google_play_id="com.example.frost",
        )
        return article

    def test_related_links_block_reinjected_when_legacy_heading_exists(self) -> None:
        article = self._build_article()
        content = (
            "<h2>相关游戏与官方链接</h2>"
            "<p>旧说明文字</p>"
            "<ul><li>旧链接项</li></ul>"
        )

        result = _ensure_related_links_block(content, article, locale="zh-CN")

        self.assertEqual(result.count('class="seo-related-links"'), 1)
        self.assertIn("相关游戏与官方链接", result)
        self.assertIn("Google Play 下载页", result)
        self.assertNotIn("旧说明文字", result)

    def test_related_links_block_has_non_cn_locale_fallback(self) -> None:
        article = self._build_article()

        result = _ensure_related_links_block("<p>body</p>", article, locale="ja")

        self.assertIn("Related Game and Official Links", result)
        self.assertIn("apps.apple.com/jp/search?term=", result)

    def test_related_links_internal_path_uses_locale_prefix(self) -> None:
        article = self._build_article()

        fr_result = _ensure_related_links_block("<p>body</p>", article, locale="fr")
        fallback_result = _ensure_related_links_block("<p>body</p>", article, locale="es")

        self.assertIn('href="/fr/games/77"', fr_result)
        self.assertIn('href="/en/games/77"', fallback_result)

    def test_summary_block_normalization_removes_url_noise(self) -> None:
        article = self._build_article()
        content = (
            '<article class="seo-article-shell">'
            '<div class="seo-summary"><strong>摘要</strong>：摘要：寒霜啟示錄資訊 https://example.com/a</div>'
            "<section><p>正文</p></section>"
            "</article>"
        )
        summary = "摘要：寒霜啟示錄版本重點整理 FB粉專 https://example.com/post/1"

        normalized = _normalize_existing_summary_block(
            content,
            locale="zh-CN",
            summary_text=summary,
            game_name=article.game.title,
        )

        self.assertEqual(normalized.count('class="seo-summary"'), 1)
        self.assertNotIn("https://", normalized)


class ArticleDetailConsistencyTests(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_detail_zh_cn_prefers_primary_content_field(self) -> None:
        article = Article.objects.create(
            title="测试文章",
            content="<p>后台主内容</p>",
            content_i18n={"zh-CN": "<p>旧翻译内容</p>"},
            excerpt="摘要",
            summary="摘要",
        )

        request = self.factory.get(f"/api/articles/{article.id}/", {"locale": "zh-CN"}, HTTP_X_LOCALE="zh-CN")
        payload = ArticleDetailSerializer(article, context={"request": request}).data

        self.assertEqual(payload["content"], "<p>后台主内容</p>")
        self.assertNotIn("seo-related-links", payload["content"])

    def test_detail_non_cn_uses_i18n_content_when_available(self) -> None:
        article = Article.objects.create(
            title="Test Article",
            content="<p>Default body</p>",
            content_i18n={"fr": "<p>Corps FR</p>"},
            excerpt="Excerpt",
            summary="Summary",
        )

        request = self.factory.get(f"/api/articles/{article.id}/", {"locale": "fr"}, HTTP_X_LOCALE="fr")
        payload = ArticleDetailSerializer(article, context={"request": request}).data

        self.assertEqual(payload["content"], "<p>Corps FR</p>")

    def test_detail_rewrites_embedded_summary_block_with_latest_summary(self) -> None:
        article = Article.objects.create(
            title="Summary Sync Test",
            content=(
                '<article class="seo-article-shell">'
                '<div class="seo-summary"><strong>摘要</strong>：旧摘要内容不会继续显示</div>'
                '<section class="seo-main-content"><p>正文内容</p></section>'
                "</article>"
            ),
            excerpt="新的摘要文本",
            summary="新的摘要文本",
        )

        request = self.factory.get(
            f"/api/articles/{article.id}/",
            {"locale": "zh-CN"},
            HTTP_X_LOCALE="zh-CN",
        )
        payload = ArticleDetailSerializer(article, context={"request": request}).data

        self.assertEqual(payload["content"].count('class="seo-summary"'), 1)
        self.assertIn("新的摘要文本", payload["content"])
        self.assertNotIn("旧摘要内容不会继续显示", payload["content"])


class _DummyBackfiller:
    def translate_text(self, value, target_lang):
        if str(target_lang) == "zh-CN":
            return str(value)
        return f"[{target_lang}] {value}"

    def translate_html(self, value, target_lang):
        if str(target_lang) == "zh-CN":
            return str(value)
        return f"{value}<!--{target_lang}-->"


class ArticleI18nBackfillSignalTests(TestCase):
    def _create_article_with_i18n(self) -> Article:
        return Article.objects.create(
            title="原始标题",
            author_name="原作者",
            excerpt="原摘要",
            summary="原总结",
            content='<p>旧内容<img src="old-image.jpg" /></p>',
            read_time="5分钟",
            title_i18n={"zh-CN": "原始标题", "en": "manual old en title"},
            author_name_i18n={"zh-CN": "原作者", "en": "manual old en author"},
            excerpt_i18n={"zh-CN": "原摘要", "en": "manual old en excerpt"},
            summary_i18n={"zh-CN": "原总结", "en": "manual old en summary"},
            content_i18n={"zh-CN": '<p>旧内容<img src="old-image.jpg" /></p>', "en": "<p>manual old en content</p>"},
            read_time_i18n={"zh-CN": "5分钟", "en": "manual old en read time"},
        )

    @mock.patch("game_article.signals.DEFAULT_BACKFILL_LANGS", ("en", "fr", "zh-CN"))
    @mock.patch("game_article.signals._get_backfiller", return_value=_DummyBackfiller())
    def test_source_field_change_overwrites_existing_translations(self, _mock_backfiller):
        article = self._create_article_with_i18n()
        article.title = "更新后标题"
        article.excerpt = "更新后摘要"
        article.summary = "更新后总结"
        article.content = '<p>新内容<img src="new-image.jpg" /></p>'
        article.save()
        article.refresh_from_db()

        self.assertEqual(article.title_i18n.get("zh-CN"), "更新后标题")
        self.assertEqual(article.title_i18n.get("en"), "[en] 更新后标题")
        self.assertEqual(article.excerpt_i18n.get("en"), "[en] 更新后摘要")
        self.assertEqual(article.summary_i18n.get("en"), "[en] 更新后总结")
        self.assertIn("new-image.jpg", article.content_i18n.get("en", ""))

    @mock.patch("game_article.signals.DEFAULT_BACKFILL_LANGS", ("en", "fr", "zh-CN"))
    @mock.patch("game_article.signals._get_backfiller", return_value=_DummyBackfiller())
    def test_non_content_update_does_not_overwrite_existing_translations(self, _mock_backfiller):
        article = self._create_article_with_i18n()
        original_title_en = article.title_i18n.get("en")
        original_content_en = article.content_i18n.get("en")

        article.status = "published"
        article.save(update_fields=["status"])
        article.refresh_from_db()

        self.assertEqual(article.title_i18n.get("en"), original_title_en)
        self.assertEqual(article.content_i18n.get("en"), original_content_en)
