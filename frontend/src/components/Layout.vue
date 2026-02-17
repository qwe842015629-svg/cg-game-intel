﻿<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="relative sticky top-0 z-50 bg-card/95 backdrop-blur-md border-b border-border/80">
      <div class="container mx-auto px-4">
        <!-- Top Bar -->
        <div class="flex items-center justify-between h-16 py-2">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center gap-3">
            <div class="logo-badge">CG</div>
            <div class="leading-tight">
              <span class="block text-base md:text-lg font-semibold tracking-wide text-foreground">Cypher Game Buy</span>
              <span class="hidden md:block text-[11px] text-muted-foreground">Premium Recharge Service</span>
            </div>
          </RouterLink>

          <!-- Search Bar -->
          <div class="hidden md:flex flex-1 max-w-xl mx-8">
            <div class="relative w-full">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                :placeholder="$t('search')"
                class="pl-10"
              />
            </div>
          </div>

          <!-- Right Actions -->
          <div class="flex items-center gap-2 text-foreground">
            <!-- Language Switcher -->
            <div class="relative">
              <Button 
                variant="ghost" 
                size="icon"
                @click="showLangMenu = !showLangMenu"
              >
                <Globe class="w-5 h-5" />
              </Button>
              
              <!-- Language Dropdown -->
              <div
                v-if="showLangMenu"
                class="menu-float-panel absolute right-0 mt-2 w-48 bg-card border border-border rounded-lg shadow-lg py-2 z-50 max-h-96 overflow-y-auto"
              >
                <button
                  v-for="(locale, localeIndex) in languageStore.availableLocales"
                  :key="locale.code"
                  @click="changeLanguage(locale.code)"
                  :class="[
                    'menu-stagger-item w-full px-4 py-2 text-left text-sm transition-colors',
                    languageStore.currentLocale === locale.code
                      ? 'bg-accent font-bold'
                      : 'hover:bg-accent'
                  ]"
                  :style="{ '--stagger-index': String(localeIndex) }"
                >
                  {{ locale.name }}
                </button>
              </div>
            </div>
            
            <!-- Theme Preset & Cursor Panel -->
            <div ref="themePanelRef" class="relative theme-panel-wrap">
              <Button variant="ghost" size="icon" @click="showThemePanel = !showThemePanel">
                <Palette class="w-5 h-5" />
              </Button>

              <div
                v-if="showThemePanel"
                class="menu-float-panel absolute right-0 mt-2 w-80 rounded-xl border border-border bg-card shadow-xl z-50 p-3"
              >
                <div class="text-xs font-semibold text-muted-foreground mb-2">配色方案</div>
                <div class="grid grid-cols-2 gap-2 mb-4">
                  <button
                    v-for="(themePreset, themeIndex) in themeStore.presetOptions"
                    :key="themePreset.id"
                    type="button"
                    class="theme-preset-btn menu-stagger-item"
                    :class="{ active: themeStore.preset === themePreset.id }"
                    :style="{ '--stagger-index': String(themeIndex) }"
                    @click="applyThemePreset(themePreset.id)"
                  >
                    <div class="theme-preset-title">{{ themePreset.name }}</div>
                    <div class="theme-preset-desc">{{ themePreset.description }}</div>
                  </button>
                </div>

                <div class="text-xs font-semibold text-muted-foreground mb-2">鼠标模式</div>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="(mode, cursorIndex) in cursorModes"
                    :key="mode.id"
                    type="button"
                    class="theme-cursor-btn menu-stagger-item"
                    :class="{ active: themeStore.cursorMode === mode.id }"
                    :style="{ '--stagger-index': String(cursorIndex) }"
                    @click="themeStore.setCursorMode(mode.id)"
                  >
                    <MousePointer2 class="w-3.5 h-3.5" />
                    <span>{{ mode.label }}</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Theme Toggle -->
            <Button variant="ghost" size="icon" @click="themeStore.toggleTheme()">
              <Sun v-if="themeStore.theme === 'dark'" class="w-5 h-5" />
              <Moon v-else class="w-5 h-5" />
            </Button>

            <!-- Customer Service -->
            <RouterLink to="/customer-service">
              <Button variant="ghost" size="icon">
                <MessageCircle class="w-5 h-5" />
              </Button>
            </RouterLink>

            <!-- User Menu -->
            <Button
              v-if="!authStore.isAuthenticated"
              variant="ghost"
              size="icon"
              @click="showAuthDialog = true"
            >
              <User class="w-5 h-5" />
            </Button>
            
            <div v-else class="relative">
              <Button
                variant="ghost"
                size="icon"
                @click="showUserMenu = !showUserMenu"
              >
                <User class="w-5 h-5" />
              </Button>
              
              <!-- User Dropdown -->
              <div
                v-if="showUserMenu"
                class="menu-float-panel absolute right-0 mt-2 w-48 bg-card border border-border rounded-lg shadow-lg py-2"
              >
                <div class="px-4 py-2 border-b border-border">
                  <p class="font-medium">{{ authStore.user?.name }}</p>
                  <p class="text-sm text-muted-foreground">{{ authStore.user?.email }}</p>
                </div>
                <RouterLink
                  to="/profile"
                  class="menu-stagger-item block px-4 py-2 hover:bg-accent"
                  style="--stagger-index: 0"
                  @click="showUserMenu = false"
                >
                  {{ $t('userProfile') }}
                </RouterLink>
                <button
                  class="menu-stagger-item block w-full text-left px-4 py-2 hover:bg-accent"
                  style="--stagger-index: 1"
                  @click="handleLogout"
                >
                  {{ $t('logout') }}
                </button>
              </div>
            </div>

            <Button variant="ghost" size="icon" class="md:hidden">
              <Menu class="w-5 h-5" />
            </Button>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex gap-8 pb-3 items-center">
          <RouterLink
            to="/"
            :class="[
              'text-base transition-colors flex items-center h-10',
              route.path === '/' 
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ $t('home') }}
          </RouterLink>
          
          <!-- 游戏下拉菜单 -->
          <div class="relative game-menu flex items-center h-10"
               @mouseenter="showGamesMenu = true"
               @mouseleave="showGamesMenu = false">
            <button
              :class="[
                'text-base transition-colors cursor-pointer flex items-center h-full',
                route.path.startsWith('/games') || route.path.startsWith('/recharge')
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground hover:text-foreground',
              ]"
              @click="showGamesMenu = !showGamesMenu"
            >
              {{ $t('games') }}
            </button>
            
            <!-- 下拉菜单 -->
             <Transition name="dropdown">
               <div v-if="showGamesMenu"
                    class="dropdown-content site-dropdown-panel absolute top-full left-0 mt-2 w-48 rounded-lg shadow-lg py-2 z-50">
                <!-- 加载中状态 -->
                <div v-if="gameCategoriesLoading" class="px-4 py-2 text-sm text-gray-400">
                  加载中...
                </div>
                <!-- 动态渲染游戏分类 -->
                <RouterLink
                  v-for="(category, gameCategoryIndex) in gameCategories"
                  :key="category.id"
                  :to="`/games?category=${category.code || 'all'}`"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors"
                  :style="{ '--stagger-index': String(gameCategoryIndex) }"
                  @click="showGamesMenu = false"
                >
                  {{ category.icon }} {{ category.name }}
                  <span v-if="category.gamesCount && category.gamesCount > 0" class="text-xs text-gray-500 ml-1">
                    ({{ category.gamesCount }})
                  </span>
                </RouterLink>
                <!-- 无分类时的提示 -->
                <div v-if="!gameCategoriesLoading && gameCategories.length === 0" 
                     class="px-4 py-2 text-sm text-gray-400">
                  暂无分类
                </div>
              </div>
            </Transition>
          </div>
          
          <!-- 资讯下拉菜单 -->
          <div class="relative news-menu flex items-center h-10"
               @mouseenter="showNewsMenu = true"
               @mouseleave="showNewsMenu = false">
            <button
              :class="[
                'text-base transition-colors cursor-pointer flex items-center h-full',
                route.path.startsWith('/articles')
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground hover:text-foreground',
              ]"
              @click="showNewsMenu = !showNewsMenu"
            >
              {{ $t('news') }}
            </button>
            
            <!-- 下拉菜单 -->
             <Transition name="dropdown">
               <div v-if="showNewsMenu"
                    class="dropdown-content site-dropdown-panel absolute top-full left-0 mt-2 w-48 rounded-lg shadow-lg py-2 z-50">
                <!-- 全部资讯选项 -->
                <RouterLink
                  to="/articles"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors font-medium border-b border-gray-700"
                  style="--stagger-index: 0"
                  @click="showNewsMenu = false"
                >
                  📰 全部资讯
                </RouterLink>
                
                <!-- 加载中状态 -->
                <div v-if="categoriesLoading" class="px-4 py-2 text-sm text-gray-400">
                  加载中...
                </div>
                <!-- 动态渲染文章分类 -->
                <RouterLink
                  v-for="(category, articleCategoryIndex) in articleCategories"
                  :key="category.id"
                  :to="`/articles?category=${encodeURIComponent(category.name)}`"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors"
                  :style="{ '--stagger-index': String(articleCategoryIndex + 1) }"
                  @click="showNewsMenu = false"
                >
                  {{ category.name }}
                  <span v-if="category.articles_count > 0" class="text-xs text-gray-500 ml-1">
                    ({{ category.articles_count }})
                  </span>
                </RouterLink>
                <!-- 无分类时的提示 -->
                <div v-if="!categoriesLoading && articleCategories.length === 0" 
                     class="px-4 py-2 text-sm text-gray-400">
                  暂无分类
                </div>
              </div>
            </Transition>
          </div>
          
          <RouterLink
            to="/cg-wiki"
            :class="[
              'text-base transition-colors flex items-center h-10',
              route.path === '/cg-wiki'
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            <span class="flex items-center gap-1">
              <span class="text-[10px] bg-primary text-primary-foreground px-1.5 py-0.5 rounded font-bold leading-none">新</span>
              攻略百科
            </span>
          </RouterLink>

          <RouterLink
            to="/customer-service"
            :class="[
              'text-base transition-colors flex items-center h-10',
              route.path === '/customer-service'
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ $t('support') }}
          </RouterLink>
        </nav>
      </div>
      <div class="route-progress" :class="{ active: pageProgressActive }" aria-hidden="true">
        <span class="route-progress-bar"></span>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <RouterView v-slot="{ Component, route: currentRoute }">
        <Transition :name="pageTransitionName" mode="out-in" appear>
          <component :is="Component" :key="currentRoute.fullPath" />
        </Transition>
      </RouterView>
    </main>

    <!-- Footer -->
    <footer class="bg-card border-t border-border mt-20">
      <div class="container mx-auto px-4 py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- 动态渲染底部板块 -->
          <div v-for="(section, idx) in effectiveFooterSections" :key="section.id">
            <h3 
              class="font-bold mb-4"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, `section_${idx}_title`)"
            >
              {{ section.title }}
            </h3>
            <!-- 如果有描述则显示描述（关于我们） -->
            <p 
              v-if="section.description" 
              class="text-muted-foreground text-sm"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, `section_${idx}_description`)"
            >
              {{ section.description }}
            </p>
            <!-- 如果有链接则显示链接列表 -->
            <ul v-if="section.links && section.links.length > 0" class="space-y-2 text-sm">
              <li v-for="(link, lidx) in section.links" :key="link.id">
                <RouterLink 
                  v-if="!link.is_external"
                  :to="link.url" 
                  class="text-muted-foreground hover:text-foreground"
                >
                  <span
                    :contenteditable="isEditMode"
                    @blur="handleInlineEdit($event, `link_${idx}_${lidx}_title`)"
                  >{{ link.title }}</span>
                </RouterLink>
                <a 
                  v-else
                  :href="link.url" 
                  target="_blank"
                  class="text-muted-foreground hover:text-foreground"
                >
                  <span
                    :contenteditable="isEditMode"
                    @blur="handleInlineEdit($event, `link_${idx}_${lidx}_title`)"
                  >{{ link.title }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div v-if="footerConfig.show_copyright" class="border-t border-border mt-8 pt-8 text-center text-muted-foreground text-sm">
          <p>{{ footerConfig.copyright_text }}</p>
        </div>
      </div>
    </footer>

    <!-- Auth Dialog -->
    <AuthDialog v-model="showAuthDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, Sun, Moon, MessageCircle, User, Menu, Globe, Palette, MousePointer2 } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { useLanguageStore } from '../stores/language'
import { getArticleCategories, type ArticleCategory } from '../api/articles'
import { getGameCategories } from '../api/games'
import { getFooterSections, getFooterConfig } from '../api/footer'
import type { FooterSection, FooterConfig } from '../api/footer'
import type { GameCategoryItem } from '../types'
import Button from './ui/Button.vue'
import Input from './ui/Input.vue'
import AuthDialog from './AuthDialog.vue'
import { useVisualEditor } from '../composables/useVisualEditor'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const languageStore = useLanguageStore()
// 不要解构，直接使用 languageStore 保持响应性
const route = useRoute()
const router = useRouter()

// 可视化装修：页脚板块
const { isEditMode, pageConfig, handleInlineEdit } = useVisualEditor('footer', '站点底部')

const searchQuery = ref('')
const showAuthDialog = ref(false)
const showUserMenu = ref(false)
const showLangMenu = ref(false)
const showGamesMenu = ref(false)
const showNewsMenu = ref(false)
const showThemePanel = ref(false)
const themePanelRef = ref<HTMLElement | null>(null)
const pageProgressActive = ref(false)
let pageProgressTimer: ReturnType<typeof setTimeout> | null = null

const cursorModes = [
  { id: 'soft', label: '柔和' },
  { id: 'system', label: '系统' },
  { id: 'crosshair', label: '十字' },
  { id: 'neon', label: '霓虹' },
] as const

// 文章分类数据
const articleCategories = ref<ArticleCategory[]>([])
const categoriesLoading = ref(true)

// 游戏分类数据
const gameCategories = ref<GameCategoryItem[]>([])
const gameCategoriesLoading = ref(true)

// 页面底部数据
const footerSections = ref<FooterSection[]>([])
const footerConfig = ref<Partial<FooterConfig>>({ 
  copyright_text: '© 2026 CYPHER GAME BUY. 版权所有', 
  show_copyright: true 
})
const footerLoading = ref(true)

const navLinks = [
  { path: '/', labelKey: 'home' },
  { path: '/games', labelKey: 'games' },
  { path: '/articles', labelKey: 'news' },
  { path: '/customer-service', labelKey: 'support' },
]

const pageTransitionName = ref('route-fade')
const previousRoutePath = ref(route.path)

watch(
  () => route.fullPath,
  () => {
    if (pageProgressTimer) {
      clearTimeout(pageProgressTimer)
    }
    pageProgressActive.value = true
    pageProgressTimer = setTimeout(() => {
      pageProgressActive.value = false
      pageProgressTimer = null
    }, 520)

    const currentPath = route.path
    const prevPath = previousRoutePath.value

    if (currentPath === prevPath) {
      pageTransitionName.value = 'route-fade'
      return
    }

    const currentDepth = currentPath.split('/').filter(Boolean).length
    const prevDepth = prevPath.split('/').filter(Boolean).length

    if (currentDepth > prevDepth) {
      pageTransitionName.value = 'route-slide-left'
    } else if (currentDepth < prevDepth) {
      pageTransitionName.value = 'route-slide-right'
    } else {
      pageTransitionName.value = 'route-fade'
    }

    previousRoutePath.value = currentPath
  }
)

// 加载文章分类
const loadArticleCategories = async () => {
  try {
    categoriesLoading.value = true
    const categories = await getArticleCategories()
    articleCategories.value = categories
    console.log('成功加载文章分类:', categories.length, '个')
  } catch (error) {
    console.error('加载文章分类失败:', error)
    // 失败时使用默认分类
    articleCategories.value = [
      { id: 1, name: '游戏资讯', description: '', sort_order: 1, is_active: true, articles_count: 0, created_at: '', updated_at: '' },
      { id: 2, name: '攻略教程', description: '', sort_order: 2, is_active: true, articles_count: 0, created_at: '', updated_at: '' },
      { id: 3, name: '充值指南', description: '', sort_order: 3, is_active: true, articles_count: 0, created_at: '', updated_at: '' },
      { id: 4, name: '活动公告', description: '', sort_order: 4, is_active: true, articles_count: 0, created_at: '', updated_at: '' },
    ]
  } finally {
    categoriesLoading.value = false
  }
}

// 加载游戏分类
const loadGameCategories = async () => {
  try {
    gameCategoriesLoading.value = true
    const categories = await getGameCategories()
    gameCategories.value = categories
    console.log('成功加载游戏分类:', categories.length, '个')
  } catch (error) {
    console.error('加载游戏分类失败:', error)
    // 失败时使用默认分类
    gameCategories.value = [
      { id: 'all', name: '全部游戏', nameKey: 'allGames', icon: '🎮', code: 'all' },
      { id: 'international', name: '国际游戏', nameKey: 'internationalGames', icon: '🌍', code: 'international' },
      { id: 'hongkong-taiwan', name: '港台游戏', nameKey: 'hongKongTaiwanGames', icon: '🏮', code: 'hongkong-taiwan' },
      { id: 'southeast-asia', name: '东南亚游戏', nameKey: 'southeastAsiaGames', icon: '🌴', code: 'southeast-asia' },
    ]
  } finally {
    gameCategoriesLoading.value = false
  }
}

// 加载底部数据
const loadFooterData = async () => {
  try {
    footerLoading.value = true
    const [sections, config] = await Promise.all([
      getFooterSections(),
      getFooterConfig()
    ])
    footerSections.value = sections
    footerConfig.value = config
    console.log('成功加载底部数据:', sections.length, '个板块')
  } catch (error) {
    console.error('加载底部数据失败:', error)
  } finally {
    footerLoading.value = false
  }
}

// 合并配置后的 Footer（支持可视化修改）
const effectiveFooterSections = computed<FooterSection[]>(() => {
  return footerSections.value.map((sec, idx) => {
    const overrideTitle = pageConfig.value?.[`section_${idx}_title`]
    const overrideDesc = pageConfig.value?.[`section_${idx}_description`]
    return {
      ...sec,
      title: overrideTitle ?? sec.title,
      description: overrideDesc ?? sec.description,
      links: (sec.links || []).map((lnk: any, lidx: number) => {
        const overrideLinkTitle = pageConfig.value?.[`link_${idx}_${lidx}_title`]
        return {
          ...lnk,
          title: overrideLinkTitle ?? lnk.title
        }
      })
    }
  })
})

const handleLogout = () => {
  authStore.logout()
  showUserMenu.value = false
  // 使用 as any 来避免类型错误
  alert((languageStore as any).t('logoutSuccess'))
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/search',
      query: { q: searchQuery.value }
    })
  }
}

