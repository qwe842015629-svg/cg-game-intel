# 游戏充值网站详细用户使用手册

版本：v2.0  
最后更新：2026-02-19  
适用项目：`e:\小程序开发\游戏充值网站`

## 1. 手册说明

本手册面向以下角色：

1. 前台用户：浏览游戏、查看资讯、注册登录、使用客服与社区功能。
2. 运营人员：通过后台管理游戏内容、文章、客服信息、底部信息与用户。
3. SEO运营人员：使用 SEO 自动化工作台执行抓取、改写、图文优化与发布。
4. 开发/测试人员：需要快速启动系统、验证接口、定位常见错误。

## 2. 系统访问总览

| 模块 | 地址 | 说明 |
|---|---|---|
| 前台站点 | `http://localhost:5176/` | 用户访问入口（Vue） |
| Django后台 | `http://127.0.0.1:8000/admin/` | 管理后台入口 |
| 运营看板 | `http://127.0.0.1:8000/admin/dashboard/` | 数据看板与快捷入口 |
| SEO工作台 | `http://127.0.0.1:8000/admin/seo-automation-workbench/` | SEO五步流程 |
| SEO API设置 | `http://127.0.0.1:8000/admin/seo-api-settings/` | 大模型接口配置 |
| 可视化装修 | `http://127.0.0.1:8000/cms-builder/` | 首页与页面可视化编辑 |
| API根路径 | `http://127.0.0.1:8000/api/` | 前后端接口 |

## 3. 快速启动

### 3.1 一键启动（推荐）

1. 双击 `启动后台.bat` 启动 Django。
2. 双击 `启动前端.bat` 启动 Vue。
3. 浏览器访问前台 `http://localhost:5176/` 或后台 `http://127.0.0.1:8000/admin/`。

注意：启动窗口不要关闭，关闭即停止服务。

### 3.2 手动启动

后台：

```powershell
cd e:\小程序开发\游戏充值网站
.\venv\Scripts\activate
python manage.py runserver
```

前端：

```powershell
cd e:\小程序开发\游戏充值网站\frontend
npm run dev
```

### 3.3 首次初始化（新环境）

