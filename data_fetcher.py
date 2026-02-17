import requests
import json
import time
import os
import re
import feedparser
from datetime import datetime

# Configuration
DATA_DIR = os.path.join("frontend", "public", "data")
DATA_FILE = os.path.join(DATA_DIR, "game_hub.json")

def ensure_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# --- 1. App Store Rankings (CN, US, JP) ---
def fetch_app_store_rankings():
    # Switching to iTunes RSS (older but supports genre filtering reliably)
    # Genre 6014 = Games
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
                # iTunes RSS structure is different from RSS Generator v2
                entry_list = data.get('feed', {}).get('entry', [])
                
                processed = []
                for idx, entry in enumerate(entry_list):
                    # Extract fields safely from iTunes RSS format
                    name = entry.get('im:name', {}).get('label', 'Unknown')
                    
                    images = entry.get('im:image', [])
                    icon = images[-1].get('label') if images else ''
                    
                    artist = entry.get('im:artist', {}).get('label', 'Unknown')
                    
                    # Link
                    raw_link = entry.get('link', [])
                    link = ''
                    if isinstance(raw_link, list) and len(raw_link) > 0:
                         link = raw_link[0].get('attributes', {}).get('href', '')
                    elif isinstance(raw_link, dict):
                         link = raw_link.get('attributes', {}).get('href', '')

                    # Release Date (not always available in this feed, use current date or skip)
                    # releaseDate label exists in some feeds
                    release_date = entry.get('im:releaseDate', {}).get('label', '')

                    processed.append({
                        "rank": idx + 1,
                        "id": entry.get('id', {}).get('attributes', {}).get('im:id'),
                        "title": name,
                        "icon": icon,
                        "artist": artist,
                        "url": link,
                        "release_date": release_date,
                        "genres": [entry.get('category', {}).get('attributes', {}).get('label', 'Game')]
                    })
                rankings[r['code']] = processed
                print(f"  - Got {len(processed)} games for {r['code']}")
            else:
                print(f"  - Failed {r['code']}: {resp.status_code}")
                rankings[r['code']] = []
        except Exception as e:
            print(f"Error fetching {r['name']}: {e}")
            rankings[r['code']] = []
            
    return rankings

# --- 2. New Releases (FreeToGame API) ---
def fetch_new_releases():
    print("Fetching New Releases from FreeToGame...")
    # Trying without platform filter first to see if it works, or check generic
    # 'https://www.freetogame.com/api/games?sort-by=release-date'
    url = "https://www.freetogame.com/api/games?sort-by=release-date"
    
    try:
        # Robust headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            games = resp.json()
            print(f"  - Got {len(games)} releases total, filtering for mobile...")
            
            # Filter client-side for platform 'Web Browser' or just take all?
            # User wants Mobile.
            # FreeToGame platforms: "PC (Windows)", "Web Browser". 
            # Actually FreeToGame is mostly PC/Browser. They have very few mobile games.
            # This might be why the 'mobile' query failed or returned 404 if not supported?
            # Let's check if we can get ANY games first.
            
            mobile_games = [g for g in games if "Android" in g.get('platform', '') or "iOS" in g.get('platform', '') or "Web" in g.get('platform', '')]
            
            # If no mobile games found, just return top 15 mixed (better than empty)
            if not mobile_games:
                print("  - No specific mobile games found, returning mixed.")
                return games[:20]
            
            return mobile_games[:20]
        else:
            print(f"FreeToGame failed: {resp.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching new releases: {e}")
        return []

