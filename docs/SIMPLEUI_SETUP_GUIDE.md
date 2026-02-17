# Simple UI 后台管理界面配置指南

## ✅ 安装完成

Simple UI 已成功安装并配置到游戏充值网站的 Django 后台管理系统中！

## 📦 安装信息

### 安装的包
```bash
django-simpleui==2026.1.13
```

### 安装命令
```bash
pip install django-simpleui
```

## 🔧 配置详情

### 1. INSTALLED_APPS 配置

在 `game_recharge/settings.py` 中，已将 `simpleui` 添加到 `INSTALLED_APPS` 的**最前面**（必须在 `django.contrib.admin` 之前）:

```python
INSTALLED_APPS = [
    'simpleui',  # Simple UI 必须放在 django.contrib.admin 之前
    'django.contrib.admin',
    'django.contrib.auth',
    # ... 其他应用
]
```

### 2. Simple UI 自定义配置

已在 `settings.py` 末尾添加了完整的 Simple UI 配置：

#### 基础配置

```python
# 设置首页模块
SIMPLEUI_HOME_PAGE = 'https://www.baidu.com'

# 设置页面标题
SIMPLEUI_HOME_TITLE = '游戏充值网站后台管理系统'

# 设置后台顶部 Logo 文字
SIMPLEUI_LOGO = '游戏充值网站'

# 设置主题
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'  # 默认黑色主题
```

#### 隐私和分析配置

```python
# 隐藏右侧SimpleUI广告和支持链接
SIMPLEUI_HOME_INFO = False

# 隐藏页脚版权信息
SIMPLEUI_HOME_QUICK = False

# 关闭使用分析
SIMPLEUI_ANALYSIS = False

# 显示默认图标
SIMPLEUI_DEFAULT_ICON = True
```

#### 自定义菜单配置

```python
SIMPLEUI_CONFIG = {
    'system_keep': False,  # 不保留系统菜单
    'menu_display': ['游戏管理', '商品管理', '资讯管理', '用户管理', '订单管理', '支付管理'],
    'dynamic': True,  # 开启动态菜单
    'menus': [
        {
            'name': '首页',
            'icon': 'fas fa-home',
            'url': '/admin/'
        },
        {
            'app': 'game_product',
            'name': '游戏管理',
            'icon': 'fas fa-gamepad',
            'models': [
                {
                    'name': '游戏分类',
                    'icon': 'fas fa-list',
                    'url': '/admin/game_product/gamecategory/'
                },
                {
                    'name': '游戏列表',
                    'icon': 'fas fa-gamepad',
                    'url': '/admin/game_product/game/'
                },
            ]
        },
        {
            'app': 'game_product',
            'name': '商品管理',
            'icon': 'fas fa-shopping-cart',
            'models': [
                {
                    'name': '商品类型',
                    'icon': 'fas fa-tags',
                    'url': '/admin/game_product/producttype/'
                },
                {
                    'name': '商品列表',
                    'icon': 'fas fa-box',
                    'url': '/admin/game_product/product/'
                },
            ]
        },
        {
            'app': 'game_article',
            'name': '资讯管理',
            'icon': 'fas fa-newspaper',
            'models': [
                {
                    'name': '文章分类',
                    'icon': 'fas fa-folder',
                    'url': '/admin/game_article/articlecategory/'
                },
                {
                    'name': '文章管理',
                    'icon': 'fas fa-file-alt',
                    'url': '/admin/game_article/article/'
                },
                {
                    'name': '文章标签',
                    'icon': 'fas fa-tag',
                    'url': '/admin/game_article/articletag/'
                },
                {
                    'name': '评论管理',
                    'icon': 'fas fa-comments',
                    'url': '/admin/game_article/comment/'
                },
            ]
        },
    ]
}
```

## 🎨 可用主题

Simple UI 提供了多种精美主题，可以在 `SIMPLEUI_DEFAULT_THEME` 中设置：

| 主题文件 | 说明 | 风格 |
|---------|------|------|
| `admin.lte.css` | 默认主题 | 黑色专业风格（已配置）|
| `layui.css` | Layui主题 | 简洁清新 |
| `ant.design.css` | Ant Design主题 | 现代商务风格 |
| `element.css` | Element UI主题 | Vue风格 |
| `purple.css` | 紫色主题 | 优雅紫色 |
| `x-green.css` | 绿色主题 | 清新绿色 |
| `x-blue.css` | 蓝色主题 | 科技蓝色 |

