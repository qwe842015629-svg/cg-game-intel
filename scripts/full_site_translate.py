# -*- coding: utf-8 -*-
"""
全站多语言翻译脚本
扫描所有 Vue 文件中的硬编码中文文本，生成翻译键并调用翻译之家 API 进行翻译
"""
import sys
import os
import json
import re
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main.translation_service import TranslationService

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / 'frontend' / 'src'
LOCALES_FILE = FRONTEND_SRC / 'i18n' / 'locales.ts'
CACHE_DIR = PROJECT_ROOT / 'scripts' / 'translation_cache'

# 目标语言
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

# 需要扫描的 Vue 文件
VUE_FILES_TO_SCAN = [
    'components/Layout.vue',
    'components/AuthDialog.vue',
    'components/GameCard.vue',
    'views/AboutPage.vue',
    'views/ActivateAccountPage.vue',
    'views/ArticlesPage.vue',
    'views/ContactPage.vue',
    'views/CustomerServicePage.vue',
    'views/GameDetailPage.vue',
    'views/GamesPage.vue',
    'views/LoginPage.vue',
]

def load_cache(lang_code):
    """加载翻译缓存"""
    cache_file = CACHE_DIR / f'{lang_code}.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(lang_code, cache):
    """保存翻译缓存"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f'{lang_code}.json'
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def extract_chinese_texts_from_file(file_path):
    """从 Vue 文件中提取所有硬编码的中文文本"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
    texts = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 跳过已经使用 $t() 或 t() 的文本
            content_without_translation = re.sub(r'\$t\([\'"].*?[\'"]\)', '', content)
            content_without_translation = re.sub(r'\bt\([\'"].*?[\'"]\)', '', content_without_translation)
            
            # 提取所有中文文本
            matches = chinese_pattern.findall(content_without_translation)
            texts.update(matches)
            
    except Exception as e:
        print(f"  ✗ 读取文件失败 {file_path}: {e}")
    
    return texts

def scan_all_vue_files():
    """扫描所有 Vue 文件，提取需要翻译的中文文本"""
    print("=" * 70)
    print("扫描全站 Vue 文件中的硬编码中文文本")
    print("=" * 70)
    
    all_texts = {}
    total_count = 0
    
    for vue_file in VUE_FILES_TO_SCAN:
        file_path = FRONTEND_SRC / vue_file
        if not file_path.exists():
            print(f"  ⚠ 文件不存在: {vue_file}")
            continue
        
        print(f"\n扫描: {vue_file}")
        texts = extract_chinese_texts_from_file(file_path)
        
        if texts:
            all_texts[vue_file] = list(texts)
            total_count += len(texts)
            print(f"  ✓ 找到 {len(texts)} 处中文文本")
            for text in sorted(texts):
                print(f"    - {text}")
        else:
            print(f"  ✓ 无硬编码中文")
    
    print(f"\n{'='*70}")
    print(f"扫描完成: 共找到 {total_count} 处需要翻译的中文文本")
    print(f"{'='*70}")
    
    return all_texts

