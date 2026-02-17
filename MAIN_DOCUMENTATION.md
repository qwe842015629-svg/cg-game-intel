# 🎮 游戏充值网站 - 项目文档

## 📋 项目概览

这是一个基于 Django + Vue 的游戏充值网站项目，包含以下核心功能模块：
- **首页管理**：轮播图、布局配置
- **游戏管理**：游戏分类、游戏列表
- **商品管理**：商品类型、商品列表
- **资讯管理**：文章分类、文章管理
- **产品展示**：游戏产品展示页面
- **游戏页面**：游戏详细介绍页面
- **客服管理**：联系方式、常见问题
- **页面底部**：底部板块、链接配置

---

## 🚀 快速开始

### 环境准备
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 数据库迁移
python manage.py migrate

# 3. 创建超级用户
python manage.py createsuperuser

# 4. 启动服务器
python manage.py runserver
```

### 访问地址
- **后台管理**: http://127.0.0.1:8000/admin/
- **前端页面**: http://localhost:5176/
- **API文档**: http://127.0.0.1:8000/api/

---

## 📂 文件结构

```
game_recharge/              # Django项目根目录
├── main/                   # 首页管理模块
├── game_product/           # 游戏产品模块
├── game_article/           # 资讯文章模块
├── game_page/              # 游戏页面模块
├── game_product_show/      # 产品展示模块
├── customer_service/       # 客服管理模块
├── footer/                 # 页面底部模块
├── frontend/               # Vue前端项目
└── scripts/                # 自动化脚本
```

---

## 🎨 功能模块详解

### 1. 首页管理 (main)
- **轮播图管理**: 支持图片上传、链接设置
- **首页布局**: 自定义首页板块显示

### 2. 游戏管理 (game_product)
- **游戏分类**: 游戏类型分类管理
- **游戏列表**: 游戏基本信息管理

### 3. 商品管理 (game_product)
- **商品类型**: 游戏商品分类
- **商品列表**: 具体商品信息

### 4. 资讯管理 (game_article)
- **文章分类**: 资讯分类管理
- **文章管理**: 富文本编辑、标签系统
- **评论管理**: 用户评论管理

### 5. 产品展示 (game_product_show)
- **展示分类**: 产品展示分类
- **产品展示页**: 支持富媒体内容

### 6. 游戏页面 (game_page)
- **页面分类**: 游戏页面分类
- **游戏页面**: 富文本编辑、图片上传
- **状态管理**: 草稿/已发布/已归档

### 7. 客服管理 (customer_service)
- **联系方式**: 多种联系方式配置
- **常见问题**: FAQ管理
- **页面配置**: 客服页面设置

### 8. 页面底部 (footer)
- **底部板块**: 底部内容板块
- **底部链接**: 底部导航链接
- **底部配置**: 底部整体配置

---

## 🛠️ 开发工具脚本

### 数据初始化脚本
```bash
# 初始化首页数据
python init_layout_data.py

# 初始化轮播图数据
python init_banner_data.py

# 初始化游戏数据
python init_game_data.py

# 初始化文章数据
python init_article_data.py

# 初始化游戏页面数据
python init_game_page_data.py

# 初始化产品展示数据
python init_product_show_data.py

# 初始化客服数据
python init_customer_service_data.py

# 初始化底部数据
python init_footer_data.py
```

### 数据库维护脚本
```bash
# 检查游戏页面配置
python check_game_page.py

# 检查产品展示配置
python check_product_show_admin.py

# 清理分类数据
python cleanup_categories.py

# 添加测试数据
python add_test_data.py
```

---

## 🔧 常见问题解决

### 1. 后台菜单不显示
- **原因**: Django服务器未重启
- **解决**: 重启服务器并清除浏览器缓存

### 2. 前端页面不更新
- **原因**: 浏览器缓存问题
- **解决**: Ctrl+Shift+R 强制刷新

### 3. API访问失败
- **原因**: 跨域配置问题
- **解决**: 检查 settings.py 中的 CORS 配置

### 4. 图片上传失败
- **原因**: media 目录权限问题
- **解决**: 确保 media 目录可写

---

## 📊 API 接口说明

### 基础路径
```
http://127.0.0.1:8000/api/
```

### 主要接口
- `/banners/` - 轮播图接口
- `/layouts/` - 首页布局接口
- `/products/` - 游戏产品接口
- `/articles/` - 资讯文章接口
- `/game-pages/` - 游戏页面接口
- `/product-show/` - 产品展示接口
- `/customer-service/` - 客服接口
- `/footer/` - 底部接口

---

## 🚀 部署说明

### 开发环境
```bash
# 启动开发服务器
python manage.py runserver

# 启动前端开发服务器
cd frontend && npm run dev
```

### 生产环境
```bash
# 收集静态文件
python manage.py collectstatic --noinput

# 运行生产服务器
gunicorn game_recharge.wsgi:application
```

---

## 📝 技术栈

- **后端**: Django 5.1.5, Django REST Framework
- **前端**: Vue 3, TypeScript, Vite
- **数据库**: MySQL 8.0
- **UI框架**: SimpleUI (后台), Element Plus (前端)
- **构建工具**: npm, webpack

---

## 📞 技术支持

如需帮助，请查看相关模块文档或联系开发团队。

---

**版本**: v1.0  
**最后更新**: 2026-01-30
