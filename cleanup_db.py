import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

tables_to_drop = [
    'game_page_gamepage',
    'game_page_gamepagecategory',
    'game_product_product',
    'game_product_producttype',
    'game_product_game',
    'game_product_gamecategory',
    'game_product_show_productshow',
    'game_product_show_productshowcategory',
    'game_article_article',
    'game_article_articlecategory',
    'game_article_articletag',
    'game_article_comment',
    'game_article_article_tags',
]

apps_to_clear_migrations = [
    'game_page',
    'game_product',
    'game_product_show',
    'game_article',
]

with connection.cursor() as cursor:
    # 1. Drop Tables
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            print(f"Dropped table: {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
            
    # 2. Clear Migrations
    for app in apps_to_clear_migrations:
        try:
            cursor.execute("DELETE FROM django_migrations WHERE app = %s;", [app])
            print(f"Cleared migrations for app: {app}")
        except Exception as e:
            print(f"Error clearing migrations for {app}: {e}")
            
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

print("Database cleanup completed.")
