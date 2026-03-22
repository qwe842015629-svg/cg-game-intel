import logging
import time

from django.db.models import F, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import GamePage, GamePageCategory
from .serializers import (
    GamePageCategorySerializer,
    GamePageCreateUpdateSerializer,
    GamePageDetailSerializer,
    GamePageListSerializer,
)

logger = logging.getLogger(__name__)


def _set_public_cache_headers(request, response: Response, max_age: int = 120) -> None:
    """Add CDN/browser cache headers for anonymous GET responses."""
    if request.method != 'GET':
        return

    user = getattr(request, 'user', None)
    if getattr(user, 'is_authenticated', False):
        return

    response['Cache-Control'] = (
        f'public, max-age={max_age}, s-maxage={max_age}, stale-while-revalidate=60'
    )

    existing_vary = response.get('Vary', '')
    vary_tokens = {
        token.strip()
        for token in str(existing_vary).split(',')
        if token.strip()
    }
    vary_tokens.update({'Accept', 'Accept-Language', 'Origin'})
    response['Vary'] = ', '.join(sorted(vary_tokens))


class GamePageListPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 60


class GamePageCategoryViewSet(viewsets.ModelViewSet):
    """游戏页面分类视图集"""

    queryset = GamePageCategory.objects.all()
    serializer_class = GamePageCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'created_at', 'name']
    ordering = ['sort_order', '-created_at']

    def get_queryset(self):
        """只显示激活的分类（前端访问）"""
        queryset = super().get_queryset()
        if getattr(self.request.user, 'is_staff', False):
            return queryset
        return queryset.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        _set_public_cache_headers(request, response, max_age=120)
        return response

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取所有激活的分类"""
        categories = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        response = Response(serializer.data)
        _set_public_cache_headers(request, response, max_age=120)
        return response


class GamePageViewSet(viewsets.ModelViewSet):
    """游戏页面视图集"""

    queryset = GamePage.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GamePageListPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_hot', 'is_recommended', 'platform']
    search_fields = ['title', 'title_tw', 'description', 'content', 'seo_keywords']
    ordering_fields = ['view_count', 'like_count', 'published_at', 'created_at', 'sort_order']
    ordering = ['sort_order', '-published_at']

    LIST_ONLY_FIELDS = (
        'id',
        'title',
        'title_i18n',
        'title_tw',
        'slug',
        'category_id',
        'category__name',
        'category__name_i18n',
        'developer',
        'platform',
        'platform_i18n',
        'regions',
        'regions_i18n',
        'icon_external_url',
        'icon_image',
        'banner_image',
        'description',
        'description_i18n',
        'description_tw',
        'status',
        'is_hot',
        'is_recommended',
        'sort_order',
        'view_count',
        'like_count',
        'published_at',
        'created_at',
    )

    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action == 'list':
            return GamePageListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return GamePageCreateUpdateSerializer
        return GamePageDetailSerializer

    def get_queryset(self):
        """根据权限过滤查询集"""
        queryset = super().get_queryset()

        if self.action == 'list':
            # List endpoint: avoid loading heavy detail columns and unused author relation.
            queryset = queryset.select_related('category').only(*self.LIST_ONLY_FIELDS)
        else:
            queryset = queryset.select_related('category', 'author')

        if getattr(self.request.user, 'is_staff', False):
            return queryset

        now = timezone.now()
        return queryset.filter(
            Q(status='published') & (Q(published_at__isnull=True) | Q(published_at__lte=now))
        )

    def list(self, request, *args, **kwargs):
        start_ts = time.perf_counter()

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        db_start_ts = time.perf_counter()
        rows = list(page) if page is not None else list(queryset)
        db_elapsed_ms = (time.perf_counter() - db_start_ts) * 1000

        serialize_start_ts = time.perf_counter()
        serializer = self.get_serializer(rows, many=True)
        serialized_data = serializer.data
        serialize_elapsed_ms = (time.perf_counter() - serialize_start_ts) * 1000

        response = self.get_paginated_response(serialized_data) if page is not None else Response(serialized_data)
        _set_public_cache_headers(request, response, max_age=120)

        total_elapsed_ms = (time.perf_counter() - start_ts) * 1000
        logger.info(
            'game_pages.list perf db_ms=%.1f serialize_ms=%.1f total_ms=%.1f rows=%s paginated=%s',
            db_elapsed_ms,
            serialize_elapsed_ms,
            total_elapsed_ms,
            len(rows),
            page is not None,
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        """获取详情时自动增加浏览次数"""
        instance = self.get_object()
        if not getattr(request.user, 'is_staff', False):
            instance.increase_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞"""
        game_page = self.get_object()
        game_page.like_count = F('like_count') + 1
        game_page.save(update_fields=['like_count'])
        game_page.refresh_from_db()
        return Response({'status': 'success', 'like_count': game_page.like_count})

    @action(detail=False, methods=['get'])
    def top_pages(self, request):
        """获取置顶页面 (此处沿用 is_recommended 或 sort_order)"""
        top_pages = self.get_queryset().order_by('sort_order')[:5]
        serializer = self.get_serializer(top_pages, many=True)
        response = Response(serializer.data)
        _set_public_cache_headers(request, response, max_age=120)
        return response

    @action(detail=False, methods=['get'])
    def hot_pages(self, request):
        """获取热门页面"""
        hot_pages = self.get_queryset().filter(is_hot=True).order_by('-view_count')[:10]
        serializer = self.get_serializer(hot_pages, many=True)
        response = Response(serializer.data)
        _set_public_cache_headers(request, response, max_age=120)
        return response

    @action(detail=False, methods=['get'])
    def recommended_pages(self, request):
        """获取推荐页面"""
        recommended = self.get_queryset().filter(is_recommended=True)[:6]
        serializer = self.get_serializer(recommended, many=True)
        response = Response(serializer.data)
        _set_public_cache_headers(request, response, max_age=120)
        return response

    @action(detail=False, methods=['get'])
    def by_slug(self, request):
        """根据 slug 获取页面详情"""
        slug = request.query_params.get('slug')
        if not slug:
            return Response({'error': '缺少 slug 参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            page = self.get_queryset().get(slug=slug)
            if not getattr(request.user, 'is_staff', False):
                page.increase_view_count()
            serializer = GamePageDetailSerializer(page, context={'request': request})
            return Response(serializer.data)
        except GamePage.DoesNotExist:
            return Response({'error': '页面不存在'}, status=status.HTTP_404_NOT_FOUND)
