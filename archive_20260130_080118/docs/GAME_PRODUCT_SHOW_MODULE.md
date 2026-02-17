# 游戏产品展示页模块 - 开发文档

## ✅ 项目完成状态

**数据库命名**: `game_product_show` (完全符合用户要求)

### 已完成的工作

#### 1. 数据库模型 ✅
- ✅ 创建 `ProductShowCategory` 模型(产品展示分类)
- ✅ 创建 `ProductShow` 模型(游戏产品展示页)
- ✅ 支持图文上传(cover_image字段)
- ✅ 支持富媒体内容编辑(content字段)
- ✅ 简化设计(相比文章页,去除了标签、评论等复杂功能)

#### 2. 数据库迁移 ✅
已创建数据表:
- `game_product_show_productshowcategory` (产品展示分类表)
- `game_product_show_productshow` (游戏产品展示表)

#### 3. Django Admin后台管理 ✅
**文件**: `game_product_show/admin.py`

**功能**:
- ✅ 富文本内容编辑器(支持HTML和Markdown)
- ✅ 图片上传功能(cover_image)
- ✅ 彩色状态标签显示
- ✅ 内联字段集分组
- ✅ 自动slug生成
- ✅ 预览链接功能

#### 4. REST API接口 ✅
**序列化器** (`serializers.py`):
- `ProductShowCategorySerializer` - 分类序列化器
- `ProductShowListSerializer` - 列表序列化器
- `ProductShowDetailSerializer` - 详情序列化器

**视图集** (`views.py`):
- `ProductShowCategoryViewSet` - 分类只读API
- `ProductShowViewSet` - 展示页只读API
  - 支持分类筛选
  - 支持搜索功能
  - 自动增加浏览量
  - 热门展示页接口(`/hot/`)
  - 推荐展示页接口(`/recommended/`)

**API端点**:
```
GET /api/product-show/categories/          # 获取所有分类
GET /api/product-show/shows/                # 获取所有展示页
GET /api/product-show/shows/{id}/           # 获取展示页详情
GET /api/product-show/shows/hot/            # 获取热门展示页
GET /api/product-show/shows/recommended/    # 获取推荐展示页
```

#### 5. SimpleUI菜单配置 ✅
菜单位置: "产品展示管理" (权重5.5, 显示在"页面底部管理"之后)

子菜单:
- 展示分类
- 产品展示页

---

## 📊 数据库表结构

### game_product_show_productshowcategory (产品展示分类表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt | 主键 |
| name | VARCHAR(100) | 分类名称 |
| description | TEXT | 分类描述 |
| sort_order | INT | 排序 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### game_product_show_productshow (游戏产品展示表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt | 主键 |
| title | VARCHAR(200) | 展示标题 |
| slug | SlugField(200) | URL别名 |
| category_id | BigInt | 展示分类ID(外键) |
| game_id | BigInt | 关联游戏ID(外键,可选) |
| author_id | BigInt | 作者ID(外键) |
| author_name | VARCHAR(100) | 作者名称 |
| cover_image | ImageField | 封面图 |
| excerpt | TEXT(500) | 摘要 |
| content | TEXT | 展示内容(支持富媒体) |
| status | VARCHAR(20) | 状态(draft/published/archived) |
| is_top | BOOLEAN | 是否置顶 |
| is_hot | BOOLEAN | 是否热门 |
| is_recommended | BOOLEAN | 是否推荐 |
| view_count | INT | 浏览次数 |
| like_count | INT | 点赞数 |
| published_at | DATETIME | 发布时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

---

## 🎯 与文章页的对比

### 相同功能
✅ 分类管理  
✅ 状态管理(草稿/已发布/已归档)  
✅ 图片上传  
✅ 富文本编辑  
✅ 浏览量统计  
✅ 置顶/热门/推荐标记  

### 简化的功能
❌ 无标签系统(文章页有ArticleTag)  
❌ 无评论系统(文章页有Comment)  
❌ 无SEO优化字段(文章页有meta_title等)  
❌ 无阅读时间字段  

### 新增功能
✅ 更适合产品展示的数据结构  
✅ 独立的API端点  

---

## 🔧 后台管理使用指南

### 访问路径
```
http://127.0.0.1:8000/admin/
登录后选择：产品展示管理
```

### 添加展示页
1. 点击"产品展示页" → "增加游戏产品展示"
2. 填写基本信息:
   - 展示标题 (必填)
   - 展示分类 (选择已有分类)
   - 关联游戏 (可选)
3. 上传封面图:
   - 点击"选择文件"上传图片
   - 建议尺寸: 1200x600px
4. 编辑内容:
   - 摘要: 简短描述(500字以内)
   - 展示内容: 支持HTML和Markdown格式
   - 可以插入图片、视频等富媒体
5. 发布设置:
   - 状态: 选择"已发布"
   - 置顶/热门/推荐: 根据需要勾选
   - 发布时间: 选择发布时间
6. 点击"保存"

### 富文本编辑技巧

**插入图片**:
```html
<img src="/media/product_shows/image.jpg" alt="产品图片">
```

**插入视频**:
```html
<video controls width="100%">
  <source src="/media/product_shows/video.mp4" type="video/mp4">
</video>
```

**Markdown格式**:
```markdown
## 产品特点

- 特点1
- 特点2

![产品截图](/media/product_shows/screenshot.jpg)
```

---

## 📝 待完成的工作

### 前端集成 (进行中)
- ⏳ 创建前端API文件 (`frontend/src/api/productShow.ts`)
- ⏳ 开发产品展示页面组件
- ⏳ 配置路由

### 数据初始化
- ⏳ 创建初始化数据脚本
- ⏳ 导入测试数据

### 测试验证
- ⏳ API功能测试
- ⏳ 后台管理测试
- ⏳ 前端显示测试

---

## 📄 文件清单

### 后端文件 (已创建)
```
game_product_show/
├── migrations/
│   ├── __init__.py              ✅
│   └── 0001_initial.py          ✅ 数据库迁移文件
├── __init__.py                   ✅
├── admin.py                      ✅ Admin后台配置
├── apps.py                       ✅ 应用配置
├── models.py                     ✅ 数据模型
├── serializers.py                ✅ 序列化器
├── urls.py                       ✅ 路由配置
└── views.py                      ✅ 视图集
```

### 配置文件 (已修改)
```
game_recharge/
├── settings.py                   ✅ 添加应用和菜单
└── urls.py                       ✅ 添加路由
```

### 前端文件 (待创建)
```
frontend/src/
├── api/
│   └── productShow.ts            ⏳ 待创建
├── views/
│   ├── ProductShowPage.vue       ⏳ 待创建
│   └── ProductShowDetailPage.vue ⏳ 待创建
└── types/
    └── productShow.ts            ⏳ 待创建
```

---

## 🚀 下一步操作

1. **创建前端API文件**
2. **开发前端展示页面**
3. **创建初始化数据脚本**
4. **完整功能测试**
5. **编写用户使用文档**

---

**文档创建时间**: 2026-01-30  
**当前状态**: 🟡 后端完成70%,前端待开发  
**数据库命名**: ✅ game_product_show (完全符合用户要求)
