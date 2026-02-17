# REST API 接口文档

## 基础URL
- 开发环境：`http://127.0.0.1:8000/api/`
- 所有API返回JSON格式数据
- 支持DRF可浏览API界面

---

## 游戏商品模块 (game_product)

基础路径：`/api/products/`

### 1. 游戏分类 (Game Categories)

#### 列表
- **GET** `/api/products/categories/`
- 获取所有游戏分类
- 查询参数：
  - `ordering`: 排序字段 (sort_order, created_at)

#### 详情
- **GET** `/api/products/categories/{id}/`
- 获取单个游戏分类详情

---

### 2. 游戏 (Games)

#### 列表
- **GET** `/api/products/games/`
- 获取所有游戏列表
- 查询参数：
  - `category`: 按分类筛选
  - `is_hot`: 是否热门 (true/false)
  - `search`: 搜索游戏名称或开发商
  - `ordering`: 排序字段 (sort_order, view_count, created_at)

#### 详情
- **GET** `/api/products/games/{id}/`
- 获取单个游戏详情（自动增加浏览次数）

#### 热门游戏
- **GET** `/api/products/games/hot/`
- 获取热门游戏列表（最多10个）

---

### 3. 商品类型 (Product Types)

#### 列表
- **GET** `/api/products/product-types/`
- 获取所有商品类型

#### 详情
- **GET** `/api/products/product-types/{id}/`
- 获取单个商品类型详情

---

### 4. 充值商品 (Products)

#### 列表
- **GET** `/api/products/products/`
- 获取所有商品列表
- 查询参数：
  - `game`: 按游戏ID筛选
  - `product_type`: 按商品类型筛选
  - `is_hot`: 是否热门
  - `is_recommended`: 是否推荐
  - `search`: 搜索商品名称或描述
  - `ordering`: 排序字段 (current_price, sales_count, created_at)
  - `page`: 页码（默认每页10条）

#### 详情
- **GET** `/api/products/products/{id}/`
- 获取单个商品详情

#### 热门商品
- **GET** `/api/products/products/hot/`
- 获取热门商品列表（最多10个）

#### 推荐商品
- **GET** `/api/products/products/recommended/`
- 获取推荐商品列表（最多10个）

#### 按游戏获取商品
- **GET** `/api/products/products/{id}/by_game/`
- 获取指定游戏的所有商品

---

## 游戏资讯模块 (game_article)

基础路径：`/api/articles/`

### 1. 文章分类 (Article Categories)

#### 列表
- **GET** `/api/articles/categories/`
- 获取所有文章分类
- 查询参数：
  - `ordering`: 排序字段 (sort_order, created_at)

#### 详情
- **GET** `/api/articles/categories/{id}/`
- 获取单个文章分类详情

---

### 2. 文章 (Articles)

#### 列表
- **GET** `/api/articles/articles/`
- 获取所有已发布文章列表
- 查询参数：
  - `category`: 按分类筛选
  - `game`: 按游戏筛选
  - `is_hot`: 是否热门
  - `is_recommended`: 是否推荐
  - `search`: 搜索标题、摘要、内容
  - `ordering`: 排序字段 (published_at, view_count, like_count, created_at)
  - `page`: 页码（默认每页10条）

#### 详情
- **GET** `/api/articles/articles/{id}/`
- 获取单个文章详情（自动增加浏览次数）

#### 热门文章
- **GET** `/api/articles/articles/hot/`
- 获取热门文章列表（最多10个）

#### 推荐文章
- **GET** `/api/articles/articles/recommended/`
- 获取推荐文章列表（最多10个）

#### 置顶文章
- **GET** `/api/articles/articles/top/`
- 获取置顶文章列表

#### 点赞文章
- **POST** `/api/articles/articles/{id}/like/`
- 为文章点赞（需要登录）
- 返回：`{"status": "liked", "like_count": 数量}`

---

### 3. 文章标签 (Article Tags)

#### 列表
- **GET** `/api/articles/tags/`
- 获取所有标签
- 查询参数：
  - `search`: 搜索标签名称

#### 详情
- **GET** `/api/articles/tags/{id}/`
- 获取单个标签详情

---

### 4. 评论 (Comments)

#### 列表
- **GET** `/api/articles/comments/`
- 获取所有已审核评论
- 查询参数：
  - `article`: 按文章ID筛选
  - `parent`: 按父评论筛选（获取回复）
  - `ordering`: 排序字段 (created_at)

#### 创建
- **POST** `/api/articles/comments/`
- 创建新评论（需要登录）
- 请求体：
```json
{
  "article": 文章ID,
  "parent": 父评论ID（可选）,
  "content": "评论内容"
}
```

#### 详情
- **GET** `/api/articles/comments/{id}/`
- 获取单个评论详情（包含回复列表）

#### 获取回复
- **GET** `/api/articles/comments/{id}/replies/`
- 获取指定评论的所有回复

#### 更新
- **PUT/PATCH** `/api/articles/comments/{id}/`
- 更新评论（需要登录且为评论作者）

#### 删除
- **DELETE** `/api/articles/comments/{id}/`
- 删除评论（需要登录且为评论作者）

---

## 认证相关

### 登录
- **访问** `/api-auth/login/`
- Django REST Framework 提供的登录界面
- 登录后可访问需要认证的API

### 登出
- **访问** `/api-auth/logout/`
- 退出登录

---

## 响应格式示例

### 成功响应（列表）
```json
{
  "count": 总数,
  "next": "下一页URL",
  "previous": "上一页URL",
  "results": [
    // 数据列表
  ]
}
```

### 成功响应（详情）
```json
{
  "id": 1,
  "name": "商品名称",
  // 其他字段...
}
```

### 错误响应
```json
{
  "detail": "错误信息"
}
```

---

## 使用示例

### 获取所有游戏
```bash
curl http://127.0.0.1:8000/api/products/games/
```

### 搜索游戏
```bash
curl "http://127.0.0.1:8000/api/products/games/?search=王者"
```

### 获取某个游戏的商品
```bash
curl http://127.0.0.1:8000/api/products/products/?game=1
```

### 获取热门文章
```bash
curl http://127.0.0.1:8000/api/articles/articles/hot/
```

### 发表评论（需要登录）
```bash
curl -X POST http://127.0.0.1:8000/api/articles/comments/ \
  -H "Content-Type: application/json" \
  -d '{"article": 1, "content": "很好的文章！"}' \
  --cookie "sessionid=YOUR_SESSION_ID"
```

---

## 注意事项

1. 所有只读操作无需认证
2. 评论的创建、更新、删除需要登录
3. 文章点赞需要登录
4. 默认分页大小为10条/页
5. 支持通过可浏览API界面进行测试
6. 开发环境下CORS已开启，允许所有来源
