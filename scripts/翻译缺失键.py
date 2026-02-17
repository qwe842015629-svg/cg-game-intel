#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译缺失的键
"""
import json
import os
from pathlib import Path
import sys

# 添加 scripts 目录到 Python 路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from translation_utils import translate_text, load_cache, save_cache

def main():
    # 定义缺失的键及其中文翻译
    missing_keys = {
        'emailSupport': '邮件支持',
        'sendEmail': '发送邮件'
    }
    
    # 目标语言
    target_languages = ['en', 'ja', 'ko', 'th', 'vi', 'zh-TW', 'fr', 'de']
    
    # 语言映射
    language_map = {
        'en': 'English',
        'ja': 'Japanese',
        'ko': 'Korean',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'zh-TW': 'Traditional Chinese',
        'fr': 'French',
        'de': 'German'
    }
    
    # 加载缓存
    cache = load_cache()
    
    # 存储结果
    translations = {
        'zh-CN': missing_keys
    }
    
    # 为每种语言翻译
    for lang_code, lang_name in language_map.items():
        print(f"\n正在翻译到 {lang_name} ({lang_code})...")
        translations[lang_code] = {}
        
        for key, chinese_text in missing_keys.items():
            print(f"  翻译 {key}: {chinese_text}")
            
            # 尝试从缓存获取
            cache_key = f"{chinese_text}|{lang_name}"
            if cache_key in cache:
                translated = cache[cache_key]
                print(f"    ✓ 从缓存获取: {translated}")
            else:
                # 调用翻译API
                translated = translate_text(chinese_text, lang_name)
                if translated:
                    cache[cache_key] = translated
                    print(f"    ✓ 翻译成功: {translated}")
                else:
                    print(f"    ✗ 翻译失败，使用原文")
                    translated = chinese_text
            
            translations[lang_code][key] = translated
    
    # 保存缓存
    save_cache(cache)
    
    # 输出结果
    output_file = script_dir / 'missing_keys_translations.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 翻译完成！结果已保存到: {output_file}")
    
    # 打印结果预览
    print("\n=== 翻译结果预览 ===")
    for lang_code, keys in translations.items():
        print(f"\n{lang_code}:")
        for key, value in keys.items():
            print(f"  {key}: '{value}'")

if __name__ == '__main__':
    main()
