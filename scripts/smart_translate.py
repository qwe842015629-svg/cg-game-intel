# -*- coding: utf-8 -*-
"""
智能翻译脚本 - 只翻译缺失的内容，节约API成本
比对现有翻译和目标翻译键，只调用API翻译缺失的部分
"""
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService

# 中文源文本（完整的翻译键列表）
CHINESE_TRANSLATIONS = {
    # 网站基础
    'siteName': 'CYPHER GAME BUY',
    'home': '首页',
    'games': '游戏',
    'recharge': '充值',
    'news': '资讯',
    'support': '支持',
    'about': '关于',
    'contact': '联系',
    'search': '搜索游戏...',
    'searchResults': '搜索结果',
    'fastSecureConvenient': '快速 · 安全 · 便捷',
    
    # 搜索相关
    'gamesFound': '款游戏',
    'articlesFound': '篇文章',
    'noResultsFound': '未找到结果',
    'tryDifferentKeywords': '尝试使用不同的关键词搜索',
    
    # 游戏相关
    'hotGames': '热门游戏',
    'allGames': '全部游戏',
    'selectGame': '选择游戏',
    'gameCategory': '分类',
    'viewAllGames': '查看全部游戏',
    'viewDetails': '查看详情',
    'startRecharge': '开始充值',
    
    # 充值相关
    'accountInfo': '账号信息',
    'rechargeAmount': '充值金额',
    'paymentMethod': '支付方式',
    'confirmRecharge': '确认充值',
    'pleaseSelectGame': '请先选择游戏',
    'rechargeProcess': '充值流程',
    'gameAccountId': '游戏账号/ID',
    'serverOptional': '服务器（可选）',
    'enterAccountId': '输入游戏账号或ID',
    'enterServer': '输入服务器名称或区域',
    'selectAmount': '选择合适的金额',
    'selectPaymentMethod': '选择便捷的支付方式',
    'rechargeNotice': '充值须知',
    'rechargeTime': '充值通常5分钟内到账',
    'verifyAccount': '请确保账号信息准确',
    'customerService247': '7x24小时客服在线支持',
    'hot': '热门',
    'bonus': '赠送',
    
    # 支付方式
    'wechatPay': '微信支付',
    'alipay': '支付宝',
    'bankCard': '银行卡',
    'onlineBanking': '网银支付',
    
    # 页面标题
    'coreFeatures': '核心特性',
    'experienceNextGen': '体验下一代游戏充值服务',
    'categories': '游戏分类',
    'browseByCategory': '按分类浏览游戏',
    
    # 特性描述
    'fastArrival': '极速到账',
    'fastArrivalDesc': '充值1-10分钟内到账，无需长时间等待',
    'secureGuarantee': '安全保障',
    'secureGuaranteeDesc': '银行级安全防护，交易加密',
    'support247': '24小时支持',
    'support247Desc': '全天候客户服务，随时为您提供帮助',
    
    # 统计数据
    'activePlayers': '活跃玩家',
    'supportedGames': '支持游戏',
    'securityRate': '安全率',
    
    # 按钮文字
    'reselect': '重新选择',
    'immediateRecharge': '立即充值',
    'viewActivity': '查看活动',
    'learnMore': '了解更多',
    'startNow': '立即开始',
    'startRechargeNow': '立即充值',
    'grabNow': '立即抢购',
    'browseMore': '浏览更多',
    'viewMore': '查看更多',
    
    # 轮播图相关
    'carouselBadgeHotSale': '热卖中',
    'carouselBadgeNewArrival': '新品上市',
    'carouselBadgeBestSeller': '热门畅销',
    'carouselBadgeSpecialOffer': '特别优惠',
    'carouselTitle1': '王者荣耀充值专区',
    'carouselTitle2': '原神创世结晶',
    'carouselTitle3': '和平精英点券',
    'carouselTitle4': '英雄联盟点券',
    'carouselDesc1': '热门MOBA手游，全场普发6折，首充双倍赠送',
    'carouselDesc2': '热门二次元开放世界手游，首充双倍，额外赠送精美周边',
    'carouselDesc3': '国民级射击手游，热卖中，充值送稀有皮肤',
    'carouselDesc4': '经典MOBA游戏，充值优惠进行中，赠送限定图标',
    
    # 通用文本
    'mostPopularGamesRecharge': '最受欢迎的游戏充值',
    'fromPrice': '元起',
    'currency': '元',
    'gamesCount': '款游戏',
    
    # Footer
    'aboutUs': '关于我们',
    'aboutUsDesc': '专业的游戏充值平台，支持多种支付方式，安全快捷',
    'customerService': '客户服务',
    'contactCustomerService': '联系客服',
    'faq': '常见问题',
    'paymentMethods': '支付方式',
    'followUs': '关注我们',
    'allRightsReserved': '版权所有',
}

