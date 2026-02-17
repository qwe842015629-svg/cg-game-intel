#!/usr/bin/env python
"""
测试文章分类API
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_article_categories():
    """测试文章分类API"""
    print("=" * 60)
    print("测试文章分类 API")
    print("=" * 60)
    
    # 测试获取分类列表
    print("\n📋 测试: GET /api/articles/categories/")
    print("-" * 60)
    try:
        response = requests.get(f'{BASE_URL}/articles/categories/')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            categories = data if isinstance(data, list) else data.get('results', [])
            
            print(f"✅ 成功！返回 {len(categories)} 个分类\n")
            
            if categories:
                print("📊 分类列表:")
                print("-" * 60)
                for cat in categories:
                    print(f"  {cat.get('sort_order', '?')}. {cat.get('name', '未知')}")
                    print(f"     ID: {cat.get('id')}")
                    print(f"     描述: {cat.get('description', '无')}")
                    print(f"     文章数: {cat.get('articles_count', 0)}")
                    print(f"     状态: {'✔ 启用' if cat.get('is_active') else '✖ 禁用'}")
                    print()
                
                # 数据格式验证
                print("\n✅ 数据格式验证:")
                print("-" * 60)
                first = categories[0]
                required_fields = ['id', 'name', 'sort_order', 'is_active', 'articles_count']
                
                for field in required_fields:
                    if field in first:
                        print(f"  ✓ {field}: {type(first[field]).__name__}")
                    else:
                        print(f"  ✗ 缺少字段: {field}")
                
            else:
                print("⚠️  分类列表为空，请在后台添加分类")
                print("   访问: http://127.0.0.1:8000/admin/game_article/articlecategory/")
        else:
            print(f"❌ 失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_article_categories()
