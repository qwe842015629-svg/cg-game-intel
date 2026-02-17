# -*- coding: utf-8 -*-
"""
自动翻译并生成完整的翻译配置
"""
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService

# 需要翻译的内容
TRANSLATIONS = {
    'startRechargeNow': '立即充值',
    'grabNow': '立即抢购',
    'browseMore': '浏览更多',
    'viewMore': '查看更多',
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
    'mostPopularGamesRecharge': '最受欢迎的游戏充值',
    'fromPrice': '元起',
    'currency': '元',
    'gamesCount': '款游戏',
}

TARGET_LANGS = ['en', 'ja', 'ko', 'th', 'vi', 'zh-TW', 'fr', 'de']

results = {}

for lang in TARGET_LANGS:
    results[lang] = {}
    for key, text in TRANSLATIONS.items():
        result = TranslationService.translate(text, lang, 'zh-CN')
        if result.get('success'):
            results[lang][key] = result['text']
        else:
            results[lang][key] = text

# 输出JSON
output_file = 'translation_output.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Translation complete! Saved to {output_file}")
print("\nResults preview:")
print(json.dumps(results, ensure_ascii=False, indent=2))
