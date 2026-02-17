# 文章分类过滤功能 - 快速测试指南

## 🎯 功能概述

实现了从前端导航栏"资讯"下拉菜单点击分类后，跳转到对应分类的文章列表页面。

## ✅ 已完成的修改

### 1. 前端修改 (ArticlesPage.vue)

- ✅ 从 URL 参数获取分类名称
- ✅ 根据分类参数调用 API
- ✅ 监听路由参数变化，自动刷新
- ✅ 添加面包屑导航
- ✅ 显示当前分类标题
- ✅ 优化空状态提示

### 2. 后端修改 (game_article/views.py)

- ✅ 重写 `get_queryset` 方法
- ✅ 支持按分类名称过滤（`category__name`）
- ✅ 兼容中文分类名称

## 🚀 快速测试

### 步骤 1: 确保后端服务运行

```bash
# 在项目根目录
python manage.py runserver
```

访问: http://127.0.0.1:8000/admin/

### 步骤 2: 检查文章分类

访问: http://127.0.0.1:8000/admin/game_article/articlecategory/

确保有几个启用的分类，例如：
- ✅ 游戏资讯 (启用)
- ✅ 攻略教程 (启用)
- ✅ 充值指南 (启用)
- ✅ 活动公告 (启用)

### 步骤 3: 确保有测试数据

访问: http://127.0.0.1:8000/admin/game_article/article/

为每个分类添加一些文章，状态设为"已发布"。

### 步骤 4: 测试 API 接口

#### 4.1 获取所有分类

浏览器访问:
```
http://127.0.0.1:8000/api/articles/categories/
```

预期结果: JSON 数组，包含所有启用的分类

#### 4.2 获取所有文章

浏览器访问:
```
http://127.0.0.1:8000/api/articles/articles/
```

预期结果: JSON 对象，包含所有已发布文章

#### 4.3 按分类过滤文章

浏览器访问:
```
http://127.0.0.1:8000/api/articles/articles/?category=游戏资讯
```

预期结果: 只包含"游戏资讯"分类的文章

### 步骤 5: 启动前端服务

```bash
cd frontend
npm run dev
```

访问: http://localhost:5176/

### 步骤 6: 测试前端功能

#### 6.1 测试分类菜单加载

1. 打开首页
2. 悬停到导航栏的"资讯"菜单
3. 检查是否显示所有分类
4. 检查是否显示文章数量

✅ 预期: 
```
资讯 ▼
  游戏资讯 (5)
  攻略教程 (3)
  充值指南 (2)
  活动公告 (1)
```

#### 6.2 测试分类跳转

1. 点击"游戏资讯"
2. 观察 URL 变化
3. 观察页面内容

✅ 预期:
- URL: `http://localhost:5176/articles?category=游戏资讯`
- 面包屑: `所有资讯 / 游戏资讯`
- 标题: `GAME NEWS`
- 副标题: `游戏资讯 - Latest Game News`
- 只显示"游戏资讯"分类的文章

#### 6.3 测试分类切换

1. 在当前"游戏资讯"页面
2. 再次悬停"资讯"菜单
3. 点击"攻略教程"

✅ 预期:
- URL 自动变为: `http://localhost:5176/articles?category=攻略教程`
- 页面无刷新，内容自动更新
- 面包屑变为: `所有资讯 / 攻略教程`
- 只显示"攻略教程"分类的文章

#### 6.4 测试返回全部

1. 在任意分类页面
2. 点击面包屑中的"所有资讯"

✅ 预期:
- URL 变为: `http://localhost:5176/articles`
- 显示所有分类的文章
- 面包屑消失

#### 6.5 测试空分类

1. 在 Django Admin 创建一个新分类
2. 不添加任何文章
3. 在前端点击该分类

✅ 预期:
- 显示: `「新分类」分类下暂无文章`
- 显示"查看全部文章"按钮

### 步骤 7: 浏览器控制台检查

打开浏览器开发者工具 (F12)，查看 Console 标签:

✅ 预期日志:
```
成功加载文章分类: 4 个
成功加载文章: 5 分类: 游戏资讯
```

### 步骤 8: 网络请求检查

在开发者工具的 Network 标签中:

✅ 预期请求:
```
Request URL: http://127.0.0.1:8000/api/articles/articles/?category=游戏资讯
Request Method: GET
Status Code: 200 OK
```

## 🔍 关键代码位置

### 前端核心代码

