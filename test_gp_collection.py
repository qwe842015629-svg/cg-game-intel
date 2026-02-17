from google_play_scraper import collection, Sort
import json

def test_collection():
    regions = [
        {"code": "hk", "name": "Hong Kong"},
        {"code": "us", "name": "USA"},
        {"code": "sg", "name": "Singapore"}
    ]

    for r in regions:
        print(f"--- Fetching Top Free Games for {r['name']} ({r['code']}) ---")
        try:
            # collection(collection, category, lang, country, sort, count)
            # TOP_FREE = 'topselling_free'
            results = collection(
                collection='TOP_FREE',
                category='GAME',
                lang='en', # Keep English for consistency or use 'zh' for HK? Let's use 'en' for now to check structure.
                country=r['code'],
                sort=Sort.NEWEST, # or Sort.NEWEST is for reviews? For collection it might be ignored or different. 
                # actually 'sort' param in collection might not be valid or used differently. 
                # Let's check documentation or source if possible, or just try defaults.
                # 'sort' is usually for reviews. For collection, the order IS the rank.
                count=5
            )
            
            for idx, app in enumerate(results):
                print(f"#{idx+1}: {app['title']} ({app['appId']})")
                
        except Exception as e:
            print(f"Error fetching {r['name']}: {e}")

if __name__ == "__main__":
    test_collection()
