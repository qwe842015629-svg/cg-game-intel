import os
import django
import sys
from django.test import RequestFactory

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_recharge.settings")
django.setup()

from game_page.views import GamePageViewSet
from game_page.models import GamePageCategory

def test_view():
    print("--- Testing ViewSet Logic ---")
    
    # 构造请求
    factory = RequestFactory()
    # 假设分类ID为1
    request = factory.get('/api/game-pages/', {'category': '1'})
    
    # 必须给 request 设置 user，因为 permission_classes 里有 IsAuthenticatedOrReadOnly
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    
    view = GamePageViewSet.as_view({'get': 'list'})
    
    try:
        response = view(request)
        print(f"Status Code: {response.status_code}")
        print(f"Data: {response.data}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_view()
