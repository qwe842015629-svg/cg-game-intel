from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductShowCategory, ProductShow
from .serializers import (
    ProductShowCategorySerializer,
    ProductShowListSerializer,
    ProductShowDetailSerializer
)


class ProductShowCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """产品展示分类视图集(只读)"""
    queryset = ProductShowCategory.objects.filter(is_active=True)
    serializer_class = ProductShowCategorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order']


class ProductShowViewSet(viewsets.ReadOnlyModelViewSet):
    """游戏产品展示视图集(只读)"""
    queryset = ProductShow.objects.filter(status='published').select_related('category', 'game')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'is_top', 'is_hot', 'is_recommended']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'view_count', 'like_count', 'created_at']
    ordering = ['-is_top', '-published_at']
    
    def get_serializer_class(self):
        """根据action选择序列化器"""
        if self.action == 'retrieve':
            return ProductShowDetailSerializer
        return ProductShowListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """获取详情时增加浏览量"""
        instance = self.get_object()
        instance.increase_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门展示页"""
        queryset = self.get_queryset().filter(is_hot=True)[:6]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """获取推荐展示页"""
        queryset = self.get_queryset().filter(is_recommended=True)[:6]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
