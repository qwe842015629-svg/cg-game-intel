# 游戏充值网站 - 完整文件目录结构说明

## 📁 项目概览
这是一个基于 **Django (后端) + Vue 3 (前端)** 的游戏充值电商平台，支持多语言、赛博朋克风格UI、用户认证、游戏充值、文章资讯等功能。

---

## 🎯 核心目录结构

```
游戏充值网站/
├── 📂 frontend/              # 前端项目 (Vue 3 + Vite + TypeScript)
├── 📂 main/                  # Django主应用 (翻译服务、邮件配置)
├── 📂 game_product/          # 游戏产品模块 (商品管理)
├── 📂 game_article/          # 游戏资讯模块 (文章管理)
├── 📂 users/                 # 用户模块 (预留扩展)
├── 📂 games/                 # 游戏基础模块 (预留扩展)
├── 📂 orders/                # 订单模块 (预留扩展)
├── 📂 payments/              # 支付模块 (预留扩展)
├── 📂 game_recharge/         # Django项目配置目录
├── 📂 scripts/               # 翻译脚本工具集
├── 📂 static/                # Django静态文件目录
├── 📂 templates/             # Django模板目录
└── 📄 各类文档...            # 项目文档和配置文件
```

---

## 🎨 前端目录详解 (frontend/)

### 📂 src/ - 源代码目录

#### 1️⃣ **views/** - 页面组件 (共20个页面)

| 文件名 | 功能说明 | 对应URL路径 |
|--------|---------|------------|
| **HomePage.vue** | 🏠 **首页** - 赛博朋克风格，轮播图、热门游戏、核心特性展示 | `/` |
| **GamesPage.vue** | 🎮 **游戏列表页** - 游戏分类浏览、筛选功能 | `/games` |
| **GameDetailPage.vue** | 🎯 **游戏详情页** - 游戏介绍、充值选项、支付方式 | `/games/:id` |
| **RechargePage.vue** | 💳 **充值页面** - 区服选择、金额选择、订单提交 | `/recharge` |
| **ArticlesPage.vue** | 📰 **资讯列表页** - 游戏资讯、攻略、公告分类 | `/articles` |
| **ArticleDetailPage.vue** | 📝 **文章详情页** - 文章内容展示 | `/articles/:id` |
| **SearchResultsPage.vue** | 🔍 **搜索结果页** - 游戏和文章聚合搜索 | `/search` |
| **CustomerServicePage.vue** | 💬 **客服中心** - 在线客服、电话、微信、常见问题 | `/customer-service` |
| **ProfilePage.vue** | 👤 **个人中心** - 用户信息、订单历史、账号设置 | `/profile` |
| **LoginPage.vue** | 🔑 **登录页** - 用户登录表单 | `/login` |
| **RegisterPage.vue** | ✍️ **注册页** - 用户注册、邮箱激活 | `/register` |
| **ActivateAccountPage.vue** | ✅ **账号激活页** - 邮箱激活确认 | `/activate/:uid/:token` |
| **AboutPage.vue** | ℹ️ **关于我们页** - 公司介绍、使命愿景 | `/about` |
| **ContactPage.vue** | 📧 **联系我们页** - 联系方式、商务合作 | `/contact` |
| **CorsTestPage.vue** | 🧪 **CORS测试页** - API跨域测试工具 | `/cors-test` |
| **TranslationDemo.vue** | 🌐 **翻译演示页** - 翻译API功能展示 | `/translation-demo` |
| GameList.vue | 🎮 游戏列表组件 (被GamesPage使用) | - |
| GameDetail.vue | 🎯 游戏详情组件 (被GameDetailPage使用) | - |
| ArticleList.vue | 📰 文章列表组件 (被ArticlesPage使用) | - |
| ArticleDetail.vue | 📝 文章详情组件 (被ArticleDetailPage使用) | - |

#### 2️⃣ **components/** - 通用组件

