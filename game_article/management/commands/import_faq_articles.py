import html
import math
import re
from typing import Any

import requests
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from lxml import html as lxml_html

from game_article.models import Article, ArticleCategory, ArticleTag


FAQ_CATEGORY_NAME = "常见问题"

FAQ_SOURCES = [
    {
        "url": "https://stargamebuy.com/payment-method/",
        "title": "支持哪些支付方式？完整说明",
        "slug": "faq-payment-method-guide",
        "tags": ["支付方式", "充值指南", "订单问题"],
    },
    {
        "url": "https://stargamebuy.com/google-authenticator/",
        "title": "Google Authenticator 二步验证绑定与找回指南",
        "slug": "faq-google-authenticator-guide",
        "tags": ["账号安全", "二步验证", "登录问题"],
    },
    {
        "url": "https://stargamebuy.com/safe-code/",
        "title": "安全码是什么？如何设置与使用",
        "slug": "faq-safe-code-guide",
        "tags": ["账号安全", "安全码", "充值流程"],
    },
    {
        "url": "https://diguogames88.com/%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/",
        "title": "购买教学：下单、付款到到账全流程",
        "slug": "faq-purchase-tutorial-guide",
        "tags": ["下单教程", "购买教学", "新手入门"],
    },
    {
        "url": "https://stargamebuy.com/steam-qa/",
        "title": "Steam 充值常见问题解答",
        "slug": "faq-steam-qa-guide",
        "tags": ["Steam", "充值问题", "FAQ"],
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

CONTENT_CANDIDATE_XPATHS = [
    "//article",
    "//*[contains(@class,'entry-content')]",
    "//*[contains(@class,'post-content')]",
    "//*[contains(@class,'article-content')]",
    "//*[contains(@class,'single-content')]",
    "//*[contains(@class,'elementor-widget-theme-post-content')]",
    "//main",
    "//div[contains(@class,'content')]",
]

NOISE_XPATH = (
    ".//script|.//style|.//noscript|.//iframe|.//svg|.//canvas|.//form|.//button|.//input|"
    ".//header|.//footer|.//nav|"
    ".//*[contains(@class,'share')]|.//*[contains(@class,'comment')]|"
    ".//*[contains(@class,'breadcrumb')]|.//*[contains(@class,'author-box')]|"
    ".//*[contains(@class,'related')]"
)

SKIP_TEXT_PATTERNS = [
    "上一篇",
    "下一篇",
    "发表评论",
    "留言",
    "分享",
    "版权所有",
    "隐私政策",
    "隱私政策",
    "登入",
    "登录",
    "注册",
    "回到顶部",
]


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


class Command(BaseCommand):
    help = "抓取外部 FAQ 页面并导入为站内常见问题文章。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅抓取与预览，不写入数据库。",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="单个页面请求超时时间（秒）。",
        )

    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        timeout = int(options.get("timeout") or 30)

        category, _ = ArticleCategory.objects.get_or_create(
            name=FAQ_CATEGORY_NAME,
            defaults={
                "description": "充值与账号相关常见问题整理",
                "sort_order": 1,
                "is_active": True,
            },
        )
        if not category.is_active:
            category.is_active = True
            category.save(update_fields=["is_active"])

        author = self._resolve_author()

        created_count = 0
        updated_count = 0
        failed_count = 0

        for source in FAQ_SOURCES:
            self.stdout.write(self.style.NOTICE(f"[抓取] {source['url']}"))
            parsed = self._fetch_source(source["url"], timeout=timeout)
            if not parsed.get("blocks"):
                failed_count += 1
                self.stdout.write(self.style.WARNING(f"  - 跳过：未提取到有效正文 {source['url']}"))
                continue

            title = source["title"] or parsed.get("title") or "常见问题说明"
            excerpt = self._build_excerpt(parsed["blocks"])
            if not excerpt:
                excerpt = f"{title}，本文整理了关键步骤与注意事项。"
            content_html = self._render_article_html(
                title=title,
                blocks=parsed["blocks"],
                images=parsed.get("images") or [],
                source_url=source["url"],
            )
            read_time = self._estimate_read_time(content_html)
            tags = self._ensure_tags(source.get("tags") or [])

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - 预览：title={title} blocks={len(parsed['blocks'])} images={len(parsed.get('images') or [])}"
                    )
                )
                continue

            article, created = Article.objects.update_or_create(
                slug=source["slug"],
                defaults={
                    "title": title,
                    "category": category,
                    "author": author,
                    "author_name": "客服中心",
                    "excerpt": excerpt[:500],
                    "summary": excerpt[:500],
                    "content": content_html,
                    "read_time": read_time,
                    "meta_title": title[:200],
                    "meta_description": excerpt[:300],
                    "meta_keywords": ",".join(["常见问题", *source.get("tags", [])])[:200],
                    "status": "published",
                    "is_top": False,
                    "is_hot": True,
                    "is_recommended": True,
                    "published_at": timezone.now(),
                },
            )
            article.tags.set(tags)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  - 已创建：{article.title}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"  - 已更新：{article.title}"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[完成-预览] 成功预览 {len(FAQ_SOURCES) - failed_count} 篇，失败 {failed_count} 篇。"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"[完成] 新增 {created_count} 篇，更新 {updated_count} 篇，失败 {failed_count} 篇。"
            )
        )

    def _resolve_author(self) -> User | None:
        return User.objects.filter(is_superuser=True).order_by("id").first() or User.objects.order_by("id").first()

    def _ensure_tags(self, names: list[str]) -> list[ArticleTag]:
        all_names = ["常见问题", *[clean_text(name) for name in names if clean_text(name)]]
        uniq_names: list[str] = []
        for name in all_names:
            if name not in uniq_names:
                uniq_names.append(name)

        tags: list[ArticleTag] = []
        for name in uniq_names:
            tag, _ = ArticleTag.objects.get_or_create(name=name)
            tags.append(tag)
        return tags

    def _fetch_source(self, url: str, timeout: int) -> dict[str, Any]:
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            if not response.encoding:
                response.encoding = response.apparent_encoding or "utf-8"
            doc = lxml_html.fromstring(response.text)
            doc.make_links_absolute(url)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"  - 抓取失败：{exc}"))
            return {"title": "", "blocks": [], "images": []}

        title = self._extract_title(doc)
        container = self._pick_content_node(doc)
        blocks, images = self._extract_blocks(container)

        if len(blocks) < 5 and doc.body is not None:
            fallback_blocks, fallback_images = self._extract_blocks(doc.body)
            if len(fallback_blocks) > len(blocks):
                blocks, images = fallback_blocks, fallback_images

        return {"title": title, "blocks": blocks, "images": images}

    def _extract_title(self, doc) -> str:
        candidates = [
            doc.xpath("string(//meta[@property='og:title']/@content)"),
            doc.xpath("string(//meta[@name='twitter:title']/@content)"),
            doc.xpath("string(//h1[1])"),
            doc.xpath("string(//title)"),
        ]
        for value in candidates:
            title = clean_text(value)
            if len(title) >= 4:
                return re.sub(r"\s*[\|\-｜].*$", "", title).strip()
        return ""

    def _pick_content_node(self, doc):
        scored_nodes: list[tuple[float, Any]] = []
        for xpath in CONTENT_CANDIDATE_XPATHS:
            for node in doc.xpath(xpath):
                if not hasattr(node, "xpath"):
                    continue
                text = clean_text(" ".join(node.xpath(".//text()")))
                text_len = len(text)
                if text_len < 220:
                    continue
                heading_bonus = len(node.xpath(".//h1|.//h2|.//h3")) * 40
                paragraph_bonus = min(len(node.xpath(".//p")) * 14, 180)
                score = float(text_len + heading_bonus + paragraph_bonus)
                scored_nodes.append((score, node))

        if scored_nodes:
            scored_nodes.sort(key=lambda item: item[0], reverse=True)
            return scored_nodes[0][1]
        return doc.body if doc.body is not None else doc

    def _extract_blocks(self, container) -> tuple[list[dict[str, Any]], list[str]]:
        if container is None:
            return [], []

        for node in container.xpath(NOISE_XPATH):
            try:
                node.drop_tree()
            except Exception:
                continue

        blocks: list[dict[str, Any]] = []
        images: list[str] = []
        list_buffer: list[str] = []
        seen_text: set[str] = set()

        def flush_list_buffer():
            nonlocal list_buffer
            if list_buffer:
                blocks.append({"type": "ul", "items": list_buffer[:8]})
                list_buffer = []

        for element in container.iter():
            if not isinstance(element.tag, str):
                continue
            tag = element.tag.lower()

            if tag in {"h1", "h2", "h3", "h4"}:
                flush_list_buffer()
                text = clean_text(element.text_content())
                if self._accept_heading(text):
                    key = f"h::{text.lower()}"
                    if key not in seen_text:
                        blocks.append({"type": "h2", "text": text})
                        seen_text.add(key)
                continue

            if tag == "p":
                flush_list_buffer()
                text = clean_text(element.text_content())
                if self._accept_paragraph(text):
                    key = f"p::{text.lower()}"
                    if key not in seen_text:
                        blocks.append({"type": "p", "text": text})
                        seen_text.add(key)
                continue

            if tag == "li":
                text = clean_text(element.text_content())
                if self._accept_list_item(text):
                    key = f"li::{text.lower()}"
                    if key not in seen_text and text not in list_buffer:
                        list_buffer.append(text)
                        seen_text.add(key)
                continue

            if tag == "img":
                src = (
                    clean_text(element.get("src"))
                    or clean_text(element.get("data-src"))
                    or clean_text(element.get("data-lazy-src"))
                    or clean_text(element.get("data-original"))
                )
                src = self._normalize_image_url(src)
                if src and src not in images:
                    images.append(src)

        flush_list_buffer()
        return blocks[:120], images[:12]

    def _normalize_image_url(self, value: str) -> str:
        src = clean_text(value)
        if not src:
            return ""
        if src.lower().startswith("data:"):
            return ""
        if src.lower().startswith("javascript:"):
            return ""
        if src.lower().endswith(".svg"):
            return ""
        return src

    def _accept_heading(self, text: str) -> bool:
        if len(text) < 4 or len(text) > 80:
            return False
        return not self._contains_skip_pattern(text)

    def _accept_paragraph(self, text: str) -> bool:
        if len(text) < 12 or len(text) > 520:
            return False
        if text.count("|") >= 4:
            return False
        return not self._contains_skip_pattern(text)

    def _accept_list_item(self, text: str) -> bool:
        if len(text) < 4 or len(text) > 180:
            return False
        return not self._contains_skip_pattern(text)

    def _contains_skip_pattern(self, text: str) -> bool:
        normalized = clean_text(text)
        return any(token in normalized for token in SKIP_TEXT_PATTERNS)

    def _build_excerpt(self, blocks: list[dict[str, Any]]) -> str:
        parts: list[str] = []
        for block in blocks:
            if block.get("type") == "p":
                parts.append(clean_text(block.get("text")))
            elif block.get("type") == "ul":
                parts.extend([clean_text(item) for item in block.get("items", [])])
            merged = " ".join(parts)
            if len(merged) >= 120:
                break
        excerpt = clean_text(" ".join(parts))
        return excerpt[:240]

    def _estimate_read_time(self, content_html: str) -> str:
        plain = re.sub(r"<[^>]+>", "", str(content_html or ""))
        chars = len(clean_text(plain))
        minutes = max(3, min(15, math.ceil(chars / 450) if chars else 3))
        return f"{minutes}分钟"

    def _render_article_html(
        self,
        title: str,
        blocks: list[dict[str, Any]],
        images: list[str],
        source_url: str,
    ) -> str:
        escaped_title = html.escape(clean_text(title))
        escaped_source = html.escape(clean_text(source_url), quote=True)
        fetch_time = timezone.now().strftime("%Y-%m-%d %H:%M")

        html_parts: list[str] = [
            '<section class="seo-article-shell">',
            '<header class="seo-article-header">',
            f"<h1>{escaped_title}</h1>",
            "</header>",
            '<section class="seo-summary"><p>本文为公开 FAQ 页面的重点整理版，补充为更易阅读的步骤说明。</p></section>',
        ]

        if images:
            cover = html.escape(images[0], quote=True)
            html_parts.extend(
                [
                    '<figure class="seo-inline-media">',
                    f'<img src="{cover}" alt="{escaped_title}" loading="lazy" />',
                    "<figcaption>来源页面示意图</figcaption>",
                    "</figure>",
                ]
            )

        for block in blocks:
            block_type = block.get("type")
            if block_type == "h2":
                html_parts.append(f"<h2>{html.escape(clean_text(block.get('text')))}</h2>")
                continue
            if block_type == "p":
                html_parts.append(f"<p>{html.escape(clean_text(block.get('text')))}</p>")
                continue
            if block_type == "ul":
                items = [clean_text(item) for item in block.get("items", []) if clean_text(item)]
                if not items:
                    continue
                html_parts.append("<ul>")
                for item in items:
                    html_parts.append(f"<li>{html.escape(item)}</li>")
                html_parts.append("</ul>")

        if len(images) > 1:
            html_parts.append('<section class="seo-media-block">')
            html_parts.append("<h2>相关图片</h2>")
            html_parts.append('<div class="seo-media-gallery">')
            for index, image in enumerate(images[1:9], start=1):
                safe_image = html.escape(image, quote=True)
                html_parts.extend(
                    [
                        '<figure class="seo-media-item">',
                        f'<img src="{safe_image}" alt="{escaped_title} - 图{index}" loading="lazy" />',
                        f"<figcaption>图 {index}</figcaption>",
                        "</figure>",
                    ]
                )
            html_parts.append("</div>")
            html_parts.append("</section>")

        html_parts.extend(
            [
                '<section class="seo-metadata">',
                f'<p><strong>原始来源：</strong><a href="{escaped_source}" target="_blank" rel="noopener noreferrer">{escaped_source}</a></p>',
                f"<p><strong>整理时间：</strong>{fetch_time}</p>",
                "</section>",
                "</section>",
            ]
        )

        return "\n".join(html_parts)
