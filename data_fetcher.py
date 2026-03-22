import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Configuration
DATA_DIR = os.path.join("frontend", "public", "data")
DATA_FILE = os.path.join(DATA_DIR, "game_hub.json")
REQUEST_TIMEOUT = 15
PER_SOURCE_LIMIT = 8
GLOBAL_NEWS_LIMIT = 120

# Headers for scraping
COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

NEWS_SOURCES = [
    {"name": "IGN中国", "url": "https://www.ign.com.cn/"},
    {"name": "机核", "url": "https://www.gcores.com/articles"},
    {"name": "游研社", "url": "https://www.yystv.cn/news"},
    {"name": "3DM", "url": "https://www.3dmgame.com/news/"},
    {"name": "游民星空", "url": "https://www.gamersky.com/news/"},
    {"name": "巴哈姆特", "url": "https://gnn.gamer.com.tw/"},
    {"name": "17173", "url": "https://news.17173.com/"},
    {"name": "电玩巴士", "url": "https://www.tgbus.com/"},
    {"name": "游侠网", "url": "https://www.ali213.net/news/"},
    {"name": "篝火营地", "url": "https://gouhuo.qq.com/games/"},
    {"name": "新浪游戏", "url": "https://games.sina.com.cn/"},
    {"name": "IGN", "url": "https://www.ign.com/articles"},
    {"name": "GameSpot", "url": "https://www.gamespot.com/news/"},
    {"name": "Eurogamer", "url": "https://www.eurogamer.net/latest"},
    {"name": "PC Gamer", "url": "https://www.pcgamer.com/news/"},
    {"name": "Polygon", "url": "https://www.polygon.com/gaming"},
    {"name": "Rock Paper Shotgun", "url": "https://www.rockpapershotgun.com/games"},
    {"name": "VG247", "url": "https://www.vg247.com/"},
    {"name": "Destructoid", "url": "https://www.destructoid.com/category/news/"},
    {"name": "Nintendo Life", "url": "https://www.nintendolife.com/news"},
    {"name": "Kotaku", "url": "https://kotaku.com/latest"},
    {"name": "Gematsu", "url": "https://www.gematsu.com/"},
    {"name": "VGC", "url": "https://www.videogameschronicle.com/news/"},
]

try:
    from zoneinfo import ZoneInfo

    SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
except Exception:
    SHANGHAI_TZ = timezone(timedelta(hours=8))


def ensure_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def build_session():
    session = requests.Session()
    session.headers.update(COMMON_HEADERS)
    return session


def normalize_time(value):
    """Convert any time representation to Asia/Shanghai ISO format."""
    dt = parse_datetime_any(value)
    if dt is None:
        dt = datetime.now(tz=SHANGHAI_TZ)
    return dt.astimezone(SHANGHAI_TZ).strftime("%Y-%m-%d %H:%M:%S")


def parse_datetime_any(value):
    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except Exception:
        pass

    text = str(value).strip()
    if not text:
        return None

    iso_candidate = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso_candidate)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        pass

    try:
        parsed = parsedate_to_datetime(text)
        if parsed is not None:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
    except Exception:
        pass

    known_formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%b %d, %Y",
    )
    for fmt in known_formats:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def parse_time_score(value):
    parsed = parse_datetime_any(value)
    if parsed is None:
        return 0
    return int(parsed.timestamp())


def clean_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def absolute_url(base_url, href):
    link = clean_text(href)
    if not link:
        return ""
    if link.startswith("javascript:") or link.startswith("mailto:"):
        return ""
    try:
        return urljoin(base_url, link.split("#", 1)[0])
    except Exception:
        return ""


def domain_suffix(hostname):
    host = (hostname or "").lower().strip(".")
    parts = [part for part in host.split(".") if part]
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return host


def same_site(url_a, url_b):
    host_a = domain_suffix(urlparse(url_a).netloc)
    host_b = domain_suffix(urlparse(url_b).netloc)
    return bool(host_a and host_b and host_a == host_b)


def looks_like_article_url(url):
    path = urlparse(url).path.lower()
    if not path or path == "/":
        return False

    if re.search(r"\.(?:jpg|jpeg|png|webp|gif|svg|ico|pdf)$", path):
        return False

    noise_keywords = (
        "/list/",
        "/tag/",
        "/tags/",
        "/search",
        "/about",
        "/privacy",
        "/terms",
        "/contact",
        "/login",
        "/register",
        "/account",
        "/forum",
        "/community",
        "/video/",
        "/videos/",
        "/podcast/",
    )
    if any(keyword in path for keyword in noise_keywords):
        return False

    article_keywords = (
        "/news",
        "/article",
        "/articles",
        "/story",
        "/stories",
        "/updates",
        "/post/",
        "/posts/",
        "/n/",
    )
    if any(keyword in path for keyword in article_keywords):
        return True

    # Many sites publish with date-based paths.
    if re.search(r"/20\d{2}/\d{1,2}/\d{1,2}/", path):
        return True

    # Fallback: path depth >= 2 often indicates content pages.
    return len([part for part in path.split("/") if part]) >= 2


