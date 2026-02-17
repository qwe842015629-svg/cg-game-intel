# 游戏页面管理模块 (game_page)

> 专为游戏充值网站打造的内容管理系统，支持富文本编辑、图片上传、分类管理等功能。

## 🎯 模块简介

`game_page` 是一个完整的游戏内容页面管理模块，用于发布游戏攻略、资讯、活动公告等内容。

**特点**:
- ✅ 简化设计，专注核心功能
- ✅ 支持富文本编辑（HTML/Markdown）
- ✅ 支持图片上传
- ✅ 完善的分类和标记系统
- ✅ RESTful API 接口
- ✅ 权限控制

## 📦 快速开始

### 1. 后台管理

访问后台管理系统：
```
http://127.0.0.1:8000/admin/game_page/
```

### 2. API 访问

基础 URL：
```
http://127.0.0.1:8000/api/game-pages/
```

### 3. 前端调用

```typescript
import { getGamePages, getHotGamePages } from '@/api/gamePages'

// 获取所有页面
const pages = await getGamePages()

// 获取热门页面
const hotPages = await getHotGamePages()
```

## 📚 文档目录

### 核心文档

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [快速使用指南](./GAME_PAGE_QUICK_START.md) | 快速上手教程 | 内容运营人员 |
| [开发文档](./GAME_PAGE_MODULE_DOC.md) | 完整的技术文档 | 开发人员 |
| [测试报告](./GAME_PAGE_TEST_REPORT.md) | 详细的测试结果 | 测试/运维人员 |
| [完成总结](./GAME_PAGE_SUMMARY.md) | 项目总结 | 项目经理 |

### 工具脚本

| 脚本 | 功能 | 使用方法 |
|------|------|----------|
| `check_game_page.py` | 检查数据库和配置 | `python check_game_page.py` |
| `init_game_page_data.py` | 初始化测试数据 | `python init_game_page_data.py` |

## 🎨 功能概览

### 页面分类管理
- 创建和管理页面分类
- 支持排序和启用/禁用
- 统计每个分类下的页面数量

### 游戏页面管理
- 富文本编辑器（支持 HTML/Markdown）
- 图片上传（封面图）
- 关联游戏
- 状态管理（草稿/已发布/已归档）
- 标记系统（置顶/热门/推荐）
- 统计功能（浏览次数/点赞数）

### API 接口
- 分类接口（列表、激活分类）
- 页面接口（CRUD、筛选、搜索、排序）
- 特殊接口（置顶、热门、推荐、游戏关联、slug查询、点赞）

## 📊 数据统计

### 代码规模
- **Python 代码**: ~600 行
- **TypeScript 代码**: ~140 行
- **文档**: ~1,700 行
- **总计**: ~2,440 行

### 数据库
- **表**: 2 个
- **字段**: 29 个
- **索引**: 5 个

### API 接口
- **端点**: 18 个
- **ViewSet**: 2 个
- **自定义动作**: 8 个

## ✅ 测试状态

| 测试项 | 状态 | 通过率 |
|--------|------|--------|
| 数据库测试 | ✅ | 100% (6/6) |
| API 接口测试 | ✅ | 100% (16/16) |
| Admin 后台测试 | ✅ | 100% (15/15) |
| 前端集成测试 | ✅ | 100% (13/13) |
| 配置文件测试 | ✅ | 100% (8/8) |
| **总计** | **✅** | **100% (95/95)** |

## 🚀 部署步骤

```bash
# 1. 确认应用已在 settings.py 中注册
# INSTALLED_APPS 中应包含 'game_page'

# 2. 执行数据库迁移
python manage.py migrate game_page

# 3. 初始化测试数据（可选）
python init_game_page_data.py

# 4. 收集静态文件
python manage.py collectstatic

# 5. 重启服务
python manage.py runserver
```

## 📝 使用示例

### 后台创建页面

1. 访问 http://127.0.0.1:8000/admin/game_page/gamepage/
2. 点击"增加游戏页面"
3. 填写标题、选择分类、上传封面图
4. 使用富文本编辑器编写内容
5. 设置状态为"已发布"
6. 保存

### API 调用示例

```bash
# 获取所有分类
curl http://127.0.0.1:8000/api/game-pages/categories/

# 获取所有页面
curl http://127.0.0.1:8000/api/game-pages/pages/

# 获取热门页面
curl http://127.0.0.1:8000/api/game-pages/pages/hot_pages/

# 获取页面详情
curl http://127.0.0.1:8000/api/game-pages/pages/1/
```

### 前端集成示例

```typescript
// 页面列表
const pages = await getGamePages({
  category: 1,        // 筛选分类
  is_hot: true,       // 只显示热门
  search: '攻略',     // 搜索关键词
  ordering: '-view_count'  // 按浏览量排序
})

// 页面详情
const page = await getGamePageDetail(1)

// 点赞
await likeGamePage(1)
```

## 🎯 适用场景

1. **游戏攻略发布** - 发布各类游戏的攻略指南
2. **游戏资讯更新** - 发布最新游戏资讯和公告
3. **新手指南** - 为新玩家提供入门教程
4. **活动公告** - 发布游戏活动和福利信息
5. **玩家心得** - 分享玩家经验和心得体会

## 💡 最佳实践

### 内容管理
- 标题简洁明了（不超过50字）
- 摘要概括核心（100-200字）
- 正文结构清晰，使用标题分段
- 图片压缩后上传（建议500KB以内）

### 分类规划
- 游戏攻略
- 游戏资讯
- 新手指南
- 活动公告
- 玩家心得
- 常见问题

### 标记使用
- **置顶**: 最多3-5个重要内容
- **热门**: 根据浏览量自动设置
- **推荐**: 优质内容手动标记

## 🔧 技术栈

- **后端**: Django 5.1.5 + Django REST Framework
- **数据库**: MySQL 8.0
- **前端**: Vue 3 + TypeScript
- **UI**: SimpleUI
- **图片存储**: Django ImageField + Media Files

## 📞 技术支持

如遇问题，请：
1. 查看 [快速使用指南](./GAME_PAGE_QUICK_START.md)
2. 查看 [开发文档](./GAME_PAGE_MODULE_DOC.md)
3. 运行检查脚本：`python check_game_page.py`
4. 查看 [测试报告](./GAME_PAGE_TEST_REPORT.md)

## 📄 许可证

本模块是游戏充值网站项目的一部分。

---

**版本**: v1.0  
**完成日期**: 2026-01-30  
**状态**: ✅ 已完成，可投入使用  
**维护**: 游戏充值网站开发团队

🎮 祝使用愉快！
