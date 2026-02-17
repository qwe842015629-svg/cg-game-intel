import os
import django
import sys
from django.db.models import Q
from django.utils import timezone

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "game_recharge.settings")
django.setup()

from game_page.models import GamePage

def check_filter():
    print("--- Checking Filter Logic ---")
    now = timezone.now()
    print(f"Current Time: {now}")
    
    queryset = GamePage.objects.all()
    print(f"Total: {queryset.count()}")
    
    # 模拟 view 中的过滤
    filtered = queryset.filter(
        Q(status='published') & 
        (Q(published_at__isnull=True) | Q(published_at__lte=now))
    )
    print(f"Filtered Count: {filtered.count()}")
    
    for g in filtered:
        print(f"  -> {g.title} (Status: {g.status}, Published: {g.published_at})")

if __name__ == "__main__":
    check_filter()
