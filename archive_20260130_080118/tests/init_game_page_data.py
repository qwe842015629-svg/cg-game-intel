import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from game_page.models import GamePage, GamePageCategory
from game_product.models import Game
from django.contrib.auth.models import User
from django.utils import timezone

def init_game_page_data():
    """初始化游戏页面数据"""
    
    print("=== 开始初始化游戏页面数据 ===\n")
    
    # 1. 创建分类
    print("1. 创建页面分类...")
    categories_data = [
        {'name': '游戏攻略', 'description': '各类游戏的攻略指南、技巧分享', 'sort_order': 1},
        {'name': '游戏资讯', 'description': '最新游戏资讯、更新公告', 'sort_order': 2},
        {'name': '新手指南', 'description': '新手入门教程和常见问题解答', 'sort_order': 3},
        {'name': '活动公告', 'description': '游戏活动、福利信息', 'sort_order': 4},
        {'name': '玩家心得', 'description': '玩家经验分享、心得体会', 'sort_order': 5},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = GamePageCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'sort_order': cat_data['sort_order'],
                'is_active': True
            }
        )
        categories[cat_data['name']] = category
        print(f"  {'✓ 创建' if created else '✓ 已存在'}: {category.name}")
    
    # 2. 获取管理员用户
    print("\n2. 获取管理员用户...")
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("  ✓ 创建管理员用户: admin")
        else:
            print(f"  ✓ 使用现有管理员: {admin_user.username}")
    except Exception as e:
        print(f"  ✗ 获取管理员失败: {e}")
        admin_user = None
    
    # 3. 获取一些游戏数据
    print("\n3. 获取游戏数据...")
    games = list(Game.objects.all()[:5])
    if games:
        print(f"  ✓ 找到 {len(games)} 个游戏")
    else:
        print("  ! 警告: 未找到游戏数据")
    
    # 4. 创建示例页面
    print("\n4. 创建示例游戏页面...")
    pages_data = [
        {
            'title': '王者荣耀新手入门指南',
            'slug': 'wzry-beginner-guide',
            'category': categories['新手指南'],
            'game': games[0] if games else None,
            'author_name': '游戏小编',
            'excerpt': '详细的王者荣耀新手入门教程，从基础操作到英雄选择，让你快速上手！',
            'content': '''<h2>一、游戏基础操作</h2>
<p>王者荣耀是一款5v5 MOBA竞技游戏，掌握基础操作是取得胜利的第一步。</p>

<h3>1. 移动和攻击</h3>
<ul>
    <li>左侧摇杆控制英雄移动</li>
    <li>右侧技能按钮释放技能</li>
    <li>普通攻击会自动进行</li>
</ul>

<h3>2. 地图认知</h3>
<p>了解地图上的三条路线（上路、中路、下路）和野区分布非常重要。</p>

<h2>二、英雄选择建议</h2>
<p>新手推荐英雄：后羿、妲己、亚瑟、孙尚香等操作简单的英雄。</p>

<h2>三、装备推荐</h2>
<p>游戏内有推荐装备，新手可以直接使用，后期可以根据对局情况调整。</p>''',
            'status': 'published',
            'is_top': True,
            'is_hot': True,
            'is_recommended': True,
            'published_at': timezone.now(),
        },
        {
            'title': '原神最新版本活动攻略',
            'slug': 'genshin-event-guide',
            'category': categories['活动公告'],
            'game': games[1] if len(games) > 1 else None,
            'author_name': '游戏小编',
            'excerpt': '最新版本活动全攻略，教你如何高效完成活动任务，获取丰厚奖励！',
            'content': '''<h2>活动概览</h2>
<p>本次活动包含多个精彩内容，为玩家准备了丰富的奖励。</p>

<h3>活动一：限时挑战</h3>
<p>完成指定挑战可获得原石、摩拉等奖励。</p>

<h3>活动二：角色试用</h3>
<p>可以试用新角色，体验不同的战斗风格。</p>

<h2>奖励一览</h2>
<ul>
    <li>原石 x 420</li>
    <li>纠缠之缘 x 10</li>
    <li>大英雄经验 x 20</li>
</ul>''',
            'status': 'published',
            'is_hot': True,
            'is_recommended': True,
            'published_at': timezone.now(),
        },
        {
            'title': '和平精英高分上分技巧',
            'slug': 'pubg-ranking-tips',
            'category': categories['游戏攻略'],
            'game': games[2] if len(games) > 2 else None,
            'author_name': '游戏高手',
            'excerpt': '分享职业选手的上分技巧，掌握这些方法让你轻松上王牌！',
            'content': '''<h2>选择合适的降落点</h2>
<p>降落点的选择直接影响游戏节奏，建议新手选择中等资源点。</p>

<h2>枪法练习技巧</h2>
<ol>
    <li>训练场每天练习15分钟</li>
    <li>掌握不同武器的后坐力</li>
    <li>学会压枪和预瞄</li>
</ol>

<h2>团队配合</h2>
<p>和队友保持良好沟通，合理分配物资，互相掩护前进。</p>''',
            'status': 'published',
            'is_recommended': True,
            'published_at': timezone.now(),
        },
        {
            'title': '英雄联盟手游版本强势英雄推荐',
            'slug': 'lol-hero-tier-list',
            'category': categories['游戏资讯'],
            'game': games[3] if len(games) > 3 else None,
            'author_name': '游戏分析师',
            'excerpt': '当前版本T0级英雄盘点，助你快速上分！',
            'content': '''<h2>上单位置</h2>
<p><strong>T0：剑姬、诺手</strong></p>
<p>这两个英雄在当前版本非常强势，适合carry。</p>

<h2>中单位置</h2>
<p><strong>T0：劫、亚索</strong></p>
<p>高爆发高机动性，适合熟练玩家。</p>

<h2>打野位置</h2>
<p><strong>T0：李青、盲僧</strong></p>
<p>节奏型打野，前期带节奏能力强。</p>''',
            'status': 'published',
            'published_at': timezone.now(),
        },
        {
            'title': '新玩家常见问题解答',
            'slug': 'faq-for-newbies',
            'category': categories['新手指南'],
            'game': None,
            'author_name': '客服小姐姐',
            'excerpt': '汇总新玩家最常遇到的问题及解决方案',
            'content': '''<h2>Q1: 如何充值？</h2>
<p>A: 点击充值按钮，选择支付方式，输入金额即可完成充值。</p>

<h2>Q2: 账号安全如何保障？</h2>
<p>A: 建议开启双重认证，定期修改密码，不要分享账号信息。</p>

<h2>Q3: 遇到bug怎么办？</h2>
<p>A: 请联系客服并提供详细的bug描述和截图。</p>

<h2>Q4: 如何联系客服？</h2>
<p>A: 可以通过在线客服、邮件或QQ群联系我们。</p>''',
            'status': 'published',
            'is_top': True,
            'published_at': timezone.now(),
        },
    ]
    
    created_count = 0
    for page_data in pages_data:
        # 检查是否已存在
        if GamePage.objects.filter(slug=page_data['slug']).exists():
            print(f"  ✓ 已存在: {page_data['title']}")
            continue
        
        # 创建页面
        page_data['author'] = admin_user
        page = GamePage.objects.create(**page_data)
        created_count += 1
        print(f"  ✓ 创建: {page.title}")
    
    print(f"\n=== 初始化完成 ===")
    print(f"创建了 {len(categories)} 个分类")
    print(f"创建了 {created_count} 个页面")
    print(f"\n可以访问后台管理查看: http://127.0.0.1:8000/admin/game_page/gamepage/")


if __name__ == '__main__':
    init_game_page_data()
