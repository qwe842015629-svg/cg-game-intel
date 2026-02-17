# 🎮 游戏充值网站 - 项目精简版

## 📋 项目结构说明

经过整理，项目文件已大幅精简，以下是当前的目录结构：

### 根目录文件（精简后）
```
游戏充值网站/
├── README.md                 # 项目说明文件
├── requirements.txt          # 项目依赖包
├── manage.py                 # Django管理脚本
├── MAIN_DOCUMENTATION.md     # 项目主文档
├── USER_GUIDE.md            # 小白用户使用指南
├── cleanup.bat              # 清理脚本
├── organize_files.py        # 文件整理脚本
├── .gitignore              # Git忽略配置
├── .env                    # 环境变量配置
└── archive_YYYYMMDD_HHMMSS/ # 归档目录（包含所有原杂乱文件）
    ├── docs/               # 原文档文件
    ├── scripts/            # 原脚本文件  
    └── tests/              # 原测试文件
```

### 核心功能模块目录
```
游戏充值网站/
├── game_recharge/           # Django项目配置
├── main/                   # 首页管理模块
├── game_product/           # 游戏产品模块
├── game_article/           # 资讯文章模块
├── game_page/              # 游戏页面模块
├── game_product_show/      # 产品展示模块
├── customer_service/       # 客服管理模块
├── footer/                 # 页面底部模块
├── frontend/               # Vue前端项目
└── scripts/                # 核心脚本目录
```

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

## 📚 文档说明

### 1. MAIN_DOCUMENTATION.md
- 项目完整技术文档
- 各模块功能说明
- API接口文档
- 部署说明

### 2. USER_GUIDE.md
- 小白用户使用指南
- 后台操作说明
- 常见问题解答

---

## 🛠️ 核心功能模块

### 1. 首页管理 (main)
- 轮播图管理
- 首页布局配置

### 2. 游戏管理 (game_product)
- 游戏分类管理
- 游戏列表管理

### 3. 资讯管理 (game_article)
- 文章分类管理
- 文章内容管理

### 4. 游戏页面 (game_page)
- 页面分类管理
- 富文本内容编辑
- 图片上传功能

### 5. 产品展示 (game_product_show)
- 产品分类管理
- 产品展示页管理

### 6. 客服管理 (customer_service)
- 联系方式配置
- 常见问题管理

### 7. 页面底部 (footer)
- 底部板块管理
- 底部链接管理

---

## 📞 技术支持

如需帮助，请查看以下文档：
1. `MAIN_DOCUMENTATION.md` - 完整技术文档
2. `USER_GUIDE.md` - 用户操作指南

---

**版本**: v1.0  
**最后更新**: 2026-01-30