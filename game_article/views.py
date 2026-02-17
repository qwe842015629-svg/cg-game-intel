from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import ArticleCategory, Article, ArticleTag, Comment
from .serializers import (
    ArticleCategorySerializer, ArticleListSerializer, ArticleDetailSerializer,
    ArticleTagSerializer, CommentSerializer, CommentDetailSerializer
)


class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """文章分类视图集（只读）"""
    queryset = ArticleCategory.objects.filter(is_active=True)
    serializer_class = ArticleCategorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order']


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """文章视图集（只读）"""
    queryset = Article.objects.filter(status='published')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # 移除category，因为我们使用自定义的category__name过滤
    filterset_fields = ['game', 'is_hot', 'is_recommended']
    search_fields = ['title', 'summary', 'content']
    ordering_fields = ['published_at', 'view_count', 'like_count', 'created_at']
    ordering = ['-is_top', '-published_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    def get_queryset(self):
        """重写查询集以支持按分类名称过滤"""
        queryset = super().get_queryset()
        
        # 支持按分类名称过滤
        category_name = self.request.query_params.get('category', None)
        if category_name:
            queryset = queryset.filter(category__name=category_name)
        
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """获取文章详情，增加浏览次数"""
        instance = self.get_object()
        instance.increase_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门文章"""
        hot_articles = self.queryset.filter(is_hot=True)[:10]
        serializer = self.get_serializer(hot_articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """获取推荐文章"""
        recommended_articles = self.queryset.filter(is_recommended=True)[:10]
        serializer = self.get_serializer(recommended_articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top(self, request):
        """获取置顶文章"""
        top_articles = self.queryset.filter(is_top=True)
        serializer = self.get_serializer(top_articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """点赞文章"""
        article = self.get_object()
        article.like_count += 1
        article.save(update_fields=['like_count'])
        return Response({'status': 'liked', 'like_count': article.like_count})
    
    @action(detail=False, methods=['get'])
    def smart_recommended(self, request):
        """
        智能推荐文章 - 基于点击量和发布时间的推荐算法
        算法：权重 = 浏览次数 * 0.6 + 时间分数 * 0.4
        时间分数：越新的文章分数越高
        """
        from django.db.models import F, ExpressionWrapper, FloatField, Value
        from django.utils import timezone
        from datetime import timedelta
        
        # 获取显示数量，默认10篇
        limit = int(request.query_params.get('limit', 10))
        
        # 计算时间分数：最近90天内的文章，越新分数越高
        now = timezone.now()
        time_window = now - timedelta(days=90)  # 扩大时间窗口到90天
        
        # 获取所有已发布的文章
        queryset = self.queryset
        
        # 计算推荐分数
        # 优先显示最近90天内的文章，但也包含较旧的文章
        queryset = queryset.annotate(
            days_old=ExpressionWrapper(
                (now - F('published_at')),
                output_field=FloatField()
            ),
            # 如果是90天内的文章，计算时间分数；否则给予低分
            time_score=ExpressionWrapper(
                F('view_count') * 0.8 + Value(10.0),  # 简化算法，主要看浏览量
                output_field=FloatField()
            )
        ).order_by('-is_top', '-time_score', '-published_at')[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ArticleTagViewSet(viewsets.ReadOnlyModelViewSet):
    """文章标签视图集（只读）"""
    queryset = ArticleTag.objects.all()
    serializer_class = ArticleTagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.filter(is_approved=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['article', 'parent']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        """创建评论时自动设置用户"""
        article = serializer.validated_data['article']
        serializer.save(user=self.request.user)
        # 更新文章评论数
        article.comment_count = article.comments.filter(is_approved=True).count()
        article.save(update_fields=['comment_count'])

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """获取评论的回复列表"""
        comment = self.get_object()
        replies = comment.replies.filter(is_approved=True)
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)