### 更换主题示例

在 `settings.py` 中修改：

```python
# 更换为蓝色主题
SIMPLEUI_DEFAULT_THEME = 'x-blue.css'

# 更换为紫色主题
SIMPLEUI_DEFAULT_THEME = 'purple.css'

# 更换为 Ant Design 主题
SIMPLEUI_DEFAULT_THEME = 'ant.design.css'
```

## 🌐 访问后台

### 后台管理地址
```
http://127.0.0.1:8000/admin/
```

### 登录信息
使用之前创建的超级管理员账号登录。

如果还没有创建超级管理员，运行：
```bash
python manage.py createsuperuser
```

## 📊 菜单结构

当前配置的菜单结构：

```
游戏充值网站后台管理系统
├─ 🏠 首页
├─ 🎮 游戏管理
│  ├─ 📋 游戏分类
│  └─ 🎮 游戏列表
├─ 🛒 商品管理
│  ├─ 🏷️ 商品类型
│  └─ 📦 商品列表
└─ 📰 资讯管理
   ├─ 📁 文章分类
   ├─ 📄 文章管理
   ├─ 🏷️ 文章标签
   └─ 💬 评论管理
```

## ✨ Simple UI 特性

### 1. 现代化界面
- ✅ 响应式设计，支持移动端
- ✅ 扁平化设计风格
- ✅ 丰富的图标系统（Font Awesome）
- ✅ 多种配色主题

### 2. 增强功能
- ✅ 多标签页支持
- ✅ 快速搜索
- ✅ 菜单折叠
- ✅ 自定义菜单结构
- ✅ 自定义 Logo 和标题

### 3. 性能优化
- ✅ 静态资源 CDN 加速
- ✅ 前端资源压缩
- ✅ 异步加载

## 🔧 自定义配置

### 修改 Logo

```python
SIMPLEUI_LOGO = 'https://your-domain.com/logo.png'
```

### 修改首页

```python
SIMPLEUI_HOME_PAGE = 'http://localhost:5175/'  # 指向Vue前端首页
```

### 添加自定义菜单项

在 `SIMPLEUI_CONFIG['menus']` 中添加：

```python
{
    'name': '订单管理',
    'icon': 'fas fa-shopping-bag',
    'url': '/admin/orders/'
}
```

### 使用自定义图标

Simple UI 使用 Font Awesome 图标库。常用图标：

- `fas fa-home` - 首页
- `fas fa-gamepad` - 游戏
- `fas fa-shopping-cart` - 购物车
- `fas fa-newspaper` - 新闻
- `fas fa-user` - 用户
- `fas fa-cog` - 设置
- `fas fa-chart-bar` - 统计

更多图标请访问：https://fontawesome.com/icons

## 📚 参考文档

- **Simple UI 官方文档**: https://newpanjing.github.io/simpleui_docs/
- **配置说明**: https://newpanjing.github.io/simpleui_docs/config.html
- **主题预览**: https://simpleui.72wo.com/docs/simpleui/theme.html
- **GitHub仓库**: https://github.com/newpanjing/simpleui

## 🎯 下一步操作

1. **访问后台管理**: http://127.0.0.1:8000/admin/
2. **体验 Simple UI 界面**: 查看新的管理界面
3. **尝试不同主题**: 修改 `SIMPLEUI_DEFAULT_THEME` 配置
4. **自定义菜单**: 根据需求调整菜单结构
5. **添加更多管理模块**: 为 users、orders、payments 等应用添加菜单

## ✅ 配置文件清单

已修改的文件：

1. **`game_recharge/settings.py`**
   - ✅ 添加 `simpleui` 到 `INSTALLED_APPS`
   - ✅ 添加 Simple UI 配置

2. **`requirements.txt`**
   - ✅ 添加 `django-simpleui==2026.1.13`

## 🎊 完成！

Simple UI 后台管理界面已成功配置！现在您可以享受更加现代化、美观、易用的 Django 后台管理体验了！

**立即访问**: http://127.0.0.1:8000/admin/

祝您使用愉快！🚀
