# 前端开发指南

## 技术选型建议

### 方案一：Vue 3 + Element Plus（推荐PC端）
- **优势**：组件丰富、开发快速、中文文档完善
- **适用**：管理后台、PC端网站

### 方案二：React + Ant Design
- **优势**：生态成熟、社区活跃
- **适用**：复杂交互应用

### 方案三：Vue 3 + Vant（推荐移动端）
- **优势**：移动端优化、组件完整
- **适用**：H5页面、微信小程序

### 方案四：uni-app（推荐跨平台）
- **优势**：一套代码多端运行
- **适用**：小程序 + H5 + App

---

## 快速开始（Vue 3 示例）

### 1. 创建项目

```bash
# 使用 Vite 创建 Vue 3 项目
npm create vite@latest game-recharge-frontend -- --template vue

cd game-recharge-frontend
npm install

# 安装依赖
npm install axios vue-router pinia element-plus
npm install -D unplugin-vue-components unplugin-auto-import
```

### 2. 配置 vite.config.js

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### 3. 创建 API 服务

**src/api/request.js**
```javascript
import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true // 支持跨域携带cookie
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 可以在这里添加token
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

export default request
```

**src/api/game.js**
```javascript
import request from './request'

// 游戏相关API
export const gameAPI = {
  // 获取游戏分类
  getCategories() {
    return request.get('/products/categories/')
  },
  
  // 获取游戏列表
  getGames(params) {
    return request.get('/products/games/', { params })
  },
  
  // 获取游戏详情
  getGameDetail(id) {
    return request.get(`/products/games/${id}/`)
  },
  
  // 获取热门游戏
  getHotGames() {
    return request.get('/products/games/hot/')
  }
}

// 商品相关API
export const productAPI = {
  // 获取商品列表
  getProducts(params) {
    return request.get('/products/products/', { params })
  },
  
  // 获取商品详情
  getProductDetail(id) {
    return request.get(`/products/products/${id}/`)
  },
  
  // 获取热门商品
  getHotProducts() {
    return request.get('/products/products/hot/')
  },
  
  // 获取推荐商品
  getRecommendedProducts() {
    return request.get('/products/products/recommended/')
  }
}
```

**src/api/article.js**
```javascript
import request from './request'

// 文章相关API
export const articleAPI = {
  // 获取文章分类
  getCategories() {
    return request.get('/articles/categories/')
  },
  
  // 获取文章列表
  getArticles(params) {
    return request.get('/articles/articles/', { params })
  },
  
  // 获取文章详情
  getArticleDetail(id) {
    return request.get(`/articles/articles/${id}/`)
  },
  
  // 获取热门文章
  getHotArticles() {
    return request.get('/articles/articles/hot/')
  },
  
  // 点赞文章
  likeArticle(id) {
    return request.post(`/articles/articles/${id}/like/`)
  }
}

// 评论相关API
export const commentAPI = {
  // 获取评论列表
  getComments(params) {
    return request.get('/articles/comments/', { params })
  },
  
  // 发表评论
  createComment(data) {
    return request.post('/articles/comments/', data)
  },
  
  // 获取评论回复
  getCommentReplies(id) {
    return request.get(`/articles/comments/${id}/replies/`)
  }
}
```

### 4. 创建页面组件

