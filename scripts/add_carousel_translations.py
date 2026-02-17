# -*- coding: utf-8 -*-
"""
补充轮播图翻译
"""
import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService

CACHE_DIR = Path(__file__).parent / 'translation_cache'
CACHE_DIR.mkdir(exist_ok=True)

# 轮播图翻译键
CAROUSEL_TRANSLATIONS = {
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
}

TARGET_LANGS = {
    'ko': '韩语',
    'th': '泰语',
    'vi': '越南语',
    'zh-TW': '繁体中文',
    'fr': '法语',
    'de': '德语',
}

def load_cache(lang_code):
    cache_file = CACHE_DIR / f'{lang_code}.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(lang_code, translations):
    cache_file = CACHE_DIR / f'{lang_code}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

def add_carousel_translations():
    print("=" * 70)
    print("补充轮播图翻译")
    print("=" * 70)
    
    total_added = 0
    
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n处理: {lang_name} ({lang_code})")
        cached = load_cache(lang_code)
        missing = [key for key in CAROUSEL_TRANSLATIONS.keys() if key not in cached]
        
        if not missing:
            print(f"  ✓ 已有全部翻译")
            continue
        
        print(f"  需要翻译: {len(missing)} 项")
        
        for i, key in enumerate(missing, 1):
            chinese_text = CAROUSEL_TRANSLATIONS[key]
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
                    
                    if i % 3 == 0:
                        save_cache(lang_code, cached)
                else:
                    cached[key] = chinese_text
                    print(f"    [{i}/{len(missing)}] ✗ {key}")
                    
            except Exception as e:
                cached[key] = chinese_text
                print(f"    [{i}/{len(missing)}] ✗ {key}: {str(e)[:30]}")
        
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
        add_carousel_translations()
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
