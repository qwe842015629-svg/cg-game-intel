from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.utils import DatabaseError
from django.shortcuts import render
from django.utils import timezone

from game_article.models import Article
from game_page.models import GamePage
from main.models import Banner, HomeLayout
from seo_automation.models import CrawlerTask, SeoArticle


def _safe_count(queryset):
    """Safely count queryset records for dashboard cards."""
    try:
        return queryset.count()
    except DatabaseError:
        return 0


def _safe_recent(queryset, limit=5):
    """Safely fetch recent records for dashboard lists."""
    try:
        return list(queryset[:limit])
    except DatabaseError:
        return []


def _last_days(days=7):
    """Return date buckets from old -> new."""
    # USE_TZ=False 时，timezone.now() 返回 naive datetime，localdate() 会报错
    now = timezone.now()
    if timezone.is_naive(now):
        end_date = now.date()
    else:
        end_date = timezone.localdate()
    return [end_date - timedelta(days=offset) for offset in range(days - 1, -1, -1)]


def _safe_daily_counts(queryset, field_name, days=7):
    """Return labels and counts for the latest N days."""
    buckets = _last_days(days)
    labels = [day.strftime('%m-%d') for day in buckets]

    try:
        start_date = buckets[0]
        end_date = buckets[-1]
        rows = (
            queryset.filter(
                **{
                    f'{field_name}__date__gte': start_date,
                    f'{field_name}__date__lte': end_date,
                }
            )
            .annotate(day=TruncDate(field_name))
            .values('day')
            .annotate(total=Count('id'))
            .order_by('day')
        )
        count_map = {row['day']: row['total'] for row in rows}
        return labels, [count_map.get(day, 0) for day in buckets]
    except DatabaseError:
        return labels, [0] * len(labels)


