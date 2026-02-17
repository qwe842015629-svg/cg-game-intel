#!/usr/bin/env python
"""游戏产品展示页数据库迁移脚本"""
import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')

# 初始化Django
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("=" * 60)
    print("游戏产品展示页数据库迁移")
    print("=" * 60)
    
    try:
        # 执行迁移
        print("\n正在执行数据库迁移...")
        call_command('migrate', 'game_product_show', verbosity=2)
        
        print("\n✅ 数据库迁移完成！")
        print("\n已创建的数据表：")
        print("  - game_product_show_productshowcategory (产品展示分类表)")
        print("  - game_product_show_productshow (游戏产品展示表)")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        sys.exit(1)
