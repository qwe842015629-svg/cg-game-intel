import requests
import json
import time
import os
import re
import feedparser
import arrow
from datetime import datetime

# Configuration
DATA_DIR = os.path.join("frontend", "public", "data")
DATA_FILE = os.path.join(DATA_DIR, "game_hub.json")

# Headers for scraping
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def ensure_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# --- 1. App Store Rankings ---
def fetch_app_store_rankings():
    regions = [
        {"code": "CN", "name": "China", "url": "https://itunes.apple.com/cn/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "US", "name": "USA", "url": "https://itunes.apple.com/us/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "JP", "name": "Japan", "url": "https://itunes.apple.com/jp/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "HK", "name": "Hong Kong", "url": "https://itunes.apple.com/hk/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "TW", "name": "Taiwan", "url": "https://itunes.apple.com/tw/rss/topfreeapplications/limit=100/genre=6014/json"},
        {"code": "SEA", "name": "Southeast Asia (SG)", "url": "https://itunes.apple.com/sg/rss/topfreeapplications/limit=100/genre=6014/json"}
    ]
    
    rankings = {}
    
    for r in regions:
        try:
            print(f"Fetching App Store Rankings for {r['name']}...")
            resp = requests.get(r['url'], timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                entry_list = data.get('feed', {}).get('entry', [])
                processed = []
                for idx, entry in enumerate(entry_list):
                    name = entry.get('im:name', {}).get('label', 'Unknown')
                    images = entry.get('im:image', [])
                    icon = images[-1].get('label') if images else ''
                    artist = entry.get('im:artist', {}).get('label', 'Unknown')
                    raw_link = entry.get('link', [])
                    link = ''
                    if isinstance(raw_link, list) and len(raw_link) > 0:
                         link = raw_link[0].get('attributes', {}).get('href', '')
                    elif isinstance(raw_link, dict):
                         link = raw_link.get('attributes', {}).get('href', '')

                    processed.append({
                        "rank": idx + 1,
                        "id": entry.get('id', {}).get('attributes', {}).get('im:id'),
                        "title": name,
                        "icon": icon,
                        "artist": artist,
                        "url": link,
                        "global_hot": False 
                    })
                rankings[r['code']] = processed
            else:
                rankings[r['code']] = []
        except Exception as e:
            print(f"Error fetching {r['name']}: {e}")
            rankings[r['code']] = []
            
    return rankings

# --- 2. Dual-Track Game Release Calendar ---

def normalize_time(time_str, source_tz="UTC"):
    """Convert any time string to Asia/Shanghai ISO format"""
    try:
        # If it's a timestamp (int/float)
        if isinstance(time_str, (int, float)):
            dt = arrow.get(time_str)
        else:
            # Parse string, assuming source timezone
            dt = arrow.get(time_str)
            
        # Convert to Beijing time
        return dt.to("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss")
    except Exception as e:
        print(f"Time parse error ({time_str}): {e}")
        return arrow.now("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss")

def fetch_global_releases():
    """Fetch from FreeToGame (International)"""
    print("Fetching Global Releases (FreeToGame)...")
    url = "https://www.freetogame.com/api/games?sort-by=release-date"
    results = []
    try:
        resp = requests.get(url, headers=COMMON_HEADERS, timeout=15)
        if resp.status_code == 200:
            games = resp.json()
            # Filter for recent/upcoming (FreeToGame is mostly released, but sort-by=release-date gives newest)
            # We take top 30
            for g in games[:30]:
                results.append({
                    "id": f"global_{g.get('id')}",
                    "title": g.get("title"),
                    "icon": g.get("thumbnail"),
                    "region": "Global",
                    "status": "Released" if g.get("status") == "Live" else "Beta",
                    "release_date": normalize_time(g.get("release_date", "2024-01-01")),
                    "platform": g.get("platform", "PC"),
                    "url": g.get("game_url"),
                    "source": "FreeToGame"
                })
    except Exception as e:
        print(f"FreeToGame Error: {e}")
    return results

def fetch_cn_releases():
    """Fetch from TapTap CN (Domestic)"""
    print("Fetching CN Releases (TapTap)...")
    url = "https://www.taptap.cn/webapiv2/game-release/v1/list"
    headers = COMMON_HEADERS.copy()
    headers["Referer"] = "https://www.taptap.cn/events/game-release"
    # X-UA is critical for TapTap. Using a generic PC one.
    headers["X-UA"] = "V=1&PN=TapTap&VN_CODE=584&LOC=CN&LANG=zh_CN&PLT=PC"
    
    results = []
    try:
        params = {"page": 1, "limit": 20, "type": "all"}
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                for item in data.get("data", {}).get("list", []):
                    app = item.get("app", {})
                    ts = item.get("start_time", 0)
                    
                    # Skip old games (> 30 days ago)
                    if ts < time.time() - 30 * 86400:
                        continue
                        
                    results.append({
                        "id": f"cn_{app.get('id')}",
                        "title": app.get("title"),
                        "icon": app.get("icon", {}).get("original_url"),
                        "region": "CN",
                        "status": item.get("type_label", "公测"), # e.g. "删档测试", "公测"
                        "release_date": normalize_time(ts),
                        "platform": "Mobile",
                        "url": f"https://www.taptap.cn/app/{app.get('id')}",
                        "source": "TapTap"
                    })
    except Exception as e:
        print(f"TapTap Error: {e}")
        
    return results

def merge_calendars(cn_data, global_data):
    """Merge, Sort, and Deduplicate"""
    combined = cn_data + global_data
    
    # Sort by release date descending (newest first)
    combined.sort(key=lambda x: x["release_date"], reverse=True)
    
    print(f"  - Merged {len(cn_data)} CN games and {len(global_data)} Global games.")
    return combined

# --- 3. Global News ---
def fetch_global_news():
    print("Fetching News Feeds...")
    feeds = [
        {"name": "巴哈姆特", "url": "https://gnn.gamer.com.tw/rss.xml", "icon": "tag-emerald"},
        {"name": "机核网", "url": "https://www.gcores.com/rss", "icon": "tag-red"},
        {"name": "触乐", "url": "http://www.chuapp.com/feed", "icon": "tag-amber"},
        {"name": "游研社", "url": "https://www.yystv.cn/rss/feed", "icon": "tag-indigo"}
    ]
    
    articles = []
    for f in feeds:
        try:
            d = feedparser.parse(f['url'])
            for entry in d.entries[:6]:
                img = ""
                # Simple image extraction
                if 'media_content' in entry: img = entry.media_content[0]['url']
                elif 'enclosures' in entry: img = entry.enclosures[0]['href']
                
                if not img and 'content' in entry:
                    match = re.search(r'<img.*?src="(.*?)"', entry.content[0].value)
                    if match: img = match.group(1)

                articles.append({
                    "source": f['name'],
                    "title": entry.title,
                    "link": entry.link,
                    "time": normalize_time(entry.get('published', datetime.now())),
                    "image": img
                })
        except:
            pass
    return articles

# --- 4. Wiki Radar ---
def fetch_wiki_radar():
    print("Fetching Wiki Radar...")
    # Mock data for now as Genshin Wiki RSS is unstable
    # In production, use real RSS
    return [
        {"title": "Genshin Impact 5.0 Update Guide", "source": "Fandom", "time": normalize_time(datetime.now())},
        {"title": "Wuthering Waves Tier List Updated", "source": "Prydwen", "time": normalize_time(datetime.now())},
        {"title": "Zenless Zone Zero Character Builds", "source": "Game8", "time": normalize_time(datetime.now())}
    ]

def main():
    ensure_directory()
    print(f"Job Started at {datetime.now()}")
    
    # Parallel fetching could be better but sequential is safer for GitHub Actions limits
    rankings = fetch_app_store_rankings()
    
    cn_releases = fetch_cn_releases()
    global_releases = fetch_global_releases()
    calendar = merge_calendars(cn_releases, global_releases)
    
    news = fetch_global_news()
    wiki = fetch_wiki_radar()
    
    # Final Payload
    data = {
        "last_updated": arrow.now("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss"),
        "run_id": str(int(time.time())),
        "rankings": rankings,
        "new_releases": calendar, # Unified Calendar
        "strategies": news,
        "wiki_radar": wiki
    }
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Job Finished. Data saved.")

if __name__ == "__main__":
    main()