def _safe_article_status_data():
    """Article status distribution for donut chart."""
    status_labels = dict(Article.STATUS_CHOICES)
    status_colors = {
        'published': '#27ae60',
        'draft': '#f2994a',
        'archived': '#95a5a6',
    }

    try:
        rows = (
            Article.objects.values('status')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
    except DatabaseError:
        rows = []

    data = []
    for row in rows:
        status = row['status']
        total = row['total']
        if not total:
            continue
        data.append(
            {
                'status': status,
                'label': status_labels.get(status, status or '未知'),
                'value': total,
                'color': status_colors.get(status, '#2f80ed'),
            }
        )

    return data


def _safe_category_ranking():
    """Top categories by game page count."""
    try:
        rows = (
            GamePage.objects.filter(category__isnull=False)
            .values('category__name')
            .annotate(total=Count('id'))
            .order_by('-total')[:6]
        )
    except DatabaseError:
        rows = []

    ranking = []
    for row in rows:
        ranking.append(
            {
                'name': row['category__name'] or '未分类',
                'value': row['total'],
            }
        )

    if not ranking:
        return []

    max_value = max(item['value'] for item in ranking) or 1
    for item in ranking:
        item['percent'] = round(item['value'] * 100 / max_value, 1)
    return ranking


def welcome(request):
    """欢迎页面视图"""
    return render(request, 'welcome.html')


@staff_member_required
def visual_builder(request):
    """可视化布局编辑器"""
    layouts = HomeLayout.objects.all().order_by('sort_order', 'created_at')
    # 增加 edit_mode=true 参数触发前端编辑状态
    frontend_url = 'http://localhost:5176/?edit_mode=true'
    return render(
        request,
        'admin/visual_builder.html',
        {
            'layouts': layouts,
            'frontend_url': frontend_url,
        }
    )


@staff_member_required
def admin_dashboard(request):
    """后台运营 Dashboard（SimpleUI 首页）。"""
    seo_task_total = _safe_count(CrawlerTask.objects.all())
    seo_task_completed = _safe_count(CrawlerTask.objects.filter(status='completed'))
    seo_article_total = _safe_count(SeoArticle.objects.all())
    seo_article_published = _safe_count(SeoArticle.objects.filter(status='published'))

    cards = [
        {
            'title': '游戏页面',
            'value': _safe_count(GamePage.objects.all()),
            'desc': f"已发布 {_safe_count(GamePage.objects.filter(status='published'))} 个",
            'url': '/admin/game_page/gamepage/',
            'accent': '#2f80ed',
        },
        {
            'title': '资讯文章',
            'value': _safe_count(Article.objects.all()),
            'desc': f"已发布 {_safe_count(Article.objects.filter(status='published'))} 篇",
            'url': '/admin/game_article/article/',
            'accent': '#9b51e0',
        },
        {
            'title': '轮播图',
            'value': _safe_count(Banner.objects.all()),
            'desc': f"启用 {_safe_count(Banner.objects.filter(status='active'))} 张",
            'url': '/admin/main/banner/',
            'accent': '#f2994a',
        },
        {
            'title': '首页模块',
            'value': _safe_count(HomeLayout.objects.all()),
            'desc': f"启用 {_safe_count(HomeLayout.objects.filter(is_enabled=True))} 个",
            'url': '/admin/main/homelayout/',
            'accent': '#eb5757',
        },
        {
            'title': '用户总数',
            'value': _safe_count(User.objects.all()),
            'desc': f"管理人员 {_safe_count(User.objects.filter(is_staff=True))} 个",
            'url': '/admin/auth/user/',
            'accent': '#56ccf2',
        },
        {
            'title': 'SEO任务',
            'value': seo_task_total,
            'desc': f"已完成 {seo_task_completed} 个",
            'url': '/admin/seo-automation-workbench/',
            'accent': '#27ae60',
        },
        {
            'title': 'SEO文章',
            'value': seo_article_total,
            'desc': f"已发布 {seo_article_published} 篇",
            'url': '/admin/seo-automation-workbench/',
            'accent': '#16a085',
        },
    ]

    quick_links = [
        {'name': '首页布局', 'url': '/admin/main/homelayout/'},
        {'name': '轮播图管理', 'url': '/admin/main/banner/'},
        {'name': '游戏页面', 'url': '/admin/game_page/gamepage/'},
        {'name': '资讯管理', 'url': '/admin/game_article/article/'},
        {'name': 'SEO自动化工作台', 'url': '/admin/seo-automation-workbench/'},
        {'name': 'SEO API设置', 'url': '/admin/seo-api-settings/'},
        {'name': '用户管理', 'url': '/admin/auth/user/'},
    ]

    labels, article_daily = _safe_daily_counts(Article.objects.all(), 'created_at', days=7)
    _, game_daily = _safe_daily_counts(GamePage.objects.all(), 'created_at', days=7)
    _, user_daily = _safe_daily_counts(User.objects.all(), 'date_joined', days=7)

    trend_data = {
        'labels': labels,
        'series': [
            {'name': '新增资讯', 'color': '#9b51e0', 'data': article_daily},
            {'name': '新增游戏', 'color': '#2f80ed', 'data': game_daily},
            {'name': '新增用户', 'color': '#56ccf2', 'data': user_daily},
        ],
    }

    status_data = _safe_article_status_data()
    category_ranking = _safe_category_ranking()

    recent_articles = _safe_recent(
        Article.objects.order_by('-updated_at').values('id', 'title', 'updated_at')
    )
    recent_banners = _safe_recent(
        Banner.objects.order_by('-updated_at').values('id', 'title', 'updated_at')
    )

    return render(
        request,
        'admin/dashboard.html',
        {
            'cards': cards,
            'quick_links': quick_links,
            'trend_data': trend_data,
            'status_data': status_data,
            'category_ranking': category_ranking,
            'recent_articles': recent_articles,
            'recent_banners': recent_banners,
            'seo_summary': {
                'task_total': seo_task_total,
                'task_completed': seo_task_completed,
                'article_total': seo_article_total,
                'article_published': seo_article_published,
            },
            'now': timezone.now(),
        },
    )


@staff_member_required
def seo_automation_workbench(request):
    """SEO 自动化工作台：论坛抓取 -> AI改写 -> SEO增强 -> 发布。"""
    game_choices = _safe_recent(
        GamePage.objects.order_by('-updated_at').values('id', 'title'),
        limit=200,
    )
    return render(
        request,
        'admin/seo_automation_workbench.html',
        {
            'game_choices': game_choices,
            'now': timezone.now(),
        },
    )


@staff_member_required
def seo_api_settings(request):
    """SEO LLM API 设置页（运营可配置 base_url / api_key / model）。"""
    return render(
        request,
        'admin/seo_api_settings.html',
        {
            'now': timezone.now(),
        },
    )

