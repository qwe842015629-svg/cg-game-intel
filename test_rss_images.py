import feedparser
import re

def check_images(url, name):
    print(f"--- Checking Images for {name} ---")
    d = feedparser.parse(url)
    if not d.entries:
        print("No entries.")
        return

    for entry in d.entries[:3]:
        print(f"Title: {entry.title}")
        image_url = None
        
        # Check standard media fields
        if 'media_content' in entry:
            image_url = entry.media_content[0]['url']
        elif 'media_thumbnail' in entry:
            image_url = entry.media_thumbnail[0]['url']
            
        # Check content/summary for <img> tags
        if not image_url:
            content = entry.get('content', [{'value': ''}])[0]['value'] or entry.get('summary', '') or entry.get('description', '')
            # print(f"Content Sample: {content[:200]}...") # Debug
            
            # Regex for <img src="...">
            match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
            if match:
                image_url = match.group(1)
        
        print(f"Image Found: {image_url}")
        print("-" * 10)

check_images("https://gnn.gamer.com.tw/rss.xml", "Bahamut")
check_images("https://gamingonphone.com/feed/", "GamingonPhone")
