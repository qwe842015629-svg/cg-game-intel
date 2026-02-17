#!/usr/bin/env python
"""
测试Layout API接口
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_layouts_api():
    """测试Layout API"""
    print("=" * 60)
    print("测试首页布局 API 接口")
    print("=" * 60)
    
    # 1. 测试获取所有启用的布局
    print("\n1️⃣  测试: GET /api/layouts/")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/layouts/')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！返回 {len(data)} 个启用的板块")
            for item in data:
                status = "🟢 已启用" if item['isEnabled'] else "🔴 已禁用"
                print(f"  - {item['sectionName']} ({item['sectionKey']}) {status} - 排序: {item['sortOrder']}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 2. 测试获取特定板块
    print("\n2️⃣  测试: GET /api/layouts/section/?key=hero_carousel")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/layouts/section/?key=hero_carousel')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！获取板块: {data['sectionName']}")
            print(f"  - 启用状态: {'🟢 已启用' if data['isEnabled'] else '🔴 已禁用'}")
            print(f"  - 排序: {data['sortOrder']}")
            print(f"  - 配置: {json.dumps(data['config'], ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 3. 测试获取禁用的板块
    print("\n3️⃣  测试: GET /api/layouts/section/?key=latest_news (已禁用)")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/layouts/section/?key=latest_news')
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"⚠️  注意：虽然返回成功，但该板块已禁用")
            print(f"  - 板块: {data['sectionName']}")
            print(f"  - 启用状态: {'🟢 已启用' if data['isEnabled'] else '🔴 已禁用'}")
        elif response.status_code == 404:
            print(f"✅ 正确：已禁用的板块应该返回404")
        else:
            print(f"状态: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    # 4. 测试数据格式
    print("\n4️⃣  测试: 数据格式验证")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/layouts/')
        if response.status_code == 200:
            data = response.json()
            if data:
                first = data[0]
                required_fields = ['id', 'sectionKey', 'sectionName', 'isEnabled', 'sortOrder', 'config']
                missing_fields = [f for f in required_fields if f not in first]
                
                if not missing_fields:
                    print("✅ 数据格式正确，包含所有必需字段:")
                    for field in required_fields:
                        print(f"  ✓ {field}: {type(first[field]).__name__}")
                else:
                    print(f"❌ 缺少字段: {missing_fields}")
            else:
                print("⚠️  返回数据为空")
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ API测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_layouts_api()
