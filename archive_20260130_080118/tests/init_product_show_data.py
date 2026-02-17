#!/usr/bin/env python
"""游戏产品展示页初始化数据脚本"""
import os
import sys
import django
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')

# 初始化Django
django.setup()

from game_product_show.models import ProductShowCategory, ProductShow
from django.contrib.auth.models import User

def init_data():
    print("=" * 60)
    print("开始初始化游戏产品展示页数据...")
    print("=" * 60)
    
    # 获取或创建管理员用户
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("\n❌ 错误: 未找到管理员用户,请先创建超级用户")
        return
    
    # 创建分类
    categories_data = [
        {'name': '热门游戏推荐', 'description': '最受欢迎的游戏产品展示', 'sort_order': 1},
        {'name': '新品上架', 'description': '最新推出的游戏产品', 'sort_order': 2},
        {'name': '限时优惠', 'description': '限时特惠游戏产品', 'sort_order': 3},
        {'name': '独家代理', 'description': '平台独家代理游戏', 'sort_order': 4},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = ProductShowCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        created_categories.append(category)
        status = "创建" if created else "已存在"
        print(f"  ✓ {status}分类: {category.name}")
    
    # 创建产品展示页
    shows_data = [
        {
            'title': '《原神》充值优惠 - 限时8折',
            'category': created_categories[0],
            'excerpt': '热门开放世界冒险游戏，创意元素战斗系统，海量优质内容等你探索！现充值享8折优惠！',
            'content': '''
## 游戏简介

《原神》是由米哈游自研的一款开放世界冒险RPG。你将在游戏中探索一个被称作「提瓦特」的幻想世界。

## 充值优惠

- 💎 首充双倍奖励
- 🎁 累充返利最高20%
- ⚡ 限时8折优惠

## 产品特色

1. **开放世界探索** - 自由探索广阔的提瓦特大陆
2. **创意战斗系统** - 元素反应带来无限可能
3. **精美画面** - 次世代动画渲染技术

![原神](https://placehold.co/800x400/1a1a2e/00ff88?text=Genshin+Impact)

立即充值，开启你的冒险之旅！
''',
            'status': 'published',
            'is_hot': True,
            'is_recommended': True,
            'published_at': datetime.now()
        },
        {
            'title': '《王者荣耀》点券充值 - 安全快捷',
            'category': created_categories[0],
            'excerpt': '国民MOBA手游，5V5公平竞技，多样英雄选择。充值秒到账，安全有保障！',
            'content': '''
## 游戏介绍

《王者荣耀》是腾讯推出的MOBA类手游，拥有海量英雄和多样玩法。

## 充值说明

- ⚡ 秒到账服务
- 🛡️ 官方合作渠道
- 💰 支持多种面额

立即充值，成为王者！
''',
            'status': 'published',
            'is_hot': True,
            'published_at': datetime.now()
        },
        {
            'title': '《崩坏：星穹铁道》充值 - 新品上架',
            'category': created_categories[1],
            'excerpt': '米哈游全新银河冒险策略游戏，回合制战斗，策略深度十足！',
            'content': '''
## 全新银河冒险

踏上星穹铁道，探索未知的银河！

## 充值优惠

新用户首充享额外奖励！

![星穹铁道](https://placehold.co/800x400/1a1a2e/00ff88?text=Star+Rail)
''',
            'status': 'published',
            'is_recommended': True,
            'published_at': datetime.now()
        },
        {
            'title': '《绝区零》限时特惠 - 限时7折',
            'category': created_categories[2],
            'excerpt': '米哈游全新都市幻想动作游戏，爽快打击感，精彩剧情体验！限时7折优惠！',
            'content': '''
## 限时特惠

限时7折，错过再等一年！

## 游戏特色

- 🎮 爽快动作战斗
- 📖 精彩剧情体验
- 🎨 独特美术风格
''',
            'status': 'published',
            'is_hot': True,
            'is_top': True,
            'published_at': datetime.now()
        },
    ]
    
    for show_data in shows_data:
        show, created = ProductShow.objects.get_or_create(
            title=show_data['title'],
            defaults={
                **show_data,
                'author': admin_user,
                'author_name': '产品运营'
            }
        )
        status = "创建" if created else "已存在"
        print(f"  ✓ {status}展示页: {show.title}")
    
    print("\n" + "=" * 60)
    print("✅ 游戏产品展示页数据初始化完成！")
    print("=" * 60)
    print("\n📊 数据统计:")
    print(f"  - 展示分类: {ProductShowCategory.objects.count()} 个")
    print(f"  - 展示页面: {ProductShow.objects.count()} 个")
    print(f"  - 已发布: {ProductShow.objects.filter(status='published').count()} 个")
    print("\n💡 提示:")
    print("  - 访问后台: http://127.0.0.1:8000/admin/game_product_show/")
    print("  - API测试: http://127.0.0.1:8000/api/product-show/shows/")

if __name__ == '__main__':
    try:
        init_data()
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
