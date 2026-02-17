# API 测试指南

## 测试环境

- 服务器地址：http://127.0.0.1:8000
- 管理员账号：admin / admin123456
- 测试账号：testuser / test123456

## 使用浏览器测试（推荐新手）

Django REST Framework 提供了可浏览的API界面，可以直接在浏览器中测试。

### 步骤

1. **确保开发服务器运行**
```bash
python manage.py runserver
```

2. **在浏览器中打开以下URL进行测试**

---

## 游戏商品模块测试

### 1. 获取游戏分类列表
```
http://127.0.0.1:8000/api/products/categories/
```
**预期结果**：显示5个游戏分类（MOBA游戏、射击游戏、RPG游戏等）

### 2. 获取游戏列表
```
http://127.0.0.1:8000/api/products/games/
```
**预期结果**：显示6个游戏（王者荣耀、和平精英、原神等）

### 3. 获取热门游戏
```
http://127.0.0.1:8000/api/products/games/hot/
```
**预期结果**：显示4个热门游戏

### 4. 搜索游戏
```
http://127.0.0.1:8000/api/products/games/?search=王者
```
**预期结果**：显示"王者荣耀"

### 5. 按分类筛选游戏
```
http://127.0.0.1:8000/api/products/games/?category=1
```
**预期结果**：显示MOBA分类下的游戏

### 6. 获取游戏详情
```
http://127.0.0.1:8000/api/products/games/1/
```
**预期结果**：显示游戏详细信息（会自动增加浏览次数）

### 7. 获取所有商品
```
http://127.0.0.1:8000/api/products/products/
```
**预期结果**：显示13个充值商品

### 8. 按游戏筛选商品
```
http://127.0.0.1:8000/api/products/products/?game=1
```
**预期结果**：显示王者荣耀的商品

### 9. 获取热门商品
```
http://127.0.0.1:8000/api/products/products/hot/
```
**预期结果**：显示热门商品列表

### 10. 获取推荐商品
```
http://127.0.0.1:8000/api/products/products/recommended/
```
**预期结果**：显示推荐商品列表

### 11. 按价格排序商品
```
http://127.0.0.1:8000/api/products/products/?ordering=current_price
```
**预期结果**：商品按价格升序排列

---

## 游戏资讯模块测试

### 1. 获取文章分类
```
http://127.0.0.1:8000/api/articles/categories/
```
**预期结果**：显示5个文章分类

### 2. 获取文章列表
```
http://127.0.0.1:8000/api/articles/articles/
```
**预期结果**：显示4篇文章（置顶文章在前）

### 3. 获取热门文章
```
http://127.0.0.1:8000/api/articles/articles/hot/
```
**预期结果**：显示3篇热门文章

### 4. 获取推荐文章
```
http://127.0.0.1:8000/api/articles/articles/recommended/
```
**预期结果**：显示1篇推荐文章

### 5. 获取置顶文章
```
http://127.0.0.1:8000/api/articles/articles/top/
```
**预期结果**：显示置顶文章

### 6. 搜索文章
```
http://127.0.0.1:8000/api/articles/articles/?search=王者
```
**预期结果**：显示包含"王者"关键词的文章

### 7. 按分类筛选文章
```
http://127.0.0.1:8000/api/articles/articles/?category=1
```
**预期结果**：显示"游戏资讯"分类的文章

### 8. 按游戏筛选文章
```
http://127.0.0.1:8000/api/articles/articles/?game=1
```
**预期结果**：显示王者荣耀相关文章

### 9. 获取文章详情
```
http://127.0.0.1:8000/api/articles/articles/1/
```
**预期结果**：显示文章完整内容（自动增加浏览数）

### 10. 获取文章标签
```
http://127.0.0.1:8000/api/articles/tags/
```
**预期结果**：显示6个标签

### 11. 获取评论列表
```
http://127.0.0.1:8000/api/articles/comments/
```
**预期结果**：显示3条评论

### 12. 按文章筛选评论
```
http://127.0.0.1:8000/api/articles/comments/?article=1
```
**预期结果**：显示文章1的评论