```powershell
cd e:\小程序开发\游戏充值网站
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

前端依赖：

```powershell
cd e:\小程序开发\游戏充值网站\frontend
npm install
```

## 4. 账号与权限

### 4.1 前台账号

1. 访问 `/register` 注册账号（邮箱+密码）。
2. 系统发送激活邮件（Djoser）。
3. 点击激活链接（`/activate/{uid}/{token}`）完成激活。
4. 激活后可在 `/login` 登录。

### 4.2 后台账号

1. 使用 Django 管理员账号登录 `/admin/`。
2. 只有 `is_staff=True` 用户可进入后台。
3. SEO API 设置页要求管理员权限（`IsAdminUser`）。

## 5. 前台用户操作手册

### 5.1 顶部导航

主要入口：

1. 首页 `/`
2. 游戏 `/games`
3. 资讯 `/articles`
4. 热榜讯息 `/cg-wiki`
5. 酒馆 `/tavern`
6. 小说剧情 `/novel-story`
7. 广场 `/plaza`
8. 客服 `/customer-service`

公共功能：

1. 全站搜索（回车跳转 `/search?q=关键词`）。
2. 语言切换。
3. 主题/鼠标样式切换。
4. 用户菜单（登录后进入个人中心、退出）。

### 5.2 首页 `/`

可浏览：

1. 轮播图 Banner。
2. 热门游戏推荐。
3. 最新资讯推荐。
4. 游戏分类入口。

首页数据来自：

1. `/api/banners/`
2. `/api/layouts/`
3. `/api/game-pages/pages/hot_pages/`
4. `/api/articles/articles/smart_recommended/`

### 5.3 游戏列表 `/games`

操作流程：

1. 点击分类标签筛选游戏。
2. 进入具体游戏详情页（`/games/:id` 或 slug）。
3. 查看图标、地区、平台、详情与充值说明。
4. 点击“联系客服充值”跳转客服中心。

### 5.4 游戏详情 `/games/:id`

页面包含：

1. 游戏基础信息（开发商、平台、区服、服务器）。
2. 标签（热门、推荐）。
3. 详情与充值说明两个内容标签页。
4. 右侧服务保障与客服入口。

说明：访问详情会增加浏览量统计。

### 5.5 资讯列表与详情

1. `/articles`：按分类浏览资讯。
2. `/articles/:id`：阅读正文、目录、热门游戏推荐、新增文章推荐。
3. 文章详情支持富文本清洗展示，自动生成目录锚点。

### 5.6 搜索 `/search?q=关键词`

搜索结果同时展示：

1. 游戏结果（跳转游戏详情）。
2. 资讯结果（跳转文章详情）。

### 5.7 客服中心 `/customer-service`

展示内容由后台控制：

1. 联系方式（在线客服、邮箱、电话等）。
2. 常见问题 FAQ。
3. 页面标题与说明文案。

### 5.8 注册/登录/激活

1. 注册：`/register`
2. 登录：`/login`
3. 激活：`/activate/:uid/:token`

常见提示：

1. 未收到激活邮件：检查垃圾箱，确认邮箱地址正确。
2. 激活失败：链接可能过期或已使用，重新注册。

### 5.9 个人中心 `/profile`

当前功能：

1. 显示用户基础信息。
2. 显示订单/消费/积分占位卡片。
3. 未登录时提示登录/注册。

说明：订单与消费统计页面为预留结构，实际业务可继续扩展。

### 5.10 充值页 `/recharge`

当前状态：

1. 充值流程 UI 已完成。
2. 真实支付尚未接入（点击提交会提示“开发中”）。

建议：正式上线前需完成支付网关与订单系统对接。

### 5.11 扩展页面

1. `/cg-wiki`：游戏榜单与资讯聚合，支持手动触发更新。
2. `/tavern`：AI酒馆聊天、角色管理、媒体生成功能。
3. `/novel-story`：小说创作、章节生成、作品保存、同步酒馆。
4. `/plaza`：发布动态/角色卡/小说作品，支持点赞评论与内容过滤。

## 6. 后台运营手册

### 6.1 后台入口与看板

1. 登录 `/admin/`。
2. 默认首页为运营看板 `/admin/dashboard/`。
3. 看板可查看核心统计（游戏、资讯、轮播、首页模块、用户、SEO任务）。
4. 可查看近7天趋势图与资讯状态占比。
5. 可使用快捷入口跳转 SEO 工作台、SEO 设置与内容管理。

### 6.2 首页管理（`main`）

主要模型：

1. 全局配置 `SiteConfig`
2. 首页布局 `HomeLayout`
3. 轮播图管理 `Banner`
4. 素材库管理 `MediaAsset`

常用操作：

1. 调整站点名称、主题配置、维护模式。
2. 控制首页板块启用状态与排序。
3. 配置轮播图状态、按钮链接与默认图。
4. 批量上传素材，系统自动去重。

### 6.3 游戏页面管理（`game_page`）

主要模型：

1. 游戏分类 `GamePageCategory`
2. 游戏页面 `GamePage`
3. 充值模板 `GamePageTemplate`

运营流程：

1. 先创建游戏分类。
2. 新增游戏页面并填写标题、slug、图标、详情、SEO信息、发布状态。
3. 可使用“Google Play 导入”快速抓取游戏基础信息。
4. 可通过模板接口复用充值说明（简体/繁体）。
5. 设置 `is_hot`、`is_recommended`、`sort_order` 影响前台展示。

### 6.4 资讯管理（`game_article`）

主要模型：

1. 文章分类 `ArticleCategory`
2. 文章 `Article`
3. 标签 `ArticleTag`
4. 评论 `Comment`

发布流程：

1. 创建分类与标签。
2. 新建文章并填写正文、摘要、封面、SEO字段。
3. 设置状态为 `published` 后前台可见。
4. 可通过置顶/热门/推荐控制前台推荐优先级。
5. 评论支持审核开关。

### 6.5 客服管理（`customer_service`）

模块内容：

1. 联系方式 `ContactMethod`
2. 常见问题 `FAQ`
3. 页面配置 `CustomerServiceConfig`

说明：

1. 页面配置通常只保留一条记录。
2. 可控制是否显示联系方式与FAQ模块。

### 6.6 页面底部管理（`footer`）

模块内容：

1. 底部板块 `FooterSection`
2. 底部链接 `FooterLink`
3. 底部配置 `FooterConfig`

说明：

1. 支持板块内联编辑链接。
2. 可配置外链/内链、排序和启用状态。

### 6.7 用户管理（`auth` + `users`）

可管理：

1. 用户基本信息（用户名、邮箱、状态）。
2. 用户扩展资料（手机号、头像、余额、积分、VIP等级）。
3. 用户组与权限。

### 6.8 可视化装修 `/cms-builder/`

核心能力：

1. 左侧组件库与图层管理。
2. 中间画布预览（桌面/移动切换）。
3. 右侧属性编辑（内容、样式、SEO）。
4. 素材库弹窗：上传、筛选、选择、删除、ALT文本维护。
5. 保存并发布：同步布局排序、全局主题和分区配置。

## 7. SEO 自动化工作台手册

入口：`/admin/seo-automation-workbench/`

### 7.1 使用前准备

1. 先在 `/admin/seo-api-settings/` 配置 Base URL、API Key、模型名。
2. 点击“测试连接”，确认返回成功。

### 7.2 五步流程

步骤1：爬取链接列表（新任务）

1. 填写 BSN 或来源 URL。
2. 可选关键词、页码范围、最大帖子数。
3. 点击“步骤1”生成任务。

步骤2：提取详情内容

1. 选择当前任务后执行步骤2。

步骤3：SEO分析

1. 生成关键词、意图、结构建议。

步骤4：SEO文章生成（草稿）

1. 生成 SEO 草稿并可入库。
2. 可选“自动发布到资讯”。

步骤5：高质量图文优化

1. 自动增强图文、补充媒体、优化元信息。

### 7.3 一键全流程

点击“一键全流程（到步骤5）”可从抓取直达图文优化，适合常规批量任务。

### 7.4 草稿编辑与发布

在工作台下方“SEO文章草稿/发布”可执行：

1. 编辑草稿（标题、Meta、标签、HTML正文）。
2. 立即发布（创建/更新资讯文章）。
3. 标记 review。
4. 删除 SEO 草稿（不会自动删除已关联资讯文章）。

### 7.5 任务维护

支持操作：

1. 设置当前任务。
2. 指定任务执行到步骤4或步骤5。
3. 一键重刷旧草稿来源与筛图。
4. 查看任务详情 JSON。

## 8. 常用 API 说明

主要接口前缀：`/api`

| 模块 | 典型接口 | 用途 |
|---|---|---|
| 游戏页面 | `/api/game-pages/pages/` | 列表与详情 |
| 按slug详情 | `/api/game-pages/pages/by_slug/?slug=xxx` | 游戏详情页读取 |
| 资讯 | `/api/articles/articles/` | 资讯列表 |
| 资讯详情 | `/api/articles/articles/{id}/` | 资讯详情 |
| 客服 | `/api/customer-service/config/current/` | 客服页配置 |
| 底部 | `/api/footer/sections/` | 底部板块与链接 |
| 布局 | `/api/layouts/` | 首页板块 |
| 媒体 | `/api/media/` | 素材上传与管理 |
| 小说草稿 | `/api/novel-drafts/current/` | 小说草稿保存 |
| 广场 | `/api/plaza-posts/` | 广场动态 |
| SEO任务 | `/api/seo-automation/tasks/run/` | 启动新任务 |
| SEO文章发布 | `/api/seo-automation/articles/{id}/publish/` | 发布到资讯 |
| 注册 | `/api/auth/users/` | 创建用户 |
| 激活 | `/api/auth/users/activation/` | 激活账号 |
| 登录 | `/api/auth/token/login/` | Token登录 |
| 退出 | `/api/auth/token/logout/` | Token退出 |

## 9. 常见问题与故障排查

### 9.1 前台或后台打不开

检查顺序：

1. 后台是否启动：`python manage.py runserver`
2. 前端是否启动：`npm run dev`
3. 端口是否被占用：8000、5176
4. 地址是否输入正确（尤其不是 5175）

### 9.2 `by_slug` 接口 500（你当前遇到的典型问题）

报错示例：`/api/game-pages/pages/by_slug/?slug=xxx` 返回 500 + `AttributeError`

定位步骤：

1. 先直接访问后端地址，排除前端代理影响：  
   `http://127.0.0.1:8000/api/game-pages/pages/by_slug/?slug=你的slug`