| 文件名 | 功能说明 | 使用位置 |
|--------|---------|---------|
| **Layout.vue** | 🏗️ **全局布局** - 导航栏、Footer、搜索框、语言切换、主题切换 | 所有页面的外层容器 |
| **GameCard.vue** | 🎴 **游戏卡片** - 游戏展示卡片，支持多语言描述 | 首页、游戏列表页 |
| **AuthDialog.vue** | 🔐 **登录注册弹窗** - 快捷登录/注册对话框 | 导航栏、需要认证的操作 |
| **CyberBackground.vue** | 🌌 **赛博背景** - 赛博朋克风格背景效果 | 首页 |
| **ui/Button.vue** | 🔘 按钮组件 | 全局通用 |
| **ui/Input.vue** | ⌨️ 输入框组件 | 表单页面 |
| **ui/Dialog.vue** | 💬 对话框组件 | 弹窗场景 |
| **ui/Badge.vue** | 🏷️ 徽章组件 | 标签展示 |
| **ui/Tabs.vue** | 📑 标签页组件 | 分类切换 |

#### 3️⃣ **stores/** - Pinia状态管理

| 文件名 | 功能说明 |
|--------|---------|
| **auth.ts** | 👤 **用户认证状态** - 登录状态、用户信息、Token管理 |
| **language.ts** | 🌍 **多语言状态** - 当前语言、语言切换、自定义翻译函数 |
| **theme.ts** | 🎨 **主题状态** - 深色/浅色主题切换 |

#### 4️⃣ **api/** - API接口封装

| 文件名 | 功能说明 |
|--------|---------|
| **client.ts** | 🔧 Axios客户端配置 - 请求拦截、响应处理 |
| **auth.ts** | 🔑 认证接口 - 登录、注册、激活、个人信息 |
| **games.ts** | 🎮 游戏接口 - 游戏列表、游戏详情 |
| **articles.ts** | 📰 文章接口 - 文章列表、文章详情 |
| **index.ts** | 📦 接口导出汇总 |

#### 5️⃣ **i18n/** - 国际化配置

| 文件名 | 功能说明 |
|--------|---------|
| **locales.ts** | 🌐 **翻译文件** - 支持9种语言 (简中、英、日、韩、泰、越、繁中、法、德) |
| **vue-i18n.config.ts** | ⚙️ vue-i18n配置 - 混合自定义翻译和vue-i18n |

#### 6️⃣ **data/** - 模拟数据

| 文件名 | 功能说明 |
|--------|---------|
| **games.ts** | 🎮 游戏数据 - 游戏列表、游戏分类、充值选项 |
| **articles.ts** | 📰 文章数据 - 示例文章数据 |

#### 7️⃣ **router/** - 路由配置

| 文件名 | 功能说明 |
|--------|---------|
| **index.ts** | 🛣️ Vue Router配置 - 所有页面路由定义 |

#### 8️⃣ **其他目录**

