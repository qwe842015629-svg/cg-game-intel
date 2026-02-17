# -*- coding: utf-8 -*-
"""
添加游戏页和文章页的翻译键
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
    # 游戏页
    'gameRecharge': '游戏充值',
    'selectGameToRecharge': '选择您要充值的游戏，体验未来式游戏服务',
    'searchGameName': '搜索游戏名称...',
    'allGamesCategory': '全部游戏',
    'internationalGames': '国际游戏',
    'hongKongTaiwanGames': '港台游戏',
    'southeastAsiaGames': '东南亚游戏',
    'gamesFound': '找到',
    'gamesUnit': '款游戏',
    'noGamesFound': '未找到游戏',
    'tryAdjustSearch': '尝试调整您的搜索条件',
    'clearFilters': '清除筛选',
    
    # 游戏卡片标签
    'rpg': 'RPG',
    'moba': 'MOBA',
    'shooting': '射击',
    'strategy': '策略',
    'competitive': '竞技',
    'openWorld': '开放世界',
    'adventure': '冒险',
    'multiplayer': '多人',
    'hotTag': '热门',
    
    # 文章/资讯页
    'gameInformation': '游戏资讯',
    'chargingGuide': '充值指南',
    'securityExpert': '安全专家',
    'gameEditor': '游戏小编',
    'rechargeNow': '立即充值',
    'andUp': '起',
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
    cache_file = CACHE_DIR / f'{lang_code}.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(lang_code, translations):
    cache_file = CACHE_DIR / f'{lang_code}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

def add_translations():
    print("=" * 70)
    print("添加游戏页和文章页翻译")
    print("=" * 70)
    
    total_added = 0
    
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n处理: {lang_name} ({lang_code})")
        
        cached = load_cache(lang_code)
        missing = []
        
        for key in NEW_TRANSLATIONS.keys():
            if key not in cached:
                missing.append(key)
        
        if not missing:
            print(f"  ✓ 无需添加")
            continue
        
        print(f"  需要翻译: {len(missing)} 项")
        
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
                    
                    if i % 5 == 0:
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
        
        add_translations()
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
