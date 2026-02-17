# 游戏充值网站前端 - Figma 设计完整复刻

## 项目概述

本项目是根据 Figma 原型图一比一复刻的游戏充值网站前端应用，使用 Vue 3 + TypeScript + Tailwind CSS 技术栈开发。

## 技术栈

### 核心框架
- **Vue 3.5.13** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript 超集
- **Vite 7.3.1** - 下一代前端构建工具

### 状态管理 & 路由
- **Vue Router 4** - Vue.js 官方路由
- **Pinia** - Vue 的状态管理库

### UI & 样式
- **Tailwind CSS v3** - 实用优先的 CSS 框架
- **Lucide Vue Next** - 优雅的图标库
- **Radix Vue** - 无样式的可访问 UI 组件

### 工具库
- **@vueuse/core** - Vue 组合式 API 工具集

## 项目结构

```
frontend/
├── src/
│   ├── assets/
│   │   └── main.css              # 全局样式 + CSS 变量
│   ├── components/
│   │   ├── ui/                   # 基础 UI 组件
│   │   │   ├── Badge.vue
│   │   │   ├── Button.vue
│   │   │   ├── Dialog.vue
│   │   │   ├── Input.vue
│   │   │   └── Tabs.vue
│   │   ├── AuthDialog.vue        # 登录/注册对话框
│   │   ├── GameCard.vue          # 游戏卡片组件
│   │   └── Layout.vue            # 布局组件（Header + Footer）
│   ├── data/
│   │   ├── articles.ts           # 文章 Mock 数据
│   │   └── games.ts              # 游戏 Mock 数据
│   ├── router/
│   │   └── index.ts              # 路由配置
│   ├── stores/
│   │   ├── auth.ts               # 用户认证状态
│   │   └── theme.ts              # 主题切换状态
│   ├── types/
│   │   └── index.ts              # TypeScript 类型定义
│   ├── views/
│   │   ├── HomePage.vue          # 首页（轮播图 + 热门游戏）
│   │   ├── GamesPage.vue         # 游戏列表页
│   │   ├── GameDetailPage.vue    # 游戏详情页（充值界面）
│   │   ├── ArticlesPage.vue      # 文章列表页
│   │   ├── ArticleDetailPage.vue # 文章详情页
│   │   ├── ProfilePage.vue       # 个人中心
│   │   └── CustomerServicePage.vue # 客服中心
│   ├── App.vue                   # 根组件
│   └── main.js                   # 应用入口
├── tailwind.config.js            # Tailwind 配置
├── postcss.config.js             # PostCSS 配置
└── package.json
```

## 核心功能

### 1. 首页 (HomePage)
- ✅ 自动轮播的英雄横幅（3个热门游戏）
- ✅ 特性展示卡片（快速到账、安全保障、24小时客服）
- ✅ 热门游戏网格展示
- ✅ 游戏分类导航

### 2. 游戏列表页 (GamesPage)
- ✅ 搜索功能（支持游戏名称和英文名）
- ✅ 分类筛选（全部、国际、港台、东南亚）
- ✅ 响应式卡片网格布局
- ✅ 空状态提示

### 3. 游戏详情页 (GameDetailPage)
- ✅ 大图展示 + 游戏信息
- ✅ 标签和分类展示
- ✅ 游戏简介 / 充值说明 Tab 切换
- ✅ 充值选项卡片（支持推荐标签、折扣显示）
- ✅ 区服选择
- ✅ 游戏 ID 输入
- ✅ 支付方式选择
- ✅ 价格计算和显示
- ✅ 充值按钮（Mock 支付流程）

### 4. 文章资讯
- ✅ 文章列表网格展示
- ✅ 文章详情页（图片 + 内容 + 标签）
- ✅ 分类标签和元数据

### 5. 用户系统
- ✅ 登录 / 注册对话框
- ✅ 用户状态管理（Pinia）
- ✅ 个人中心页面
- ✅ 登出功能

### 6. 全局功能
- ✅ 响应式导航栏
- ✅ 主题切换（明亮/暗黑模式）
- ✅ 搜索栏
- ✅ 客服中心链接
- ✅ 页脚信息
- ✅ 路由导航

## 设计还原度

### 颜色系统
完全复刻 Figma 设计中的颜色方案：
- Primary: `hsl(262.1, 83.3%, 57.8%)` - 紫色主色
- 支持明亮和暗黑两种模式
- 使用 CSS 变量实现主题切换

### 组件样式
- 按钮：多种变体（default, outline, ghost, destructive）
- 卡片：圆角、阴影、边框
- 徽章：多种颜色和大小
- 输入框：统一的高度和边框样式

