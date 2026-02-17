# 🎮 游戏充值网站

一个基于 **Django 5 + Vue 3** 的全栈游戏充值平台。

## ✨ 特性

- 🎯 **多游戏支持** - 支持原神、崩坏、王者荣耀等热门游戏充值
- 💳 **灵活充值** - 多档位充值选项，支持折扣和推荐标记
- 📱 **响应式设计** - 完美适配PC和移动端
- 🔍 **智能搜索** - 快速搜索和分类筛选游戏
- 📰 **资讯系统** - 游戏资讯、攻略教程、活动公告
- 🔐 **用户系统** - 用户注册、登录、个人中心
- 🎨 **现代化UI** - 基于Tailwind CSS的美观界面

## 🛠️ 技术栈

### 后端
- Django 5.1.5
- Django REST Framework 3.16.1
- MySQL
- django-cors-headers
- Simple UI

### 前端
- Vue 3.5.13 + TypeScript
- Vite 7.3.1
- Vue Router 4 + Pinia
- Axios
- Tailwind CSS v3
- Lucide Vue Next

## 📦 安装与运行

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 后端启动

```bash
# 1. 进入项目目录
cd 游戏充值网站

# 2. 创建虚拟环境（如果还没有）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置数据库（修改 game_recharge/settings.py）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'game_recharge_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# 6. 运行迁移
python manage.py migrate

# 7. 创建管理员账号
python manage.py createsuperuser

# 8. 添加测试数据
python add_test_data.py

# 9. 启动服务器
python manage.py runserver
```

访问:
- API: http://127.0.0.1:8000/api/
- 后台: http://127.0.0.1:8000/admin/

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

访问: http://localhost:5176/

## 📚 项目文档

| 文档 | 说明 |
|------|------|
| [📘 主文档](./MAIN_DOCUMENTATION.md) | 项目完整技术文档 |
| [🎮 用户指南](./USER_GUIDE.md) | 小白用户使用指南 |
| [📁 项目结构](./PROJECT_STRUCTURE.md) | 项目目录结构说明 |
| [📁 历史文档](./archive_*/docs/) | 归档的历史文档 |

## 🎯 核心功能

### 游戏充值
- 游戏列表展示
- 分类筛选（国际游戏、港台游戏、东南亚游戏）
- 搜索功能
- 游戏详情查看
- 多档位充值选项
- 充值说明

### 资讯系统
- 文章列表
- 文章分类（游戏资讯、攻略教程、充值指南、活动公告）
- 文章标签
- 热门文章推荐
- 文章点赞

### 用户中心
- 用户注册/登录
- 个人信息管理
- 订单查询
- 充值记录

## 📊 测试数据

系统已预置测试数据:
- **6个游戏**: 原神、崩坏：星穹铁道、绝区零、王者荣耀、Mobile Legends、PUBG Mobile
- **36个充值商品**: 每个游戏6个充值档位 (¥6 ~ ¥648)
- **5篇文章**: 涵盖游戏资讯、攻略、充值指南等

## 🔧 开发指南

### 后端开发

```bash
# 创建新的Django app
python manage.py startapp your_app

# 创建数据库迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 进入Django shell
python manage.py shell
```

### 前端开发

```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```

## 📁 项目结构

```
游戏充值网站/
├── game_product/          # 游戏产品模块
├── game_article/          # 游戏资讯模块
├── game_recharge/         # 项目配置
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── api/          # API服务层
│   │   ├── components/   # 组件
│   │   ├── views/        # 页面
│   │   ├── types/        # 类型定义
│   │   └── stores/       # 状态管理
│   └── ...
├── add_test_data.py      # 测试数据脚本
├── manage.py             # Django管理脚本
└── README.md             # 本文件
```

## 🚧 待实现功能

- [ ] JWT认证系统
- [ ] 支付宝/微信支付对接
- [ ] 订单管理系统
- [ ] 图片上传功能
- [ ] 评论系统
- [ ] 数据缓存
- [ ] SEO优化

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系方式

如有问题或建议，欢迎提Issue或PR。

---

**当前版本**: v1.0.0  
**最后更新**: 2026-01-29  
**项目状态**: 🟢 核心功能已完成，可正常运行
