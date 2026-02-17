from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CrawlerTaskViewSet,
    LLMApiConnectionTestAPIView,
    LLMApiSettingAPIView,
    SeoArticleViewSet,
    SeoKeywordWeightViewSet,
    SeoRewriteAPIView,
)

router = DefaultRouter()
router.register(r"tasks", CrawlerTaskViewSet, basename="seo-task")
router.register(r"keywords", SeoKeywordWeightViewSet, basename="seo-keyword")
router.register(r"articles", SeoArticleViewSet, basename="seo-article")

urlpatterns = [
    path("llm-settings/current/", LLMApiSettingAPIView.as_view(), name="llm-settings-current"),
    path("llm-settings/test/", LLMApiConnectionTestAPIView.as_view(), name="llm-settings-test"),
    path("rewrite/", SeoRewriteAPIView.as_view(), name="seo-rewrite"),
    path("", include(router.urls)),
]