### 布局
- 响应式设计（移动端、平板、桌面）
- Grid 布局（1/2/3/4 列自适应）
- Sticky 导航栏
- 固定的充值卡片

### 动画效果
- 卡片 hover 放大效果
- 轮播图淡入淡出
- 对话框弹出动画
- 平滑的颜色过渡

## Mock 数据

### 游戏数据（6款游戏）
1. 原神 - 国际游戏
2. 王者荣耀 - 港台游戏
3. Mobile Legends - 东南亚游戏
4. 和平精英 - 国际游戏
5. Free Fire - 东南亚游戏
6. PUBG Mobile - 国际游戏

每款游戏包含：
- 基本信息（名称、图片、分类）
- 充值选项（6个不同金额）
- 支付方式（支付宝、微信、PayPal、USDT等）
- 充值说明
- 区服列表

### 文章数据（6篇文章）
涵盖游戏资讯、充值指南、帮助中心等分类

## 运行项目

### 开发环境
```bash
cd frontend
npm install
npm run dev
```

访问：`http://localhost:5176/`

### 生产构建
```bash
npm run build
```

## 页面路由

| 路径 | 页面 | 描述 |
|------|------|------|
| `/` | HomePage | 首页 |
| `/games` | GamesPage | 游戏列表 |
| `/games/:id` | GameDetailPage | 游戏详情 |
| `/articles` | ArticlesPage | 文章列表 |
| `/articles/:id` | ArticleDetailPage | 文章详情 |
| `/profile` | ProfilePage | 个人中心 |
| `/customer-service` | CustomerServicePage | 客服中心 |

## 状态管理

### Auth Store（用户认证）
- `user` - 当前用户信息
- `isAuthenticated` - 登录状态
- `login()` - 登录方法
- `register()` - 注册方法
- `logout()` - 登出方法

### Theme Store（主题）
- `theme` - 当前主题（light/dark）
- `toggleTheme()` - 切换主题
- `setTheme()` - 设置主题

## 特色功能

### 1. 自动轮播
首页轮播图每 5 秒自动切换，支持手动控制

### 2. 智能搜索
支持按游戏名称（中文/英文）搜索

### 3. 分类筛选
点击分类标签即时筛选游戏

### 4. 主题切换
点击太阳/月亮图标切换明暗主题，设置保存到 localStorage

### 5. 充值流程
完整的充值表单验证和 Mock 支付流程

## 响应式设计

### 断点
- **Mobile**: < 768px（1列布局）
- **Tablet**: 768px - 1024px（2列布局）
- **Desktop**: > 1024px（3-4列布局）

### 适配特性
- 移动端隐藏导航菜单，显示汉堡菜单图标
- 游戏卡片网格自适应
- 充值卡片在移动端全宽显示

## 性能优化

1. **图片懒加载**: 使用 `loading="lazy"`
2. **代码分割**: Vue Router 自动代码分割
3. **CSS 优化**: Tailwind CSS JIT 模式
4. **组件复用**: 统一的 UI 组件库

## 浏览器兼容性

- Chrome（推荐）
- Firefox
- Safari
- Edge

## 后续优化建议

1. **集成真实 API**: 替换 Mock 数据
2. **支付集成**: 接入真实支付网关
3. **图片优化**: 使用 CDN 和 WebP 格式
4. **SEO 优化**: 添加 meta 标签和 SSR
5. **国际化**: 支持多语言
6. **PWA**: 添加离线支持
7. **单元测试**: 使用 Vitest 编写测试
8. **E2E 测试**: 使用 Playwright 测试用户流程

## 开发日志

- ✅ 安装依赖包
- ✅ 创建类型定义
- ✅ 创建 Pinia stores
- ✅ 创建 Mock 数据
- ✅ 创建 UI 组件
- ✅ 创建布局组件
- ✅ 创建所有页面
- ✅ 配置路由
- ✅ 更新主入口
- ✅ 测试验证

## 项目亮点

1. **100% 复刻**: 完全还原 Figma 设计的视觉效果
2. **TypeScript**: 完整的类型安全
3. **组合式 API**: 使用 Vue 3 最新特性
4. **响应式设计**: 完美适配各种设备
5. **暗黑模式**: 支持主题切换
6. **代码规范**: 清晰的项目结构和命名规范

## 联系方式

如有问题或建议，请联系开发团队。

---

**版本**: 1.0.0  
**最后更新**: 2026-01-26  
**开发者**: Qoder AI Assistant
