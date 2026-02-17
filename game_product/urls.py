from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameCategoryViewSet, GameViewSet, ProductTypeViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', GameCategoryViewSet, basename='game-category')
router.register(r'games', GameViewSet, basename='game')
router.register(r'product-types', ProductTypeViewSet, basename='product-type')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
