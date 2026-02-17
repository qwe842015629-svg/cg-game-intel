"""初始化页面底部数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from footer.models import FooterSection, FooterLink, FooterConfig

def init_data():
    print("开始初始化页面底部数据...")
    
    # 创建页面底部板块
    sections_data = [
        {
            'section_type': 'about',
            'title': '关于我们',
            'description': '专业游戏充值平台，支持多种支付方式，安全快捷',
            'sort_order': 1
        },
        {
            'section_type': 'service',
            'title': '客服服务',
            'description': '',
            'sort_order': 2
        },
        {
            'section_type': 'payment',
            'title': '支付方式',
            'description': '',
            'sort_order': 3
        },
        {
            'section_type': 'social',
            'title': '关注我们',
            'description': '',
            'sort_order': 4
        },
    ]
    
    for data in sections_data:
        section, created = FooterSection.objects.get_or_create(
            section_type=data['section_type'],
            defaults=data
        )
        if created:
            print(f"  ✓ 创建板块: {section.title}")
    
    # 创建客服服务链接
    service_section = FooterSection.objects.get(section_type='service')
    service_links = [
        {'title': '联系客服', 'url': '/customer-service', 'is_external': False, 'sort_order': 1},
        {'title': '常见问题', 'url': '/customer-service', 'is_external': False, 'sort_order': 2},
    ]
    
    for link_data in service_links:
        FooterLink.objects.get_or_create(
            section=service_section,
            title=link_data['title'],
            defaults=link_data
        )
    print(f"  ✓ 创建客服服务链接: {len(service_links)} 个")
    
    # 创建支付方式链接
    payment_section = FooterSection.objects.get(section_type='payment')
    payment_links = [
        {'title': '支付宝', 'url': '#', 'is_external': False, 'sort_order': 1},
        {'title': '微信支付', 'url': '#', 'is_external': False, 'sort_order': 2},
        {'title': 'PayPal', 'url': '#', 'is_external': False, 'sort_order': 3},
        {'title': 'USDT', 'url': '#', 'is_external': False, 'sort_order': 4},
    ]
    
    for link_data in payment_links:
        FooterLink.objects.get_or_create(
            section=payment_section,
            title=link_data['title'],
            defaults=link_data
        )
    print(f"  ✓ 创建支付方式链接: {len(payment_links)} 个")
    
    # 创建社交媒体链接
    social_section = FooterSection.objects.get(section_type='social')
    social_links = [
        {'title': '微博', 'url': '#', 'is_external': True, 'sort_order': 1},
        {'title': 'Twitter', 'url': '#', 'is_external': True, 'sort_order': 2},
        {'title': 'Discord', 'url': '#', 'is_external': True, 'sort_order': 3},
    ]
    
    for link_data in social_links:
        FooterLink.objects.get_or_create(
            section=social_section,
            title=link_data['title'],
            defaults=link_data
        )
    print(f"  ✓ 创建社交媒体链接: {len(social_links)} 个")
    
    # 创建页面底部配置
    if not FooterConfig.objects.exists():
        FooterConfig.objects.create(
            copyright_text='© 2026 CYPHER GAME BUY. 版权所有',
            show_copyright=True
        )
        print("  ✓ 创建页面底部配置")
    else:
        print("  ✓ 页面底部配置已存在")
    
    print("\n✅ 页面底部数据初始化完成！")
    print("\n📊 数据统计:")
    print(f"  - 底部板块: {FooterSection.objects.count()} 个")
    print(f"  - 底部链接: {FooterLink.objects.count()} 个")
    print(f"  - 配置记录: {FooterConfig.objects.count()} 条")

if __name__ == '__main__':
    init_data()
