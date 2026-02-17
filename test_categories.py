import os
import django
import sys
from django.test import RequestFactory

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_recharge.settings")
django.setup()

from game_page.views import GamePageCategoryViewSet

def test_categories():
    print("--- Testing Category API ---")
    factory = RequestFactory()
    request = factory.get('/api/game-pages/categories/')
    
    # 设置用户
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    
    view = GamePageCategoryViewSet.as_view({'get': 'list'})
    
    try:
        response = view(request)
        print(f"Status Code: {response.status_code}")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_categories()
