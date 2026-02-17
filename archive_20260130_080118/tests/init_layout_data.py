#!/usr/bin/env python
"""
初始化首页布局数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from main.models import HomeLayout


def init_layout_data():
    """初始化首页布局数据"""
    print("=" * 60)
    print("开始初始化首页布局数据...")
    print("=" * 60)
    
    # 定义首页布局配置
    layouts = [
        {
            'section_key': 'hero_carousel',
            'section_name': '轮播图区域',
            'is_enabled': True,
            'sort_order': 1,
            'config': {
                'auto_play': True,
                'interval': 5000,
                'show_indicators': True,
            }
        },
        {
            'section_key': 'features',
            'section_name': '核心特性',
            'is_enabled': True,
            'sort_order': 2,
            'config': {
                'display_count': 3,
                'show_icons': True,
            }
        },
        {
            'section_key': 'hot_games',
            'section_name': '热门游戏',
            'is_enabled': True,
            'sort_order': 3,
            'config': {
                'display_count': 8,
                'columns': 4,
                'show_badge': True,
            }
        },
        {
            'section_key': 'categories',
            'section_name': '游戏分类',
            'is_enabled': True,
            'sort_order': 4,
            'config': {
                'display_count': 4,
                'show_game_count': True,
            }
        },
        {
            'section_key': 'latest_news',
            'section_name': '最新资讯',
            'is_enabled': False,  # 默认禁用
            'sort_order': 5,
            'config': {
                'display_count': 6,
                'show_excerpt': True,
            }
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for layout_data in layouts:
        section_key = layout_data['section_key']
        
        # 检查是否已存在
        layout, created = HomeLayout.objects.update_or_create(
            section_key=section_key,
            defaults={
                'section_name': layout_data['section_name'],
                'is_enabled': layout_data['is_enabled'],
                'sort_order': layout_data['sort_order'],
                'config': layout_data['config'],
            }
        )
        
        if created:
            created_count += 1
            status = "✓ 创建"
            color = '\033[92m'  # Green
        else:
            updated_count += 1
            status = "↻ 更新"
            color = '\033[93m'  # Yellow
        
        reset = '\033[0m'
        enabled_icon = "🟢" if layout.is_enabled else "🔴"
        
        print(f"{color}{status}{reset} {enabled_icon} {layout.section_name} ({layout.section_key}) - 排序: {layout.sort_order}")
    
    print("\n" + "=" * 60)
    print(f"✅ 初始化完成！")
    print(f"   - 新创建: {created_count} 个板块")
    print(f"   - 已更新: {updated_count} 个板块")
    print(f"   - 总计: {created_count + updated_count} 个板块")
    print("=" * 60)
    
    # 显示当前启用的板块
    print("\n📋 当前启用的首页板块（按排序）:")
    print("-" * 60)
    enabled_layouts = HomeLayout.objects.filter(is_enabled=True).order_by('sort_order')
    for i, layout in enumerate(enabled_layouts, 1):
        print(f"  {i}. {layout.section_name} ({layout.section_key})")
    print("-" * 60)


if __name__ == '__main__':
    try:
        init_layout_data()
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
