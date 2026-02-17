# 首页布局动态排序和内容配置实现指南

## 问题1：排序功能不一致 ✅ 已解决

### 后端改动
- ✅ 已在 `main/views.py` 中的 `HomeLayoutViewSet` 使用 `.order_by('sort_order', 'created_at')`
- ✅ 已在 `main/serializers.py` 中返回 `sortOrder` 字段

### 前端改动
- ✅ 已添加 `sortedEnabledSections` 计算属性（按 `sortOrder` 排序）
- ⚠️ **待完成**：需要将所有section包裹在 `<template v-for="section in sortedEnabledSections">` 中

### 实现方式
```vue
<template>
  <div>
    <!-- 按后台排序动态渲染 -->
    <template v-for="section in sortedEnabledSections" :key="section.sectionKey">
      
      <!-- 轮播图板块 -->
      <section v-if="section.sectionKey === 'banner_section'">
        <!-- 轮播图内容 -->
      </section>
      
      <!-- 核心特性板块 -->
      <section v-else-if="section.sectionKey === 'features'">
        <!-- 特性内容 -->
      </section>
      
      <!-- 其他板块... -->
      
    </template>
  </div>
</template>
```

## 问题2：支持修改模块内容 ✅ 部分完成

### 后端改动
- ✅ 已更新 `main/models.py` 中 `config` 字段的 help_text
- ✅ 已在 `main/admin.py` 中添加详细的配置说明和示例

### 配置格式示例

#### 轮播图板块 (banner_section)
```json
{
  "title": "热门轮播",
  "description": "最新活动与优惠",
  "auto_play": true,
  "interval": 5000
}
```

#### 核心特性板块 (features)
```json
{
  "title": "核心特性",
  "subtitle": "专业、安全、快速",
  "features": [
    {"icon": "⚡", "title": "快速到账", "desc": "5分钟内到账"},
    {"icon": "🔒", "title": "安全保障", "desc": "SSL加密保护"},
    {"icon": "👥", "title": "7x24客服", "desc": "全天候服务"}
  ]
}
```

#### 热门游戏板块 (hot_games)
```json
{
  "title": "热门游戏",
  "subtitle": "最受欢迎的游戏充值",
  "display_count": 8,
  "show_more_button": true
}
```

#### 游戏分类板块 (categories)
```json
{
  "title": "游戏分类",
  "subtitle": "按分类浏览游戏",
  "show_all_category": true
}
```

#### 最新资讯板块 (latest_news)
```json
{
  "title": "最新资讯",
  "subtitle": "智能推荐 · 热门阅读",
  "display_count": 6,
  "show_category": true,
  "show_author": true,
  "show_date": true
}
```

### 前端改动（待完成）

需要修改每个section，从 `section.config` 读取配置内容：

```vue
<!-- Features Section 示例 -->
<section v-else-if="section.sectionKey === 'features'">
  <div class="container mx-auto px-4">
    <div class="text-center mb-16">
      <h2>{{ section.config.title || '核心特性' }}</h2>
      <p>{{ section.config.subtitle || '体验次世代服务' }}</p>
    </div>
    
    <!-- 如果config中有自定义features，使用config的；否则使用默认的 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div v-for="(feature, index) in (section.config.features || defaultFeatures)" :key="index">
        <div>{{ feature.icon }}</div>
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.desc }}</p>
      </div>
    </div>
  </div>
</section>
```

## 下一步操作

### 立即需要完成：

1. **修改 HomePage.vue 模板结构**
   - 将所有 `v-if="isSectionEnabled('xxx')"` 改为 `v-else-if="section.sectionKey === 'xxx'"`
   - 第一个section使用 `v-if`，其余使用 `v-else-if`
   - 在最后添加 `</template>` 关闭 `v-for`

2. **添加默认配置数据**（script部分）
   ```typescript
   const defaultFeatures = [
     { icon: '⚡', title: t('fastArrival'), desc: t('fastArrivalDesc') },
     { icon: '🔒', title: t('secureGuarantee'), desc: t('secureGuaranteeDesc') },
     { icon: '👥', title: t('support247'), desc: t('support247Desc') }
   ]
   ```

3. **修改每个section的标题和内容**
   - 从 `section.config.title` 读取标题，提供默认值
   - 从 `section.config.subtitle` 读取副标题
   - 从 `section.config.xxx` 读取其他配置

### 测试步骤：

1. 在后台修改某个板块的 `sort_order`（如将热门游戏改为10，特性改为5）
2. 刷新前端，检查板块顺序是否改变
3. 在后台修改板块的 `config`（如修改标题）
4. 刷新前端，检查内容是否更新

## 技术说明

- 使用 `computed` 属性确保数据响应式更新
- 使用 `v-for` + `v-if/v-else-if` 组合实现动态顺序渲染
- 通过 `section.config` 传递配置，保持灵活性
- 提供默认值确保向后兼容

