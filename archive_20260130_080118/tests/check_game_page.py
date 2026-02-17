import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from django.db import connection

# 检查数据表
cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'game_page%'")
tables = cursor.fetchall()

print("=== game_page 数据表检查 ===")
if tables:
    print(f"✓ 找到 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
else:
    print("✗ 未找到 game_page 相关表")

# 检查迁移状态
from django.db.migrations.recorder import MigrationRecorder
recorder = MigrationRecorder(connection)
applied_migrations = recorder.applied_migrations()

game_page_migrations = [m for m in applied_migrations if m[0] == 'game_page']
print(f"\n=== game_page 迁移记录 ===")
if game_page_migrations:
    print(f"✓ 已应用 {len(game_page_migrations)} 个迁移:")
    for app, name in game_page_migrations:
        print(f"  - {name}")
else:
    print("✗ 未找到已应用的迁移")

# 检查 Admin 注册
from django.contrib import admin
from game_page.models import GamePage, GamePageCategory

print(f"\n=== Admin 注册检查 ===")
if admin.site.is_registered(GamePage):
    print("✓ GamePage 已注册到 Admin")
else:
    print("✗ GamePage 未注册到 Admin")

if admin.site.is_registered(GamePageCategory):
    print("✓ GamePageCategory 已注册到 Admin")
else:
    print("✗ GamePageCategory 未注册到 Admin")

# 测试数据库查询
print(f"\n=== 数据库查询测试 ===")
try:
    category_count = GamePageCategory.objects.count()
    page_count = GamePage.objects.count()
    print(f"✓ GamePageCategory 数量: {category_count}")
    print(f"✓ GamePage 数量: {page_count}")
except Exception as e:
    print(f"✗ 查询失败: {e}")