**src/views/Home.vue**
```vue
<template>
  <div class="home">
    <h1>游戏充值平台</h1>
    
    <!-- 热门游戏 -->
    <section class="hot-games">
      <h2>热门游戏</h2>
      <div class="game-grid">
        <div 
          v-for="game in hotGames" 
          :key="game.id"
          class="game-card"
          @click="goToGame(game.id)"
        >
          <img :src="game.icon" :alt="game.name">
          <h3>{{ game.name }}</h3>
          <p>{{ game.category_name }}</p>
        </div>
      </div>
    </section>
    
    <!-- 热门文章 -->
    <section class="hot-articles">
      <h2>热门资讯</h2>
      <div class="article-list">
        <div 
          v-for="article in hotArticles" 
          :key="article.id"
          class="article-item"
          @click="goToArticle(article.id)"
        >
          <img :src="article.cover_image" :alt="article.title">
          <div class="article-info">
            <h3>{{ article.title }}</h3>
            <p>{{ article.summary }}</p>
            <div class="meta">
              <span>{{ article.view_count }} 浏览</span>
              <span>{{ article.like_count }} 点赞</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { gameAPI } from '@/api/game'
import { articleAPI } from '@/api/article'

const router = useRouter()
const hotGames = ref([])
const hotArticles = ref([])

onMounted(async () => {
  // 加载热门游戏
  const gamesData = await gameAPI.getHotGames()
  hotGames.value = gamesData
  
  // 加载热门文章
  const articlesData = await articleAPI.getHotArticles()
  hotArticles.value = articlesData
})

const goToGame = (id) => {
  router.push(`/game/${id}`)
}

const goToArticle = (id) => {
  router.push(`/article/${id}`)
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.game-card {
  cursor: pointer;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s;
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.game-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.article-list {
  margin-top: 20px;
}

.article-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.article-item:hover {
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.article-item img {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}

.article-info {
  flex: 1;
}

.meta {
  display: flex;
  gap: 20px;
  color: #999;
  font-size: 14px;
  margin-top: 10px;
}
</style>
```

**src/views/GameList.vue**
```vue
<template>
  <div class="game-list">
    <h1>游戏列表</h1>
    
    <!-- 搜索和筛选 -->
    <div class="filters">
      <el-input 
        v-model="searchText" 
        placeholder="搜索游戏" 
        @input="handleSearch"
        clearable
      />
      
      <el-select 
        v-model="selectedCategory" 
        placeholder="选择分类"
        @change="handleCategoryChange"
        clearable
      >
        <el-option
          v-for="cat in categories"
          :key="cat.id"
          :label="cat.name"
          :value="cat.id"
        />
      </el-select>
    </div>
    
    <!-- 游戏列表 -->
    <div class="games">
      <div 
        v-for="game in games" 
        :key="game.id"
        class="game-card"
        @click="goToDetail(game.id)"
      >
        <img :src="game.icon" :alt="game.name">
        <h3>{{ game.name }}</h3>
        <p>{{ game.category_name }}</p>
        <el-tag v-if="game.is_hot" type="danger">热门</el-tag>
      </div>
    </div>
    
    <!-- 分页 -->
    <el-pagination
      v-if="total > 0"
      v-model:current-page="currentPage"
      :page-size="10"
      :total="total"
      layout="prev, pager, next"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { gameAPI } from '@/api/game'

const router = useRouter()
const games = ref([])
const categories = ref([])
const searchText = ref('')
const selectedCategory = ref(null)
const currentPage = ref(1)
const total = ref(0)

onMounted(async () => {
  await loadCategories()
  await loadGames()
})

const loadCategories = async () => {
  const data = await gameAPI.getCategories()
  categories.value = data
}

const loadGames = async () => {
  const params = {
    page: currentPage.value,
    search: searchText.value,
    category: selectedCategory.value
  }
  
  const data = await gameAPI.getGames(params)
  games.value = data.results
  total.value = data.count
}

const handleSearch = () => {
  currentPage.value = 1
  loadGames()
}

const handleCategoryChange = () => {
  currentPage.value = 1
  loadGames()
}

const handlePageChange = () => {
  loadGames()
}

const goToDetail = (id) => {
  router.push(`/game/${id}`)
}
</script>

<style scoped>
.game-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin: 20px 0;
}

.games {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.game-card {
  cursor: pointer;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s;
}

.game-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.el-pagination {
  margin-top: 30px;
  text-align: center;
}
</style>
```

### 5. 配置路由

