# 游戏充值网站 - 项目总览

## 📋 项目简介

这是一个基于Django开发的游戏充值平台，提供多种游戏的充值服务、游戏资讯、用户管理等功能。项目采用前后端分离架构，后端提供完整的REST API接口。

---

## 🎯 核心功能

### ✅ 已实现功能

#### 1. 游戏商品模块
- **游戏分类管理**：支持多级分类，热门标记
- **游戏信息管理**：游戏详情、图标、封面、开发商信息
- **商品类型管理**：点券/会员/道具/礼包等类型
- **充值商品管理**：商品价格、库存、销量、折扣
- **完整的REST API**：查询、搜索、筛选、排序、分页

#### 2. 游戏资讯模块
- **文章分类管理**：资讯/攻略/指南/公告等分类
- **文章发布系统**：富文本内容、封面图、标签系统
- **评论互动系统**：评论、回复、点赞功能
- **内容推荐**：热门、推荐、置顶文章
- **完整的REST API**：全文搜索、多维度筛选

#### 3. 管理后台
- **Django Admin**：强大的后台管理界面
- **数据管理**：游戏、商品、文章、评论的CRUD操作
- **批量操作**：批量编辑、批量审核
- **统计信息**：浏览量、销量、评论数等

#### 4. 测试数据
- 自动化测试数据生成脚本
- 6个热门游戏（王者荣耀、和平精英、原神等）
- 13个充值商品
- 4篇资讯文章
- 测试用户账号

### ⬜ 待开发功能

#### 1. 用户系统
- 用户注册/登录
- 第三方登录（微信、QQ）
- 用户资料管理
- 积分系统
- 会员等级

#### 2. 订单系统
- 订单创建
- 订单支付
- 订单查询
- 订单状态管理
- 自动充值

#### 3. 支付系统
- 支付宝支付
- 微信支付
- 余额支付
- 支付回调处理

#### 4. 运营功能
- 优惠券系统
- 活动管理
- 轮播图管理
- 公告系统
- 客服系统

---

## 🏗️ 技术架构

### 后端技术栈
```
Python 3.13
├── Django 6.0.1              # Web框架
├── Django REST Framework 3.16.1  # API框架
├── django-cors-headers 4.9.0     # 跨域支持
├── django-filter 25.2            # 数据过滤
├── Pillow 12.1.0                 # 图像处理
└── python-decouple 3.8           # 环境变量管理
```

### 前端技术栈（建议）
```
Vue 3 / React
├── Axios                    # HTTP客户端
├── Vue Router / React Router  # 路由管理
├── Pinia / Redux           # 状态管理
└── Element Plus / Ant Design  # UI组件库
```

### 数据库
- **开发环境**: SQLite
- **生产环境**: MySQL / PostgreSQL（推荐）

---

## 📁 项目结构

```
游戏充值网站/
├── game_recharge/          # Django项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 主路由配置
│   └── wsgi.py            # WSGI配置
│
├── main/                   # 主应用（首页、全局）
├── users/                  # 用户管理
├── games/                  # 游戏管理（预留）
├── orders/                 # 订单管理
├── payments/               # 支付管理
│
├── game_product/           # 游戏商品模块★
│   ├── models.py          # 数据模型
│   ├── serializers.py     # 序列化器
│   ├── views.py           # 视图
│   ├── admin.py           # Admin配置
│   └── urls.py            # 路由
│
├── game_article/           # 游戏资讯模块★
│   ├── models.py          # 数据模型
│   ├── serializers.py     # 序列化器
│   ├── views.py           # 视图
│   ├── admin.py           # Admin配置
│   └── urls.py            # 路由
│
├── static/                 # 静态文件
├── media/                  # 媒体文件
├── venv/                   # 虚拟环境
│
├── manage.py               # Django管理脚本
├── create_test_data.py     # 测试数据生成脚本
├── requirements.txt        # 依赖清单
├── .env                    # 环境变量
├── .gitignore             # Git忽略文件
│
└── 文档/
    ├── README.md                  # 项目说明
    ├── API_DOCUMENTATION.md       # API接口文档
    ├── API_TEST_GUIDE.md         # API测试指南
    ├── FRONTEND_GUIDE.md         # 前端开发指南
    ├── DEVELOPMENT_PLAN.md       # 功能开发计划
    └── PROJECT_OVERVIEW.md       # 项目总览（本文档）
```

---

## 🔗 API接口总览

### 基础URL
```
http://127.0.0.1:8000/api/
```

### 游戏商品模块 `/api/products/`

| 功能 | 方法 | URL | 说明 |
|------|------|-----|------|
| 游戏分类列表 | GET | `/categories/` | 获取所有分类 |
| 游戏列表 | GET | `/games/` | 支持搜索、筛选 |
| 游戏详情 | GET | `/games/{id}/` | 自动增加浏览数 |
| 热门游戏 | GET | `/games/hot/` | 最多10个 |
| 商品类型 | GET | `/product-types/` | 所有商品类型 |
| 商品列表 | GET | `/products/` | 支持多维度筛选 |
| 商品详情 | GET | `/products/{id}/` | 完整商品信息 |
| 热门商品 | GET | `/products/hot/` | 热门推荐 |
| 推荐商品 | GET | `/products/recommended/` | 编辑推荐 |

### 游戏资讯模块 `/api/articles/`

