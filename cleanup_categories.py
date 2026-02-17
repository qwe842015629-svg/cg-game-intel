"""清理重复的游戏分类"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from game_product.models import GameCategory, Game

def cleanup_categories():
    # 删除重复的新分类（保留旧的，因为可能有游戏关联）
    print("开始清理重复的游戏分类...")
    
    # 删除新创建的重复分类
    duplicates = GameCategory.objects.filter(code__in=['hongkong-taiwan', 'southeast-asia'])
    print(f"找到 {duplicates.count()} 个重复分类需要删除:")
    for cat in duplicates:
        print(f"  - {cat.id}: {cat.name} ({cat.code})")
    duplicates.delete()
    
    # 更新旧分类的code以匹配前端期望
    print("\n更新旧分类的code...")
    
    # 港台游戏 hktw -> hongkong-taiwan
    hktw = GameCategory.objects.filter(code='hktw').first()
    if hktw:
        hktw.code = 'hongkong-taiwan'
        hktw.icon = '🏮'
        hktw.save()
        print(f"  ✓ 更新 {hktw.name}: hktw -> hongkong-taiwan")
    
    # 东南亚游戏 sea -> southeast-asia
    sea = GameCategory.objects.filter(code='sea').first()
    if sea:
        sea.code = 'southeast-asia'
        sea.icon = '🌴'
        sea.save()
        print(f"  ✓ 更新 {sea.name}: sea -> southeast-asia")
    
    # 更新国际游戏的图标
    international = GameCategory.objects.filter(code='international').first()
    if international:
        international.icon = '🌍'
        international.save()
        print(f"  ✓ 更新 {international.name} 图标")
    
    print("\n当前所有分类:")
    for cat in GameCategory.objects.all():
        games_count = cat.games.filter(is_active=True).count()
        print(f"  - {cat.id}: {cat.name} ({cat.code}) {cat.icon} - {games_count}个游戏")
    
    print("\n✅ 清理完成！")

if __name__ == '__main__':
    cleanup_categories()