# 已有的翻译（从 locales.ts 提取）
EXISTING_TRANSLATIONS = {
    'en': {
        'siteName', 'home', 'games', 'recharge', 'news', 'support', 'about', 'contact',
        'search', 'searchResults', 'fastSecureConvenient', 'gamesFound', 'articlesFound',
        'noResultsFound', 'tryDifferentKeywords', 'hotGames', 'allGames', 'selectGame',
        'gameCategory', 'viewAllGames', 'viewDetails', 'startRecharge', 'accountInfo',
        'rechargeAmount', 'paymentMethod', 'confirmRecharge', 'pleaseSelectGame',
        'rechargeProcess', 'gameAccountId', 'serverOptional', 'enterAccountId',
        'enterServer', 'selectAmount', 'selectPaymentMethod', 'rechargeNotice',
        'rechargeTime', 'verifyAccount', 'customerService247', 'hot', 'bonus',
        'wechatPay', 'alipay', 'bankCard', 'onlineBanking', 'coreFeatures',
        'experienceNextGen', 'categories', 'browseByCategory', 'fastArrival',
        'fastArrivalDesc', 'secureGuarantee', 'secureGuaranteeDesc', 'support247',
        'support247Desc', 'activePlayers', 'supportedGames', 'securityRate',
        'reselect', 'immediateRecharge', 'viewActivity', 'learnMore', 'startNow',
        'startRechargeNow', 'grabNow', 'browseMore', 'viewMore',
        'carouselBadgeHotSale', 'carouselBadgeNewArrival', 'carouselBadgeBestSeller',
        'carouselBadgeSpecialOffer', 'carouselTitle1', 'carouselTitle2',
        'carouselTitle3', 'carouselTitle4', 'carouselDesc1', 'carouselDesc2',
        'carouselDesc3', 'carouselDesc4', 'mostPopularGamesRecharge', 'fromPrice',
        'currency', 'gamesCount', 'aboutUs', 'aboutUsDesc', 'customerService',
        'contactCustomerService', 'faq', 'paymentMethods', 'followUs', 'allRightsReserved'
    },
    'ja': {
        'siteName', 'home', 'games', 'recharge', 'news', 'support', 'about', 'contact',
        'search', 'searchResults', 'fastSecureConvenient', 'gamesFound', 'articlesFound',
        'noResultsFound', 'tryDifferentKeywords', 'hotGames', 'allGames', 'selectGame',
        'gameCategory', 'viewAllGames', 'viewDetails', 'startRecharge', 'accountInfo',
        'rechargeAmount', 'paymentMethod', 'confirmRecharge', 'pleaseSelectGame',
        'rechargeProcess', 'gameAccountId', 'serverOptional', 'enterAccountId',
        'enterServer', 'selectAmount', 'selectPaymentMethod', 'rechargeNotice',
        'rechargeTime', 'verifyAccount', 'customerService247', 'hot', 'bonus',
        'wechatPay', 'alipay', 'bankCard', 'onlineBanking', 'coreFeatures',
        'experienceNextGen', 'categories', 'browseByCategory', 'fastArrival',
        'fastArrivalDesc', 'secureGuarantee', 'secureGuaranteeDesc', 'support247',
        'support247Desc', 'activePlayers', 'supportedGames', 'securityRate',
        'reselect', 'immediateRecharge', 'viewActivity', 'learnMore', 'startNow',
        'startRechargeNow', 'grabNow', 'browseMore', 'viewMore',
        'carouselBadgeHotSale', 'carouselBadgeNewArrival', 'carouselBadgeBestSeller',
        'carouselBadgeSpecialOffer', 'carouselTitle1', 'carouselTitle2',
        'carouselTitle3', 'carouselTitle4', 'carouselDesc1', 'carouselDesc2',
        'carouselDesc3', 'carouselDesc4', 'mostPopularGamesRecharge', 'fromPrice',
        'currency', 'gamesCount'
    },
    'ko': set(),  # 韩语需要全部翻译
    'th': set(),  # 泰语需要全部翻译
    'vi': set(),  # 越南语需要全部翻译
    'zh-TW': set(),  # 繁体中文需要全部翻译
    'fr': set(),  # 法语需要全部翻译
    'de': set(),  # 德语需要全部翻译
}

