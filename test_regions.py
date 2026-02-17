from google_play_scraper import search
import json

def test_region_search():
    regions = [
        {"name": "Taiwan/HongKong", "term": "最新手遊", "lang": "zh", "country": "tw"},
        {"name": "USA", "term": "New Games", "lang": "en", "country": "us"},
        {"name": "SEA (SG)", "term": "New Games", "lang": "en", "country": "sg"}
    ]
    
    for r in regions:
        print(f"--- Testing {r['name']} ---")
        try:
            results = search(r['term'], lang=r['lang'], country=r['country'], n_hits=3)
            for app in results:
                print(f"[{r['name']}] {app['title']} ({app['appId']}) - Score: {app['score']}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_region_search()
