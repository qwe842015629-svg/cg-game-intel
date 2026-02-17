from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Banner, HomeLayout, SiteConfig, MediaAsset
from .media_library import upsert_media_asset
from .serializers import (
    BannerSerializer, BannerListSerializer, 
    HomeLayoutSerializer, SiteConfigSerializer,
    MediaAssetSerializer
)
class MediaAssetViewSet(viewsets.ModelViewSet):
    """媒体资源管理视图集"""
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'alt_text']
    ordering_fields = ['created_at', 'file_size']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=400)
        requested_name = request.data.get('name', getattr(file_obj, 'name', ''))
        category = request.data.get('category', 'other')
        alt_text = request.data.get('alt_text', '')

        try:
            instance, created = upsert_media_asset(
                file_obj=file_obj,
                requested_name=requested_name,
                category=category,
                alt_text=alt_text,
                create_thumbnail=True,
            )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=400)
        except Exception as exc:
            return Response({'error': f'Upload failed: {str(exc)}'}, status=500)

        serializer = self.get_serializer(instance)
        response_payload = dict(serializer.data)
        response_payload['deduped'] = not created
        return Response(response_payload, status=201 if created else 200)

    def perform_destroy(self, instance):
        # Delete files from storage
        if instance.file:
            instance.file.delete(save=False)
        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        instance.delete()


class SiteConfigViewSet(viewsets.ModelViewSet):
    """全局配置视图集"""
    queryset = SiteConfig.objects.all()
    serializer_class = SiteConfigSerializer
    pagination_class = None

    @action(detail=False, methods=['post'])
    def update_global(self, request):
        """批量更新全局配置"""
        theme_config = request.data.get('theme_config')
        if not theme_config:
            return Response({'detail': '缺少参数'}, status=400)
            
        # 这里假设 SiteConfig 存储了全局主题配置，或者我们可以根据 key 存储
        config, created = SiteConfig.objects.get_or_create(id=1)
        # 将 CSS 变量存入 config 字段
        current = dict(config.theme_config or {})
        current.update(theme_config)
        config.theme_config = current
        config.save(update_fields=['theme_config', 'updated_at'])
        return Response({'status': 'success'})
    
    def list(self, request, *args, **kwargs):
        """获取唯一的全局配置"""
        config = SiteConfig.objects.first()
        if not config:
            # 如果不存在，则创建一个默认配置
            config = SiteConfig.objects.create(site_name='CYPHER GAME BUY')
        
        serializer = self.get_serializer(config)
        return Response(serializer.data)


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """轮播图视图集（只读）"""
    queryset = Banner.objects.filter(status='active').order_by('sort_order', '-created_at')
    serializer_class = BannerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at', 'view_count']
    
    def get_serializer_class(self):
        """根据不同的action选择不同的序列化器"""
        if self.action == 'list':
            return BannerListSerializer
        return BannerSerializer
    
    @action(detail=True, methods=['post'])
    def click(self, request, pk=None):
        """记录轮播图点击"""
        banner = self.get_object()
        banner.increase_click_count()
        return Response({
            'status': 'success',
            'click_count': banner.click_count
        })
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """获取默认轮播图"""
        default_banner = Banner.objects.filter(
            status='active',
            is_default=True
        ).first()
        
        if default_banner:
            serializer = self.get_serializer(default_banner)
            return Response(serializer.data)
        
        # 如果没有默认轮播图，返回第一个活动的轮播图
        first_banner = self.get_queryset().first()
        if first_banner:
            serializer = self.get_serializer(first_banner)
            return Response(serializer.data)
        
        return Response({'detail': '暂无轮播图'}, status=404)


class HomeLayoutViewSet(viewsets.ModelViewSet):
    """首页布局视图集"""
    queryset = HomeLayout.objects.all().order_by('sort_order', 'created_at')
    serializer_class = HomeLayoutSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    pagination_class = None
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """获取所有启用的板块（按排序）"""
        layouts = self.get_queryset().filter(is_enabled=True)
        serializer = self.get_serializer(layouts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get', 'patch'])
    def section(self, request):
        """根据section_key获取或更新特定板块"""
        section_key = request.query_params.get('key')
        if not section_key:
            return Response({'detail': '缺少section_key参数'}, status=400)
        
        try:
            layout = HomeLayout.objects.get(section_key=section_key)
        except HomeLayout.DoesNotExist:
            # 如果不存在，尝试根据 SECTION_CHOICES 创建一个默认的
            section_name = dict(HomeLayout.SECTION_CHOICES).get(section_key, section_key)
            layout = HomeLayout.objects.create(
                section_key=section_key,
                section_name=section_name,
                is_enabled=True,
                sort_order=99
            )
        
        if request.method == 'PATCH':
            # 更新配置
            config_data = request.data.get('config')
            if config_data:
                # 深度合并
                layout.config = {**layout.config, **config_data}
                layout.save()
                return Response({'status': 'success', 'config': layout.config})
            
        # GET 请求逻辑
        layout.increase_view_count()
        serializer = self.get_serializer(layout)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """重新排序板块"""
        order_data = request.data.get('order', [])
        if not order_data:
            return Response({'status': 'error', 'message': '缺少排序数据'}, status=400)
        
        try:
            for item in order_data:
                layout_id = item.get('id')
                sort_order = item.get('sort_order')
                if layout_id is not None and sort_order is not None:
                    HomeLayout.objects.filter(id=layout_id).update(sort_order=sort_order)
            
            return Response({'status': 'success'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def index(request):
    """首页视图 - 显示HTML欢迎页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>游戏充值网站</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #333;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 60px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                text-align: center;
                animation: fadeIn 0.8s ease-in;
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            h1 {
                font-size: 48px;
                color: #667eea;
                margin-bottom: 20px;
                font-weight: 700;
            }
            .emoji {
                font-size: 80px;
                margin-bottom: 20px;
                display: block;
            }
            p {
                font-size: 18px;
                color: #666;
                margin-bottom: 40px;
                line-height: 1.6;
            }
            .buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .btn {
                display: inline-block;
                padding: 15px 40px;
                border-radius: 50px;
                text-decoration: none;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s;
                cursor: pointer;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            .btn-secondary {
                background: white;
                color: #667eea;
                border: 2px solid #667eea;
            }
            .btn-secondary:hover {
                background: #667eea;
                color: white;
                transform: translateY(-2px);
            }
            .info {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 1px solid #eee;
            }
            .info-item {
                display: inline-block;
                margin: 10px 20px;
                color: #999;
                font-size: 14px;
            }
            .badge {
                display: inline-block;
                background: #4ade80;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <span class="emoji">🎮</span>
            <h1>游戏充值网站</h1>
            <p>快速、安全、便捷的游戏充值服务<br/>专业的游戏资讯和商品管理平台</p>
            
            <div class="buttons">
                <a href="http://localhost:5175" class="btn btn-primary">
                    🌟 进入前台
                </a>
                <a href="/admin/" class="btn btn-secondary">
                    🛠️ 后台管理
                </a>
            </div>
            
            <div class="info">
                <div class="info-item">
                    💻 版本: 1.0.0
                    <span class="badge">运行中</span>
                </div>
                <div class="info-item">
                    🔧 Django 5.1.5
                </div>
                <div class="info-item">
                    🎨 Simple UI
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)
