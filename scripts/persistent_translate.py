# -*- coding: utf-8 -*-
"""
持久化智能翻译系统
- 翻译结果保存到缓存文件
- 下次只翻译新增内容
- 自动同步到 locales.ts
"""
import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService

# 缓存文件路径
CACHE_DIR = Path(__file__).parent / 'translation_cache'
CACHE_DIR.mkdir(exist_ok=True)

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
    """从缓存加载已翻译内容"""
    cache_file = CACHE_DIR / f'{lang_code}.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(lang_code, translations):
    """保存翻译到缓存"""
    cache_file = CACHE_DIR / f'{lang_code}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print(f"  💾 缓存已保存: {cache_file}")

def incremental_translate():
    """增量翻译 - 只翻译新内容"""
    print("=" * 70)
    print("持久化智能翻译系统")
    print("=" * 70)
    
    stats = {
        'total_keys': len(CHINESE_TRANSLATIONS),
        'total_cached': 0,
        'total_translated': 0,
        'total_api_calls': 0
    }
    
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n{'='*70}")
        print(f"处理语言: {lang_name} ({lang_code})")
        print(f"{'='*70}")
        
        # 加载缓存
        cached = load_cache(lang_code)
        all_keys = set(CHINESE_TRANSLATIONS.keys())
        cached_keys = set(cached.keys())
        missing_keys = all_keys - cached_keys
        
        print(f"✓ 缓存已有: {len(cached_keys)} 项")
        print(f"✗ 需要翻译: {len(missing_keys)} 项")
        
        stats['total_cached'] += len(cached_keys)
        
        if not missing_keys:
            print(f"  🎉 跳过 - 该语言已完成所有翻译")
            continue
        
        print(f"💰 本次API调用: {len(missing_keys)}")
        
        # 翻译缺失的键
        success_count = 0
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
                    cached[key] = translated_text
                    success_count += 1
                    stats['total_api_calls'] += 1
                    
                    # 每翻译10个就保存一次
                    if i % 10 == 0:
                        save_cache(lang_code, cached)
                    
                    print(f"  [{i}/{len(missing_keys)}] ✓ {key}")
                else:
                    cached[key] = chinese_text
                    print(f"  [{i}/{len(missing_keys)}] ✗ {key}: 失败")
                    
            except Exception as e:
                cached[key] = chinese_text
                print(f"  [{i}/{len(missing_keys)}] ✗ {key}: {str(e)[:30]}")
        
        # 最终保存
        save_cache(lang_code, cached)
        stats['total_translated'] += success_count
        print(f"\n{lang_name} 完成: 成功 {success_count}/{len(missing_keys)}")
    
    print(f"\n{'='*70}")
    print("📊 总体统计")
    print(f"{'='*70}")
    print(f"📝 总键数: {stats['total_keys']}")
    print(f"✓ 使用缓存: {stats['total_cached']} 项")
    print(f"🆕 新翻译: {stats['total_translated']} 项")
    print(f"💰 API调用: {stats['total_api_calls']} 次")
    print(f"💵 节约成本: {stats['total_cached']} 次 ({stats['total_cached']*100//(stats['total_keys']*len(TARGET_LANGS))}%)")
    
    return stats

def generate_locales_update():
    """生成 locales.ts 更新代码"""
    print(f"\n{'='*70}")
    print("生成 locales.ts 更新代码")
    print(f"{'='*70}")
    
    output_file = CACHE_DIR / 'locales_update.ts'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// 自动生成的翻译更新代码\n")
        f.write("// 复制到 frontend/src/i18n/locales.ts 对应位置\n\n")
        
        for lang_code, lang_name in TARGET_LANGS.items():
            cached = load_cache(lang_code)
            if not cached:
                continue
                
            f.write(f"// {lang_name} ({lang_code})\n")
            f.write(f"{lang_code}: {{\n")
            f.write(f"  code: '{lang_code}',\n")
            f.write(f"  name: '{lang_name}',\n")
            f.write(f"  translations: {{\n")
            
            for key, value in sorted(cached.items()):
                escaped = value.replace("'", "\\'").replace('"', '\\"')
                f.write(f"    {key}: '{escaped}',\n")
            
            f.write(f"  }}\n")
            f.write(f"}},\n\n")
    
    print(f"✓ 更新代码已生成: {output_file}")
    print(f"\n提示: 可以直接复制该文件内容到 locales.ts")

if __name__ == '__main__':
    try:
        # 显示API状态
        stats = TranslationService.get_user_stats()
        if stats.get('success'):
            print(f"\n📡 API 状态:")
            print(f"  可用次数: {stats['available']}")
            print(f"  已使用: {stats['used']}")
            print(f"  剩余: {stats['available'] - stats['used']}")
        
        # 执行增量翻译
        result_stats = incremental_translate()
        
        # 生成更新代码
        generate_locales_update()
        
        print(f"\n{'='*70}")
        print("✅ 完成！")
        print(f"{'='*70}")
        print(f"1. 翻译缓存已保存在: {CACHE_DIR}")
        print(f"2. 下次运行只会翻译新增的键")
        print(f"3. locales.ts 更新代码: {CACHE_DIR}/locales_update.ts")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
