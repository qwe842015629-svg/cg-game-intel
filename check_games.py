import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_recharge.settings")
django.setup()

from game_page.models import GamePage, GamePageCategory

def check_games():
    games = GamePage.objects.all()
    print(f"Total games: {games.count()}")
    for game in games:
        print(f"ID: {game.id}, Title: {game.title}, Status: {game.status}, Published At: {game.published_at}")
        print(f"  -> Category ID: {game.category_id}, Category Name: {game.category.name if game.category else 'None'}")
    
    print("\n--- Categories ---")
    cats = GamePageCategory.objects.all()
    for c in cats:
        print(f"ID: {c.id}, Name: {c.name}, Slug: {c.slug}")

if __name__ == "__main__":
    check_games()
