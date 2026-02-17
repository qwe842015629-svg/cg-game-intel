"""
自动翻译工具脚本
用于自动生成多语言翻译配置
"""
import sys
import os
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main.translation_service import TranslationService


def translate_locales_file():
    """
    自动翻译locales文件
    将英文翻译成其他8种语言
    """
    
    # 英文原文（从 locales.ts 中提取）
    english_texts = {
        # 网站基础
        'siteName': 'CYPHER GAME BUY',
        'home': 'Home',
        'games': 'Games',
        'recharge': 'Recharge',
        'news': 'News',
        'support': 'Support',
        'about': 'About',
        'contact': 'Contact',
        'search': 'Search games...',
        'searchResults': 'Search Results',
        'fastSecureConvenient': 'Fast · Secure · Convenient',
        
        # 搜索相关
        'gamesFound': 'games found',
        'articlesFound': 'articles found',
        'noResultsFound': 'No results found',
        'tryDifferentKeywords': 'Try searching with different keywords',
        
        # 游戏相关
        'hotGames': 'Hot Games',
        'allGames': 'All Games',
        'selectGame': 'Select Game',
        'gameCategory': 'Category',
        'viewAllGames': 'View All Games',
        'viewDetails': 'View Details',
        'startRecharge': 'Start Recharge',
    }
    
    # 目标语言列表
    target_languages = {
        'ja': '日本語',
        'ko': '한국어',
        'th': 'ไทย',
        'vi': 'Tiếng Việt',
        'zh-CN': '简体中文',
        'zh-TW': '繁體中文',
        'fr': 'Français',
        'de': 'Deutsch',
    }
    
    print("=" * 60)
    print("开始自动翻译...")
    print("=" * 60)
    
    # 收集所有要翻译的文本
    keys = list(english_texts.keys())
    values = list(english_texts.values())
    
    # 对每种语言进行翻译
    for lang_code, lang_name in target_languages.items():
        print(f"\n正在翻译到 {lang_name} ({lang_code})...")
        
        try:
            # 使用批量翻译API
            result = TranslationService.translate_batch(
                texts=values,
                target_language=lang_code
            )
            
            if result['success']:
                translated_values = result['texts']
                
                # 组合成字典
                translations = dict(zip(keys, translated_values))
                
                # 输出为TypeScript格式
                print(f"\n{lang_code}: {{")
                print(f"  code: '{lang_code}',")
                print(f"  name: '{lang_name}',")
                print("  translations: {")
                
                for key, value in translations.items():
                    # 转义特殊字符
                    escaped_value = value.replace("'", "\\'").replace('"', '\\"')
                    print(f"    {key}: '{escaped_value}',")
                
                print("  }")
                print("},")
                
                print(f"✅ {lang_name} 翻译完成！")
            else:
                print(f"❌ {lang_name} 翻译失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ {lang_name} 翻译出错: {str(e)}")
    
    print("\n" + "=" * 60)
    print("翻译完成！")
    print("=" * 60)
    
    # 显示统计信息
    stats = TranslationService.get_user_stats()
    if stats['success']:
        print(f"\n翻译额度统计:")
        print(f"  可用字符数: {stats['available']:,}")
        print(f"  已使用字符数: {stats['used']:,}")
        print(f"  剩余字符数: {stats['available'] - stats['used']:,}")


def translate_single_text(text, target_lang):
    """
    翻译单个文本（测试用）
    """
    print(f"\n翻译: '{text}' -> {target_lang}")
    result = TranslationService.translate(text, target_lang)
    
    if result['success']:
        print(f"结果: {result['text']}")
    else:
        print(f"失败: {result.get('error', '未知错误')}")


def translate_multi_language_demo():
    """
    多语种翻译演示
    """
    text = "Welcome to our game recharge platform"
    languages = ['ja', 'ko', 'zh-CN', 'fr', 'de']
    
    print(f"\n多语种翻译演示")
    print(f"原文: {text}")
    print("=" * 60)
    
    result = TranslationService.translate_multi_language(text, languages)
    
    if result['success']:
        for lang_code, translated_text in result['translations'].items():
            print(f"{lang_code}: {translated_text}")
    else:
        print(f"翻译失败: {result.get('error', '未知错误')}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'locales':
            # 翻译整个locales文件
            translate_locales_file()
        elif command == 'test':
            # 测试单个翻译
            if len(sys.argv) >= 4:
                text = sys.argv[2]
                target_lang = sys.argv[3]
                translate_single_text(text, target_lang)
            else:
                print("用法: python translate_tool.py test <文本> <目标语言>")
        elif command == 'multi':
            # 多语种翻译演示
            translate_multi_language_demo()
        else:
            print("未知命令")
            print("可用命令:")
            print("  locales - 自动翻译locales文件")
            print("  test <文本> <语言> - 测试单个翻译")
            print("  multi - 多语种翻译演示")
    else:
        print("翻译工具")
        print("=" * 60)
        print("用法:")
        print("  python translate_tool.py locales       # 翻译整个locales文件")
        print("  python translate_tool.py test 'Hello' ja  # 测试翻译")
        print("  python translate_tool.py multi         # 多语种翻译演示")
        print("=" * 60)
