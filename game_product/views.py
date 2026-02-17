from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import GameCategory, Game, ProductType, Product
from .serializers import (
    GameCategorySerializer, GameListSerializer, GameDetailSerializer,
    ProductTypeSerializer, ProductListSerializer, ProductDetailSerializer
)


class GameCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """游戏分类视图集（只读）"""
    queryset = GameCategory.objects.filter(is_active=True)
    serializer_class = GameCategorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order']


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """游戏视图集（只读）"""
    queryset = Game.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_hot']
    search_fields = ['name', 'name_en', 'developer']
    ordering_fields = ['sort_order', 'view_count', 'created_at']
    ordering = ['sort_order', '-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameDetailSerializer
        return GameListSerializer
    
    def get_queryset(self):
        """自定义queryset，支持按category code筛选"""
        queryset = super().get_queryset()
        category_code = self.request.query_params.get('category', None)
        if category_code and category_code != 'all':
            queryset = queryset.filter(category__code=category_code)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """获取游戏详情，增加浏览次数"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门游戏"""
        hot_games = self.queryset.filter(is_hot=True)[:10]
        serializer = self.get_serializer(hot_games, many=True)
        return Response(serializer.data)


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """商品类型视图集（只读）"""
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """商品视图集（只读）"""
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['game', 'product_type', 'is_hot', 'is_recommended']
    search_fields = ['name', 'description']
    ordering_fields = ['current_price', 'sales_count', 'created_at']
    ordering = ['sort_order', '-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=False, methods=['get'])
    def hot(self, request):
        """获取热门商品"""
        hot_products = self.queryset.filter(is_hot=True)[:10]
        serializer = self.get_serializer(hot_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """获取推荐商品"""
        recommended_products = self.queryset.filter(is_recommended=True)[:10]
        serializer = self.get_serializer(recommended_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def by_game(self, request, pk=None):
        """根据游戏ID获取商品列表"""
        products = self.queryset.filter(game_id=pk)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
