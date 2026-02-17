from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FooterSection, FooterLink, FooterConfig
from .serializers import FooterSectionSerializer, FooterLinkSerializer, FooterConfigSerializer


class FooterSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """页面底部板块视图集（只读）"""
    queryset = FooterSection.objects.filter(is_active=True).prefetch_related('links')
    serializer_class = FooterSectionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'id']


class FooterLinkViewSet(viewsets.ReadOnlyModelViewSet):
    """底部链接视图集（只读）"""
    queryset = FooterLink.objects.filter(is_active=True)
    serializer_class = FooterLinkSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'id']


class FooterConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """页面底部配置视图集（只读）"""
    queryset = FooterConfig.objects.all()
    serializer_class = FooterConfigSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前配置"""
        config = FooterConfig.objects.first()
        if not config:
            # 如果没有配置，返回默认值
            config = FooterConfig(
                copyright_text='© 2026 CYPHER GAME BUY. 版权所有',
                show_copyright=True
            )
        serializer = self.get_serializer(config)
        return Response(serializer.data)