| 目录/文件 | 功能说明 |
|----------|---------|
| **composables/** | 🎣 可组合函数 - 可复用的逻辑钩子 |
| **services/** | 🔧 服务层 - translationApi.ts (翻译服务) |
| **types/** | 📐 TypeScript类型定义 - index.ts (全局类型) |
| **assets/** | 🖼️ 静态资源 - 图片、字体等 |
| **plugins/** | 🔌 插件配置 - axios配置 |
| **App.vue** | 🎯 根组件 - 应用入口 |
| **main.js** | 🚀 主入口文件 - Vue应用初始化 |

---

## 🐍 后端目录详解 (Django)

### 📂 main/ - 主应用模块

| 文件名 | 功能说明 |
|--------|---------|
| **translation_service.py** | 🌐 **翻译服务** - 调用翻译之家API，支持缓存 |
| **translation_views.py** | 🔧 翻译视图 - 提供前端翻译接口 |
| **email.py** | 📧 邮件配置 - 激活邮件发送 |
| **views.py** | 🏠 主视图 - 网站首页等 |
| **urls.py** | 🛣️ URL路由 |

### 📂 game_product/ - 游戏产品模块

| 文件名 | 功能说明 |
|--------|---------|
| **models.py** | 📊 数据模型 - 游戏、充值商品、充值选项 |
| **admin.py** | 🛠️ 后台管理 - SimpleUI美化后台 |
| **serializers.py** | 🔄 序列化器 - API数据序列化 |
| **views.py** | 🔧 视图函数 - 游戏CRUD接口 |
| **urls.py** | 🛣️ URL路由 |

### 📂 game_article/ - 游戏资讯模块

| 文件名 | 功能说明 |
|--------|---------|
| **models.py** | 📊 数据模型 - 文章、分类、标签 |
| **admin.py** | 🛠️ 后台管理 |
| **serializers.py** | 🔄 序列化器 |
| **views.py** | 🔧 视图函数 - 文章CRUD接口 |
| **urls.py** | 🛣️ URL路由 |

### 📂 users/ - 用户模块 (预留扩展)

| 文件名 | 功能说明 |
|--------|---------|
| **models.py** | 📊 用户模型 (使用Djoser默认) |
| **admin.py** | 🛠️ 后台管理 |
| **views.py** | 🔧 用户相关视图 |

### 📂 其他Django模块

| 模块 | 功能说明 | 状态 |
|------|---------|------|
| **games/** | 游戏基础模块 | 预留扩展 |
| **orders/** | 订单管理模块 | 预留扩展 |
| **payments/** | 支付接口模块 | 预留扩展 |

### 📂 game_recharge/ - Django项目配置

| 文件名 | 功能说明 |
|--------|---------|
| **settings.py** | ⚙️ 项目配置 - 数据库、CORS、邮件、静态文件 |
| **urls.py** | 🛣️ 根URL配置 |
| **wsgi.py** | 🚀 WSGI配置 |
| **asgi.py** | 🚀 ASGI配置 |

---

## 🛠️ scripts/ - 翻译工具脚本

| 文件名 | 功能说明 |
|--------|---------|
| **full_site_translate.py** | 🌐 全站翻译脚本 - 一键翻译所有页面 |
| **smart_translate.py** | 🧠 智能翻译 - 自动提取中文并翻译 |
| **persistent_translate.py** | 💾 持久化翻译 - 带缓存的翻译 |
| **auto_translate_carousel.py** | 🎠 轮播图翻译 - 专门翻译轮播图内容 |
| **add_carousel_translations.py** | 📝 添加轮播图翻译到配置文件 |
| **add_games_page_translations.py** | 🎮 添加游戏页面翻译 |
| **补充组件翻译.py** | 🧩 补充组件翻译 - 组件级翻译 |
| **翻译缺失键.py** | 🔍 翻译缺失键 - 查找并翻译缺失的键 |
| **component_translations.json** | 📦 组件翻译结果文件 |
| **translation_cache/** | 💾 翻译缓存目录 - 缓存已翻译内容 |

---

## 📄 根目录文件说明

### 🐍 Python管理脚本

| 文件名 | 功能说明 |
|--------|---------|
| **manage.py** | Django管理命令 |
| **create_superuser.py** | 创建超级管理员 |
| **add_test_data.py** | 添加测试数据 |
| **create_test_data.py** | 创建测试数据 |
| **check_db_schema.py** | 检查数据库结构 |
| **fix_db_schema.py** | 修复数据库结构 |
| **update_password.py** | 更新用户密码 |

### 🧪 测试脚本

| 文件名 | 功能说明 |
|--------|---------|
| **test_api.py** | API接口测试 |
| **test_login.py** | 登录功能测试 |
| **test_register.py** | 注册功能测试 |
| **test_mysql.py** | MySQL连接测试 |

### 📚 文档文件

| 文件名 | 功能说明 |
|--------|---------|
| **README.md** | 项目说明文档 |
| **PROJECT_OVERVIEW.md** | 项目概览 |
| **PROJECT_STATUS.md** | 项目状态总结 |
| **API_DOCUMENTATION.md** | API接口文档 |
| **FRONTEND_GUIDE.md** | 前端开发指南 |
| **DEVELOPMENT_PLAN.md** | 开发计划 |
| **INTEGRATION_COMPLETE.md** | 集成完成报告 |
| **数据库切换总结.md** | 数据库迁移文档 |
| **全站多语言翻译方案.md** | 多语言实现方案 |
| **vue-i18n混合方案说明.md** | 翻译系统架构 |
| **邮件激活快速指南.md** | 邮件激活配置 |
| **个人中心页面更新说明.md** | 个人中心功能说明 |

### ⚙️ 配置文件

| 文件名 | 功能说明 |
|--------|---------|
| **requirements.txt** | Python依赖包 |
| **.gitignore** | Git忽略文件 |
| **package.json** | Node.js依赖配置 |
| **vite.config.js** | Vite构建配置 |
| **tailwind.config.js** | Tailwind CSS配置 |
| **postcss.config.js** | PostCSS配置 |

---

## 🎯 核心功能页面映射

### 用户端页面流程

```
首页 (HomePage.vue)
  ↓
游戏列表 (GamesPage.vue) → 游戏详情 (GameDetailPage.vue) → 充值页面 (RechargePage.vue)
  ↓
资讯列表 (ArticlesPage.vue) → 文章详情 (ArticleDetailPage.vue)
  ↓
搜索结果 (SearchResultsPage.vue)
  ↓
客服中心 (CustomerServicePage.vue)
  ↓
用户注册 (RegisterPage.vue) → 邮箱激活 (ActivateAccountPage.vue) → 登录 (LoginPage.vue)
  ↓
个人中心 (ProfilePage.vue)
```

### 管理端页面

- **Django Admin后台**: `http://localhost:8000/admin/`
- 使用SimpleUI美化，支持游戏、文章、用户管理

---

## 🚀 技术栈总结

### 前端技术栈
- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript + JavaScript
- **构建工具**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia
- **UI样式**: Tailwind CSS
- **国际化**: vue-i18n + 自定义翻译系统
- **HTTP客户端**: Axios
- **图标库**: Lucide Vue Next

### 后端技术栈
- **框架**: Django 5.0
- **数据库**: MySQL
- **REST API**: Django REST Framework
- **认证**: Djoser + JWT
- **后台UI**: SimpleUI
- **跨域**: django-cors-headers
- **邮件**: Django Email + SMTP

### 第三方服务
- **翻译API**: 翻译之家 (trans-home.com)
- **邮件服务**: SMTP邮件服务

---

## 📊 项目统计

- **前端页面**: 20个Vue组件
- **通用组件**: 9个
- **API接口**: 30+ 个
- **支持语言**: 9种 (简中、英、日、韩、泰、越、繁中、法、德)
- **Django应用**: 8个模块
- **数据模型**: 20+ 个

---

## 🎨 设计风格

- **主题**: 赛博朋克 (Cyberpunk) 风格
- **配色**: 
  - 主色: 青色 (#00FFFF)、粉色 (#FF1493)、紫色 (#9D00FF)
  - 金色渐变: CYPHER GAME BUY Logo
  - 深色背景: slate-900 → purple-900
- **特效**: 霓虹灯发光、毛玻璃效果、渐变动画

---

## 📝 注意事项

1. **首页文件**: 必须使用 `HomePage.vue`，不要创建 `Home.vue`
2. **Layout组件**: 所有响应式变量必须在 `Layout.vue` 的 setup 中声明
3. **翻译缓存**: 使用 `scripts/translation_cache/` 目录缓存翻译结果
4. **CORS配置**: 已配置允许前端跨域访问后端API
5. **邮件激活**: 需要配置SMTP服务器才能使用注册功能

---

## 🔗 相关链接

- **前端开发服务器**: http://localhost:5173
- **后端API服务器**: http://localhost:8000
- **后台管理界面**: http://localhost:8000/admin/
- **API文档**: http://localhost:8000/api/docs/

---

**最后更新**: 2026年1月

**项目负责人**: 开发团队

**版本**: v1.0.0
