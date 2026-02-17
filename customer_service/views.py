from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ContactMethod, FAQ, CustomerServiceConfig
from .serializers import ContactMethodSerializer, FAQSerializer, CustomerServiceConfigSerializer


class ContactMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """联系方式视图集（只读）"""
    queryset = ContactMethod.objects.filter(is_active=True)
    serializer_class = ContactMethodSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', 'id']


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    """常见问题视图集（只读）"""
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['sort_order', 'view_count', 'created_at']
    ordering = ['sort_order', '-created_at']
    
    def retrieve(self, request, *args, **kwargs):
        """获取FAQ详情时增加查看次数"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CustomerServiceConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """客服页面配置视图集（只读）"""
    queryset = CustomerServiceConfig.objects.all()
    serializer_class = CustomerServiceConfigSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """获取当前配置"""
        config = CustomerServiceConfig.objects.first()
        if not config:
            # 如果没有配置，返回默认值
            config = CustomerServiceConfig(
                page_title='客服中心',
                show_contact_methods=True,
                show_faq=True,
                faq_title='常见问题'
            )
        serializer = self.get_serializer(config)
        return Response(serializer.data)
