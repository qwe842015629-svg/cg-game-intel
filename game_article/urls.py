from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleCategoryViewSet, ArticleViewSet, ArticleTagViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'categories', ArticleCategoryViewSet, basename='article-category')
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'tags', ArticleTagViewSet, basename='article-tag')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