---

## 使用 Postman 测试

### 1. 安装 Postman
下载地址：https://www.postman.com/downloads/

### 2. 导入测试集合

创建新的 Collection，添加以下请求：

#### GET 请求示例（获取游戏列表）
```
URL: http://127.0.0.1:8000/api/products/games/
Method: GET
Headers: 
  Content-Type: application/json
```

#### POST 请求示例（发表评论）
```
URL: http://127.0.0.1:8000/api/articles/comments/
Method: POST
Headers: 
  Content-Type: application/json
Body (raw JSON):
{
  "article": 1,
  "content": "这是一条测试评论"
}
```

**注意**：POST请求需要先登录。

### 3. 登录认证

使用 Session 认证，需要先在浏览器中登录：
```
http://127.0.0.1:8000/api-auth/login/
```

然后在 Postman 中：
1. 打开 Cookies 管理
2. 添加从浏览器复制的 sessionid cookie

---

## 使用 cURL 测试

### GET 请求示例
```bash
# 获取游戏列表
curl http://127.0.0.1:8000/api/products/games/

# 搜索游戏
curl "http://127.0.0.1:8000/api/products/games/?search=王者"

# 获取热门文章
curl http://127.0.0.1:8000/api/articles/articles/hot/
```

### POST 请求示例（需要登录）
```bash
# 发表评论
curl -X POST http://127.0.0.1:8000/api/articles/comments/ \
  -H "Content-Type: application/json" \
  -d '{"article": 1, "content": "测试评论"}' \
  --cookie "sessionid=YOUR_SESSION_ID"
```

---

## 使用 Python requests 测试

```python
import requests

# 基础URL
BASE_URL = "http://127.0.0.1:8000"

# 获取游戏列表
response = requests.get(f"{BASE_URL}/api/products/games/")
print(response.json())

# 搜索游戏
response = requests.get(f"{BASE_URL}/api/products/games/?search=王者")
print(response.json())

# 获取文章列表
response = requests.get(f"{BASE_URL}/api/articles/articles/")
print(response.json())

# 登录并发表评论
session = requests.Session()
login_data = {
    'username': 'testuser',
    'password': 'test123456'
}
session.post(f"{BASE_URL}/api-auth/login/", data=login_data)

# 发表评论
comment_data = {
    'article': 1,
    'content': '这是测试评论'
}
response = session.post(f"{BASE_URL}/api/articles/comments/", json=comment_data)
print(response.json())
```

---

## 测试检查清单

### 基础功能
- [ ] 所有列表接口返回正常
- [ ] 分页功能正常工作
- [ ] 搜索功能返回正确结果
- [ ] 筛选功能正常工作
- [ ] 排序功能正常工作

### 详情页面
- [ ] 游戏详情页浏览数自动增加
- [ ] 文章详情页浏览数自动增加
- [ ] 详情页显示完整信息

### 特殊接口
- [ ] 热门内容接口返回正确
- [ ] 推荐内容接口返回正确
- [ ] 置顶文章接口返回正确

### 需要认证的接口
- [ ] 未登录无法发表评论
- [ ] 登录后可以发表评论
- [ ] 文章点赞需要登录
- [ ] 评论可以编辑和删除

---

## 常见问题

### 1. CSRF 验证失败
**解决方案**：使用 DRF 的可浏览API界面，或在请求中包含 CSRF token

### 2. 认证失败
**解决方案**：
- 确保已在浏览器中登录
- 使用 Postman 时正确配置 cookies
- 使用 Python requests 时使用 Session 对象

### 3. 404 Not Found
**解决方案**：
- 检查 URL 是否正确
- 确保开发服务器正在运行
- 检查数据是否已创建

### 4. 分页问题
**解决方案**：
- 使用 `?page=2` 访问第二页
- 使用 `next` 和 `previous` 链接导航

---

## 下一步

测试完成后，可以：
1. 开始前端开发
2. 集成更多功能（用户认证、订单、支付等）
3. 优化API性能
4. 添加API文档（Swagger/OpenAPI）
