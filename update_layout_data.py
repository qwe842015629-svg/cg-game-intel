#!/usr/bin/env python
"""
更新首页布局数据 - 将 hero_carousel 迁移到 banner_section
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from main.models import HomeLayout


def update_layout_data():
    """更新首页布局数据"""
    print("="*60)
    print("开始更新首页布局数据")
    print("="*60)
    
    # 1. 更新 hero_carousel 为 banner_section
    try:
        old_layout = HomeLayout.objects.get(section_key='hero_carousel')
        print(f"\n找到旧的配置: {old_layout}")
        print(f"  - section_key: {old_layout.section_key}")
        print(f"  - section_name: {old_layout.section_name}")
        print(f"  - is_enabled: {old_layout.is_enabled}")
        print(f"  - sort_order: {old_layout.sort_order}")
        
        # 更新字段
        old_layout.section_key = 'banner_section'
        old_layout.section_name = '轮播图板块'
        old_layout.save()
        
        print(f"\n✅ 已更新为:")
        print(f"  - section_key: {old_layout.section_key}")
        print(f"  - section_name: {old_layout.section_name}")
        
    except HomeLayout.DoesNotExist:
        print("\nℹ️ 未找到旧的 hero_carousel 配置")
        print("   尝试创建新的 banner_section 配置...")
        
        # 创建新配置
        banner_section, created = HomeLayout.objects.get_or_create(
            section_key='banner_section',
            defaults={
                'section_name': '轮播图板块',
                'is_enabled': True,
                'sort_order': 1,
                'config': {
                    'auto_play': True,
                    'interval': 5000,
                    'show_indicators': True
                }
            }
        )
        
        if created:
            print(f"✅ 已创建新的配置: {banner_section}")
        else:
            print(f"ℹ️ banner_section 配置已存在: {banner_section}")
    
    # 2. 更新其他板块名称（添加"板块"后缀）
    print("\n" + "="*60)
    print("更新其他板块名称")
    print("="*60)
    
    updates = [
        ('features', '核心特性板块'),
        ('hot_games', '热门游戏板块'),
        ('categories', '游戏分类板块'),
        ('latest_news', '最新资讯板块'),
    ]
    
    for section_key, new_name in updates:
        try:
            layout = HomeLayout.objects.get(section_key=section_key)
            old_name = layout.section_name
            layout.section_name = new_name
            layout.save()
            print(f"✅ 更新 {section_key}: {old_name} → {new_name}")
        except HomeLayout.DoesNotExist:
            print(f"ℹ️ {section_key} 不存在，跳过")
    
    # 3. 显示所有板块状态
    print("\n" + "="*60)
    print("当前所有板块状态")
    print("="*60)
    
    layouts = HomeLayout.objects.all().order_by('sort_order')
    if layouts.exists():
        print(f"\n{'板块标识':<20} {'板块名称':<20} {'状态':<10} {'排序':<10}")
        print("-"*60)
        for layout in layouts:
            status = "✔ 已启用" if layout.is_enabled else "✖ 已禁用"
            print(f"{layout.section_key:<20} {layout.section_name:<20} {status:<10} {layout.sort_order:<10}")
    else:
        print("\n⚠️ 暂无板块配置")
    
    print("\n" + "✅"*30)
    print("数据更新完成！")
    print("✅"*30)
    print("\n提示:")
    print("1. 前端需要更新 section_key 从 'hero_carousel' 改为 'banner_section'")
    print("2. 请检查后台管理界面是否正确显示")
    print("3. 测试前端首页布局功能是否正常")


if __name__ == '__main__':
    update_layout_data()
