from django.db.models import ExpressionWrapper, F, FloatField, Value
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from game_recharge.i18n_utils import localize_text, resolve_request_locale

from .models import Article, ArticleCategory, ArticleTag, Comment
from .serializers import (
    ArticleCategorySerializer,
    ArticleDetailSerializer,
    ArticleListSerializer,
    ArticleTagSerializer,
    CommentDetailSerializer,
    CommentSerializer,
)


class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """文章分类视图集（只读）"""

    queryset = ArticleCategory.objects.filter(is_active=True)
    serializer_class = ArticleCategorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order"]


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """文章视图集（只读）"""

    queryset = Article.objects.filter(status="published")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["game", "is_hot", "is_recommended"]
    search_fields = ["title", "summary", "content"]
    ordering_fields = ["published_at", "view_count", "like_count", "created_at"]
    ordering = ["-is_top", "-published_at"]

    @staticmethod
    def _attach_no_cache_headers(response: Response) -> Response:
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return ArticleListSerializer

    def _resolve_category_ids(self, category_query: str) -> list[int]:
        category_text = str(category_query or "").strip()
        if not category_text:
            return []
        if category_text.isdigit():
            return [int(category_text)]

        locale = resolve_request_locale(self.request)
        matched_ids: list[int] = []
        categories = ArticleCategory.objects.filter(is_active=True).only("id", "name", "name_i18n")

        for category in categories:
            candidate_names = {
                str(category.name or "").strip(),
                localize_text(category.name, getattr(category, "name_i18n", {}), locale),
            }

            raw_i18n = getattr(category, "name_i18n", {})
            if isinstance(raw_i18n, dict):
                candidate_names.update(str(value or "").strip() for value in raw_i18n.values())

            candidate_names = {name for name in candidate_names if name}
            if category_text in candidate_names:
                matched_ids.append(category.id)

        return matched_ids

    def get_queryset(self):
        """支持按分类 id 或多语言分类名称过滤。"""

        queryset = super().get_queryset()
        category_query = self.request.query_params.get("category")
        if not category_query:
            return queryset

        matched_ids = self._resolve_category_ids(category_query)
        if not matched_ids:
            return queryset.none()
        return queryset.filter(category_id__in=matched_ids)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self._attach_no_cache_headers(response)

    def retrieve(self, request, *args, **kwargs):
        """获取文章详情并增加浏览次数。"""

        instance = self.get_object()
        instance.increase_view_count()
        serializer = self.get_serializer(instance)
        response = Response(serializer.data)
        return self._attach_no_cache_headers(response)

    @action(detail=False, methods=["get"])
    def hot(self, request):
        """获取热门文章"""

        hot_articles = self.queryset.filter(is_hot=True)[:10]
        serializer = self.get_serializer(hot_articles, many=True)
        response = Response(serializer.data)
        return self._attach_no_cache_headers(response)

    @action(detail=False, methods=["get"])
    def recommended(self, request):
        """获取推荐文章"""

        recommended_articles = self.queryset.filter(is_recommended=True)[:10]
        serializer = self.get_serializer(recommended_articles, many=True)
        response = Response(serializer.data)
        return self._attach_no_cache_headers(response)

    @action(detail=False, methods=["get"])
    def top(self, request):
        """获取置顶文章"""

        top_articles = self.queryset.filter(is_top=True)
        serializer = self.get_serializer(top_articles, many=True)
        response = Response(serializer.data)
        return self._attach_no_cache_headers(response)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """点赞文章"""

        article = self.get_object()
        article.like_count += 1
        article.save(update_fields=["like_count"])
        return Response({"status": "liked", "like_count": article.like_count})

    @action(detail=False, methods=["get"])
    def smart_recommended(self, request):
        """基于浏览量和发布时间的推荐列表。"""

        limit = int(request.query_params.get("limit", 10))

        queryset = self.queryset.annotate(
            time_score=ExpressionWrapper(F("view_count") * 0.8 + Value(10.0), output_field=FloatField()),
        ).order_by("-is_top", "-time_score", "-published_at")[:limit]

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        return self._attach_no_cache_headers(response)


class ArticleTagViewSet(viewsets.ReadOnlyModelViewSet):
    """文章标签视图集（只读）"""

    queryset = ArticleTag.objects.all()
    serializer_class = ArticleTagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""

    queryset = Comment.objects.filter(is_approved=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["article", "parent"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CommentDetailSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        """创建评论时自动设置用户并更新计数。"""

        article = serializer.validated_data["article"]
        serializer.save(user=self.request.user)
        article.comment_count = article.comments.filter(is_approved=True).count()
        article.save(update_fields=["comment_count"])

    @action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        """获取评论回复列表"""

        comment = self.get_object()
        replies = comment.replies.filter(is_approved=True)
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)
