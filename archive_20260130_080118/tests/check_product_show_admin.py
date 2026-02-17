#!/usr/bin/env python
"""检查产品展示分类Admin配置"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from django.contrib import admin
from game_product_show.models import ProductShowCategory, ProductShow

print("=" * 60)
print("检查产品展示页Admin配置")
print("=" * 60)

# 检查模型是否已注册
if ProductShowCategory in admin.site._registry:
    print("✅ ProductShowCategory 已在Admin中注册")
    admin_class = admin.site._registry[ProductShowCategory]
    print(f"   Admin类: {admin_class.__class__.__name__}")
    print(f"   list_display: {admin_class.list_display}")
else:
    print("❌ ProductShowCategory 未在Admin中注册")

if ProductShow in admin.site._registry:
    print("✅ ProductShow 已在Admin中注册")
    admin_class = admin.site._registry[ProductShow]
    print(f"   Admin类: {admin_class.__class__.__name__}")
else:
    print("❌ ProductShow 未在Admin中注册")

# 检查数据
print(f"\n数据统计:")
print(f"  - 分类数量: {ProductShowCategory.objects.count()}")
print(f"  - 展示页数量: {ProductShow.objects.count()}")

# 检查应用配置
from django.apps import apps
app_config = apps.get_app_config('game_product_show')
print(f"\n应用配置:")
print(f"  - 应用名: {app_config.name}")
print(f"  - 显示名: {app_config.verbose_name}")

print("\n" + "=" * 60)
print("检查完成!")