def choose_image_url(raw):
    if isinstance(raw, str):
        return clean_text(raw)
    if isinstance(raw, list):
        for item in raw:
            img = choose_image_url(item)
            if img:
                return img
        return ""
    if isinstance(raw, dict):
        for key in ("url", "contentUrl", "thumbnailUrl", "src"):
            img = clean_text(raw.get(key))
            if img:
                return img
    return ""


def iter_json_nodes(payload):
    stack = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            yield current
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def normalize_news_item(source_name, base_url, title, link, raw_time="", image=""):
    normalized_title = clean_text(title)
    normalized_link = absolute_url(base_url, link)
    if not normalized_title or len(normalized_title) < 8:
        return None
    if not normalized_link:
        return None
    if not looks_like_article_url(normalized_link):
        return None
    if not same_site(base_url, normalized_link):
        return None

    return {
        "source": source_name,
        "title": normalized_title[:220],
        "link": normalized_link,
        "time": normalize_time(raw_time),
        "image": absolute_url(base_url, image) if image else "",
    }


def dedupe_news(items, limit=None):
    seen = set()
    output = []
    for item in sorted(items, key=lambda row: parse_time_score(row.get("time")), reverse=True):
        key = f"{item.get('link', '')}|{item.get('title', '').lower()}"
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
        if limit and len(output) >= limit:
            break
    return output


def extract_ldjson_articles(soup, source_name, source_url):
    rows = []
    scripts = soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)})
    for script in scripts:
        raw_text = script.string or script.get_text()
        if not raw_text:
            continue
        raw_text = raw_text.strip()
        if not raw_text:
            continue
        try:
            payload = json.loads(raw_text)
        except Exception:
            continue

        for node in iter_json_nodes(payload):
            node_type = str(node.get("@type", "")).lower()
            if not node_type:
                continue
            if "article" not in node_type and "news" not in node_type and "posting" not in node_type:
                continue

            title = node.get("headline") or node.get("name") or ""
            link = node.get("url") or node.get("mainEntityOfPage") or ""
            if isinstance(link, dict):
                link = link.get("@id") or link.get("url") or ""

            published = node.get("datePublished") or node.get("dateCreated") or node.get("dateModified") or ""
            image = choose_image_url(node.get("image") or node.get("thumbnailUrl") or "")

            item = normalize_news_item(source_name, source_url, title, link, published, image)
            if item:
                rows.append(item)
    return rows


def extract_time_from_container(container):
    if container is None:
        return ""

    time_node = container.find("time")
    if time_node:
        for key in ("datetime", "content", "title"):
            value = clean_text(time_node.get(key))
            if value:
                return value
        text_value = clean_text(time_node.get_text(" ", strip=True))
        if text_value:
            return text_value

    text = clean_text(container.get_text(" ", strip=True))
    matched = re.search(
        r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)",
        text,
    )
    if matched:
        return matched.group(1)
    return ""


def extract_article_tag_items(soup, source_name, source_url):
    rows = []
    for article in soup.find_all("article"):
        anchor = article.find("a", href=True)
        if not anchor:
            continue

        heading = article.find(["h1", "h2", "h3", "h4"])
        title = clean_text((heading.get_text(" ", strip=True) if heading else "") or anchor.get_text(" ", strip=True))
        link = anchor.get("href")
        raw_time = extract_time_from_container(article)

        image_url = ""
        image_node = article.find("img")
        if image_node:
            for key in ("src", "data-src", "data-original", "data-lazy-src"):
                value = clean_text(image_node.get(key))
                if value:
                    image_url = value
                    break

        item = normalize_news_item(source_name, source_url, title, link, raw_time, image_url)
        if item:
            rows.append(item)
    return rows


