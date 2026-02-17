"""
自动翻译轮播图和首页内容到所有语言
使用百度翻译之家 API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService

# 需要翻译的新增内容（中文）
NEW_TRANSLATIONS = {
    # 按钮文字（追加）
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
}

# 目标语言映射
TARGET_LANGUAGES = {
    'en': '英文',
    'ja': '日文', 
    'ko': '韩文',
    'th': '泰文',
    'vi': '越南文',
    'zh-TW': '繁体中文',
    'fr': '法文',
    'de': '德文',
}

def translate_all_texts():
    """翻译所有文本到所有目标语言"""
    print("=" * 60)
    print("开始自动翻译轮播图和首页内容...")
    print("=" * 60)
    
    results = {}
    
    for lang_code, lang_name in TARGET_LANGUAGES.items():
        print(f"\n正在翻译到 {lang_name} ({lang_code})...")
        results[lang_code] = {}
        
        for key, chinese_text in NEW_TRANSLATIONS.items():
            try:
                # 调用翻译 API
                response = TranslationService.translate(
                    text=chinese_text,
                    target_language=lang_code,
                    source_language='zh-CN'
                )
                
                if response.get('success'):
                    translated_text = response['text']
                    results[lang_code][key] = translated_text
                    print(f"  ✓ {key}: {chinese_text} → {translated_text}")
                else:
                    error_msg = response.get('error', '未知错误')
                    print(f"  ✗ {key}: 翻译失败 - {error_msg}")
                    results[lang_code][key] = chinese_text  # 失败时保留中文
                    
            except Exception as e:
                print(f"  ✗ {key}: 翻译出错 - {str(e)}")
                results[lang_code][key] = chinese_text
    
    print("\n" + "=" * 60)
    print("翻译完成！")
    print("=" * 60)
    
    return results

def generate_typescript_code(results):
    """生成 TypeScript 代码片段"""
    print("\n\n生成的 TypeScript 代码片段：")
    print("=" * 60)
    
    for lang_code in TARGET_LANGUAGES.keys():
        print(f"\n// {lang_code.upper()} 语言新增翻译：")
        print(f"{lang_code}: {{")
        print("  translations: {")
        print("    // ... 现有翻译 ...")
        
        for key, value in results[lang_code].items():
            # 转义引号
            escaped_value = value.replace("'", "\\'").replace('"', '\\"')
            print(f"    {key}: '{escaped_value}',")
        
        print("  }")
        print("},")
    
    print("=" * 60)

if __name__ == '__main__':
    try:
        # 执行翻译
        translation_results = translate_all_texts()
        
        # 生成代码
        generate_typescript_code(translation_results)
        
        print("\n提示：请将上述代码手动添加到 locales.ts 文件的对应语言中")
        
    except Exception as e:
        print(f"\n错误：{str(e)}")
        import traceback
        traceback.print_exc()
