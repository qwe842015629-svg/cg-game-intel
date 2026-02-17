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
          >{{ getPageConfig('title', '游戏') }}</span> 
          <span
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'subtitle')"
          >{{ getPageConfig('subtitle', $t('gameRecharge').toUpperCase()) }}</span>
        </h1>
        <p 
          class="text-xl text-cyber-neon-blue max-w-2xl mx-auto"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >{{ getPageConfig('description', $t('selectGameToRecharge')) }}</p>
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
            <span class="mr-2">{{ category.icon }}</span>
            {{ category.name }}
            <span v-if="category.gamesCount" class="ml-2 text-sm">({{ category.gamesCount }})</span>
          </button>
        </div>
      </div>

      <!-- 结果统计 -->
      <div class="text-center mb-8">
        <p class="text-xl text-cyber-neon-blue">
          {{ $t('gamesFound') }}：<span class="text-cyber-neon-green text-2xl font-black">{{ filteredGames.length }}</span> {{ $t('gamesUnit') }}
        </p>
      </div>

      <!-- 游戏列表 -->
      <div v-if="filteredGames && filteredGames.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 md:gap-6">
        <GameCard v-for="game in filteredGames" :key="game.id" :game="game" />
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center py-20">
        <div class="inline-block p-8 rounded-2xl bg-cyber-dark/60 border border-cyber-neon-pink/20 mb-6 clip-corner">
          <svg class="w-16 h-16 text-cyber-neon-pink mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
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
import GameCard from '../components/GameCard.vue'
import { getGames, getGameCategories } from '../api/games'
import type { RechargeGame, GameCategoryItem } from '../types'
import { useVisualEditor } from '../composables/useVisualEditor'

const route = useRoute()
const router = useRouter()

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('games_page', '游戏列表页')

const selectedCategory = ref(route.query.category as string || 'all')
const games = ref<RechargeGame[]>([])
const gameCategories = ref<GameCategoryItem[]>([])
const loading = ref(true)

// 加载游戏分类
const loadCategories = async () => {
  try {
    const categories = await getGameCategories()
    gameCategories.value = categories
  } catch (error) {
    console.error('加载游戏分类失败:', error)
    // 使用默认分类
    gameCategories.value = [
      { id: 'all', name: '全部游戏', nameKey: 'allGames', icon: '🎮', code: 'all' },
      { id: 'international', name: '国际游戏', nameKey: 'internationalGames', icon: '🌍', code: 'international' },
      { id: 'hongkong-taiwan', name: '港台游戏', nameKey: 'hongKongTaiwanGames', icon: '🏮', code: 'hongkong-taiwan' },
      { id: 'southeast-asia', name: '东南亚游戏', nameKey: 'southeastAsiaGames', icon: '🌴', code: 'southeast-asia' },
    ]
  }
}

// 加载游戏列表
const loadGames = async () => {
  try {
    loading.value = true
    const params: any = {}
    
    // 如果 selectedCategory 是 'all'，则不传 category 参数给 API
    // 只有当 selectedCategory 有值且不为 'all' 时才传
    if (selectedCategory.value && selectedCategory.value !== 'all') {
      params.category = selectedCategory.value
    }
    
    console.log('Loading games with params:', params)
    const data = await getGames(params)
    console.log('Loaded games:', data)
    games.value = data
  } catch (error) {
    console.error('加载游戏列表失败:', error)
    games.value = []
  } finally {
    loading.value = false
  }
}

const filteredGames = computed(() => games.value)

const clearFilters = () => {
  selectedCategory.value = 'all'
  router.push('/games')
}

// 监听 URL 参数变化
watch(() => route.query.category, (newCategory) => {
  selectedCategory.value = (newCategory as string) || 'all'
  loadGames()
})

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
  loadGames()
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
