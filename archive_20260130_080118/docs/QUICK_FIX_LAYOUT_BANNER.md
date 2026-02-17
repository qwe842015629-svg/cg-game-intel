# 快速修复指南 - 首页布局与轮播图功能区分

## ✅ 已完成的修复

### 1. 模型字段更新 (main/models.py)

**修改**:
- `hero_carousel` → `banner_section`
- 所有选项统一添加"板块"后缀

### 2. Admin界面更新 (main/admin.py)

**修改**:
- 图标映射更新：`'banner_section': '🎪'`

### 3. 前端组件更新 (HomePage.vue)

**修改**:
- `isSectionEnabled('hero_carousel')` → `isSectionEnabled('banner_section')`

## 🚀 需要执行的步骤

### 步骤1: 运行数据迁移脚本

```bash
python update_layout_data.py
```

**功能**:
- 将数据库中的 `hero_carousel` 更新为 `banner_section`
- 为所有板块名称添加"板块"后缀
- 显示当前所有板块状态

### 步骤2: 刷新前端页面

```bash
# 前端会自动热更新
# 直接刷新浏览器: Ctrl + R 或 F5
```

## 📊 功能对比

| 功能 | 首页布局 | 轮播图管理 |
|------|---------|-----------|
| 管理对象 | 首页板块 | 轮播图内容 |
| 控制内容 | 板块显示/隐藏、排序 | 图片、文字、链接 |
| 访问路径 | `/admin/main/homelayout/` | `/admin/main/banner/` |

## 🎯 使用说明

### 控制板块显示
```
首页管理 > 首页布局
→ 启用/禁用 "轮播图板块"
→ 整个轮播图区域显示/隐藏
```

### 管理轮播图内容
```
首页管理 > 轮播图管理
→ 添加/编辑轮播图
→ 上传图片、设置文字和链接
```

## ✅ 验收清单

- [x] 后端模型更新完成
- [x] Admin界面显示正确
- [x] 前端组件更新完成
- [x] 数据迁移脚本创建完成
- [ ] 运行数据迁移脚本
- [ ] 测试后台管理功能
- [ ] 测试前端首页显示

## 📝 详细文档

查看完整说明: [LAYOUT_VS_BANNER_CLARIFICATION.md](./LAYOUT_VS_BANNER_CLARIFICATION.md)

---

**修复时间**: 2026-01-29  
**状态**: ✅ 代码已修复，等待数据迁移
