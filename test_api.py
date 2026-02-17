import os
import django
import sys
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_recharge.settings")
django.setup()

from game_page.views import GamePageViewSet
from game_page.models import GamePage, GamePageCategory

def test_api():
    print("--- Checking Database ---")
    games = GamePage.objects.all()
    for g in games:
        print(f"Game: {g.title}, ID: {g.id}, Status: {g.status}, Category: {g.category}, Published: {g.published_at}")
        
    categories = GamePageCategory.objects.all()
    for c in categories:
        print(f"Category: {c.name}, ID: {c.id}")

    print("\n--- Testing API ViewSet ---")
    factory = APIRequestFactory()
    
    # 模拟前端请求: /game-pages/?category=1 (假设分类ID为1)
    # 这里的 ID 需要根据实际查出来的 ID 填
    if categories.exists():
        cat_id = categories.first().id
        request = factory.get(f'/game-pages/', {'category': cat_id})
        view = GamePageViewSet.as_view({'get': 'list'})
        response = view(request)
        print(f"Requesting category={cat_id}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Data Count: {len(response.data.get('results', []))}")
        print(f"Response Data: {response.data}")
    else:
        print("No categories found to test.")

if __name__ == "__main__":
    test_api()
