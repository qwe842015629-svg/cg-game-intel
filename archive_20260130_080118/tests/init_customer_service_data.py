"""初始化客服数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_recharge.settings')
django.setup()

from customer_service.models import ContactMethod, FAQ, CustomerServiceConfig

def init_data():
    print("开始初始化客服数据...")
    
    # 创建联系方式
    contact_methods_data = [
        {
            'contact_type': 'online_chat',
            'title': '在线客服',
            'description': '全天候服务，随时为您解答',
            'contact_info': '点击右下角图标开始对话',
            'icon': 'MessageCircle',
            'button_text': '开始对话',
            'button_link': '#',
            'sort_order': 1
        },
        {
            'contact_type': 'email',
            'title': '邮件支持',
            'description': 'support@example.com',
            'contact_info': 'support@example.com',
            'icon': 'Mail',
            'button_text': '发送邮件',
            'button_link': 'mailto:support@example.com',
            'sort_order': 2
        },
        {
            'contact_type': 'phone',
            'title': '电话客服',
            'description': '400-123-4567',
            'contact_info': '400-123-4567',
            'icon': 'Phone',
            'button_text': '立即拨打',
            'button_link': 'tel:400-123-4567',
            'sort_order': 3
        },
        {
            'contact_type': 'wechat',
            'title': '微信客服',
            'description': '扫码添加客服微信',
            'contact_info': 'GameRecharge001',
            'icon': 'MessageSquare',
            'button_text': '查看二维码',
            'button_link': '#',
            'sort_order': 4
        },
    ]
    
    for data in contact_methods_data:
        ContactMethod.objects.update_or_create(
            contact_type=data['contact_type'],
            defaults=data
        )
    print(f"✓ 创建了 {len(contact_methods_data)} 个联系方式")
    
    # 创建常见问题
    faqs_data = [
        {
            'question': '充值需要多长时间？',
            'answer': '通常在1-10分钟内到账，高峰期可能稍有延迟。',
            'category': '充值问题',
            'sort_order': 1
        },
        {
            'question': '支持哪些支付方式？',
            'answer': '我们支持支付宝、微信支付、银行卡、USDT等多种支付方式。',
            'category': '支付问题',
            'sort_order': 2
        },
        {
            'question': '充值遇到问题怎么办？',
            'answer': '请联系我们的24小时在线客服，我们会第一时间为您解决问题。',
            'category': '充值问题',
            'sort_order': 3
        },
        {
            'question': '是否支持退款？',
            'answer': '虚拟商品一经充值成功无法退款，请确认信息后再进行充值。',
            'category': '退款问题',
            'sort_order': 4
        },
    ]
    
    for data in faqs_data:
        FAQ.objects.get_or_create(
            question=data['question'],
            defaults=data
        )
    print(f"✓ 创建了 {len(faqs_data)} 个常见问题")
    
    # 创建客服页面配置
    if not CustomerServiceConfig.objects.exists():
        CustomerServiceConfig.objects.create(
            page_title='客服中心',
            page_description='我们提供7x24小时专业客服服务，随时为您解答问题',
            show_contact_methods=True,
            show_faq=True,
            faq_title='常见问题'
        )
        print("✓ 创建了客服页面配置")
    else:
        print("✓ 客服页面配置已存在")
    
    print("\n✅ 客服数据初始化完成！")

if __name__ == '__main__':
    init_data()
