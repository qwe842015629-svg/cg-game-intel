<template>
  <div class="min-h-screen py-10">
    <div class="container mx-auto px-4">
      <div class="mb-8">
        <h1
          class="text-3xl md:text-4xl font-black text-foreground mb-3"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'title')"
        >
          {{ getPageConfig('title', $t('searchResults')) }}
        </h1>
        <div class="flex items-center gap-2 text-muted-foreground">
          <Search class="w-5 h-5" />
          <span
            class="text-base"
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'query_label')"
          >
            {{ getPageConfig('query_label', '搜索关键词：') }}
          </span>
          <span class="text-base font-semibold text-primary">{{ query }}</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-8">
        <div class="surface-card p-4">
          <div class="text-2xl font-black text-primary mb-1">{{ filteredGames.length }}</div>
          <div class="text-muted-foreground text-sm">{{ $t('gamesFound') }}</div>
        </div>
        <div class="surface-card p-4">
          <div class="text-2xl font-black text-secondary mb-1">{{ filteredArticles.length }}</div>
          <div class="text-muted-foreground text-sm">{{ $t('articlesFound') }}</div>
        </div>
      </div>

      <div v-if="loading" class="surface-card text-center py-16">
        <div class="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary"></div>
      </div>

      <div v-else-if="filteredGames.length > 0" class="mb-12">
        <h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
          <Gamepad2 class="w-5 h-5 text-primary" />
          {{ $t('games') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <RouterLink
            v-for="(game, gameIndex) in filteredGames"
            :key="game.id"
            :to="`/games/${game.slug || game.id}`"
            class="group block"
            v-motion-reveal="{ delay: Math.min(gameIndex * 55, 330), y: 16 }"
          >
            <div class="surface-card p-4 hover:-translate-y-1 hover:shadow-lg transition-all duration-300 flex items-center gap-4">
              <img
                :src="getGameImagePrimary(game)"
                :data-fallbacks="getGameImageFallbackData(game)"
                :data-placeholder="getGameImagePlaceholder(game)"
                :alt="game.name"
                class="w-14 h-14 rounded-lg border border-border object-cover"
                @error="handleGameImageError"
              />
              <div class="flex-1">
                <h3 class="text-base font-semibold text-foreground mb-1">{{ game.name }}</h3>
                <p class="text-muted-foreground text-sm">{{ game.categoryName || game.category_name || '-' }}</p>
              </div>
              <ChevronRight class="w-4 h-4 text-muted-foreground" />
            </div>
          </RouterLink>
        </div>
      </div>

      <div v-if="!loading && filteredArticles.length > 0">
        <h2 class="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
          <FileText class="w-5 h-5 text-secondary" />
          {{ $t('news') }}
        </h2>
        <div class="grid grid-cols-1 gap-4">
          <RouterLink
            v-for="(article, articleIndex) in filteredArticles"
            :key="article.id"
            :to="`/articles/${article.id}`"
            class="group block"
            v-motion-reveal="{ delay: Math.min(articleIndex * 45, 280), y: 14 }"
          >
            <div class="surface-card p-5 hover:-translate-y-1 hover:shadow-lg transition-all duration-300">
              <h3 class="text-lg font-semibold text-foreground mb-2 group-hover:text-primary transition-colors">
                {{ article.title }}
              </h3>
              <p class="text-muted-foreground mb-3 line-clamp-2">{{ article.excerpt }}</p>
              <div class="flex items-center gap-3 text-xs text-muted-foreground">
                <span>{{ article.date }}</span>
                <span class="px-2 py-1 bg-muted rounded">
                  {{ article.category }}
                </span>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>

      <div v-if="!loading && filteredGames.length === 0 && filteredArticles.length === 0" class="surface-card text-center py-16">
        <div class="mb-5">
          <Search class="w-16 h-16 text-muted-foreground mx-auto" />
        </div>
        <h3 class="text-xl font-bold text-foreground mb-2">{{ $t('noResultsFound') }}</h3>
        <p class="text-muted-foreground">{{ $t('tryDifferentKeywords') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Gamepad2, FileText, ChevronRight } from 'lucide-vue-next'
import { useLanguageStore } from '../stores/language'
import { getGames } from '../api/games'
import { getArticles } from '../api/articles'
import { useVisualEditor } from '../composables/useVisualEditor'

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('search_results', '搜索结果页')

const route = useRoute()
const languageStore = useLanguageStore()
const { t } = languageStore

const query = ref((route.query.q as string) || '')
const loading = ref(false)
const games = ref<any[]>([])
const articles = ref<any[]>([])

let lastSearchToken = 0

const loadSearchResults = async () => {
  const keyword = query.value.trim()
  if (!keyword) {
    games.value = []
    articles.value = []
    return
  }

  const token = Date.now()
  lastSearchToken = token
  loading.value = true

  try {
    const [gameResults, articleResults] = await Promise.all([
      getGames({ search: keyword }),
      getArticles({ search: keyword }),
    ])

    if (token !== lastSearchToken) return
    games.value = gameResults || []
    articles.value = articleResults || []
  } catch (error) {
    if (token !== lastSearchToken) return
    console.error('加载搜索结果失败:', error)
    games.value = []
    articles.value = []
  } finally {
    if (token === lastSearchToken) {
      loading.value = false
    }
  }
}

const filteredGames = computed(() => games.value)
const filteredArticles = computed(() => articles.value)

const getGameImageCandidates = (game: any): string[] => {
  const unique = new Set<string>()
  const candidates = [game?.icon_image_url, game?.icon_external_url, game?.image, game?.banner_image_url]

  for (const candidate of candidates) {
    const value = String(candidate || '').trim()
    if (value) unique.add(value)
  }

  return Array.from(unique)
}

const buildInlineGamePlaceholder = (label: string, size: number = 80): string => {
  const safeLabel = String(label || 'GAME').slice(0, 10)
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" rx="${Math.round(size * 0.16)}" fill="#f1f5f9"/>
  <rect x="1.5" y="1.5" width="${size - 3}" height="${size - 3}" rx="${Math.round(size * 0.16) - 1}" fill="none" stroke="#dbe5f4"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-size="${Math.round(size * 0.16)}" font-family="Arial, sans-serif">${safeLabel}</text>
</svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

const getGameImagePlaceholder = (game: any): string => {
  return buildInlineGamePlaceholder(String(game?.name || game?.title || 'GAME'), 80)
}

const getGameImagePrimary = (game: any): string => {
  const candidates = getGameImageCandidates(game)
  return candidates[0] || getGameImagePlaceholder(game)
}

const getGameImageFallbackData = (game: any): string => {
  const candidates = getGameImageCandidates(game)
  return JSON.stringify(candidates.slice(1))
}

const handleGameImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  let queue: string[] = []

  try {
    queue = JSON.parse(img.dataset.fallbacks || '[]')
  } catch {
    queue = []
  }

  const next = queue.shift()
  if (next) {
    img.dataset.fallbacks = JSON.stringify(queue)
    img.src = next
    return
  }

  const placeholder = img.dataset.placeholder || buildInlineGamePlaceholder('GAME', 80)
  if (img.src !== placeholder) {
    img.src = placeholder
    return
  }

  img.onerror = null
}

onMounted(() => {
  query.value = (route.query.q as string) || ''
  loadSearchResults()
})

watch(
  () => route.query.q,
  (newQuery) => {
    query.value = (newQuery as string) || ''
    loadSearchResults()
  }
)
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