def generate_translation_keys(texts_by_file):
    """为提取的中文文本生成翻译键"""
    key_mapping = {}
    used_keys = set()
    
    # 读取现有的 locales.ts 获取已有的键
    try:
        with open(LOCALES_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取所有已存在的键
            existing_keys = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*:", content)
            used_keys.update(existing_keys)
    except Exception as e:
        print(f"  ⚠ 无法读取 locales.ts: {e}")
    
    print(f"\n已存在 {len(used_keys)} 个翻译键")
    
    # 为每个中文文本生成唯一的键
    for file_name, texts in texts_by_file.items():
        for text in texts:
            # 生成基础键名（拼音或简化）
            base_key = generate_key_from_text(text)
            
            # 确保键唯一
            key = base_key
            counter = 1
            while key in used_keys:
                key = f"{base_key}{counter}"
                counter += 1
            
            key_mapping[text] = key
            used_keys.add(key)
    
    return key_mapping

def generate_key_from_text(text):
    """从中文文本生成键名"""
    # 常见词汇映射
    common_mappings = {
        '个人中心': 'userProfile',
        '退出登录': 'logout',
        '全部游戏': 'allGames',
        '国际服': 'internationalServer',
        '港台服': 'hktwServer',
        '东南亚服': 'seaServer',
        '游戏资讯': 'gameNews',
        '攻略教程': 'guides',
        '活动公告': 'announcements',
        '最新动态': 'latestUpdates',
        '关于我们': 'aboutUs',
        '联系方式': 'contactInfo',
        '在线客服': 'onlineSupport',
        '使用条款': 'termsOfService',
        '隐私政策': 'privacyPolicy',
        '加载中': 'loading',
        '提交': 'submit',
        '取消': 'cancel',
        '确认': 'confirm',
        '保存': 'save',
        '删除': 'delete',
        '编辑': 'edit',
        '搜索': 'search',
        '筛选': 'filter',
        '排序': 'sort',
        '更多': 'more',
        '返回': 'back',
        '下一步': 'next',
        '上一步': 'previous',
        '完成': 'complete',
        '成功': 'success',
        '失败': 'failed',
        '错误': 'error',
        '警告': 'warning',
        '提示': 'tip',
        '用户名': 'username',
        '密码': 'password',
        '邮箱': 'email',
        '手机号': 'phone',
        '验证码': 'verificationCode',
        '登录': 'login',
        '注册': 'register',
        '忘记密码': 'forgotPassword',
        '重置密码': 'resetPassword',
    }
    
    if text in common_mappings:
        return common_mappings[text]
    
    # 否则生成通用键名
    # 简单地使用文本的前几个字生成键
    safe_text = text[:20].replace(' ', '').replace('，', '').replace('。', '')
    return f'text_{safe_text}'

def translate_texts(key_mapping):
    """翻译所有文本到目标语言"""
    print(f"\n{'='*70}")
    print(f"开始翻译到 {len(TARGET_LANGS)} 种语言")
    print(f"{'='*70}")
    
    all_translations = {
        'zh-CN': {}  # 简体中文原文
    }
    
    # 添加简体中文原文
    for text, key in key_mapping.items():
        all_translations['zh-CN'][key] = text
    
    # 翻译到其他语言
    for lang_code, lang_name in TARGET_LANGS.items():
        print(f"\n{'-'*70}")
        print(f"翻译到 {lang_name} ({lang_code})")
        print(f"{'-'*70}")
        
        # 加载缓存
        cache = load_cache(lang_code)
        translations = {}
        new_count = 0
        cached_count = 0
        
        for text, key in key_mapping.items():
            # 检查缓存
            if text in cache:
                translations[key] = cache[text]
                cached_count += 1
                print(f"  ✓ [缓存] {key}: {text[:30]}... -> {cache[text][:30]}...")
                continue
            
            # 调用翻译 API
            try:
                response = TranslationService.translate(
                    text=text,
                    target_language=lang_code,
                    source_language='zh-CN'
                )
                
                if response.get('success'):
                    translated = response['text']
                    translations[key] = translated
                    cache[text] = translated
                    new_count += 1
                    print(f"  ✓ [新译] {key}: {text[:30]}... -> {translated[:30]}...")
                else:
                    translations[key] = text
                    print(f"  ✗ [失败] {key}: {text[:30]}...")
            except Exception as e:
                translations[key] = text
                print(f"  ✗ [错误] {key}: {str(e)[:50]}...")
        
        # 保存缓存
        save_cache(lang_code, cache)
        all_translations[lang_code] = translations
        
        print(f"\n{lang_name} 统计: 新译 {new_count}, 缓存 {cached_count}")
    
    return all_translations

def generate_locales_update(all_translations):
    """生成 locales.ts 更新内容"""
    print(f"\n{'='*70}")
    print("生成 locales.ts 更新内容")
    print(f"{'='*70}")
    
    output = {}
    
    for lang_code in ['zh-CN', 'en', 'ja', 'ko', 'th', 'vi', 'zh-TW', 'fr', 'de']:
        translations = all_translations.get(lang_code, {})
        output[lang_code] = translations
    
    # 保存到文件
    output_file = PROJECT_ROOT / 'scripts' / 'full_site_translations.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 翻译结果已保存到: {output_file}")
    print(f"\n提示: 请手动将这些翻译添加到 locales.ts 的对应语言部分")
    
    return output

def main():
    """主函数"""
    try:
        print("\n全站多语言翻译工具")
        print("使用翻译之家 API 进行在线翻译\n")
        
        # 1. 扫描 Vue 文件
        texts_by_file = scan_all_vue_files()
        
        if not texts_by_file:
            print("\n✓ 所有文件都已使用翻译函数，无需额外翻译")
            return
        
        # 2. 生成翻译键
        print(f"\n{'='*70}")
        print("生成翻译键")
        print(f"{'='*70}")
        key_mapping = generate_translation_keys(texts_by_file)
        print(f"\n✓ 生成了 {len(key_mapping)} 个翻译键")
        
        # 3. 检查 API 状态
        print(f"\n{'='*70}")
        print("检查翻译 API 状态")
        print(f"{'='*70}")
        stats = TranslationService.get_user_stats()
        if stats.get('success'):
            available = stats['available']
            used = stats['used']
            remaining = available - used
            print(f"  可用次数: {available}")
            print(f"  已使用: {used}")
            print(f"  剩余: {remaining}")
            
            required = len(key_mapping) * len(TARGET_LANGS)
            print(f"\n  预计需要: {required} 次翻译")
            
            if remaining < required:
                print(f"\n  ⚠ 警告: API 次数可能不足")
        
        # 4. 翻译
        all_translations = translate_texts(key_mapping)
        
        # 5. 生成输出
        generate_locales_update(all_translations)
        
        print(f"\n{'='*70}")
        print("✓ 全站翻译完成!")
        print(f"{'='*70}")
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
