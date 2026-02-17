from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GamePageViewSet, GamePageCategoryViewSet

router = DefaultRouter()
router.register(r'categories', GamePageCategoryViewSet, basename='gamepage-category')
router.register(r'pages', GamePageViewSet, basename='gamepage')

app_name = 'game_page'

urlpatterns = [
    path('', include(router.urls)),
]