const changeLanguage = (locale: string) => {
  languageStore.setLocale(locale as any)
  showLangMenu.value = false
}

const applyThemePreset = (presetId: string) => {
  themeStore.setPreset(presetId)
}

const handleDocumentClick = (event: MouseEvent) => {
  const target = event.target as Node
  if (themePanelRef.value && !themePanelRef.value.contains(target)) {
    showThemePanel.value = false
  }
}

// 组件加载时获取分类数据
onMounted(() => {
  loadArticleCategories()
  loadGameCategories()
  loadFooterData()
  document.addEventListener('click', handleDocumentClick)
  pageProgressActive.value = true
  pageProgressTimer = setTimeout(() => {
    pageProgressActive.value = false
    pageProgressTimer = null
  }, 420)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  if (pageProgressTimer) {
    clearTimeout(pageProgressTimer)
    pageProgressTimer = null
  }
})
</script>

<style scoped>
.logo-badge {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid hsl(var(--border));
  background: hsl(var(--card));
  color: hsl(var(--foreground));
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.menu-float-panel {
  transform-origin: top right;
  animation: menu-float-in 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

.menu-stagger-item {
  opacity: 0;
  transform: translateY(7px) scale(0.995);
  animation: menu-stagger-in 260ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: calc(var(--stagger-index, 0) * 34ms + 24ms);
}

.route-progress {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  overflow: hidden;
  pointer-events: none;
  opacity: 0;
  transition: opacity 180ms ease;
}

.route-progress.active {
  opacity: 1;
}

.route-progress-bar {
  display: block;
  width: 26%;
  height: 100%;
  background: linear-gradient(90deg, transparent 0%, hsl(var(--primary)) 40%, hsl(var(--accent)) 100%);
  transform: translateX(-130%);
}

.route-progress.active .route-progress-bar {
  animation: route-progress-run 520ms cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes route-progress-run {
  to {
    transform: translateX(360%);
  }
}

@keyframes menu-float-in {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes menu-stagger-in {
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dropdown-content {
  pointer-events: auto;
}

.site-dropdown-panel {
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  box-shadow: 0 16px 34px -24px rgba(15, 23, 42, 0.32);
}

.dropdown-item {
  color: hsl(var(--muted-foreground));
}

.dropdown-item:hover {
  background-color: hsl(var(--accent) / 0.15);
  color: hsl(var(--foreground));
}

.theme-preset-btn {
  border: 1px solid hsl(var(--border));
  background: color-mix(in srgb, hsl(var(--card)) 86%, transparent);
  border-radius: 10px;
  padding: 10px;
  text-align: left;
}

.theme-preset-btn:hover {
  border-color: color-mix(in srgb, var(--primary-color) 60%, hsl(var(--border)));
  transform: translateY(-1px);
}

.theme-preset-btn.active {
  border-color: color-mix(in srgb, var(--primary-color) 80%, hsl(var(--border)));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--primary-color) 26%, transparent);
}

.theme-preset-title {
  font-size: 12px;
  font-weight: 700;
  color: hsl(var(--foreground));
}

.theme-preset-desc {
  margin-top: 2px;
  font-size: 11px;
  color: hsl(var(--muted-foreground));
  line-height: 1.35;
}

.theme-cursor-btn {
  border: 1px solid hsl(var(--border));
  background: color-mix(in srgb, hsl(var(--card)) 88%, transparent);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  display: inline-flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  color: hsl(var(--muted-foreground));
}

.theme-cursor-btn:hover {
  border-color: color-mix(in srgb, var(--secondary-color) 58%, hsl(var(--border)));
  color: hsl(var(--foreground));
}

.theme-cursor-btn.active {
  color: hsl(var(--foreground));
  border-color: color-mix(in srgb, var(--secondary-color) 75%, hsl(var(--border)));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--secondary-color) 24%, transparent);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 220ms cubic-bezier(0.16, 1, 0.3, 1), transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.985);
}

.dropdown-enter-to,
.dropdown-leave-from {
  opacity: 1;
  transform: translateY(0);
}

@media (prefers-reduced-motion: reduce) {
  .menu-stagger-item {
    opacity: 1;
    transform: none;
    animation: none;
  }
}
</style>