**文件**: `frontend/src/views/ArticlesPage.vue`

```typescript
// 从URL获取分类参数
const category = route.query.category as string || ''
currentCategory.value = category

// 根据分类请求文章
const params = category ? { category } : undefined
articles.value = await getArticles(params)

// 监听路由变化
watch(() => route.query.category, () => {
  loadArticles()
})
```

### 后端核心代码

**文件**: `game_article/views.py`

```python
def get_queryset(self):
    """重写查询集以支持按分类名称过滤"""
    queryset = super().get_queryset()
    
    # 支持按分类名称过滤
    category_name = self.request.query_params.get('category', None)
    if category_name:
        queryset = queryset.filter(category__name=category_name)
    
    return queryset
```

## 📊 数据流程

```
用户点击"游戏资讯"
    ↓
路由跳转: /articles?category=游戏资讯
    ↓
ArticlesPage 组件加载
    ↓
从 route.query.category 获取参数
    ↓
调用 getArticles({ category: '游戏资讯' })
    ↓
发送请求: GET /api/articles/articles/?category=游戏资讯
    ↓
后端 get_queryset 方法处理
    ↓
过滤: Article.objects.filter(category__name='游戏资讯')
    ↓
返回该分类的文章列表
    ↓
前端渲染文章卡片
```

## 🐛 常见问题排查

### 问题 1: 点击分类后页面显示"暂无文章"

**检查清单**:
- [ ] 后端该分类下是否有文章
- [ ] 文章状态是否为"已发布" (published)
- [ ] 文章分类是否正确关联

**验证方法**:
```python
# Django shell
python manage.py shell

from game_article.models import Article, ArticleCategory

# 查看分类
category = ArticleCategory.objects.get(name='游戏资讯')
print(f"分类: {category.name}")

# 查看该分类的文章
articles = Article.objects.filter(
    category=category,
    status='published'
)
print(f"文章数量: {articles.count()}")
for article in articles:
    print(f"- {article.title}")
```

### 问题 2: API 返回 404

**检查清单**:
- [ ] 后端服务是否运行
- [ ] URL 是否正确
- [ ] 分类名称是否存在

**验证方法**:
直接在浏览器访问 API:
```
http://127.0.0.1:8000/api/articles/articles/?category=游戏资讯
```

### 问题 3: 切换分类时页面不更新

**检查清单**:
- [ ] ArticlesPage.vue 中是否有 watch 监听
- [ ] 浏览器是否缓存了数据

**解决方法**:
清除浏览器缓存或强制刷新 (Ctrl+F5)

### 问题 4: 中文分类名称乱码

**检查清单**:
- [ ] 前端是否使用 encodeURIComponent
- [ ] 后端 settings.py 中 DEFAULT_CHARSET 是否为 'utf-8'

**验证方法**:
查看 Network 标签中的请求 URL，确认已正确编码

## 📝 修改文件清单

| 文件 | 状态 | 修改内容 |
|------|------|----------|
| `frontend/src/views/ArticlesPage.vue` | ✅ 已修改 | 添加分类过滤、面包屑、监听 |
| `game_article/views.py` | ✅ 已修改 | 添加分类名称过滤支持 |
| `test_article_category_filter.py` | ✅ 新建 | API 测试脚本 |
| `ARTICLE_CATEGORY_FILTER.md` | ✅ 新建 | 详细技术文档 |
| `QUICK_TEST_GUIDE.md` | ✅ 新建 | 本快速测试指南 |

## 🎉 功能验收标准

- ✅ 导航栏"资讯"菜单显示所有分类
- ✅ 显示每个分类的文章数量
- ✅ 点击分类跳转到对应的文章列表
- ✅ URL 包含正确的 category 参数
- ✅ 只显示该分类的文章
- ✅ 面包屑导航显示正确
- ✅ 分类标题显示正确
- ✅ 可以快速返回"所有资讯"
- ✅ 切换分类无需刷新页面
- ✅ 空分类显示友好提示

## 📞 需要帮助？

如果测试过程中遇到问题：

1. **检查后端日志**: 查看 Django 控制台输出
2. **检查前端控制台**: 查看浏览器 Console 标签
3. **检查网络请求**: 查看浏览器 Network 标签
4. **查看详细文档**: 阅读 `ARTICLE_CATEGORY_FILTER.md`

---

**测试时间**: 2026-01-29  
**版本**: 1.0  
**状态**: ✅ 准备就绪
