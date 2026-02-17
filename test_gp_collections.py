from google_play_scraper import collection
import json

# Check available collections if possible, or just test standard ones
# Common collections: 'topselling_free', 'topselling_paid', 'grossing', 'movers_shakers', 'topselling_new_free', 'topselling_new_paid'
# The library maps these to constants.

try:
    print("Fetching US Top New Free Games...")
    # constant for TOP_NEW_FREE might be 'topselling_new_free' string or collection.TOP_NEW_FREE
    # Let's try string first as library often accepts strings.
    result = collection(
        collection='topselling_new_free',
        category='GAME',
        lang='en',
        country='us',
        count=5
    )
    print("Success: topselling_new_free")
    for app in result:
        print(f"- {app['title']} ({app['appId']})")
except Exception as e:
    print(f"Failed topselling_new_free: {e}")

try:
    print("\nFetching US Top Free Games...")
    result = collection(
        collection='topselling_free',
        category='GAME',
        lang='en',
        country='us',
        count=5
    )
    print("Success: topselling_free")
    for app in result:
        print(f"- {app['title']} ({app['appId']})")
except Exception as e:
    print(f"Failed topselling_free: {e}")