TARGET_LANGS = {
    'ko': '韩语',
    'th': '泰语',
    'vi': '越南语',
    'zh-TW': '繁体中文',
    'fr': '法语',
    'de': '德语',
}

def translate_missing_keys():
    """只翻译缺失的键"""
    print("=" * 70)
    print("智能翻译系统 - 只翻译缺失内容")
    print("=" * 70)
    
    all_results = {}
    total_translated = 0
    total_skipped = 0
    
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n{'='*70}")
        print(f"目标语言: {lang_name} ({lang_code})")
        print(f"{'='*70}")
        
        existing = EXISTING_TRANSLATIONS.get(lang_code, set())
        all_keys = set(CHINESE_TRANSLATIONS.keys())
        missing_keys = all_keys - existing
        
        print(f"✓ 已有翻译: {len(existing)} 项")
        print(f"✗ 需要翻译: {len(missing_keys)} 项")
        print(f"💰 预计消耗API次数: {len(missing_keys)}")
        
        if not missing_keys:
            print(f"  跳过 - 该语言已完成所有翻译")
            continue
        
        results = {}
        success_count = 0
        fail_count = 0
        
        for i, key in enumerate(missing_keys, 1):
            chinese_text = CHINESE_TRANSLATIONS[key]
            
            try:
                response = TranslationService.translate(
                    text=chinese_text,
                    target_language=lang_code,
                    source_language='zh-CN'
                )
                
                if response.get('success'):
                    translated_text = response['text']
                    results[key] = translated_text
                    success_count += 1
                    total_translated += 1
                    print(f"  [{i}/{len(missing_keys)}] ✓ {key}: {chinese_text[:30]}... -> {translated_text[:30]}...")
                else:
                    results[key] = chinese_text
                    fail_count += 1
                    print(f"  [{i}/{len(missing_keys)}] ✗ {key}: 翻译失败")
                    
            except Exception as e:
                results[key] = chinese_text
                fail_count += 1
                print(f"  [{i}/{len(missing_keys)}] ✗ {key}: 错误 - {str(e)[:50]}")
        
        all_results[lang_code] = results
        print(f"\n{lang_name} 统计: 成功 {success_count}, 失败 {fail_count}")
        total_skipped += len(existing)
    
    print(f"\n{'='*70}")
    print("翻译完成统计")
    print(f"{'='*70}")
    print(f"✓ 新翻译: {total_translated} 项")
    print(f"→ 跳过（已存在）: {total_skipped} 项")
    print(f"💰 API调用次数: {total_translated}")
    
    # 保存到文件
    output_file = 'smart_translation_output.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 翻译结果已保存到: {output_file}")
    print("\n提示: 请将翻译结果手动添加到 frontend/src/i18n/locales.ts")
    
    return all_results

if __name__ == '__main__':
    try:
        # 获取用户统计
        stats = TranslationService.get_user_stats()
        if stats.get('success'):
            print(f"\nAPI 状态:")
            print(f"  可用次数: {stats['available']}")
            print(f"  已使用: {stats['used']}")
            print(f"  剩余: {stats['available'] - stats['used']}")
        
        print("\n是否继续翻译? (输入 yes 继续)")
        # confirm = input().strip().lower()
        # if confirm != 'yes':
        #     print("已取消")
        #     sys.exit(0)
        
        results = translate_missing_keys()
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