def extract_anchor_items(soup, source_name, source_url):
    rows = []
    container_selectors = [
        "main a[href]",
        "section a[href]",
        "div a[href]",
    ]
    anchors = []
    for selector in container_selectors:
        anchors.extend(soup.select(selector))

    for anchor in anchors:
        title = clean_text(anchor.get_text(" ", strip=True))
        if len(title) < 8:
            continue
        link = anchor.get("href")
        raw_time = extract_time_from_container(anchor.parent)

        image_url = ""
        image_node = anchor.find("img")
        if image_node:
            for key in ("src", "data-src", "data-original", "data-lazy-src"):
                value = clean_text(image_node.get(key))
                if value:
                    image_url = value
                    break

        item = normalize_news_item(source_name, source_url, title, link, raw_time, image_url)
        if item:
            rows.append(item)

        if len(rows) >= PER_SOURCE_LIMIT * 6:
            break
    return rows


def fetch_source_news(session, source):
    source_name = source["name"]
    source_url = source["url"]
    print(f"  - Scraping {source_name}: {source_url}")

    try:
        response = session.get(source_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except Exception as exc:
        print(f"    ! Failed to fetch {source_name}: {exc}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    candidates = []
    candidates.extend(extract_ldjson_articles(soup, source_name, source_url))
    candidates.extend(extract_article_tag_items(soup, source_name, source_url))
    candidates.extend(extract_anchor_items(soup, source_name, source_url))

    normalized = dedupe_news(candidates, limit=PER_SOURCE_LIMIT)
    print(f"    + {len(normalized)} items")
    return normalized


# --- 1. App Store Rankings ---
def fetch_app_store_rankings(session):
    regions = [
        {"code": "CN", "name": "China", "url": "https://itunes.apple.com/cn/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "US", "name": "USA", "url": "https://itunes.apple.com/us/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "JP", "name": "Japan", "url": "https://itunes.apple.com/jp/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "HK", "name": "Hong Kong", "url": "https://itunes.apple.com/hk/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "TW", "name": "Taiwan", "url": "https://itunes.apple.com/tw/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "SEA", "name": "Southeast Asia (VN)", "url": "https://itunes.apple.com/vn/rss/topfreeapplications/limit=100/genre=6014/json"},
    ]

    rankings = {}
    for region in regions:
        try:
            print(f"Fetching App Store Rankings for {region['name']}...")
            response = session.get(region["url"], timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            entry_list = data.get("feed", {}).get("entry", [])
            processed = []

            for idx, entry in enumerate(entry_list):
                name = entry.get("im:name", {}).get("label", "Unknown")
                images = entry.get("im:image", [])
                icon = images[-1].get("label") if images else ""
                artist = entry.get("im:artist", {}).get("label", "Unknown")
                raw_link = entry.get("link", [])
                link = ""
                if isinstance(raw_link, list) and raw_link:
                    link = raw_link[0].get("attributes", {}).get("href", "")
                elif isinstance(raw_link, dict):
                    link = raw_link.get("attributes", {}).get("href", "")

                processed.append(
                    {
                        "rank": idx + 1,
                        "id": entry.get("id", {}).get("attributes", {}).get("im:id"),
                        "title": name,
                        "icon": icon,
                        "artist": artist,
                        "url": link,
                        "global_hot": False,
                    }
                )
            rankings[region["code"]] = processed
        except Exception as exc:
            print(f"Error fetching {region['name']}: {exc}")
            rankings[region["code"]] = []
    return rankings


# --- 2. Global News (Direct scraping, no RSS) ---
def fetch_global_news(session):
    print("Fetching Global News via direct site scraping...")
    all_items = []
    for source in NEWS_SOURCES:
        items = fetch_source_news(session, source)
        all_items.extend(items)

    deduped = dedupe_news(all_items, limit=GLOBAL_NEWS_LIMIT)
    return deduped


def build_wiki_radar(news_items, limit=24):
    radar = []
    for item in news_items[:limit]:
        radar.append(
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "time": item.get("time", ""),
                "source": item.get("source", ""),
            }
        )
    return radar


def main(return_data=False):
    ensure_directory()
    print(f"Job Started at {datetime.now()}")
    session = build_session()

    rankings = fetch_app_store_rankings(session)
    news = fetch_global_news(session)
    wiki_radar = build_wiki_radar(news)

    data = {
        "last_updated": datetime.now(tz=SHANGHAI_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": str(int(time.time())),
        "rankings": rankings,
        "strategies": news,
        "new_releases": [],
        "wiki_radar": wiki_radar,
    }

    print(
        f"Stats: {sum(len(v) for v in rankings.values())} Ranked Games, "
        f"{len(news)} News Items"
    )

    with open(DATA_FILE, "w", encoding="utf-8") as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)

    print(f"Job Finished. Data saved to {DATA_FILE}")

    if return_data:
        return data
    return data


if __name__ == "__main__":
    main()
