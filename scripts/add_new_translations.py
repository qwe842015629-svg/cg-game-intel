# -*- coding: utf-8 -*-
"""
添加新的翻译键（客服页、文章页、游戏卡片）
"""
import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService

CACHE_DIR = Path(__file__).parent / 'translation_cache'
CACHE_DIR.mkdir(exist_ok=True)

# 新增的翻译键
NEW_TRANSLATIONS = {
    # 客服页
    'customerServiceCenter': '客服中心',
    'onlineCustomerService': '在线客服',
    'emailSupport': '邮件支持',
    'phoneCustomerService': '电话客服',
    'wechatCustomerService': '微信客服',
    'available247': '7x24小时在线，随时为您服务',
    'startChat': '开始对话',
    'sendEmail': '发送邮件',
    'callNow': '立即拨打',
    'viewQRCode': '查看二维码',
    'scanToAdd': '扫码添加客服微信',
    
    # 常见问题
    'frequentlyAskedQuestions': '常见问题',
    'howLongRecharge': '充值多久能到账？',
    'rechargeTimeAnswer': '一般充值后1-10分钟内到账，具体时间取决于游戏和支付方式。',
    'whatPaymentMethods': '支持哪些支付方式？',
    'paymentMethodsAnswer': '我们支持支付宝、微信支付、PayPal、USDT等多种支付方式。',
    'rechargeIssues': '充值遇到问题怎么办？',
    'rechargeIssuesAnswer': '请联系我们的24小时在线客服，我们会第一时间为您解决问题。',
    'refundSupport': '是否支持退款？',
    'refundSupportAnswer': '虚拟商品一经充值成功无法退款，请确认信息后再进行充值。',
    
    # 文章页
    'gameNews': '游戏资讯',
    'latestNews': '最新游戏资讯、攻略和活动公告',
    'author': '作者',
    'readTime': '阅读时间',
    'minutes': '分钟',
    
    # 游戏卡片
    'startingFrom': '起',
    'rechargeNow': '充值',
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

def load_cache(lang_code):
    """从缓存加载"""
    cache_file = CACHE_DIR / f'{lang_code}.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(lang_code, translations):
    """保存到缓存"""
    cache_file = CACHE_DIR / f'{lang_code}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

def add_new_translations():
    """添加新的翻译"""
    print("=" * 70)
    print("添加新的翻译键")
    print("=" * 70)
    
    total_added = 0
    
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n处理: {lang_name} ({lang_code})")
        
        cached = load_cache(lang_code)
        missing = []
        
        # 找出缺失的键
        for key in NEW_TRANSLATIONS.keys():
            if key not in cached:
                missing.append(key)
        
        if not missing:
            print(f"  ✓ 无需添加")
            continue
        
        print(f"  需要翻译: {len(missing)} 项")
        
        # 翻译缺失的键
        for i, key in enumerate(missing, 1):
            chinese_text = NEW_TRANSLATIONS[key]
            
            try:
                response = TranslationService.translate(
                    text=chinese_text,
                    target_language=lang_code,
                    source_language='zh-CN'
                )
                
                if response.get('success'):
                    cached[key] = response['text']
                    total_added += 1
                    print(f"    [{i}/{len(missing)}] ✓ {key}")
                    
                    # 每5个保存一次
                    if i % 5 == 0:
                        save_cache(lang_code, cached)
                else:
                    cached[key] = chinese_text
                    print(f"    [{i}/{len(missing)}] ✗ {key}")
                    
            except Exception as e:
                cached[key] = chinese_text
                print(f"    [{i}/{len(missing)}] ✗ {key}: {str(e)[:30]}")
        
        # 最终保存
        save_cache(lang_code, cached)
        print(f"  💾 已保存")
    
    print(f"\n{'='*70}")
    print(f"完成！共添加 {total_added} 个新翻译")
    print(f"{'='*70}")

if __name__ == '__main__':
    try:
        stats = TranslationService.get_user_stats()
        if stats.get('success'):
            print(f"API 剩余: {stats['available'] - stats['used']}\n")
        
        add_new_translations()
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
