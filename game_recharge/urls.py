"""
URL configuration for game_recharge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from .views import (
    welcome,
    admin_dashboard,
    seo_automation_workbench,
    ops_gateway_workbench,
    seo_api_settings,
    i18n_tools,
    visual_builder,
)

def debug_admin(request):
    """SimpleUI 缓存清理工具页"""
    return render(request, 'debug_admin.html')

urlpatterns = [
    path('debug/fix-admin/', debug_admin, name='debug_admin'),  # 移出 admin/ 路径，避免被 admin.site.urls 捕获
    path('', welcome, name='welcome'),  # 欢迎页面
    path('cms-builder/', visual_builder, name='visual_builder'),
    path('admin/visual-builder/', visual_builder, name='admin_visual_builder'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/seo-automation-workbench/', seo_automation_workbench, name='seo_automation_workbench'),
    path('admin/ops-gateway-workbench/', ops_gateway_workbench, name='ops_gateway_workbench'),
    path('admin/seo-api-settings/', seo_api_settings, name='seo_api_settings'),
    path('admin/i18n-tools/', i18n_tools, name='admin_i18n_tools'),
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/', include('main.urls')),  # 轮播图 API
    # path('api/products/', include('game_product.urls')),
    path('api/articles/', include('game_article.urls')),
    path('api/customer-service/', include('customer_service.urls')),  # 客服 API
    path('api/footer/', include('footer.urls')),  # 页面底部 API
    path('api/recharge/', include('orders.urls')),  # 充值/库存 API
    # path('api/product-show/', include('game_product_show.urls')),  # 产品展示页 API
    path('api/game-pages/', include('game_page.urls')),  # 游戏页面 API
    path('api/seo-automation/', include('seo_automation.urls')),  # SEO automation API
    path('api/ops/v1/', include('ops_gateway.urls')),  # 机器人中间层 API
    path('api/', include('users.urls')),  # 用户API
    # Djoser 用户认证 API
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    # REST Framework browsable API login
    path('api-auth/', include('rest_framework.urls')),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

