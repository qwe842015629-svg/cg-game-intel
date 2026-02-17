# 前端资讯模块修复说明

## 问题描述

前端资讯页面使用的是静态mock数据，没有从后台API获取真实文章数据。

## 修复内容

### 1. 修复API路由 ✅

**文件**: `frontend/src/api/articles.ts`

**修改原因**: 
- 原API调用 `/articles/` → `http://localhost:8000/api/articles/` （错误）
- 正确路由应该是 `/articles/articles/` → `http://localhost:8000/api/articles/articles/`

**修改内容**:
```typescript
// 之前
export const getArticles = async (): Promise<Article[]> => {
  const response: any = await client.get('/articles/')
  return response as Article[]
}

// 修改后
export const getArticles = async (): Promise<Article[]> => {
  const response: any = await client.get('/articles/articles/')
  return response.results || response  // 处理分页响应
}
```

所有相关API都已更新：
- ✅ `getArticles()` - 文章列表
- ✅ `getArticleDetail()` - 文章详情
- ✅ `getHotArticles()` - 热门文章
- ✅ `getRecommendedArticles()` - 推荐文章
- ✅ `likeArticle()` - 点赞文章

### 2. 修复文章列表页面 ✅

**文件**: `frontend/src/views/ArticlesPage.vue`

**修改内容**:
1. 移除静态mock数据导入
2. 添加API调用逻辑
3. 添加加载状态、错误处理、空状态

**新增功能**:
```typescript
const articles = ref<Article[]>([])
const loading = ref(true)
const error = ref('')

const loadArticles = async () => {
  try {
    loading.value = true
    articles.value = await getArticles()
  } catch (err) {
    error.value = '加载文章失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadArticles()
})
```

**UI改进**:
- ✅ 加载动画（旋转的赛博风格加载器）
- ✅ 错误提示（带重试按钮）
- ✅ 空状态提示
- ✅ 保持原有的赛博朋克风格设计

### 3. 修复文章详情页面 ✅

**文件**: `frontend/src/views/ArticleDetailPage.vue`

**修改内容**:
1. 移除静态数据查找逻辑
2. 添加API调用
3. 添加加载状态和错误处理

**新增功能**:
```typescript
const article = ref<Article | null>(null)
const loading = ref(true)
const error = ref('')

const loadArticle = async () => {
  try {
    loading.value = true
    const id = route.params.id as string
    article.value = await getArticleDetail(id)
  } catch (err) {
    error.value = '文章不存在或加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadArticle()
})
```

**UI改进**:
- ✅ 加载状态（与列表页一致的加载器）
- ✅ 404错误提示（保持原有设计）
- ✅ 自动增加浏览量（后台序列化器已实现）

## 数据字段映射

后台序列化器已经完美地将Django字段转换为前端期望的格式：

| 后台字段 | 前端字段 | 说明 |
|---------|---------|------|
| `id` | `id` | 文章ID（转为字符串） |
| `title` | `title` | 文章标题 |
| `excerpt` or `summary` | `excerpt` | 文章摘要 |
| `content` | `content` | 文章内容 |
| `cover_image` | `image` | 封面图片URL |
| `category.name` | `category` | 分类名称 |
| `author_name` | `author` | 作者名称 |
| `published_at` | `date` | 发布日期（格式化为YYYY-MM-DD） |
| `read_time` | `readTime` | 阅读时间 |
| `tags` | `tags` | 标签列表 |

## 测试确认

### 后台API测试 ✅

```bash
python test_article_api_quick.py
```

**结果**:
```
✅ 成功获取文章列表，共 9 篇文章
文章 1: 王者荣耀S35赛季英雄强度排行榜
文章 2: 英雄联盟手游限时活动：峡谷新春庆典
文章 3: 和平精英新手快速上手指南
...
```

### 数据库文章状态 ✅

```bash
python publish_articles.py
```

**结果**:
- 数据库中共有 9 篇文章
- 所有文章状态都是 `published`
- API可以正常返回所有文章

## 前端访问说明

### 访问文章列表页

URL: `http://localhost:5178/news`

**预期行为**:
1. 显示加载动画
2. 从后台API获取文章列表
3. 显示9篇真实文章（从数据库获取）
4. 点击文章卡片可以查看详情

### 访问文章详情页

URL: `http://localhost:5178/articles/{id}`

**预期行为**:
1. 显示加载动画
2. 从后台API获取文章详情
3. 显示完整文章内容
4. 自动增加文章浏览量
5. 如果文章不存在，显示404页面

## 待优化项

### 1. 搜索页面文章（后续）

**文件**: `frontend/src/views/SearchResultsPage.vue`

当前仍使用mock数据，需要修改为调用后台搜索API：
```typescript
// 建议使用
const searchArticles = async (query: string) => {
  return await getArticles({ search: query })
}
```

### 2. 首页文章模块（如有）

如果首页有展示文章的模块，也需要修改为使用API。

### 3. 图片问题

当前文章的 `cover_image` 可能为空，显示的是占位图。
建议在Django后台为每篇文章上传封面图片。

### 4. 分类筛选功能

前端API已支持分类筛选：
```typescript
getArticles({ category: '游戏攻略' })
```

可以在文章列表页添加分类筛选功能。

## 运行说明

### 1. 启动Django后台

```bash
cd e:\小程序开发\游戏充值网站
python manage.py runserver
```

确保运行在 `http://127.0.0.1:8000`

### 2. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

确保运行在 `http://localhost:5178`

### 3. 访问测试

打开浏览器访问：
- 文章列表: `http://localhost:5178/news`
- 文章详情: `http://localhost:5178/articles/1`

## CORS配置确认

Django后台已正确配置CORS：

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5176',
    'http://127.0.0.1:5176',
    'http://localhost:5178',
    'http://127.0.0.1:5178',
]
```

前端请求配置：
```typescript
baseURL: 'http://localhost:8000/api'
withCredentials: true
```

## 修复完成清单

- ✅ API路由修复（/articles/articles/）
- ✅ 文章列表页面使用真实API
- ✅ 文章详情页面使用真实API  
- ✅ 加载状态和错误处理
- ✅ 数据字段映射正确
- ✅ 后台API测试通过
- ✅ 所有文章已发布状态
- ✅ CORS配置正确
- ⏳ 搜索页面文章（待优化）
- ⏳ 文章封面图片上传（待优化）

## 总结

前端资讯模块已成功从使用静态mock数据切换到真实的后台API数据。
现在前端页面会实时显示Django后台添加/修改的文章内容。

**修复时间**: 2026-01-29
**状态**: ✅ 完成
