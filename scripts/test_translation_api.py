"""
测试百度翻译API的实际响应格式
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.translation_service import TranslationService
import json

def test_single_translation():
    """测试单文本翻译"""
    print("=" * 60)
    print("测试单文本翻译")
    print("=" * 60)
    
    result = TranslationService.translate(
        text="立即充值",
        target_language="en",
        source_language="zh-CN"
    )
    
    print(f"\n原始返回结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get('success'):
        print(f"\n✅ 翻译成功!")
        print(f"翻译结果: {result.get('text')}")
    else:
        print(f"\n❌ 翻译失败!")
        print(f"错误信息: {result.get('error')}")

def test_user_stats():
    """测试获取用户统计"""
    print("\n" + "=" * 60)
    print("测试获取用户统计")
    print("=" * 60)
    
    result = TranslationService.get_user_stats()
    
    print(f"\n原始返回结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get('success'):
        print(f"\n✅ 获取成功!")
        print(f"可用次数: {result.get('available')}")
        print(f"已使用: {result.get('used')}")
    else:
        print(f"\n❌ 获取失败!")
        print(f"错误信息: {result.get('error')}")

def test_raw_api():
    """测试原始API响应"""
    print("\n" + "=" * 60)
    print("测试原始API响应")
    print("=" * 60)
    
    import requests
    
    url = "http://www.trans-home.com/api/index/translate?token=mnnwBJkNAlkt7UHWxqo2"
    
    payload = {
        "keywords": "立即充值",
        "targetLanguage": "en"
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"\nHTTP 状态码: {response.status_code}")
        print(f"\n原始响应内容：")
        print(response.text)
        
        try:
            json_data = response.json()
            print(f"\nJSON 解析结果：")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except:
            print("\n无法解析为 JSON")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")

if __name__ == '__main__':
    try:
        # 测试原始API
        test_raw_api()
        
        print("\n\n")
        
        # 测试封装的服务
        test_single_translation()
        
        print("\n\n")
        
        # 测试统计信息
        test_user_stats()
        
    except Exception as e:
        print(f"\n错误：{str(e)}")
        import traceback
        traceback.print_exc()
