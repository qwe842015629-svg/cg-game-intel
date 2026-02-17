# 游戏页面管理模块 (game_page) 开发文档

## 📋 模块概述

`game_page` 模块是一个专门用于管理游戏相关内容页面的Django应用，支持富文本编辑、图片上传、分类管理等功能。

**开发日期**: 2026-01-30  
**数据库表名**: `game_page_gamepage`, `game_page_gamepagecategory`  
**API路径**: `/api/game-pages/`

---

## 🎯 功能特性

### 核心功能
- ✅ **分类管理**: 支持多级分类，可自定义排序
- ✅ **富文本编辑**: 支持HTML/Markdown格式内容
- ✅ **图片上传**: 支持封面图片上传
- ✅ **状态管理**: 草稿/已发布/已归档三种状态
- ✅ **标记系统**: 置顶、热门、推荐标记
- ✅ **统计功能**: 浏览次数、点赞数统计
- ✅ **游戏关联**: 可关联到具体游戏
- ✅ **权限控制**: 前端只显示已发布内容，后台可管理所有内容

### 简化设计
相比文章模块，本模块做了以下简化：
- ❌ 移除了标签系统
- ❌ 移除了评论功能
- ❌ 简化了作者系统（使用字符串而非完整用户关系）

---

## 📊 数据库结构

### GamePageCategory（游戏页面分类）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| name | CharField(100) | 分类名称 |
| description | TextField | 分类描述 |
| sort_order | IntegerField | 排序序号 |
| is_active | BooleanField | 是否启用 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### GamePage（游戏页面）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| title | CharField(200) | 页面标题 |
| slug | SlugField(200) | URL别名（唯一） |
| category | ForeignKey | 关联分类 |
| game | ForeignKey | 关联游戏（可选） |
| author | ForeignKey(User) | 作者用户 |
| author_name | CharField(100) | 作者名称 |
| cover_image | ImageField | 封面图片 |
| excerpt | TextField(500) | 摘要 |
| content | TextField | 页面内容（富文本） |
| status | CharField(20) | 状态（draft/published/archived） |
| is_top | BooleanField | 是否置顶 |
| is_hot | BooleanField | 是否热门 |
| is_recommended | BooleanField | 是否推荐 |
| view_count | IntegerField | 浏览次数 |
| like_count | IntegerField | 点赞数 |
| published_at | DateTimeField | 发布时间 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

---

## 🔌 API 接口

### 基础路径
```
http://127.0.0.1:8000/api/game-pages/
```

### 分类接口

#### 1. 获取所有分类
```http
GET /api/game-pages/categories/
```

**响应示例**:
```json
[
  {
    "id": 1,
    "name": "游戏攻略",
    "description": "各类游戏的攻略指南、技巧分享",
    "sort_order": 1,
    "is_active": true,
    "game_pages_count": 5,
    "created_at": "2026-01-30T10:00:00",
    "updated_at": "2026-01-30T10:00:00"
  }
]
```

#### 2. 获取激活的分类
```http
GET /api/game-pages/categories/active/
```

### 页面接口

#### 1. 获取页面列表
```http
GET /api/game-pages/pages/
```

**查询参数**:
- `category`: 分类ID
- `game`: 游戏ID
- `status`: 状态（draft/published/archived）
- `is_top`: 是否置顶（true/false）
- `is_hot`: 是否热门（true/false）
- `is_recommended`: 是否推荐（true/false）
- `search`: 搜索关键词（标题、摘要、内容、作者）
- `ordering`: 排序字段（view_count, like_count, published_at, created_at, is_top）

**响应示例**:
```json
[
  {
    "id": 1,
    "title": "王者荣耀新手入门指南",
    "slug": "wzry-beginner-guide",
    "category": 1,
    "category_name": "新手指南",
    "game": 1,
    "game_name": "王者荣耀",
    "author_name": "游戏小编",
    "cover_image_url": "http://127.0.0.1:8000/media/game_pages/cover.jpg",
    "excerpt": "详细的王者荣耀新手入门教程...",
    "status": "published",
    "is_top": true,
    "is_hot": true,
    "is_recommended": true,
    "view_count": 100,
    "like_count": 20,
    "published_at": "2026-01-30T10:00:00",
    "created_at": "2026-01-30T10:00:00",
    "updated_at": "2026-01-30T10:00:00"
  }
]
```

