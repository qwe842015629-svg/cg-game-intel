#!/usr/bin/env python
"""
添加"最新资讯"板块到首页布局
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from main.models import HomeLayout


def add_latest_news_section():
    """添加最新资讯板块"""
    # 检查是否已存在
    if HomeLayout.objects.filter(section_key='latest_news').exists():
        print('✅ "最新资讯"板块已存在，跳过创建')
        return
    
    # 创建最新资讯板块
    latest_news = HomeLayout.objects.create(
        section_key='latest_news',
        section_name='最新资讯',
        is_enabled=True,
        sort_order=40,  # 排在热门游戏和分类板块之后
        config={
            'display_count': 6,
            'show_title': True,
            'show_category': True,
            'show_author': True,
            'show_date': True,
            'show_read_time': True,
        }
    )
    print(f'✅ 成功创建"最新资讯"板块: {latest_news.section_name}')
    print(f'   - 板块键: {latest_news.section_key}')
    print(f'   - 状态: {"已启用" if latest_news.is_enabled else "已禁用"}')
    print(f'   - 排序: {latest_news.sort_order}')
    print(f'   - 配置: {latest_news.config}')


if __name__ == '__main__':
    print('开始添加"最新资讯"板块...')
    add_latest_news_section()
    print('\n✨ 数据迁移完成！')
