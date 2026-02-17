# -*- coding: utf-8 -*-
"""
补充 Layout.vue 和 AuthDialog.vue 等组件的翻译
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService
import json
from pathlib import Path

# 需要补充的翻译键（从组件中提取的硬编码中文）
ADDITIONAL_TRANSLATIONS = {
    # Layout.vue
    'userProfile': '个人中心',
    'logout': '退出登录',
    'allGames1': '全部游戏',
    'internationalServer': '国际服',
    'hktwServer': '港台服',
    'seaServer': '东南亚服',
    'gameNews1': '游戏资讯',
    'guides': '攻略教程',
    'announcements': '活动公告',
    'latestUpdates': '最新动态',
    'logoutSuccess': '已退出登录',
    
    # AuthDialog.vue  
    'closeDialog': '关闭',
    'login': '登录',
    'register': '注册',
    'username': '用户名',
    'email': '邮箱',
    'password': '密码',
    'confirmPassword': '确认密码',
    'passwordMismatch': '两次输入的密码不一致',
    'pleaseEnterUsername': '请输入用户名',
    'pleaseEnterEmail': '请输入邮箱',
    'pleaseEnterPassword': '请输入密码',
    'pleaseConfirmPassword': '请确认密码',
    'registerNow': '立即注册',
    'loginNow': '立即登录',
    'alreadyHaveAccount': '已有账号？',
    'noAccountYet': '还没有账号？',
    'forgotPassword': '忘记密码',
    'registrationSuccess': '注册成功',
    'activationEmailSent': '激活邮件已发送至',
    'clickEmailLink': '点击邮件中的激活链接即可登录使用',
    'didNotReceiveEmail': '没收到邮件？',
    'checkSpamFolder': '请检查垃圾箱',
    'orRetryAfterMinutes': '或等待几分钟后重试',
    'emailOrPasswordError': '邮箱或密码错误',
    'pleaseRetryLater': '请稍后重试',
    'networkError': '网络错误',
    'checkConnection': '请检查您的网络连接',
    'loginInProgress': '登录中...',
    'submitting': '提交中...',
    
    # CustomerServicePage.vue
    'onlineSupport': '在线客服',
    'available247': '7x24小时在线，随时为您服务',
    'startChat': '开始咨询',
    'phoneSupport': '电话客服',
    'wechatSupport': '微信客服',
    'scanQRCode': '扫描二维码添加客服微信',
    'viewQRCode': '查看二维码',
    'callNow': '拨打电话',
    'commonQuestions': '常见问题',
    'howLongToArrive': '充值多久到账？',
    'arrivalTimeAnswer': '通常1-10分钟内到账，高峰期可能稍有延迟。',
    'supportedPayments': '支持哪些支付方式？',
    'paymentsAnswer': '我们支持支付宝、微信支付、银行卡、USDT等多种支付方式。',
    'rechargeProblems': '充值遇到问题怎么办？',
    'problemsAnswer': '请联系我们的24小时在线客服，我们会第一时间为您解决问题。',
    'supportsRefund': '是否支持退款？',
    'refundAnswer': '虚拟商品一旦充值成功无法退款，请在充值前确认信息。',
    'needHelp': '需要帮助？',
    'contactService': '请随时联系我们的客服团队',
    
    # ContactPage.vue
    'contactInfo': '联系方式',
    'businessCooperation': '商务合作',
    'technicalSupport': '技术支持',
    'companyAddress': '公司地址',
    'workingHours': '工作时间',
    'weekdays': '周一至周五',
    'timeRange': '9:00 - 18:00',
    'holidays': '节假日休息',
    
    # AboutPage.vue
    'companyIntroduction': '公司介绍',
    'ourMission': '我们的使命',
    'ourVision': '我们的愿景',
    'coreValues': '核心价值',
    'developmentHistory': '发展历程',
    'teamIntroduction': '团队介绍',
    
    # GameDetailPage.vue
    'serverSelection': '选择区服',
    'selectServer': '请选择游戏区服',
    'amountSelection': '选择充值金额',
    'selectAmount1': '请选择合适的充值金额',
    'paymentSelection': '选择支付方式',
    'selectPayment': '请选择支付方式',
    'confirmOrder': '确认订单',
    'orderInfo': '订单信息',
    'gameName': '游戏名称',
    'serverName': '游戏区服',
    'rechargeItem': '充值项目',
    'payAmount': '支付金额',
    'submitOrder': '提交订单',
    'backToGames': '返回游戏列表',
    'serverRequired': '请选择游戏区服',
    'amountRequired': '请选择充值金额',
    'paymentRequired': '请选择支付方式',
    
    # ActivateAccountPage.vue
    'accountActivation': '账号激活',
    'activating': '激活中...',
    'activationSuccess': '激活成功',
    'activationFailed': '激活失败',
    'accountActivated': '您的账号已激活成功',
    'canLoginNow': '现在可以登录使用了',
    'goToLogin': '前往登录',
    'invalidActivationLink': '激活链接无效或已过期',
    'contactSupportTeam': '请联系客服团队',
    'retryActivation': '重试',
    'backToHome': '返回首页',
}

TARGET_LANGS = {
    'en': '英语',
    'ja': '日语',
    'ko': '韩语',
    'th': '泰语',
    'vi': '越南语',
    'zh-TW': '繁体中文',
    'fr': '法语',
    'de': '德语',
}

CACHE_DIR = Path(__file__).parent / 'translation_cache'

def load_cache(lang_code):
    """加载缓存"""
    cache_file = CACHE_DIR / f'{lang_code}.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(lang_code, cache):
    """保存缓存"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f'{lang_code}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def translate_additional_keys():
    """翻译补充键"""
    print("=" * 70)
    print("补充组件翻译")
    print("=" * 70)
    print(f"\n需要翻译 {len(ADDITIONAL_TRANSLATIONS)} 个键到 {len(TARGET_LANGS)} 种语言")
    print(f"预计API调用: {len(ADDITIONAL_TRANSLATIONS) * len(TARGET_LANGS)}\n")
    
    all_results = {
        'zh-CN': ADDITIONAL_TRANSLATIONS.copy()
    }
    
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n{'='*70}")
        print(f"翻译到 {lang_name} ({lang_code})")
        print(f"{'='*70}")
        
        cache = load_cache(lang_code)
        translations = {}
        new_count = 0
        cached_count = 0
        
        for key, chinese_text in ADDITIONAL_TRANSLATIONS.items():
            # 检查缓存
            if chinese_text in cache:
                translations[key] = cache[chinese_text]
                cached_count += 1
                print(f"  ✓ [缓存] {key}: {chinese_text} -> {cache[chinese_text]}")
                continue
            
            # 翻译
            try:
                response = TranslationService.translate(
                    text=chinese_text,
                    target_language=lang_code,
                    source_language='zh-CN'
                )
                
                if response.get('success'):
                    translated = response['text']
                    translations[key] = translated
                    cache[chinese_text] = translated
                    new_count += 1
                    print(f"  ✓ [新译] {key}: {chinese_text} -> {translated}")
                else:
                    translations[key] = chinese_text
                    print(f"  ✗ [失败] {key}: {chinese_text}")
            except Exception as e:
                translations[key] = chinese_text
                print(f"  ✗ [错误] {key}: {str(e)[:50]}")
        
        save_cache(lang_code, cache)
        all_results[lang_code] = translations
        print(f"\n{lang_name} 统计: 新译 {new_count}, 缓存 {cached_count}")
    
    # 保存结果
    output_file = Path(__file__).parent / 'component_translations.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✓ 翻译完成！")
    print(f"✓ 结果已保存到: {output_file}")
    print(f"{'='*70}")
    
    return all_results

if __name__ == '__main__':
    try:
        # 检查 API 状态
        stats = TranslationService.get_user_stats()
        if stats.get('success'):
            print(f"\nAPI 状态:")
            print(f"  可用次数: {stats['available']}")
            print(f"  已使用: {stats['used']}")
            print(f"  剩余: {stats['available'] - stats['used']}\n")
        
        results = translate_additional_keys()
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
