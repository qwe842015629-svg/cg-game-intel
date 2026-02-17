#!/usr/bin/env python
"""
初始化文章测试数据
"""
import os
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from game_article.models import ArticleCategory, Article, ArticleTag
from django.contrib.auth.models import User


def create_test_data():
    """创建测试数据"""
    print("="*60)
    print("开始初始化文章测试数据")
    print("="*60)
    
    # 1. 确保有用户
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ 创建管理员用户: {user.username}")
    else:
        print(f"✅ 管理员用户已存在: {user.username}")
    
    # 2. 创建文章分类
    categories_data = [
        {'name': '游戏资讯', 'description': '最新游戏资讯和动态', 'sort_order': 1},
        {'name': '攻略教程', 'description': '游戏攻略和教程指南', 'sort_order': 2},
        {'name': '充值指南', 'description': '游戏充值相关说明', 'sort_order': 3},
        {'name': '活动公告', 'description': '游戏活动和公告信息', 'sort_order': 4},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = ArticleCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'sort_order': cat_data['sort_order'],
                'is_active': True,
            }
        )
        categories[cat_data['name']] = category
        if created:
            print(f"✅ 创建分类: {category.name}")
        else:
            print(f"✅ 分类已存在: {category.name}")
    
    # 3. 创建文章标签
    tags_data = ['热门', '推荐', '新手', '进阶', '充值优惠', '活动']
    tags = {}
    for tag_name in tags_data:
        tag, created = ArticleTag.objects.get_or_create(name=tag_name)
        tags[tag_name] = tag
        if created:
            print(f"✅ 创建标签: {tag.name}")
    
    # 4. 创建测试文章
    articles_data = [
        # 游戏资讯
        {
            'title': '2026年最热门手游排行榜TOP10',
            'category': '游戏资讯',
            'excerpt': '盘点2026年最受欢迎的10款手游，看看你玩过几款？',
            'content': '''
## 2026年最热门手游排行榜

在2026年，手游市场持续火爆，各种类型的游戏层出不穷。今天我们来盘点一下今年最受欢迎的10款手游。

### 1. 原神（Genshin Impact）
依然保持着超高人气，米哈游的这款开放世界冒险游戏继续霸榜。

### 2. 王者荣耀
腾讯的MOBA经典之作，玩家基数依然庞大。

### 3. 和平精英
吃鸡类游戏的代表作，持续更新保持新鲜感。

### 4. 崩坏：星穹铁道
米哈游的又一力作，回合制战斗玩法深受好评。

### 5. 第五人格
非对称竞技游戏的代表，剧情和玩法都很出色。

以上就是今年最热门的手游排行榜，你最喜欢哪一款呢？
            ''',
            'tags': ['热门', '推荐'],
            'is_hot': True,
        },
        {
            'title': '新游戏《星际探索》今日正式上线',
            'category': '游戏资讯',
            'excerpt': '期待已久的科幻题材手游《星际探索》今日正式上线，首日登录即可获得豪华礼包。',
            'content': '''
## 《星际探索》今日正式上线

经过长时间的测试和优化，科幻题材手游《星际探索》今日正式上线！

### 游戏特色
- 🚀 浩瀚的星际世界等你探索
- ⚔️ 刺激的星际战斗体验
- 🏆 丰富的PVE和PVP玩法
- 👥 多人组队副本挑战

### 首日福利
1. 登录即送SSR角色
2. 充值双倍返利
3. 新手礼包限时领取

赶快下载体验吧！
            ''',
            'tags': ['热门', '活动'],
            'is_hot': True,
        },
        
        # 攻略教程
        {
            'title': '原神新手入门完全攻略',
            'category': '攻略教程',
            'excerpt': '从零开始教你玩转原神，新手必看的完整攻略指南。',
            'content': '''
## 原神新手入门完全攻略

作为一名原神新手，面对这个庞大的开放世界可能会感到迷茫。本文将为你提供详细的入门指南。

### 一、角色培养
1. **优先培养主C**：选择一个主力输出角色重点培养
2. **平衡发展**：注意队伍的元素反应搭配
3. **资源规划**：合理分配有限的资源

### 二、世界探索
- 完成主线任务解锁更多区域
- 收集风神瞳和岩神瞳提升体力
- 开启传送点方便快速移动

### 三、体力使用
- 每天刷取圣遗物副本
- 升级天赋和武器
- 完成每日委托任务

### 四、抽卡建议
- 保证池：推荐新手抽取
- 角色池：根据需要选择
- 武器池：不建议新手抽取

跟着这份攻略，相信你很快就能成为提瓦特大陆的强者！
            ''',
            'tags': ['新手', '推荐'],
            'is_recommended': True,
        },
        {
            'title': '王者荣耀上分秘籍：从青铜到王者',
            'category': '攻略教程',
            'excerpt': '分享从青铜到王者的上分经验，帮助你快速提升段位。',
            'content': '''
## 王者荣耀上分秘籍

想要在王者荣耀中快速上分？这些技巧你必须掌握！

### 1. 英雄选择
- 选择适合版本的强势英雄
- 至少精通2-3个位置
- 学会看队友阵容补位

### 2. 意识培养
- 观察小地图
- 注意敌方打野动向
- 及时支援队友

### 3. 对线技巧
- 控制兵线
- 消耗对手血量
- 寻找击杀机会

### 4. 团战要点
- 注意站位
- 保护C位
- 找准切入时机

只要坚持练习，王者就在不远处！
            ''',
            'tags': ['进阶', '推荐'],
        },
        
        # 充值指南
        {
            'title': '游戏充值常见问题解答',
            'category': '充值指南',
            'excerpt': '详细解答游戏充值过程中的常见问题，让你充值无忧。',
            'content': '''
## 游戏充值常见问题解答

### Q1: 充值后多久到账？
A: 通常情况下，充值会在5分钟内到账。如果超过30分钟未到账，请联系客服。

### Q2: 支持哪些支付方式？
A: 我们支持：
- 支付宝
- 微信支付
- PayPal
- USDT加密货币

### Q3: 充值失败怎么办？
A: 如果充值失败：
1. 检查账号是否正确
2. 确认支付是否成功
3. 联系在线客服

### Q4: 可以退款吗？
A: 游戏虚拟商品一经充值概不退款，请谨慎操作。

### Q5: 充值有优惠吗？
A: 我们经常推出充值优惠活动，请关注公告。

更多问题请咨询客服！
            ''',
            'tags': ['新手', '充值优惠'],
        },
        {
            'title': '如何安全充值：防止账号被盗',
            'category': '充值指南',
            'excerpt': '教你如何安全地进行游戏充值，保护账号和财产安全。',
            'content': '''
## 如何安全充值

在进行游戏充值时，安全是第一位的。以下是一些安全充值的建议。

### 1. 选择官方渠道
- 只在官方平台充值
- 警惕第三方代充
- 避免使用来路不明的链接

### 2. 保护账号安全
- 设置复杂密码
- 开启两步验证
- 不要共享账号

### 3. 支付安全
- 使用安全的支付方式
- 确认收款方信息
- 保存支付凭证

### 4. 遇到问题及时联系
- 充值异常立即联系客服
- 保留相关截图和记录
- 不要轻信陌生人

记住：安全第一，谨慎充值！
            ''',
            'tags': ['新手'],
        },
        
        # 活动公告
        {
            'title': '周年庆典：充值返利活动开启',
            'category': '活动公告',
            'excerpt': '平台周年庆典来袭！充值即可享受最高30%返利，机不可失！',
            'content': '''
## 周年庆典充值返利活动

🎉 感谢各位玩家一年来的支持！我们特别推出周年庆典活动！

### 活动时间
2026年1月25日 - 2026年2月5日

### 活动内容
#### 充值返利
- 充值100元，返利10元
- 充值500元，返利60元
- 充值1000元，返利150元
- 充值5000元，返利1000元

#### 额外奖励
- 累计充值满1000元，送限定称号
- 累计充值满5000元，送专属头像框
- 累计充值满10000元，送神秘大奖

### 参与方式
1. 在活动期间进行充值
2. 返利金额会在充值后24小时内到账
3. 可在个人中心查看返利记录

### 注意事项
- 每个账号只能参与一次
- 返利金额仅限游戏内使用
- 活动最终解释权归平台所有

赶快参与吧，错过再等一年！
            ''',
            'tags': ['活动', '充值优惠'],
            'is_hot': True,
            'is_recommended': True,
        },
    ]
    
    print("\n" + "="*60)
    print("创建测试文章")
    print("="*60)
    
    for i, article_data in enumerate(articles_data, 1):
        # 检查文章是否已存在
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"⚠️  文章已存在: {article_data['title']}")
            continue
        
        # 创建文章
        article = Article.objects.create(
            title=article_data['title'],
            category=categories[article_data['category']],
            author=user,
            author_name='游戏小编',
            excerpt=article_data['excerpt'],
            summary=article_data['excerpt'],
            content=article_data['content'],
            read_time=f'{len(article_data["content"]) // 200 + 1}分钟',
            status='published',
            is_hot=article_data.get('is_hot', False),
            is_recommended=article_data.get('is_recommended', False),
            published_at=datetime.now() - timedelta(days=i),
        )
        
        # 添加标签
        for tag_name in article_data['tags']:
            article.tags.add(tags[tag_name])
        
        print(f"✅ 创建文章 #{i}: {article.title}")
    
    # 5. 统计信息
    print("\n" + "="*60)
    print("初始化完成！统计信息")
    print("="*60)
    
    for category in ArticleCategory.objects.all():
        count = category.articles.filter(status='published').count()
        print(f"📁 {category.name}: {count} 篇文章")
    
    total = Article.objects.filter(status='published').count()
    print(f"\n📊 总计: {total} 篇已发布文章")
    
    print("\n" + "✅"*30)
    print("数据初始化成功！")
    print("✅"*30)
    

if __name__ == '__main__':
    create_test_data()
