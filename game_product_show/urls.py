from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductShowCategoryViewSet, ProductShowViewSet

router = DefaultRouter()
router.register(r'categories', ProductShowCategoryViewSet, basename='productshowcategory')
router.register(r'shows', ProductShowViewSet, basename='productshow')

urlpatterns = [
    path('', include(router.urls)),
]