#### 2. 获取页面详情
```http
GET /api/game-pages/pages/{id}/
```

**响应示例**:
```json
{
  "id": 1,
  "title": "王者荣耀新手入门指南",
  "slug": "wzry-beginner-guide",
  "category": 1,
  "category_name": "新手指南",
  "category_info": {
    "id": 1,
    "name": "新手指南",
    "description": "新手入门教程和常见问题解答"
  },
  "game": 1,
  "game_info": {
    "id": 1,
    "name": "王者荣耀",
    "icon": "/media/games/wzry.jpg"
  },
  "author_name": "游戏小编",
  "cover_image_url": "http://127.0.0.1:8000/media/game_pages/cover.jpg",
  "excerpt": "详细的王者荣耀新手入门教程...",
  "content": "<h2>一、游戏基础操作</h2><p>...</p>",
  "status": "published",
  "is_top": true,
  "is_hot": true,
  "is_recommended": true,
  "view_count": 101,
  "like_count": 20,
  "published_at": "2026-01-30T10:00:00",
  "created_at": "2026-01-30T10:00:00",
  "updated_at": "2026-01-30T10:00:00"
}
```

#### 3. 根据slug获取详情
```http
GET /api/game-pages/pages/by_slug/?slug=wzry-beginner-guide
```

#### 4. 获取置顶页面
```http
GET /api/game-pages/pages/top_pages/
```

#### 5. 获取热门页面
```http
GET /api/game-pages/pages/hot_pages/
```

#### 6. 获取推荐页面
```http
GET /api/game-pages/pages/recommended_pages/
```

#### 7. 根据游戏获取页面
```http
GET /api/game-pages/pages/by_game/?game_id=1
```

#### 8. 点赞页面
```http
POST /api/game-pages/pages/{id}/like/
```

**响应示例**:
```json
{
  "status": "success",
  "like_count": 21
}
```

---

## 🎨 后台管理

### 访问地址
```
http://127.0.0.1:8000/admin/game_page/
```

### 功能特性

#### 页面分类管理
- 分类列表显示：名称、描述、页面数量、状态
- 支持搜索、过滤、排序
- 批量启用/禁用

#### 游戏页面管理
- **字段分组**:
  - 基本信息：标题、slug、分类、游戏、作者、封面图
  - 内容编辑：摘要、富文本内容（支持HTML/Markdown）
  - 状态设置：发布状态、置顶/热门/推荐标记
  - 时间管理：发布时间、创建时间、更新时间
  
- **列表显示**:
  - 封面图缩略图预览
  - 彩色状态标签
  - 快速筛选器（状态、标记）
  - 搜索功能
  
- **富文本编辑器**:
  - 20行大文本框
  - 支持HTML标签
  - 支持Markdown语法
  - 可嵌入图片、视频

---

## 💻 前端集成

### TypeScript类型定义

```typescript
// frontend/src/api/gamePages.ts

export interface GamePageCategory {
  id: number
  name: string
  description: string
  sort_order: number
  is_active: boolean
  game_pages_count: number
  created_at: string
  updated_at: string
}

export interface GamePage {
  id: number
  title: string
  slug: string
  category: number
  category_name: string
  game?: number
  game_name?: string
  author_name: string
  cover_image_url?: string
  excerpt: string
  content?: string
  status: 'draft' | 'published' | 'archived'
  is_top: boolean
  is_hot: boolean
  is_recommended: boolean
  view_count: number
  like_count: number
  published_at: string
  created_at: string
  updated_at: string
}
```

### API调用示例

```typescript
import { 
  getGamePages, 
  getGamePageDetail, 
  getHotGamePages 
} from '@/api/gamePages'

// 获取所有页面
const pages = await getGamePages()

// 获取特定分类的页面
const categoryPages = await getGamePages({ category: 1 })

// 获取热门页面
const hotPages = await getHotGamePages()

// 获取页面详情
const page = await getGamePageDetail(1)
```

---

## 🧪 测试验证

### 1. 数据库迁移验证

```bash
# 执行检查脚本
python check_game_page.py
```