2. 观察 Django 终端 traceback，定位具体文件与行号。
3. 核对 slug 是否存在且唯一：

```powershell
cd e:\小程序开发\游戏充值网站
.\venv\Scripts\activate
python manage.py shell -c "from game_page.models import GamePage; print(list(GamePage.objects.filter(slug='999-464ef6').values('id','title','slug','status')[:5]))"
```

4. 如果是字段/序列化异常，检查 `game_page/views.py` 与 `game_page/serializers.py` 的字段映射。
5. 若前端显示 HTML 错误页，说明是后端真实异常，不是纯前端问题。

### 9.3 代理或跨域问题

说明：

1. 前端默认通过 Vite 代理 `/api -> http://127.0.0.1:8000`。
2. 若代理失败，开发模式下 GET 请求会尝试直连后端地址。
3. 仍失败时检查 `VITE_BACKEND_TARGET`、Django CORS 配置与后端是否可访问。

### 9.4 登录后接口 401

检查：

1. 浏览器是否保存 `authToken`。
2. Token 是否过期或已清除。
3. 重新登录后重试。

### 9.5 注册后收不到激活邮件

检查：

1. SMTP 配置是否有效。
2. 发件邮箱授权码是否正确。
3. 垃圾邮箱/拦截规则。
4. `DJOSER` 域名配置是否与前端地址一致（默认 `localhost:5176`）。

