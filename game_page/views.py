from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, F

from .models import GamePage, GamePageCategory
from .serializers import (
    GamePageListSerializer,
    GamePageDetailSerializer,
    GamePageCreateUpdateSerializer,
    GamePageCategorySerializer
)


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
        # 如果是管理员，显示所有分类
        if self.request.user.is_staff:
            return queryset
        # 前端只显示激活的分类
        return queryset.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取所有激活的分类"""
        categories = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class GamePageViewSet(viewsets.ModelViewSet):
    """游戏页面视图集"""
    queryset = GamePage.objects.select_related('category', 'author').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_hot', 'is_recommended', 'platform']
    search_fields = ['title', 'title_tw', 'description', 'content', 'seo_keywords']
    ordering_fields = ['view_count', 'like_count', 'published_at', 'created_at', 'sort_order']
    ordering = ['sort_order', '-published_at']
    
    def get_serializer_class(self):
        """根据不同操作返回不同的序列化器"""
        if self.action == 'list':
            return GamePageListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GamePageCreateUpdateSerializer
        return GamePageDetailSerializer
    
    def get_queryset(self):
        """根据权限过滤查询集"""
        queryset = super().get_queryset()
        
        # 调试模式：暂时返回所有数据，忽略状态过滤
        return queryset
        
        # 原有逻辑暂存
        # if self.request.user.is_staff:
        #     return queryset
        
        # now = timezone.now()
        # return queryset.filter(
        #     Q(status='published') & 
        #     (Q(published_at__isnull=True) | Q(published_at__lte=now))
        # )
    
    def retrieve(self, request, *args, **kwargs):
        """获取详情时自动增加浏览次数"""
        instance = self.get_object()
        # 增加浏览次数
        if not request.user.is_staff:  # 管理员访问不计数
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
        return Response({
            'status': 'success',
            'like_count': game_page.like_count
        })
    
    @action(detail=False, methods=['get'])
    def top_pages(self, request):
        """获取置顶页面 (此处沿用 is_recommended 或 sort_order)"""
        # is_top 字段已移除，使用 sort_order 或 is_recommended
        top_pages = self.get_queryset().order_by('sort_order')[:5]
        serializer = self.get_serializer(top_pages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hot_pages(self, request):
        """获取热门页面"""
        hot_pages = self.get_queryset().filter(is_hot=True).order_by('-view_count')[:10]
        serializer = self.get_serializer(hot_pages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended_pages(self, request):
        """获取推荐页面"""
        recommended = self.get_queryset().filter(is_recommended=True)[:6]
        serializer = self.get_serializer(recommended, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_slug(self, request):
        """根据 slug 获取页面详情"""
        slug = request.query_params.get('slug')
        if not slug:
            return Response({'error': '缺少 slug 参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            page = self.get_queryset().get(slug=slug)
            # 增加浏览次数
            if not request.user.is_staff:
                page.increase_view_count()
            serializer = GamePageDetailSerializer(page, context={'request': request})
            return Response(serializer.data)
        except GamePage.DoesNotExist:
            return Response({'error': '页面不存在'}, status=status.HTTP_404_NOT_FOUND)