**预期输出**:
```
=== game_page 数据表检查 ===
✓ 找到 2 个表:
  - game_page_gamepage
  - game_page_gamepagecategory

=== game_page 迁移记录 ===
✓ 已应用 1 个迁移:
  - 0001_initial

=== Admin 注册检查 ===
✓ GamePage 已注册到 Admin
✓ GamePageCategory 已注册到 Admin

=== 数据库查询测试 ===
✓ GamePageCategory 数量: 5
✓ GamePage 数量: 5
```

### 2. 初始化测试数据

```bash
# 执行初始化脚本
python init_game_page_data.py
```

**生成数据**:
- 5个分类：游戏攻略、游戏资讯、新手指南、活动公告、玩家心得
- 5个示例页面：包含各种状态和标记的测试数据

### 3. API接口测试

```bash
# 测试分类接口
curl http://127.0.0.1:8000/api/game-pages/categories/

# 测试页面列表
curl http://127.0.0.1:8000/api/game-pages/pages/

# 测试热门页面
curl http://127.0.0.1:8000/api/game-pages/pages/hot_pages/

# 测试页面详情
curl http://127.0.0.1:8000/api/game-pages/pages/1/
```

### 4. 后台管理测试

1. 访问 http://127.0.0.1:8000/admin/game_page/
2. 验证菜单显示"游戏页面管理"
3. 测试分类的增删改查
4. 测试页面的富文本编辑
5. 测试图片上传功能
6. 测试筛选和搜索功能

---

## 📁 文件清单

### Django应用文件
```
game_page/
├── __init__.py              # 应用配置引用
├── apps.py                  # 应用配置（verbose_name）
├── models.py                # 数据模型
├── admin.py                 # 后台管理配置
├── serializers.py           # REST序列化器
├── views.py                 # API视图集
├── urls.py                  # URL路由
└── migrations/
    └── 0001_initial.py      # 初始迁移文件
```

### 工具脚本
```
check_game_page.py           # 数据库检查脚本
init_game_page_data.py       # 初始化数据脚本
```

### 前端文件
```
frontend/src/api/
├── gamePages.ts             # API接口和类型定义
└── index.ts                 # API统一导出
```

### 配置文件
```
game_recharge/
├── settings.py              # SimpleUI菜单配置
└── urls.py                  # 主URL路由配置
```

---

## 🚀 部署清单

### 1. 数据库准备
```bash
# 执行迁移
python manage.py migrate game_page

# 初始化数据
python init_game_page_data.py
```

### 2. 配置检查
- ✅ `settings.py` 中已添加 `'game_page'` 到 INSTALLED_APPS
- ✅ SimpleUI菜单配置已添加
- ✅ 主URL路由已配置

### 3. 静态文件
```bash
# 收集静态文件
python manage.py collectstatic
```

### 4. 权限设置
- 确保 `media/game_pages/` 目录可写
- 配置Nginx/Apache处理媒体文件

---

## 📝 使用场景

### 场景1: 游戏攻略发布
1. 后台创建"游戏攻略"分类
2. 创建新页面，选择分类和关联游戏
3. 使用富文本编辑器编写攻略内容
4. 上传封面图和内容图片
5. 设置为"热门"和"推荐"
6. 发布后前端自动展示

### 场景2: 活动公告
1. 创建"活动公告"分类页面
2. 设置为"置顶"确保优先展示
3. 发布时间可设置为活动开始时间
4. 前端按时间自动展示

### 场景3: 新手指南
1. 创建多个新手指南页面
2. 关联到不同游戏
3. 前端根据游戏ID筛选显示
4. 提供搜索功能方便查找

---

## 🔧 维护建议

### 性能优化
1. 使用 `select_related` 优化数据库查询（已实现）
2. 对热门页面使用缓存
3. 图片上传限制大小（建议500KB以内）
4. 定期清理归档内容

### 内容管理
1. 定期审核和更新过时内容
2. 监控浏览量和点赞数，优化推荐算法
3. 收集用户反馈，改进内容质量
4. 建立内容审核流程

### 安全建议
1. 富文本内容需过滤危险HTML标签
2. 图片上传需验证文件类型
3. 限制内容长度防止攻击
4. 定期备份数据库

---

## 📞 技术支持

如有问题，请检查：
1. Django服务器运行状态
2. 数据库连接是否正常
3. 迁移是否全部执行
4. 静态文件是否正确配置
5. 权限设置是否正确

---

**文档版本**: v1.0  
**最后更新**: 2026-01-30  
**维护者**: 游戏充值网站开发团队
