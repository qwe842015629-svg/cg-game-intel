import feedparser
import json
import re

def parse_rss_feed(url, name):
    print(f"--- Parsing {name} ({url}) ---")
    try:
        feed = feedparser.parse(url)
        print(f"Status: {feed.status if 'status' in feed else 'Unknown'}")
        if feed.entries:
            print(f"Found {len(feed.entries)} entries.")
            for entry in feed.entries[:3]:
                print(f"Title: {entry.title}")
                print(f"Link: {entry.link}")
                # Try to find image in content/summary/media_content
                image_url = None
                
                # Method 1: media_content
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                
                # Method 2: media_thumbnail
                if not image_url and 'media_thumbnail' in entry:
                    image_url = entry.media_thumbnail[0]['url']
                
                # Method 3: content/summary (regex search)
                if not image_url:
                    content = entry.get('content', [{'value': ''}])[0]['value'] or entry.get('summary', '')
                    img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
                    if img_match:
                        image_url = img_match.group(1)
                
                print(f"Image: {image_url}")
                print("-" * 20)
        else:
            print("No entries found or feed is empty/blocked.")
    except Exception as e:
        print(f"Error parsing feed: {e}")

if __name__ == "__main__":
    # Test multiple feeds
    feeds = [
        ("Pocket Gamer", "https://www.pocketgamer.com/rss/"),
        ("TouchArcade", "https://toucharcade.com/feed/"),
        ("Bahamut GNN", "https://gnn.gamer.com.tw/rss.xml"),
        ("GamingonPhone", "https://gamingonphone.com/feed/"),
        ("GameSpot Mobile", "https://www.gamespot.com/feeds/mashup/?type=1200"), # Type 1200 usually news
        ("Reddit AndroidGaming", "https://www.reddit.com/r/AndroidGaming/new/.rss"),
    ]
    
    for name, url in feeds:
        parse_rss_feed(url, name)
