﻿<template>
  <div class="relative min-h-screen py-12">
    <div class="absolute inset-0 bg-gradient-to-b from-cyber-dark/30 to-cyber-blue/30"></div>
    <div class="container mx-auto px-4 relative">
      <!-- 页面标题 -->
      <div class="text-center mb-16">
        <h1 class="cyber-title text-5xl md:text-6xl font-black mb-6">
          <span 
            class="text-cyber-neon-green"
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'title')"
          >{{ pageTitleText }}</span> 
          <span
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'subtitle')"
          >{{ pageSubtitleText }}</span>
        </h1>
        <p 
          class="text-xl text-cyber-neon-blue max-w-2xl mx-auto"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >{{ pageDescriptionText }}</p>
      </div>

      <!-- 筛选分类 -->
      <div class="mb-12">
        <!-- 分类按钮 -->
        <div class="flex flex-wrap justify-center gap-4">
          <button
            v-for="category in gameCategories"
            :key="category.id"
            @click="selectedCategory = category.id"
            :class="[
              'px-6 py-3 rounded-xl text-lg font-bold tracking-wide transition-all duration-300 clip-corner',
              selectedCategory === category.id
                ? 'bg-cyber-neon-green text-cyber-black shadow-neon-green'
                : 'bg-cyber-dark border-2 border-cyber-neon-blue/30 text-cyber-neon-blue hover:border-cyber-neon-green hover:text-cyber-neon-green',
            ]"
          >
            <component
              :is="resolveGameCategoryIcon(category)"
              class="mr-2 inline-block h-5 w-5 align-[-0.12em]"
            />
            {{ resolveGameCategoryName(category) }}
            <span v-if="category.gamesCount" class="ml-2 text-sm">({{ category.gamesCount }})</span>
          </button>
        </div>
      </div>

      <!-- 结果统计 -->
      <div class="text-center mb-8">
        <p class="text-xl text-cyber-neon-blue">
          {{ $t('gamesFound') }}：<span class="text-cyber-neon-green text-2xl font-black">{{ resultTotalCount }}</span> {{ $t('gamesUnit') }}
        </p>
      </div>

      <div v-if="loading" class="text-center py-20">
        <div class="inline-block p-8 rounded-2xl bg-cyber-dark/60 border border-cyber-neon-blue/20 mb-6 clip-corner">
          <p class="text-cyber-neon-blue text-lg">{{ t('common.loading') }}</p>
        </div>
      </div>

      <!-- 游戏列表 -->
      <div v-else-if="filteredGames && filteredGames.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
        <GameCard v-for="game in filteredGames" :key="game.id" :game="game" />
      </div>

      <div v-if="!loading && filteredGames.length > 0 && hasMoreGames" class="text-center mt-10">
        <button
          @click="loadMoreGames"
          :disabled="loadingMoreGames"
          class="px-8 py-3 rounded-xl font-bold text-lg tracking-wide bg-cyber-neon-blue/20 border-2 border-cyber-neon-blue text-cyber-neon-blue hover:bg-cyber-neon-blue hover:text-cyber-black transition-all duration-300 clip-corner disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {{ loadingMoreGames ? t('common.loading') : loadMoreText }}
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && (!filteredGames || filteredGames.length === 0)" class="text-center py-20">
        <div class="inline-block p-8 rounded-2xl bg-cyber-dark/60 border border-cyber-neon-pink/20 mb-6 clip-corner">
          <SearchX class="w-16 h-16 text-cyber-neon-pink mx-auto mb-6" />
          <h3 class="text-2xl font-bold text-white mb-4">{{ $t('noGamesFound') }}</h3>
          <p class="text-cyber-neon-blue text-lg mb-6">{{ $t('tryAdjustSearch') }}</p>
          <button
            @click="clearFilters"
            class="px-8 py-4 rounded-xl font-bold text-lg tracking-wide bg-cyber-neon-pink/20 border-2 border-cyber-neon-pink text-cyber-neon-pink hover:bg-cyber-neon-pink hover:text-cyber-black transition-all duration-300 clip-corner"
          >
            {{ $t('clearFilters') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { SearchX } from 'lucide-vue-next'
import GameCard from '../components/GameCard.vue'
import { getGamesPage, getGameCategories } from '../api/games'
import type { RechargeGame, GameCategoryItem } from '../types'
import { useVisualEditor } from '../composables/useVisualEditor'
import { useI18n } from '../composables/useI18n'
import { resolveGameCategoryIcon } from '../utils/iconMap'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('games_page', '游戏列表页')
const PAGE_SIZE = 24

const selectedCategory = ref(route.query.category as string || 'all')
const games = ref<RechargeGame[]>([])
const gameCategories = ref<GameCategoryItem[]>([])
const totalGamesCount = ref(0)
const currentPage = ref(1)
const hasMoreGames = ref(false)
const loading = ref(true)
const loadingMoreGames = ref(false)

const isZhCNLocale = computed(() => String(locale.value || '').toLowerCase().startsWith('zh'))
const pageTitleText = computed(() =>
  isZhCNLocale.value ? getPageConfig('title', t('games')) : t('games')
)
const pageSubtitleText = computed(() => {
  const rawSubtitle = isZhCNLocale.value
    ? getPageConfig('subtitle', t('recharge'))
    : getPageConfig('subtitle', t('gameRecharge').toUpperCase())

  if (!isZhCNLocale.value) return String(rawSubtitle || '')

  // Avoid duplicated heading like "游戏游戏充值" and normalize accidental English "Recharge".
  const normalized = String(rawSubtitle || '')
    .trim()
    .replace(/recharge/gi, '充值')
    .replace(/^(游戏)+/, '')
  return normalized || t('recharge')
})
const pageDescriptionText = computed(() =>
  isZhCNLocale.value ? getPageConfig('description', t('selectGameToRecharge')) : t('selectGameToRecharge')
)
const loadMoreText = computed(() => (isZhCNLocale.value ? '加载更多游戏' : 'Load More Games'))

const GAME_CATEGORY_TRANSLATION_KEYS: Record<string, string> = {
  all: 'allGames',
  allgames: 'allGames',
  allgamescategory: 'allGames',
  international: 'internationalGames',
  internationalgames: 'internationalGames',
  global: 'internationalGames',
  'hongkong-taiwan': 'hongKongTaiwanGames',
  hongkong: 'hongKongTaiwanGames',
  taiwan: 'hongKongTaiwanGames',
  hk: 'hongKongTaiwanGames',
  tw: 'hongKongTaiwanGames',
  'southeast-asia': 'southeastAsiaGames',
  southeastasia: 'southeastAsiaGames',
  southeast: 'southeastAsiaGames',
  sea: 'southeastAsiaGames',
}

const resolveGameCategoryName = (category: Partial<GameCategoryItem>): string => {
  const candidates = [category?.nameKey, category?.code, category?.id]
    .map((item) => String(item || '').trim().toLowerCase())
    .filter(Boolean)

  for (const token of candidates) {
    const compact = token.replace(/[\s_-]+/g, '')
    const key = GAME_CATEGORY_TRANSLATION_KEYS[token] || GAME_CATEGORY_TRANSLATION_KEYS[compact]
    if (key) return t(key)
  }

  return String(category?.name || '')
}

// 加载游戏分类
const loadCategories = async () => {
  try {
    const categories = await getGameCategories()
    gameCategories.value = categories
  } catch (error) {
    console.error('加载游戏分类失败:', error)
    // 使用默认分类
    gameCategories.value = [
      { id: 'all', name: t('allGames'), nameKey: 'allGames', icon: '🎮', code: 'all' },
      { id: 'international', name: t('internationalGames'), nameKey: 'internationalGames', icon: '🌍', code: 'international' },
      { id: 'hongkong-taiwan', name: t('hongKongTaiwanGames'), nameKey: 'hongKongTaiwanGames', icon: '🏮', code: 'hongkong-taiwan' },
      { id: 'southeast-asia', name: t('southeastAsiaGames'), nameKey: 'southeastAsiaGames', icon: '🌴', code: 'southeast-asia' },
    ]
  }
}

// 加载游戏列表
const loadGames = async () => {
  try {
    loading.value = true
    const params: Record<string, any> = {}

    if (selectedCategory.value && selectedCategory.value !== 'all') {
      params.category = selectedCategory.value
    }

    const pageData = await getGamesPage(params, { page: 1, pageSize: PAGE_SIZE })
    games.value = pageData.items
    totalGamesCount.value = pageData.total
    currentPage.value = pageData.page
    hasMoreGames.value = pageData.hasNext
  } catch (error) {
    console.error('加载游戏列表失败:', error)
    games.value = []
    totalGamesCount.value = 0
    currentPage.value = 1
    hasMoreGames.value = false
  } finally {
    loading.value = false
  }
}

const filteredGames = computed(() => games.value)
const resultTotalCount = computed(() => {
  return totalGamesCount.value > 0 ? totalGamesCount.value : filteredGames.value.length
})

const loadMoreGames = async () => {
  if (loading.value || loadingMoreGames.value || !hasMoreGames.value) return

  try {
    loadingMoreGames.value = true
    const params: Record<string, any> = {}

    if (selectedCategory.value && selectedCategory.value !== 'all') {
      params.category = selectedCategory.value
    }

    const nextPage = currentPage.value + 1
    const pageData = await getGamesPage(params, { page: nextPage, pageSize: PAGE_SIZE })

    games.value = [...games.value, ...pageData.items]
    totalGamesCount.value = pageData.total
    currentPage.value = pageData.page
    hasMoreGames.value = pageData.hasNext
  } catch (error) {
    console.error('加载更多游戏失败:', error)
  } finally {
    loadingMoreGames.value = false
  }
}

const clearFilters = () => {
  selectedCategory.value = 'all'
  router.push('/games')
}

// 监听 URL 参数变化
watch(() => route.query.category, (newCategory) => {
  selectedCategory.value = (newCategory as string) || 'all'
  void loadGames()
}, { immediate: true })

// 监听分类变化
watch(selectedCategory, (newValue) => {
  if (newValue === 'all') {
    router.push('/games')
  } else {
    router.push(`/games?category=${newValue}`)
  }
})

// 组件加载时初始化
onMounted(() => {
  loadCategories()
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