**src/router/index.js**
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GameList from '../views/GameList.vue'
import GameDetail from '../views/GameDetail.vue'
import ProductList from '../views/ProductList.vue'
import ArticleList from '../views/ArticleList.vue'
import ArticleDetail from '../views/ArticleDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/games',
    name: 'GameList',
    component: GameList
  },
  {
    path: '/game/:id',
    name: 'GameDetail',
    component: GameDetail
  },
  {
    path: '/products',
    name: 'ProductList',
    component: ProductList
  },
  {
    path: '/articles',
    name: 'ArticleList',
    component: ArticleList
  },
  {
    path: '/article/:id',
    name: 'ArticleDetail',
    component: ArticleDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

### 6. 运行项目

```bash
npm run dev
```

---

## 移动端开发（uni-app示例）

### 1. 创建项目

```bash
# 使用 HBuilderX 或 命令行创建
npx degit dcloudio/uni-preset-vue#vite my-game-app
cd my-game-app
npm install
```

### 2. API 封装

**utils/request.js**
```javascript
const BASE_URL = 'http://127.0.0.1:8000/api'

export default function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: reject
    })
  })
}
```

### 3. 页面示例

**pages/index/index.vue**
```vue
<template>
  <view class="container">
    <view class="header">
      <text class="title">游戏充值平台</text>
    </view>
    
    <!-- 热门游戏 -->
    <view class="section">
      <view class="section-title">热门游戏</view>
      <scroll-view scroll-x class="game-scroll">
        <view 
          v-for="game in hotGames" 
          :key="game.id"
          class="game-item"
          @tap="goToGame(game.id)"
        >
          <image :src="game.icon" mode="aspectFill"></image>
          <text>{{ game.name }}</text>
        </view>
      </scroll-view>
    </view>
    
    <!-- 热门文章 -->
    <view class="section">
      <view class="section-title">热门资讯</view>
      <view 
        v-for="article in hotArticles" 
        :key="article.id"
        class="article-item"
        @tap="goToArticle(article.id)"
      >
        <image :src="article.cover_image" mode="aspectFill"></image>
        <view class="article-info">
          <text class="article-title">{{ article.title }}</text>
          <text class="article-summary">{{ article.summary }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request'

export default {
  data() {
    return {
      hotGames: [],
      hotArticles: []
    }
  },
  onLoad() {
    this.loadHotGames()
    this.loadHotArticles()
  },
  methods: {
    async loadHotGames() {
      const data = await request('/products/games/hot/')
      this.hotGames = data
    },
    async loadHotArticles() {
      const data = await request('/articles/articles/hot/')
      this.hotArticles = data
    },
    goToGame(id) {
      uni.navigateTo({
        url: `/pages/game/detail?id=${id}`
      })
    },
    goToArticle(id) {
      uni.navigateTo({
        url: `/pages/article/detail?id=${id}`
      })
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
}

.header {
  text-align: center;
  padding: 40rpx 0;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
}

.section {
  margin: 40rpx 0;
}

.section-title {
  font-size: 36rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.game-scroll {
  white-space: nowrap;
}

.game-item {
  display: inline-block;
  width: 200rpx;
  margin-right: 20rpx;
  text-align: center;
}

.game-item image {
  width: 200rpx;
  height: 200rpx;
  border-radius: 16rpx;
}

.article-item {
  display: flex;
  padding: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
}

.article-item image {
  width: 240rpx;
  height: 160rpx;
  border-radius: 8rpx;
  margin-right: 20rpx;
}

.article-info {
  flex: 1;
}

.article-title {
  font-size: 32rpx;
  font-weight: bold;
}

.article-summary {
  font-size: 28rpx;
  color: #666;
  margin-top: 10rpx;
}
</style>
```

---

## 开发建议

### 1. 状态管理
使用 Pinia（Vue）或 Redux（React）管理全局状态

### 2. 组件复用
创建通用组件：游戏卡片、商品卡片、文章卡片等

### 3. 性能优化
- 图片懒加载
- 虚拟列表（长列表）
- 路由懒加载
- API请求缓存

### 4. 用户体验
- Loading状态
- 错误提示
- 空数据提示
- 下拉刷新/上拉加载

### 5. 响应式设计
- 使用CSS Grid/Flexbox
- 移动端适配
- 不同屏幕尺寸测试

---

## 下一步开发任务

1. ✅ 完成首页展示
2. ✅ 实现游戏列表和详情页
3. ✅ 实现商品列表和详情页
4. ✅ 实现文章列表和详情页
5. ⬜ 用户注册/登录功能
6. ⬜ 购物车功能
7. ⬜ 订单管理
8. ⬜ 支付集成

---

## 参考资源

- Vue 3 官方文档：https://cn.vuejs.org/
- Element Plus：https://element-plus.org/zh-CN/
- Vant：https://vant-ui.github.io/vant/
- uni-app：https://uniapp.dcloud.net.cn/
- Axios：https://axios-http.com/zh/
