<template>
  <div class="relative min-h-screen py-12">
    <div class="absolute inset-0 bg-gradient-to-b from-cyber-dark/30 to-cyber-blue/30"></div>
    <div class="container mx-auto px-4 relative">
      <!-- Page Header -->
      <div class="text-center mb-16">
        <!-- Breadcrumb Navigation -->
        <div v-if="currentCategory" class="flex items-center justify-center gap-2 text-sm text-cyber-neon-blue mb-4">
          <RouterLink to="/articles" class="hover:text-cyber-neon-green transition-colors">
            所有资讯
          </RouterLink>
          <span>/</span>
          <span class="text-cyber-neon-green">{{ currentCategory }}</span>
        </div>
        
        <h1 class="cyber-title text-5xl md:text-6xl font-black mb-6">
          <span 
            class="text-cyber-neon-green"
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'title')"
          >{{ getPageConfig('title', 'GAME') }}</span> 
          <span
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'subtitle')"
          >{{ getPageConfig('subtitle', $t('news').toUpperCase()) }}</span>
        </h1>
        <p 
          class="text-xl text-cyber-neon-blue max-w-2xl mx-auto"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >
          {{ getPageConfig('description', currentCategory ? `${currentCategory} - ${$t('latestNews')}` : $t('latestNews')) }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-20">
        <div class="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyber-neon-green"></div>
        <p class="text-cyber-neon-blue mt-4 text-lg">加载中...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20">
        <p class="text-cyber-neon-pink text-xl mb-4">❗ {{ error }}</p>
        <button 
          @click="loadArticles" 
          class="px-6 py-3 rounded-xl bg-cyber-neon-blue/20 border border-cyber-neon-blue text-cyber-neon-blue hover:bg-cyber-neon-blue/30 transition-all"
        >
          重试
        </button>
      </div>

      <!-- Articles Grid -->
      <div v-else-if="articles.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <RouterLink
          v-for="article in articles"
          :key="article.id"
          :to="`/articles/${article.id}`"
          class="group relative rounded-2xl clip-corner overflow-hidden"
        >
          <div class="absolute inset-0 bg-gradient-to-br from-cyber-dark to-cyber-blue"></div>
          <img
            v-if="resolveArticleImage(article)"
            :src="resolveArticleImage(article)"
            :alt="article.title"
            class="w-full h-48 object-cover opacity-60 group-hover:opacity-80 transition-opacity"
            @error="handleCardImageError"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-cyber-dark to-transparent opacity-80"></div>
          <div class="relative p-6">
            <div class="mb-4">
              <div class="inline-block px-3 py-1 rounded-full bg-cyber-neon-blue/20 border border-cyber-neon-blue text-cyber-neon-blue text-xs font-bold uppercase tracking-wider">
                {{ article.category }}
              </div>
            </div>
            <h2 class="text-xl font-bold text-white mb-3 group-hover:text-cyber-neon-green transition-colors">{{ article.title }}</h2>
            <p class="text-cyber-neon-blue mb-4">{{ article.excerpt }}</p>
            <div class="flex items-center justify-between text-sm text-cyber-neon-pink">
              <span>{{ article.author }}</span>
              <div class="flex items-center gap-4">
                <span>{{ article.date }}</span>
                <span>{{ article.readTime }}</span>
              </div>
            </div>
          </div>
          <div class="absolute inset-0 border-2 border-transparent group-hover:border-cyber-neon-green/50 rounded-2xl clip-corner transition-all duration-300"></div>
        </RouterLink>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-20">
        <p class="text-cyber-neon-blue text-xl">
          <span v-if="currentCategory">
            「{{ currentCategory }}」分类下暂无文章
          </span>
          <span v-else>
            暂无文章
          </span>
        </p>
        <RouterLink 
          v-if="currentCategory" 
          to="/articles"
          class="inline-block mt-6 px-6 py-3 rounded-xl bg-cyber-neon-blue/20 border border-cyber-neon-blue text-cyber-neon-blue hover:bg-cyber-neon-blue/30 transition-all"
        >
          查看全部文章
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getArticles } from '../api/articles'
import type { Article } from '../types'
import { useVisualEditor } from '../composables/useVisualEditor'

const route = useRoute()
const articles = ref<Article[]>([])
const loading = ref(true)
const error = ref('')
const currentCategory = ref<string>('')

// 可视化编辑支持
const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('articles_page', '资讯列表页')

const normalizeBaseUrl = (value: string) => value.replace(/\/+$/, '')
const BACKEND_ORIGIN = normalizeBaseUrl(
  (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim() || 'http://127.0.0.1:8000'
)

const normalizeImageUrl = (raw: unknown): string => {
  const value = String(raw || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  if (value.startsWith('//')) return `https:${value}`
  if (value.startsWith('/')) return `${BACKEND_ORIGIN}${value}`
  return value
}

const resolveArticleImage = (article: Article): string => {
  const item = article as Article & { cover_image?: string }
  return normalizeImageUrl(item.image || item.cover_image)
}

const handleCardImageError = (event: Event) => {
  const img = event.target as HTMLImageElement | null
  if (!img) return
  img.style.display = 'none'
  img.onerror = null
}

// 加载文章列表
const loadArticles = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 从URL查询参数获取分类
    const category = route.query.category as string || ''
    currentCategory.value = category
    
    // 根据分类参数请求文章
    const params = category ? { category } : undefined
    articles.value = await getArticles(params)
    
    console.log('成功加载文章:', articles.value.length, category ? `分类: ${category}` : '全部')
  } catch (err: any) {
    console.error('加载文章失败:', err)
    error.value = '加载文章失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化，重新加载文章
watch(() => route.query.category, () => {
  loadArticles()
})

onMounted(() => {
  loadArticles()
})
</script>

<style scoped>
.clip-corner {
  clip-path: polygon(
    0% 0%, 
    calc(100% - 15px) 0%, 
    100% 15px, 
    100% 100%, 
    15px 100%, 
    0% calc(100% - 15px)
  );
}
</style>
