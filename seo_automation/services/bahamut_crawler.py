import random
import re
from datetime import datetime, timedelta
from html import unescape
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import requests


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


class BahamutCrawler:
    """
    Two-stage crawler:
    1) Crawl board pages to collect topic links.
    2) Crawl each topic page to extract structured content.
    """

    def __init__(self, timeout_seconds: int = 20, retries: int = 2):
        self.timeout_seconds = timeout_seconds
        self.retries = max(1, retries)
        self.session = requests.Session()

    def crawl_board(
        self,
        *,
        bsn: int | None = None,
        source_url: str = "",
        start_page: int = 1,
        end_page: int = 1,
        max_posts: int = 20,
        keyword: str = "",
        include_details: bool = True,
    ) -> dict[str, Any]:
        board_url, board_bsn = self._resolve_board_info(bsn=bsn, source_url=source_url)
        if not board_url:
            raise ValueError("Invalid board url or bsn")

        start_page = max(1, int(start_page))
        end_page = max(start_page, int(end_page))
        max_posts = max(1, int(max_posts))
        keyword_lower = (keyword or "").strip().lower()

        topic_links: list[dict[str, Any]] = []
        link_seen: set[str] = set()
        page_errors: list[dict[str, str]] = []

        # Stage 1: collect topic links
        for page in range(start_page, end_page + 1):
            page_url = self._build_page_url(board_url=board_url, page=page)
            try:
                html = self._get_text(page_url, referer=board_url)
            except Exception as exc:
                page_errors.append(
                    {
                        "page": str(page),
                        "page_url": page_url,
                        "error": str(exc)[:200],
                    }
                )
                continue

            for candidate in self._extract_topic_rows(html=html, board_base_url=board_url):
                topic_url = candidate["topic_url"]
                if topic_url in link_seen:
                    continue
                link_seen.add(topic_url)

                title = (candidate.get("title") or "").strip()
                if keyword_lower and keyword_lower not in title.lower():
                    continue

                topic_links.append(candidate)
                if len(topic_links) >= max_posts:
                    break

            if len(topic_links) >= max_posts:
                break

        posts: list[dict[str, Any]] = []
        detail_errors: list[dict[str, str]] = []
        if include_details:
            detail_result = self.crawl_topic_details(topic_links=topic_links)
            posts = detail_result.get("posts", []) or []
            detail_errors = detail_result.get("detail_errors", []) or []

        return {
            "board_url": board_url,
            "bsn": board_bsn,
            "start_page": start_page,
            "end_page": end_page,
            "max_posts": max_posts,
            "keyword": keyword,
            "topic_links": topic_links,
            "links_count": len(topic_links),
            "posts": posts,
            "details_count": len(posts),
            "page_errors": page_errors,
            "detail_errors": detail_errors,
        }

    def crawl_topic_details(self, *, topic_links: list[dict[str, Any]]) -> dict[str, Any]:
        """Stage 2 only: crawl topic links and extract structured detail posts."""
        posts: list[dict[str, Any]] = []
        detail_errors: list[dict[str, str]] = []

        for candidate in topic_links or []:
            topic_url = candidate.get("topic_url", "")
            if not topic_url:
                continue

            try:
                detail = self.fetch_topic_detail(
                    topic_url=topic_url,
                    fallback_title=candidate.get("title", ""),
                )
            except Exception as exc:
                detail_errors.append(
                    {
                        "topic_url": topic_url,
                        "error": str(exc)[:220],
                    }
                )
                continue

            detail["list_time"] = candidate.get("list_time", "")
            detail["list_reply_count"] = candidate.get("reply_count", "")
            detail["list_popularity"] = candidate.get("popularity", "")
            detail["source_stage"] = "detail_extracted"

            if not detail.get("content"):
                fallback = "\n".join(
                    text
                    for text in [
                        detail.get("title", ""),
                        detail.get("snippet", ""),
                        detail.get("list_time", ""),
                    ]
                    if text
                ).strip()
                if fallback:
                    detail["content"] = fallback
                    detail["snippet"] = fallback[:220]
                    detail["source_stage"] = "detail_fallback"

            posts.append(detail)

        return {
            "posts": posts,
            "details_count": len(posts),
            "detail_errors": detail_errors,
        }

    def fetch_topic_detail(self, topic_url: str, fallback_title: str = "") -> dict[str, Any]:
        html = self._get_text(topic_url, referer="https://forum.gamer.com.tw/")
        title = self._extract_topic_title(html) or fallback_title or "Untitled"

        post_blocks = self._extract_post_blocks(html)
        comments: list[dict[str, str]] = []
        for block in post_blocks:
            content = self._clean_text(block.get("content_html", ""))
            if not content:
                continue
            comments.append(
                {
                    "author": block.get("author", ""),
                    "published_at": block.get("published_at", ""),
                    "content": content,
                }
            )

        comments = self._select_primary_comments(comments)

        if not comments:
            fallback_html = self._extract_main_content_html(html)
            fallback_text = self._clean_text(fallback_html)
            if fallback_text:
                comments.append({"author": "", "published_at": "", "content": fallback_text})

        merged_content = "\n\n".join(item["content"] for item in comments[:8]).strip()
        image_urls = self._extract_image_urls_from_html(html=html, base_url=topic_url)
        published_at = next(
            (item.get("published_at", "") for item in comments if item.get("published_at")),
            "",
        ) or self._extract_publish_time(html)

        return {
            "topic_url": topic_url,
            "title": title,
            "content": merged_content,
            "published_at": published_at,
            "image_urls": image_urls,
            "snippet": merged_content[:220],
            "comment_count": len(comments),
            "comments": comments[:12],
        }

    def _resolve_board_info(self, *, bsn: int | None, source_url: str) -> tuple[str, int | None]:
        if bsn:
            bsn_int = int(bsn)
            return f"https://forum.gamer.com.tw/B.php?bsn={bsn_int}", bsn_int

        raw = (source_url or "").strip()
        if not raw:
            return "", None

        if raw.isdigit():
            bsn_int = int(raw)
            return f"https://forum.gamer.com.tw/B.php?bsn={bsn_int}", bsn_int

        parsed = urlparse(raw)
        if not parsed.scheme:
            raw = f"https://{raw.lstrip('/')}"
            parsed = urlparse(raw)

        query = parse_qs(parsed.query)
        bsn_str = query.get("bsn", [""])[0]
        if bsn_str.isdigit():
            bsn_int = int(bsn_str)
            return f"https://forum.gamer.com.tw/B.php?bsn={bsn_int}", bsn_int

        if "forum.gamer.com.tw" in parsed.netloc and parsed.path.lower().endswith("/b.php"):
            return raw, None

        return "", None

    def _build_page_url(self, *, board_url: str, page: int) -> str:
        parsed = urlparse(board_url)
        query = parse_qs(parsed.query)
        query["page"] = [str(page)]
        query_string = urlencode(query, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"

    def _get_text(self, url: str, referer: str = "") -> str:
        last_error: Exception | None = None
        for _ in range(self.retries):
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
            if referer:
                headers["Referer"] = referer
            try:
                response = self.session.get(url, headers=headers, timeout=(12, self.timeout_seconds))
                response.raise_for_status()
                response.encoding = response.apparent_encoding or response.encoding or "utf-8"
                return response.text
            except Exception as exc:
                last_error = exc

        if last_error:
            raise last_error
        raise RuntimeError("failed to fetch page")

    def _extract_topic_rows(self, *, html: str, board_base_url: str) -> list[dict[str, str]]:
        rows = self._extract_topic_rows_from_table(html=html, board_base_url=board_base_url)
        if rows:
            return rows
        return self._extract_topic_rows_from_anchors(html=html, board_base_url=board_base_url)

    def _extract_topic_rows_from_table(self, *, html: str, board_base_url: str) -> list[dict[str, str]]:
        candidates: list[dict[str, str]] = []
        seen: set[str] = set()

        row_pattern = re.compile(
            r'(<tr[^>]+class="[^"]*b-list__row[^"]*"[^>]*>[\s\S]*?</tr>)',
            flags=re.I,
        )
        rows = row_pattern.findall(html)

        for row_html in rows:
            href_match = re.search(r'href="([^"]*C\.php\?[^"]*bsn=\d+[^"]*snA=\d+[^"]*)"', row_html, re.I)
            if not href_match:
                continue

            topic_url = urljoin(board_base_url, unescape(href_match.group(1))).replace("&amp;", "&")
            if topic_url in seen:
                continue

            title_match = re.search(
                r'<p[^>]*class="[^"]*b-list__main__title[^"]*"[^>]*>(.*?)</p>',
                row_html,
                flags=re.I | re.S,
            )
            raw_title = title_match.group(1) if title_match else href_match.group(1)
            title = self._clean_text(raw_title)
            if self._is_skip_title(title):
                continue

            span_values = re.findall(r"<span[^>]*>(.*?)</span>", row_html, flags=re.I | re.S)
            cleaned_values = [self._clean_text(value) for value in span_values]
            cleaned_values = [value for value in cleaned_values if value]
            reply_count = cleaned_values[0] if len(cleaned_values) > 0 else ""
            popularity = cleaned_values[1] if len(cleaned_values) > 1 else ""

            time_match = re.search(
                r'<td[^>]*class="[^"]*b-list__time[^"]*"[^>]*>[\s\S]*?<a[^>]*>(.*?)</a>',
                row_html,
                flags=re.I | re.S,
            )
            list_time = self._clean_text(time_match.group(1)) if time_match else ""

            seen.add(topic_url)
            candidates.append(
                {
                    "topic_url": topic_url,
                    "title": title,
                    "list_time": list_time,
                    "reply_count": reply_count,
                    "popularity": popularity,
                }
            )

        return candidates

    def _extract_topic_rows_from_anchors(self, *, html: str, board_base_url: str) -> list[dict[str, str]]:
        candidates: list[dict[str, str]] = []
        seen: set[str] = set()
        pattern = re.compile(
            r'<a[^>]+href="([^"]*C\.php\?[^"]*bsn=\d+[^"]*snA=\d+[^"]*)"[^>]*>(.*?)</a>',
            flags=re.I | re.S,
        )

        for href, raw_text in pattern.findall(html):
            topic_url = urljoin(board_base_url, unescape(href)).replace("&amp;", "&")
            if topic_url in seen:
                continue

            title = self._clean_text(raw_text)
            if self._is_skip_title(title):
                continue

            seen.add(topic_url)
            candidates.append(
                {
                    "topic_url": topic_url,
                    "title": title,
                    "list_time": "",
                    "reply_count": "",
                    "popularity": "",
                }
            )

        return candidates

    def _extract_topic_title(self, html: str) -> str:
        patterns = [
            re.compile(r'<h1[^>]*class="[^"]*c-post__header__title[^"]*"[^>]*>(.*?)</h1>', re.I | re.S),
            re.compile(r"<title>(.*?)</title>", re.I | re.S),
        ]
        for pattern in patterns:
            match = pattern.search(html)
            if not match:
                continue
            title = self._clean_text(match.group(1))
            title = re.sub(r"\s*[-|]\s*巴哈姆特.*$", "", title).strip()
            if title:
                return title
        return ""

    def _extract_post_blocks(self, html: str) -> list[dict[str, str]]:
        content_blocks = self._extract_div_blocks_by_class(html, "c-article__content")
        if not content_blocks:
            return []

        author_blocks = re.findall(
            r'<div[^>]+class="[^"]*c-post__header__author[^"]*"[^>]*>[\s\S]*?</div>',
            html,
            flags=re.I,
        )
        authors: list[str] = []
        for block in author_blocks:
            names = re.findall(r"<a[^>]*>(.*?)</a>", block, flags=re.I | re.S)
            clean_names = [self._clean_text(name) for name in names]
            clean_names = [name for name in clean_names if name]
            authors.append(clean_names[-1] if clean_names else "")

        published_at_values = [
            value.strip() for value in re.findall(r'data-mtime="([^"]+)"', html, flags=re.I)
        ]

        rows: list[dict[str, str]] = []
        for idx, content_html in enumerate(content_blocks):
            rows.append(
                {
                    "author": authors[idx] if idx < len(authors) else "",
                    "published_at": published_at_values[idx] if idx < len(published_at_values) else "",
                    "content_html": content_html,
                }
            )
        return rows

    def _extract_main_content_html(self, html: str) -> str:
        blocks = self._extract_div_blocks_by_class(html, "c-article__content")
        if blocks:
            return "\n".join(blocks[:3])

        article_match = re.search(r"<article[^>]*>([\s\S]*?)</article>", html, flags=re.I)
        if article_match:
            return article_match.group(1)
        return html

    def _extract_div_blocks_by_class(self, html: str, class_name: str) -> list[str]:
        open_pattern = re.compile(
            rf"<div[^>]*class=[\"'][^\"']*{re.escape(class_name)}[^\"']*[\"'][^>]*>",
            flags=re.I,
        )
        blocks: list[str] = []
        for match in open_pattern.finditer(html):
            start = match.start()
            end = self._find_matching_div_end(html=html, start_pos=match.end())
            if end <= start:
                continue
            blocks.append(html[start:end])
        return blocks

    def _find_matching_div_end(self, *, html: str, start_pos: int) -> int:
        depth = 1
        pos = start_pos
        tag_pattern = re.compile(r"<div\b|</div>", flags=re.I)
        while True:
            found = tag_pattern.search(html, pos)
            if not found:
                return len(html)

            token = found.group(0).lower()
            depth = depth - 1 if token.startswith("</div") else depth + 1
            pos = found.end()
            if depth == 0:
                return pos

    def _extract_image_urls_from_html(self, html: str, base_url: str) -> list[str]:
        urls: list[str] = []
        seen: set[str] = set()
        image_sources = re.findall(
            r'<img[^>]+(?:src|data-src|data-original)=["\']([^"\']+)["\']',
            html,
            flags=re.I,
        )

        for raw_src in image_sources:
            src = unescape(raw_src).strip()
            if not src:
                continue
            full = urljoin(base_url, src)
            if full in seen:
                continue
            seen.add(full)
            urls.append(full)

        if not urls:
            og_image = re.search(
                r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
                html,
                flags=re.I,
            )
            if og_image:
                value = og_image.group(1).strip()
                if value:
                    urls.append(value)

        return urls

    def _extract_publish_time(self, html: str) -> str:
        data_mtime = re.search(r'data-mtime="([^"]+)"', html, flags=re.I)
        if data_mtime:
            return data_mtime.group(1).strip()

        iso = re.search(r'datetime="([^"]+)"', html, flags=re.I)
        if iso:
            return iso.group(1).strip()

        explicit = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)", html)
        if explicit:
            return explicit.group(1).strip()

        relative = re.search(r"(\d+\s*(?:分鐘前|分钟前|小時前|小时前|天前)|昨天\s*\d{1,2}:\d{2}|剛剛|刚刚)", html)
        if relative:
            parsed = self._parse_relative_time(relative.group(1))
            if parsed:
                return parsed

        return ""

    def _parse_relative_time(self, raw: str) -> str:
        now = datetime.now()
        text = (raw or "").strip()

        if text in {"剛剛", "刚刚"}:
            return now.strftime("%Y-%m-%d %H:%M:%S")

        minute = re.search(r"(\d+)\s*(?:分鐘前|分钟前)", text)
        if minute:
            return (now - timedelta(minutes=int(minute.group(1)))).strftime("%Y-%m-%d %H:%M:%S")

        hour = re.search(r"(\d+)\s*(?:小時前|小时前)", text)
        if hour:
            return (now - timedelta(hours=int(hour.group(1)))).strftime("%Y-%m-%d %H:%M:%S")

        day = re.search(r"(\d+)\s*天前", text)
        if day:
            return (now - timedelta(days=int(day.group(1)))).strftime("%Y-%m-%d %H:%M:%S")

        yday = re.search(r"昨天\s*(\d{1,2}:\d{2})", text)
        if yday:
            dt = now - timedelta(days=1)
            return f"{dt.strftime('%Y-%m-%d')} {yday.group(1)}:00"

        return ""

    def _is_skip_title(self, title: str) -> bool:
        normalized = (title or "").strip()
        if len(normalized) < 4:
            return True

        skip_words = ("置頂", "置顶", "公告", "精華", "精华", "板規", "站務", "板务")
        if any(word in normalized for word in skip_words):
            return True

        return self._is_noise_line(normalized)

    def _clean_text(self, html_or_text: str) -> str:
        value = html_or_text or ""
        value = re.sub(r"<blockquote[\s\S]*?</blockquote>", " ", value, flags=re.I)
        value = re.sub(r"<script[\s\S]*?</script>", " ", value, flags=re.I)
        value = re.sub(r"<style[\s\S]*?</style>", " ", value, flags=re.I)
        value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
        value = re.sub(r"</p>", "\n", value, flags=re.I)
        value = re.sub(r"<[^>]+>", " ", value)
        value = unescape(value)
        value = re.sub(r"\r\n?", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        value = re.sub(r"[ \t]+", " ", value)

        lines = [line.strip(" \t\u3000") for line in value.split("\n")]
        lines = [
            line
            for line in lines
            if line
            and len(line) >= 2
            and not self._is_noise_line(line)
            and not self._is_comment_like_text(line)
        ]

        deduped: list[str] = []
        for line in lines:
            if deduped and deduped[-1] == line:
                continue
            deduped.append(line)

        return "\n".join(deduped).strip()

    def _is_noise_line(self, line: str) -> bool:
        if re.fullmatch(r"https?://\S+", line, flags=re.I):
            return True
        if re.fullmatch(r"[\W_]+", line):
            return True
        if re.fullmatch(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\s]+", line):
            return True

        semantic_chars = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]", line)
        if len(semantic_chars) <= 1 and len(line) <= 4:
            return True

        return False

    def _is_comment_like_text(self, line: str) -> bool:
        value = (line or "").strip()
        if not value:
            return True
        patterns = [
            r"(?i)\b(?:gp|bp)\b",
            r"@[\w\u4e00-\u9fff]{2,20}",
            r"(留言|回覆|回复|樓主|楼主|網友|网友|推|噓|→)",
            r"(簽到|签到|卡位|沙發|沙发|路過|路过)",
            r"^\d+\s*[Ff樓楼].*",
            r"^\+?\d+\s*(?:GP|BP)?$",
        ]
        for pattern in patterns:
            if re.search(pattern, value):
                return True
        if len(value) < 8 and re.search(r"[!?？！~～]{2,}", value):
            return True
        return False

    def _select_primary_comments(self, comments: list[dict[str, str]]) -> list[dict[str, str]]:
        if not comments:
            return []

        selected: list[dict[str, str]] = []
        for idx, item in enumerate(comments):
            content = str(item.get("content") or "").strip()
            if not content:
                continue
            if idx == 0:
                selected.append(item)
                continue
            if len(content) < 80:
                continue
            if self._is_comment_like_text(content):
                continue
            selected.append(item)
            if len(selected) >= 3:
                break

        if selected:
            return selected
        return comments[:1]