| 功能 | 方法 | URL | 说明 |
|------|------|-----|------|
| 文章分类 | GET | `/categories/` | 所有分类 |
| 文章列表 | GET | `/articles/` | 已发布文章 |
| 文章详情 | GET | `/articles/{id}/` | 自动增加浏览数 |
| 热门文章 | GET | `/articles/hot/` | 热门内容 |
| 推荐文章 | GET | `/articles/recommended/` | 编辑推荐 |
| 置顶文章 | GET | `/articles/top/` | 置顶内容 |
| 文章点赞 | POST | `/articles/{id}/like/` | 需登录 |
| 标签列表 | GET | `/tags/` | 所有标签 |
| 评论列表 | GET | `/comments/` | 支持筛选 |
| 发表评论 | POST | `/comments/` | 需登录 |
| 评论详情 | GET | `/comments/{id}/` | 包含回复 |

---

## 📊 数据模型设计

### 游戏商品模块

```
GameCategory (游戏分类)
├── name: 分类名称
├── icon: 分类图标
├── sort_order: 排序
└── is_active: 是否启用

Game (游戏)
├── category: 所属分类 [FK]
├── name: 游戏名称
├── icon: 游戏图标
├── cover: 游戏封面
├── developer: 开发商
├── description: 游戏描述
├── is_hot: 是否热门
├── is_active: 是否上架
└── view_count: 浏览次数

ProductType (商品类型)
├── name: 类型名称
├── code: 类型代码
└── description: 类型描述

Product (充值商品)
├── game: 所属游戏 [FK]
├── product_type: 商品类型 [FK]
├── name: 商品名称
├── description: 商品描述
├── original_price: 原价
├── current_price: 现价
├── discount: 折扣
├── stock: 库存
├── sales_count: 销量
├── is_hot: 是否热门
├── is_recommended: 是否推荐
└── is_active: 是否上架
```

### 游戏资讯模块

```
ArticleCategory (文章分类)
├── name: 分类名称
├── description: 分类描述
├── sort_order: 排序
└── is_active: 是否启用

Article (文章)
├── category: 所属分类 [FK]
├── game: 关联游戏 [FK]
├── author: 作者 [FK]
├── title: 文章标题
├── cover_image: 封面图
├── summary: 摘要
├── content: 正文内容
├── tags: 标签 [M2M]
├── status: 状态（草稿/已发布/已归档）
├── is_top: 是否置顶
├── is_hot: 是否热门
├── is_recommended: 是否推荐
├── view_count: 浏览次数
├── like_count: 点赞数
└── comment_count: 评论数

ArticleTag (文章标签)
└── name: 标签名称

Comment (评论)
├── article: 所属文章 [FK]
├── user: 评论用户 [FK]
├── parent: 父评论 [FK] (支持回复)
├── content: 评论内容
└── is_approved: 是否审核通过
```

---

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository>
cd 游戏充值网站

# 创建虚拟环境
py -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置
```bash
# 执行迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 生成测试数据
python create_test_data.py
```

### 3. 启动服务
```bash
python manage.py runserver
```

### 4. 访问系统
- **管理后台**: http://127.0.0.1:8000/admin/
- **API接口**: http://127.0.0.1:8000/api/
- **账号**: admin / admin123456

---

## 📖 文档导航

| 文档 | 说明 | 链接 |
|------|------|------|
| 完整技术文档 | API文档、开发规范、部署指南 | [DOCUMENTATION.md](./DOCUMENTATION.md) |
| 项目总览 | 项目功能概览和架构 | [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) (本文档) |
| 项目状态 | 完成度和待办事项 | [PROJECT_STATUS.md](./PROJECT_STATUS.md) |
| 功能开发计划 | 功能规划和开发路线图 | [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) |
| 快速开始 | 快速安装和启动指南 | [README.md](./README.md) |
| 归档文档 | 历史文档和开发记录 | [docs/](./docs/) |

---

## 🎯 开发路线图

### Phase 1: 基础功能（已完成✅）
- [x] 项目初始化
- [x] 数据模型设计
- [x] REST API开发
- [x] 管理后台配置
- [x] 测试数据生成

### Phase 2: 用户系统（进行中🔄）
- [ ] 用户注册/登录
- [ ] JWT认证
- [ ] 第三方登录
- [ ] 用户资料管理

### Phase 3: 订单支付（待开发⏳）
- [ ] 订单创建与管理
- [ ] 支付宝支付
- [ ] 微信支付
- [ ] 支付回调处理

### Phase 4: 运营功能（待开发⏳）
- [ ] 优惠券系统
- [ ] 活动管理
- [ ] 积分系统
- [ ] 客服系统

### Phase 5: 前端开发（待开发⏳）
- [ ] PC端网站
- [ ] H5移动端
- [ ] 微信小程序
- [ ] 管理后台

### Phase 6: 优化部署（待开发⏳）
- [ ] 性能优化
- [ ] 安全加固
- [ ] 服务器部署
- [ ] 域名配置

---

## 🤝 贡献指南

### 开发规范
1. 代码风格遵循PEP 8
2. 提交信息使用规范格式
3. 所有API必须编写文档
4. 新功能需要编写测试

### 分支管理
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 修复分支

---

## 📞 联系方式

- **项目地址**: e:\小程序开发\游戏充值网站
- **开发服务器**: http://127.0.0.1:8000
- **管理后台**: http://127.0.0.1:8000/admin/

---

## 📝 更新日志

### v0.1.0 (2026-01-29)
- ✅ 整理项目文档结构
- ✅ 创建统一的 DOCUMENTATION.md
- ✅ 归档历史文档到 docs/ 目录
- ✅ 删除冗余测试文件

### v0.1.0 (2026-01-26)
- ✅ 初始化Django项目
- ✅ 创建游戏商品模块（game_product）
- ✅ 创建游戏资讯模块（game_article）
- ✅ 实现完整的REST API
- ✅ 配置Django Admin管理后台
- ✅ 生成测试数据
- ✅ 编写项目文档

---

## 📄 许可证

本项目仅供学习和研究使用。
