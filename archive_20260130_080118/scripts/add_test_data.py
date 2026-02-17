"""
添加测试数据脚本
用于快速填充游戏充值网站的测试数据
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from game_product.models import GameCategory, Game, ProductType, Product
from game_article.models import ArticleCategory, ArticleTag, Article
from decimal import Decimal

def add_game_categories():
    """添加游戏分类"""
    # 先清理重复数据，只保留第一条
    print("  清理重复的分类数据...")
    for code in ['international', 'hktw', 'sea']:
        categories = GameCategory.objects.filter(code=code)
        if categories.count() > 1:
            # 保留第一个，删除其他
            keep = categories.first()
            GameCategory.objects.filter(code=code).exclude(id=keep.id).delete()
            print(f"  清理了 {categories.count() - 1} 条重复的 {code} 分类")
    
    categories = [
        {'code': 'international', 'name': '国际游戏', 'sort_order': 1},
        {'code': 'hktw', 'name': '港台游戏', 'sort_order': 2},
        {'code': 'sea', 'name': '东南亚游戏', 'sort_order': 3},
    ]
    
    for cat_data in categories:
        category, created = GameCategory.objects.update_or_create(
            code=cat_data['code'],
            defaults={
                'name': cat_data['name'],
                'sort_order': cat_data['sort_order'],
                'is_active': True
            }
        )
        if created:
            print(f"✓ 创建游戏分类: {category.name}")
        else:
            print(f"- 更新游戏分类: {category.name}")
    
    return GameCategory.objects.all()

def add_games(categories):
    """添加游戏"""
    international_cat = categories.get(code='international')
    hktw_cat = categories.get(code='hktw')
    sea_cat = categories.get(code='sea')
    
    games_data = [
        {
            'name': '原神',
            'name_en': 'Genshin Impact',
            'category': international_cat,
            'is_hot': True,
            'tags': ['RPG', '冒险', '开放世界'],
            'regions': ['中国', '美国', '欧洲', '日本', '东南亚'],
            'description': '米哈游开发的开放世界冒险游戏，探索提瓦特大陆的奇幻世界。',
            'instructions': '1. 输入您的UID\n2. 选择充值金额\n3. 完成支付\n4. 创世结晶将在5分钟内到账',
            'processing_time': '5-10分钟',
            'developer': '米哈游',
            'sort_order': 1,
        },
        {
            'name': '崩坏：星穹铁道',
            'name_en': 'Honkai: Star Rail',
            'category': international_cat,
            'is_hot': True,
            'tags': ['RPG', '回合制', '科幻'],
            'regions': ['中国', '美国', '欧洲', '日本'],
            'description': '米哈游全新银河冒险策略游戏，搭乘星穹列车，踏上群星璀璨的冒险之旅。',
            'instructions': '1. 输入您的UID\n2. 选择充值金额\n3. 完成支付\n4. 星琼将在5分钟内到账',
            'processing_time': '5-10分钟',
            'developer': '米哈游',
            'sort_order': 2,
        },
        {
            'name': '绝区零',
            'name_en': 'Zenless Zone Zero',
            'category': international_cat,
            'is_hot': True,
            'tags': ['动作', '都市', '潮流'],
            'regions': ['中国', '美国', '日本'],
            'description': '米哈游都市奇幻动作游戏，在新艾利都这座充满活力的都市中展开冒险。',
            'instructions': '1. 输入您的UID\n2. 选择充值金额\n3. 完成支付\n4. 菲林将在5分钟内到账',
            'processing_time': '5-10分钟',
            'developer': '米哈游',
            'sort_order': 3,
        },
        {
            'name': '王者荣耀',
            'name_en': 'Honor of Kings',
            'category': hktw_cat,
            'is_hot': True,
            'tags': ['MOBA', '竞技', '多人'],
            'regions': ['中国'],
            'description': '腾讯天美工作室开发的MOBA手游，5V5公平竞技，英雄策略对战。',
            'instructions': '1. 输入您的QQ号或微信号\n2. 选择充值金额\n3. 完成支付\n4. 点券将在5分钟内到账',
            'processing_time': '即时到账',
            'developer': '腾讯天美',
            'sort_order': 4,
        },
        {
            'name': 'Mobile Legends',
            'name_en': 'Mobile Legends: Bang Bang',
            'category': sea_cat,
            'is_hot': True,
            'tags': ['MOBA', '竞技', '多人'],
            'regions': ['东南亚', '中国'],
            'description': '沐瞳科技开发的5V5 MOBA手游，在东南亚地区非常流行。',
            'instructions': '1. 输入您的User ID和Zone ID\n2. 选择充值金额\n3. 完成支付\n4. 钻石将在5分钟内到账',
            'processing_time': '5-10分钟',
            'developer': '沐瞳科技',
            'sort_order': 5,
        },
        {
            'name': 'PUBG Mobile',
            'name_en': 'PUBG Mobile',
            'category': sea_cat,
            'is_hot': False,
            'tags': ['射击', '生存', '竞技'],
            'regions': ['全球'],
            'description': '大逃杀类射击游戏，100人空降海岛，争夺最后的生存权。',
            'instructions': '1. 输入您的Player ID\n2. 选择充值金额\n3. 完成支付\n4. UC将在10分钟内到账',
            'processing_time': '10-30分钟',
            'developer': 'Krafton',
            'sort_order': 6,
        },
    ]
    
    created_games = []
    for game_data in games_data:
        game, created = Game.objects.update_or_create(
            name=game_data['name'],
            defaults={
                'name_en': game_data['name_en'],
                'category': game_data['category'],
                'is_hot': game_data['is_hot'],
                'tags': ','.join(game_data['tags']),
                'regions': ','.join(game_data['regions']),
                'description': game_data['description'],
                'instructions': game_data['instructions'],
                'processing_time': game_data['processing_time'],
                'developer': game_data['developer'],
                'sort_order': game_data['sort_order'],
                'is_active': True,
                'view_count': 0,
            }
        )
        if created:
            print(f"✓ 创建游戏: {game.name}")
        else:
            print(f"- 更新游戏: {game.name}")
        created_games.append(game)
    
    return created_games

def add_product_types():
    """添加商品类型"""
    # ProductType.code 的 choices 是: point, vip, item, gift, other
    # 我们只创建一个 point 类型，其他游戏都使用这个
    product_type, created = ProductType.objects.get_or_create(
        code='point',
        defaults={'name': '游戏货币', 'description': '游戏内充值货币'}
    )
    if created:
        print(f"✓ 创建商品类型: {product_type.name}")
    else:
        print(f"- 商品类型已存在: {product_type.name}")
    
    return ProductType.objects.all()

def add_products(games, product_types):
    """为每个游戏添加充值商品"""
    # 通用的充值档位
    recharge_options = [
        {'amount': '60', 'price': 6.00, 'original_price': 6.00, 'popular': False},
        {'amount': '300', 'price': 30.00, 'original_price': 30.00, 'popular': False},
        {'amount': '980', 'price': 98.00, 'original_price': 98.00, 'popular': True},
        {'amount': '1980', 'price': 198.00, 'original_price': 198.00, 'popular': False},
        {'amount': '3280', 'price': 328.00, 'original_price': 328.00, 'popular': False},
        {'amount': '6480', 'price': 648.00, 'original_price': 648.00, 'popular': False},
    ]
    
    # 游戏货币名称映射
    game_currency_map = {
        '原神': '创世结晶',
        '崩坏：星穹铁道': '星琼',
        '绝区零': '菲林',
        '王者荣耀': '点券',
        'Mobile Legends': '钻石',
        'PUBG Mobile': 'UC',
    }
    
    # 使用第一个 ProductType (通常是 point 类型)
    product_type = product_types.first()
    if not product_type:
        print("✗ 没有找到商品类型，跳过商品创建")
        return
    
    for game in games:
        currency_name = game_currency_map.get(game.name, '游戏币')
        
        for idx, option in enumerate(recharge_options, 1):
            # 计算折扣
            discount = 0
            if option['original_price'] > option['price']:
                discount = int((1 - option['price'] / option['original_price']) * 100)
            
            product, created = Product.objects.update_or_create(
                game=game,
                amount=option['amount'],
                defaults={
                    'product_type': product_type,
                    'name': f"{option['amount']} {currency_name}",
                    'current_price': Decimal(str(option['price'])),
                    'original_price': Decimal(str(option['original_price'])),
                    'discount': discount,
                    'is_popular': option['popular'],
                    'is_active': True,
                    'stock': 9999,
                    'sort_order': idx,
                }
            )
            if created:
                print(f"  ✓ 为 {game.name} 创建商品: {option['amount']} {currency_name}")
            else:
                print(f"  - 更新商品: {game.name} - {option['amount']} {currency_name}")

def add_article_categories():
    """添加文章分类"""
    categories_data = [
        {'name': '游戏资讯'},
        {'name': '攻略教程'},
        {'name': '充值指南'},
        {'name': '活动公告'},
    ]
    
    for cat_data in categories_data:
        category, created = ArticleCategory.objects.update_or_create(
            name=cat_data['name'],
            defaults={'is_active': True}
        )
        if created:
            print(f"✓ 创建文章分类: {category.name}")
        else:
            print(f"- 更新文章分类: {category.name}")
    
    return ArticleCategory.objects.all()

def add_article_tags():
    """添加文章标签"""
    tags_data = ['原神', '崩铁', '绝区零', '攻略', '新手', '充值', '活动', '更新']
    
    for tag_name in tags_data:
        tag, created = ArticleTag.objects.update_or_create(
            name=tag_name
        )
        if created:
            print(f"✓ 创建文章标签: {tag.name}")
        else:
            print(f"- 更新文章标签: {tag.name}")
    
    return ArticleTag.objects.all()

def add_articles(categories, tags):
    """添加文章"""
    news_cat = categories.filter(name='游戏资讯').first()
    guide_cat = categories.filter(name='攻略教程').first()
    recharge_cat = categories.filter(name='充值指南').first()
    
    articles_data = [
        {
            'title': '原神4.4版本「瑶华昭昭·镜中奇缘」即将上线',
            'category': news_cat,
            'tags': ['原神', '更新', '活动'],
            'excerpt': '原神4.4版本将于2024年1月31日更新，新角色「云堇」和「申鹤」复刻，还有全新活动等你来战！',
            'content': '''
# 原神4.4版本更新内容

## 新角色复刻
- 云堇（岩元素·长柄武器）
- 申鹤（冰元素·长柄武器）

## 全新活动
1. **灯海邀约** - 完成任务获得原石奖励
2. **试炼挑战** - 挑战强敌获得稀有材料
3. **拍照活动** - 分享美图赢取好礼

## 版本优化
- 优化了深渊难度
- 新增了圣遗物筛选功能
- 修复了已知bug

立即登录游戏体验全新版本内容！
            ''',
            'author': '游戏小编',
            'is_hot': True,
            'is_recommended': True,
            'read_time': 5,
        },
        {
            'title': '原神充值攻略：如何安全快捷地为账户充值',
            'category': recharge_cat,
            'tags': ['原神', '充值', '新手'],
            'excerpt': '本文将详细介绍原神的充值流程、注意事项以及如何选择合适的充值渠道。',
            'content': '''
# 原神充值完整指南

## 充值前的准备
1. 确认您的UID（游戏内右下角可查看）
2. 选择可信赖的充值平台
3. 确保账户安全

## 充值流程
1. **输入UID** - 在充值页面输入您的游戏UID
2. **选择金额** - 选择您需要的创世结晶数量
3. **选择支付方式** - 支持微信、支付宝、银行卡
4. **完成支付** - 按提示完成支付流程
5. **等待到账** - 通常5-10分钟内到账

## 充值注意事项
- ⚠️ 请仔细核对UID，充值后无法退款
- ⚠️ 选择正规充值渠道，避免账号风险
- ⚠️ 保存好支付凭证，以备查询

## 常见问题
**Q: 充值多久到账？**
A: 通常5-10分钟，最迟不超过30分钟

**Q: 充值错了UID怎么办？**
A: 请立即联系客服，提供支付凭证

**Q: 如何查看充值记录？**
A: 在个人中心-充值记录中查看
            ''',
            'author': '充值小助手',
            'is_hot': True,
            'is_recommended': True,
            'read_time': 8,
        },
        {
            'title': '崩坏：星穹铁道新手入门指南',
            'category': guide_cat,
            'tags': ['崩铁', '攻略', '新手'],
            'excerpt': '刚开始玩星穹铁道？这篇新手指南将帮助你快速了解游戏机制，少走弯路。',
            'content': '''
# 星穹铁道新手指南

## 开局建议
1. **完成新手教程** - 获取基础奖励
2. **抽取新手池** - 50抽必出5星角色
3. **完成每日任务** - 获取星琼和材料

## 角色培养
- 优先培养主C角色
- 不要分散资源
- 根据队伍配置合理分配

## 资源获取
- 每日任务：星琼 x60
- 模拟宇宙：星琼和材料
- 忘却之庭：大量奖励

## 充值建议
如需充值，建议：
- 首次双倍非常划算
- 月卡性价比最高
- 理性消费，适度充值

祝各位开拓者旅途愉快！
            ''',
            'author': '开拓者',
            'is_hot': False,
            'is_recommended': True,
            'read_time': 6,
        },
        {
            'title': '绝区零限时活动：「都市传说」即将开启',
            'category': news_cat,
            'tags': ['绝区零', '活动'],
            'excerpt': '全新限时活动「都市传说」即将上线，完成任务可获得大量菲林和稀有材料奖励。',
            'content': '''
# 绝区零限时活动预告

## 活动时间
2024年2月1日 - 2月14日

## 活动内容
- 探索神秘的都市传说
- 完成挑战任务
- 收集活动道具兑换奖励

## 活动奖励
- 菲林 x1600
- 稀有材料礼包
- 限定头像框
- 活动专属称号

## 参与条件
- 绳网等级达到30级
- 完成特定主线任务

不要错过这次精彩的活动！
            ''',
            'author': '空洞调查员',
            'is_hot': True,
            'is_recommended': False,
            'read_time': 4,
        },
        {
            'title': 'Mobile Legends充值指南：钻石购买全攻略',
            'category': recharge_cat,
            'tags': ['充值'],
            'excerpt': 'Mobile Legends是东南亚最火的MOBA手游之一，本文将教你如何安全快捷地充值钻石。',
            'content': '''
# Mobile Legends充值攻略

## 充值前准备
1. 查看您的User ID
2. 确认您的Zone ID
3. 选择可靠的充值平台

## 充值步骤
1. 输入User ID和Zone ID
2. 选择钻石数量
3. 选择支付方式
4. 完成支付
5. 等待到账（通常5-10分钟）

## 钻石用途
- 购买英雄
- 购买皮肤
- 抽取奖池

## 充值建议
- 活动期间充值更划算
- 周卡月卡性价比高
- 理性消费

Happy gaming!
            ''',
            'author': 'MLBB玩家',
            'is_hot': False,
            'is_recommended': False,
            'read_time': 5,
        },
    ]
    
    for article_data in articles_data:
        article, created = Article.objects.update_or_create(
            title=article_data['title'],
            defaults={
                'category': article_data['category'],
                'excerpt': article_data['excerpt'],
                'content': article_data['content'],
                'author_name': article_data['author'],
                'is_hot': article_data['is_hot'],
                'is_recommended': article_data['is_recommended'],
                'read_time': article_data['read_time'],
                'status': 'published',
                'view_count': 0,
                'like_count': 0,
            }
        )
        
        if created:
            # 添加标签
            for tag_name in article_data['tags']:
                tag = tags.filter(name=tag_name).first()
                if tag:
                    article.tags.add(tag)
            print(f"✓ 创建文章: {article.title}")
        else:
            # 更新时也更新标签
            article.tags.clear()
            for tag_name in article_data['tags']:
                tag = tags.filter(name=tag_name).first()
                if tag:
                    article.tags.add(tag)
            print(f"- 更新文章: {article.title}")

def main():
    """主函数"""
    print("="*60)
    print("开始添加测试数据...")
    print("="*60)
    
    print("\n1. 添加游戏分类...")
    game_categories = add_game_categories()
    
    print("\n2. 添加游戏...")
    games = add_games(game_categories)
    
    print("\n3. 添加商品类型...")
    product_types = add_product_types()
    
    print("\n4. 添加充值商品...")
    add_products(games, product_types)
    
    print("\n5. 添加文章分类...")
    article_categories = add_article_categories()
    
    print("\n6. 添加文章标签...")
    article_tags = add_article_tags()
    
    print("\n7. 添加文章...")
    add_articles(article_categories, article_tags)
    
    print("\n" + "="*60)
    print("✓ 测试数据添加完成！")
    print("="*60)
    print("\n现在您可以：")
    print("1. 访问后台查看数据：http://127.0.0.1:8000/admin/")
    print("2. 测试API接口：http://127.0.0.1:8000/api/")
    print("3. 启动前端查看效果：cd frontend && npm run dev")
    print("="*60)

if __name__ == '__main__':
    main()
