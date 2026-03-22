from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BannerViewSet,
    HomeLayoutViewSet,
    SiteConfigViewSet,
    MediaAssetViewSet,
    NovelWorkViewSet,
    PlazaPostViewSet,
    NovelDraftCurrentView,
    CoquiTtsSynthesizeView,
    trigger_wiki_update,
    get_wiki_hub_data,
)

router = DefaultRouter()
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'layouts', HomeLayoutViewSet, basename='layout')
router.register(r'site-config', SiteConfigViewSet, basename='site-config')
router.register(r'media', MediaAssetViewSet, basename='media')
router.register(r'novel-works', NovelWorkViewSet, basename='novel-work')
router.register(r'plaza-posts', PlazaPostViewSet, basename='plaza-post')

urlpatterns = [
    path('wiki-update/', trigger_wiki_update, name='wiki-update'),
    path('wiki-hub/', get_wiki_hub_data, name='wiki-hub'),
    path('novel-drafts/current/', NovelDraftCurrentView.as_view(), name='novel-draft-current'),
    path('tts/coqui/synthesize/', CoquiTtsSynthesizeView.as_view(), name='tts-coqui-synthesize'),
    path('', include(router.urls)),
]
