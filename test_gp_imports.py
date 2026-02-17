from google_play_scraper import collection
import json

try:
    print(collection)
except:
    print("Cannot import 'collection'. Check package.")
    
# Maybe it's exposed differently or as 'top_charts'?
# It's usually 'collection' but let's check what's available.
import google_play_scraper
print(dir(google_play_scraper))
