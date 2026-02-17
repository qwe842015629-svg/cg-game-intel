#!/usr/bin/env python
"""
测试文章分类过滤功能
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_article_categories():
    """测试获取文章分类列表"""
    print("\n" + "="*60)
    print("测试1: 获取文章分类列表")
    print("="*60)
    
    url = f"{BASE_URL}/api/articles/categories/"
    response = requests.get(url)
    
    print(f"请求URL: {url}")
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        categories = response.json()
        print(f"成功获取 {len(categories)} 个分类:")
        for cat in categories:
            print(f"  - {cat['name']} (ID: {cat['id']}, 文章数: {cat['articles_count']})")
        return categories
    else:
        print(f"错误: {response.text}")
        return []

def test_all_articles():
    """测试获取所有文章"""
    print("\n" + "="*60)
    print("测试2: 获取所有文章（不带分类过滤）")
    print("="*60)
    
    url = f"{BASE_URL}/api/articles/articles/"
    response = requests.get(url)
    
    print(f"请求URL: {url}")
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('results', data) if isinstance(data, dict) else data
        print(f"成功获取 {len(articles)} 篇文章")
        if articles:
            print("\n前5篇文章:")
            for article in articles[:5]:
                print(f"  - {article['title']} (分类: {article.get('category_name', 'N/A')})")
        return articles
    else:
        print(f"错误: {response.text}")
        return []

def test_articles_by_category(category_name):
    """测试按分类名称获取文章"""
    print("\n" + "="*60)
    print(f"测试3: 获取「{category_name}」分类的文章")
    print("="*60)
    
    url = f"{BASE_URL}/api/articles/articles/"
    params = {'category': category_name}
    response = requests.get(url, params=params)
    
    print(f"请求URL: {url}")
    print(f"查询参数: {params}")
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('results', data) if isinstance(data, dict) else data
        print(f"成功获取 {len(articles)} 篇「{category_name}」分类的文章")
        if articles:
            print(f"\n「{category_name}」分类下的文章:")
            for article in articles:
                print(f"  - {article['title']}")
                print(f"    分类: {article.get('category_name', 'N/A')}")
        else:
            print(f"该分类下暂无文章")
        return articles
    else:
        print(f"错误: {response.text}")
        return []

def test_articles_by_category_id(category_id):
    """测试按分类ID获取文章（备用方法）"""
    print("\n" + "="*60)
    print(f"测试4: 获取分类ID={category_id}的文章")
    print("="*60)
    
    url = f"{BASE_URL}/api/articles/articles/"
    params = {'category': category_id}
    response = requests.get(url, params=params)
    
    print(f"请求URL: {url}")
    print(f"查询参数: {params}")
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('results', data) if isinstance(data, dict) else data
        print(f"成功获取 {len(articles)} 篇文章")
        return articles
    else:
        print(f"错误: {response.text}")
        return []

def main():
    print("\n" + "🎮"*30)
    print("开始测试文章分类过滤功能")
    print("🎮"*30)
    
    try:
        # 测试1: 获取所有分类
        categories = test_article_categories()
        
        # 测试2: 获取所有文章
        all_articles = test_all_articles()
        
        # 测试3: 如果有分类，测试按分类名称过滤
        if categories:
            # 测试第一个分类
            first_category = categories[0]
            test_articles_by_category(first_category['name'])
            
            # 测试按ID过滤（备用）
            test_articles_by_category_id(first_category['id'])
        
        print("\n" + "✅"*30)
        print("所有测试完成!")
        print("✅"*30 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请确保Django开发服务器正在运行: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
