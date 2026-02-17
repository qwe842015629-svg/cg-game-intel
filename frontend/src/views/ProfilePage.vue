<template>
  <div class="min-h-screen relative pt-16 pb-8 bg-gray-50" @touchstart="handleTouchStart" @touchmove="handleTouchMove" @touchend="handleTouchEnd">
    <!-- Pull to Refresh Indicator -->
    <div v-if="pullDistance > 0" class="fixed top-16 left-0 right-0 z-50 flex justify-center transition-opacity duration-300" :style="{ opacity: pullDistance / 80 }">
      <div class="bg-white rounded-full shadow-lg px-4 py-2 flex items-center gap-2">
        <div class="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full" :class="{ 'animate-spin': isRefreshing }" :style="{ transform: `rotate(${pullDistance * 3}deg)` }"></div>
        <span class="text-sm text-gray-700">{{ isRefreshing ? '刷新中...' : pullDistance > 80 ? '释放刷新' : '下拉刷新' }}</span>
      </div>
    </div>
    
    <div class="container mx-auto px-4 max-w-6xl">
      <div class="mb-8 text-center">
        <h1 
          class="text-4xl md:text-5xl font-bold text-gray-800 mb-2"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'title')"
        >
          {{ getPageConfig('title', '个人中心') }}
        </h1>
        <p 
          class="text-gray-500 text-base"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >{{ getPageConfig('description', '管理您的账户信息和订单') }}</p>
      </div>

      <div v-if="authStore.isAuthenticated" class="space-y-6">
        <!-- User Info Card -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:p-8 cursor-pointer transition-all duration-200 active:scale-[0.98]" @click="handleCardClick('user')">
          <div class="flex flex-col md:flex-row items-center gap-6">
            <div class="flex-shrink-0">
              <img
                :src="authStore.user?.avatar || '/api/placeholder/120/120'"
                :alt="authStore.user?.name"
                class="w-20 h-20 md:w-24 md:h-24 rounded-full border-2 border-gray-200"
              />
            </div>
            <div class="text-center md:text-left flex-1">
              <h2 class="text-2xl md:text-3xl font-semibold text-gray-800 mb-1">
                {{ authStore.user?.name || '匿名用户' }}
              </h2>
              <p class="text-gray-600 text-base mb-3">
                {{ authStore.user?.email || '未提供邮箱' }}
              </p>
              <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-md">
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                <span class="text-xs text-green-700 font-medium">在线</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5 text-center hover:shadow-md transition-all duration-200 cursor-pointer active:scale-[0.95]" @click="handleCardClick('orders')">
            <div class="text-4xl md:text-5xl font-semibold text-gray-800 mb-2">0</div>
            <p 
              class="text-gray-600 text-base"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'stat_1_label')"
            >{{ getPageConfig('stat_1_label', '充值订单') }}</p>
          </div>
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5 text-center hover:shadow-md transition-all duration-200 cursor-pointer active:scale-[0.95]" @click="handleCardClick('spent')">
            <div class="text-4xl md:text-5xl font-semibold text-gray-800 mb-2">¥0</div>
            <p 
              class="text-gray-600 text-base"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'stat_2_label')"
            >{{ getPageConfig('stat_2_label', '累计消费') }}</p>
          </div>
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5 text-center hover:shadow-md transition-all duration-200 cursor-pointer active:scale-[0.95]" @click="handleCardClick('points')">
            <div class="text-4xl md:text-5xl font-semibold text-gray-800 mb-2">0</div>
            <p 
              class="text-gray-600 text-base"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'stat_3_label')"
            >{{ getPageConfig('stat_3_label', '积分余额') }}</p>
          </div>
        </div>

        <!-- Recent Orders -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:p-8 cursor-pointer transition-all duration-200 active:scale-[0.98]" @click="handleCardClick('recent-orders')">
          <h3 class="text-xl md:text-2xl font-semibold text-gray-800 mb-4">
            最近订单
          </h3>
          <div class="text-center py-12 text-gray-500">
            <div class="mb-3 inline-block p-4 bg-gray-50 rounded-lg">
              <FileText class="w-12 h-12 mx-auto text-gray-400" />
            </div>
            <p class="text-base">暂无订单记录</p>
          </div>
        </div>
      </div>

      <!-- Not Logged In -->
      <div v-else class="text-center py-16 bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="mb-6 inline-block p-5 bg-gray-50 rounded-full">
          <User class="w-14 h-14 text-gray-400 mx-auto" />
        </div>
        <h2 class="text-xl md:text-2xl font-semibold text-gray-800 mb-3">未登录</h2>
        <p class="text-gray-600 mb-6 max-w-md mx-auto text-sm">请先登录以访问个人中心</p>
        <button 
          @click="showAuthDialog = true"
          class="px-6 py-2.5 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition-colors"
        >
          登录 / 注册
        </button>
      </div>
    </div>

    <AuthDialog v-model="showAuthDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, FileText } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import AuthDialog from '../components/AuthDialog.vue'
import { useVisualEditor } from '../composables/useVisualEditor'

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('profile_page', '个人中心页')

const authStore = useAuthStore()
const showAuthDialog = ref(false)

// Pull to refresh
const pullDistance = ref(0)
const isRefreshing = ref(false)
const startY = ref(0)
let canPull = false

const handleTouchStart = (e: TouchEvent) => {
  // Only allow pull to refresh when scrolled to top
  if (window.scrollY === 0) {
    startY.value = e.touches[0].clientY
    canPull = true
  }
}

const handleTouchMove = (e: TouchEvent) => {
  if (!canPull || isRefreshing.value) return
  
  const currentY = e.touches[0].clientY
  const distance = currentY - startY.value
  
  if (distance > 0 && window.scrollY === 0) {
    pullDistance.value = Math.min(distance, 120)
    // Prevent default scroll behavior when pulling down
    if (distance > 10) {
      e.preventDefault()
    }
  }
}

const handleTouchEnd = async () => {
  if (!canPull) return
  
  canPull = false
  
  if (pullDistance.value > 80 && !isRefreshing.value) {
    isRefreshing.value = true
    
    // Simulate refresh - you can replace this with actual data fetching
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Refresh user data
    if (authStore.isAuthenticated) {
      console.log('Refreshing user data...')
      // TODO: Add actual data refresh logic here
    }
    
    isRefreshing.value = false
  }
  
  pullDistance.value = 0
}

// Card click handlers
const handleCardClick = (type: string) => {
  console.log('Card clicked:', type)
  // TODO: Add navigation or action based on card type
  switch(type) {
    case 'user':
      // Navigate to user profile edit
      break
    case 'orders':
      // Navigate to orders list
      break
    case 'spent':
      // Navigate to transaction history
      break
    case 'points':
      // Navigate to points details
      break
    case 'recent-orders':
      // Navigate to full orders list
      break
  }
}
</script>