# --- 3. Global Game News (RSS - Chinese) ---
def fetch_global_news():
    print("Fetching Global Game News (Chinese)...")
    # Using traditional/simplified Chinese sources that cover global gaming news
    feeds = [
        # Taiwan/Global (Traditional Chinese)
        {"name": "巴哈姆特", "url": "https://gnn.gamer.com.tw/rss.xml", "icon": "https://i2.bahamut.com.tw/baha_logo_s.png"},
        # Mainland/Global (Simplified Chinese)
        {"name": "机核网", "url": "https://www.gcores.com/rss", "icon": "https://image.gcores.com/assets/37527663-71a7-4b95-b040-97495033c94e.png"},
        {"name": "触乐", "url": "http://www.chuapp.com/feed", "icon": "http://www.chuapp.com/static/img/logo.png"},
        {"name": "爱玩网", "url": "http://play.163.com/special/0031444U/rss_newtop.xml", "icon": "https://img1.cache.netease.com/f2e/play/head/images/logo.png"},
        {"name": "游研社", "url": "https://www.yystv.cn/rss/feed", "icon": "https://www.yystv.cn/favicon.ico"}
    ]
    
    articles = []
    for f in feeds:
        try:
            print(f"  - Parsing {f['name']}...")
            d = feedparser.parse(f['url'])
            if not d.entries:
                print(f"    - No entries for {f['name']}")
                continue
                
            # Fetch up to 8 items per source to reach ~40 total
            for entry in d.entries[:8]:
                # Extract image
                img = ""
                if 'media_content' in entry and len(entry.media_content) > 0:
                    img = entry.media_content[0]['url']
                elif 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
                    img = entry.media_thumbnail[0]['url']
                elif 'enclosures' in entry and len(entry.enclosures) > 0:
                    img = entry.enclosures[0]['href']
                
                # Regex fallback for image in content
                if not img:
                    content = entry.get('content', [{'value': ''}])[0]['value'] if 'content' in entry else entry.get('summary', '')
                    match = re.search(r'<img.*?src="(.*?)"', content)
                    if match:
                        img = match.group(1)
                
                # Clean title
                title = entry.title
                
                # Date
                published = entry.get('published', '')
                try:
                    # Attempt to parse common date formats
                    if len(published) > 5:
                         # Simple check, real parsing is complex without dateutil
                         published_str = published[:16] 
                    else:
                        published_str = datetime.now().strftime("%Y-%m-%d")
                except:
                    published_str = published

                articles.append({
                    "source": f['name'],
                    "source_icon": f['icon'],
                    "title": title,
                    "link": entry.link,
                    "time": published_str,
                    "image": img
                })
        except Exception as e:
            print(f"Error fetching {f['name']}: {e}")
            
    # Shuffle slightly to mix sources? Or just sort by time?
    # Sorting by string time is risky but let's try to just return the list.
    # Frontend can shuffle or display as is.
    print(f"  - Total news items: {len(articles)}")
    return articles

# --- 4. Wiki Activity (RSS) ---
def fetch_wiki_activity():
    print("Fetching Wiki Activity...")
    # Genshin Wiki as primary example
    url = "https://genshin-impact.fandom.com/wiki/Special:NewPages?feed=rss"
    try:
        d = feedparser.parse(url)
        activity = []
        for entry in d.entries[:12]:
            activity.append({
                "title": entry.title,
                "user": entry.author if 'author' in entry else "Wiki User",
                "link": entry.link,
                "time": entry.get('updated', '') or entry.get('published', ''),
                "source": "Genshin Wiki"
            })
        print(f"  - Got {len(activity)} wiki updates")
        return activity
    except Exception as e:
        print(f"Error fetching Wiki: {e}")
        return []

def main():
    ensure_directory()
    
    print("Starting Data Fetch...")
    
    rankings = fetch_app_store_rankings()
    new_releases = fetch_new_releases()
    strategies = fetch_global_news()
    wiki_radar = fetch_wiki_activity()
    
    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": str(int(time.time())),  # Force update even if content is same
        "rankings": rankings,
        "new_releases": new_releases,
        "strategies": strategies,
        "wiki_radar": wiki_radar
    }
    
    # Validation stats
    count_rank = sum(len(v) for v in rankings.values())
    count_new = len(new_releases)
    count_strat = len(strategies)
    print(f"Summary: {count_rank} Rankings, {count_new} New Games, {count_strat} Articles")
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Data saved to {DATA_FILE}")

if __name__ == "__main__":
    main()
