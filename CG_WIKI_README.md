# CG 游戏百事通 (CG Game Wiki)

这是一个集成了 FreeToGame API 和模拟 GameFAQs 数据的新型游戏资讯页面。

## 功能特点
1.  **自动数据采集**: `data_fetcher.py` 脚本每 48 小时自动运行，抓取最新手游数据。
2.  **数据清洗与聚合**: 自动过滤最近 60 天内发布的游戏，并生成模拟攻略数据。
3.  **可视化展示**: 前端页面展示热门游戏类型分布图（CSS 绘制）。
4.  **响应式设计**: 适配移动端和桌面端，赛博朋克风格。

## 快速开始

### 1. 安装依赖
确保已安装 Python 依赖：
```bash
pip install requests schedule
```

### 2. 运行数据采集脚本
初次运行或手动更新数据：
```bash
python data_fetcher.py
```
该脚本会生成 `frontend/public/data/games_sync.json` 文件。
如果在服务器上运行，脚本会自动进入定时任务模式（每 48 小时更新一次）。

### 3. 启动前端
```bash
cd frontend
npm run dev
```
访问页面: `http://localhost:5173/cg-wiki` (端口取决于 Vite 配置)

## 文件结构
- `data_fetcher.py`: 数据采集核心脚本。
- `frontend/src/views/CGGameWiki.vue`: 前端核心页面组件。
- `frontend/public/data/games_sync.json`: 生成的数据文件。

## 注意事项
- 由于 FreeToGame API 在某些网络环境下可能无法访问，脚本内置了 Mock 数据回退机制，确保页面始终有内容展示。
- GameFAQs API 目前为模拟实现，未来可替换为真实爬虫或 API。