### 9.6 图片上传失败

检查：

1. 文件格式（建议 jpg/png/webp）。
2. Django `MEDIA_ROOT` 是否可写。
3. Nginx/静态配置（生产环境）。

## 10. 日常运维建议

### 10.1 数据备份

```powershell
cd e:\小程序开发\游戏充值网站
.\venv\Scripts\activate
python manage.py dumpdata > backup_$(Get-Date -Format yyyyMMdd_HHmmss).json
```

### 10.2 数据恢复

```powershell
python manage.py loaddata .\backup_xxxxx.json
```

### 10.3 日志建议

建议至少保留：

1. Django运行日志（终端输出）。
2. 前端构建/运行日志。
3. 关键异常日志文件（如 `_runtime_backend_err.log`）。

### 10.4 上线前检查清单

1. `DEBUG=False`
2. 修改 `SECRET_KEY`
3. 配置正式 `ALLOWED_HOSTS`
4. 清理测试账号与测试数据
5. 更换真实邮件与支付配置
6. 配置 HTTPS 与反向代理

## 11. 命令速查

```powershell
# 启动后台
python manage.py runserver

# 启动前端
cd frontend
npm run dev

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser
```

---

如果你希望，我可以继续输出一版“运营岗位标准操作流程（SOP）”，把每周/每日该做的动作和检查项做成表格版。

运营SOP文档：`docs/运营SOP.md`
