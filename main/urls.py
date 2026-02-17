from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BannerViewSet, HomeLayoutViewSet, SiteConfigViewSet, MediaAssetViewSet

router = DefaultRouter()
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'layouts', HomeLayoutViewSet, basename='layout')
router.register(r'site-config', SiteConfigViewSet, basename='site-config')
router.register(r'media', MediaAssetViewSet, basename='media')

urlpatterns = [
    path('', include(router.urls)),
]
