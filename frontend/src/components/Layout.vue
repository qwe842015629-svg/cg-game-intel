﻿﻿﻿﻿﻿<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="relative sticky top-0 z-50 galaxy-header">
      <div class="container mx-auto px-4 relative">
        <!-- Top Bar -->
        <div class="flex items-center justify-between h-16 py-2">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center gap-2 sm:gap-3">
            <div class="logo-badge">CG</div>
            <div class="leading-tight">
              <span
                class="block text-sm sm:text-base md:text-lg font-semibold tracking-wide text-foreground"
                >Cypher Game Buy</span
              >
              <span class="hidden md:block text-[11px] text-muted-foreground">{{
                $t("layout.brandTagline")
              }}</span>
            </div>
          </RouterLink>
          <!-- Search Bar -->
          <div class="hidden md:flex flex-1 max-w-xl mx-8">
            <div class="relative w-full">
              <Search
                class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground"
              />
              <Input
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                :placeholder="$t('search')"
                class="pl-10"
              />
            </div>
          </div>
          <!-- Right Actions -->
          <div class="flex items-center gap-1 sm:gap-2 text-foreground">
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
                  v-for="(
                    locale, localeIndex
                  ) in languageStore.availableLocales"
                  :key="locale.code"
                  @click="changeLanguage(locale.code)"
                  :class="[
                    'menu-stagger-item w-full px-4 py-2 text-left text-sm transition-colors',
                    languageStore.currentLocale === locale.code
                      ? 'bg-accent font-bold'
                      : 'hover:bg-accent',
                  ]"
                  :style="{ '--stagger-index': String(localeIndex) }"
                >
                  {{ locale.name }}
                </button>
              </div>
            </div>
            <!-- Theme Preset & Cursor Panel -->
            <div ref="themePanelRef" class="relative theme-panel-wrap">
              <Button
                variant="ghost"
                size="icon"
                @click="showThemePanel = !showThemePanel"
              >
                <Palette class="w-5 h-5" />
              </Button>
              <div
                v-if="showThemePanel"
                class="menu-float-panel absolute right-0 mt-2 w-80 rounded-xl border border-border bg-card shadow-xl z-50 p-3"
              >
                <div class="text-xs font-semibold text-muted-foreground mb-2">
                  {{ $t("layout.themeScheme") }}
                </div>
                <div class="grid grid-cols-2 gap-2 mb-4">
                  <button
                    v-for="(
                      themePreset, themeIndex
                    ) in themeStore.presetOptions"
                    :key="themePreset.id"
                    type="button"
                    class="theme-preset-btn menu-stagger-item"
                    :class="{ active: themeStore.preset === themePreset.id }"
                    :style="{ '--stagger-index': String(themeIndex) }"
                    @click="applyThemePreset(themePreset.id)"
                  >
                    <div class="theme-preset-title">{{ themePreset.name }}</div>
                    <div class="theme-preset-desc">
                      {{ themePreset.description }}
                    </div>
                  </button>
                </div>
                <div class="text-xs font-semibold text-muted-foreground mb-2">
                  {{ $t("layout.cursorMode") }}
                </div>
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
                    <span>{{ $t(mode.labelKey) }}</span>
                  </button>
                </div>
              </div>
            </div>
            <!-- Customer Service -->
            <RouterLink to="/customer-service" class="hidden sm:inline-flex">
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
                  <p class="text-sm text-muted-foreground">
                    {{ authStore.user?.email }}
                  </p>
                </div>
                <RouterLink
                  :to="authStore.user?.id ? `/user/${authStore.user.id}` : '/profile'"
                  class="menu-stagger-item block px-4 py-2 hover:bg-accent"
                  style="--stagger-index: 0"
                  @click="showUserMenu = false"
                >
                  {{ $t("layout.profileCenter") }}
                </RouterLink>
                <button
                  class="menu-stagger-item block w-full text-left px-4 py-2 hover:bg-accent"
                  style="--stagger-index: 1"
                  @click="handleLogout"
                >
                  {{ $t("logout") }}
                </button>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              class="md:hidden"
              :aria-expanded="showMobileMenu ? 'true' : 'false'"
              :aria-label="$t('layout.toggleMobileMenu')"
              @click="toggleMobileMenu"
            >
              <component :is="showMobileMenu ? X : Menu" class="w-5 h-5" />
            </Button>
          </div>
        </div>
        <!-- Navigation -->
        <nav class="top-nav hidden md:flex gap-8 pb-3 items-center whitespace-nowrap">
          <RouterLink
            to="/"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ $t("home") }}
          </RouterLink>
          <!-- 娓告垙涓嬫媺鑿滃崟 -->
          <div
            class="relative game-menu top-nav-dropdown flex items-center h-10"
            @mouseenter="showGamesMenu = true"
            @mouseleave="showGamesMenu = false"
          >
            <button
              :class="[
                'text-base transition-colors cursor-pointer flex items-center h-full',
                routePathStartsWith('/games') ||
                routePathStartsWith('/recharge')
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground hover:text-foreground',
              ]"
              @click="showGamesMenu = !showGamesMenu"
            >
              {{ $t("games") }}
            </button>
            <!-- 涓嬫媺鑿滃崟 -->
            <Transition name="dropdown">
              <div
                v-if="showGamesMenu"
                class="dropdown-content site-dropdown-panel absolute top-full left-0 mt-2 w-48 rounded-lg shadow-lg py-2 z-50"
              >
                <!-- 鍔犺浇涓姸锟?-->
                <div
                  v-if="gameCategoriesLoading"
                  class="px-4 py-2 text-sm text-gray-400"
                >
                  {{ $t("common.loading") }}
                </div>
                <!-- 鍔ㄦ€佹覆鏌撴父鎴忓垎锟?-->
                <RouterLink
                  v-for="(category, gameCategoryIndex) in gameCategories"
                  :key="category.id"
                  :to="`/games?category=${category.code || 'all'}`"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors"
                  :style="{ '--stagger-index': String(gameCategoryIndex) }"
                  @click="showGamesMenu = false"
                >
                  <span class="inline-flex items-center gap-2">
                    <component
                      :is="resolveGameCategoryIcon(category)"
                      class="h-4 w-4 text-slate-600"
                    />
                    <span>{{ resolveGameCategoryName(category) }}</span>
                  </span>
                  <span
                    v-if="category.gamesCount && category.gamesCount > 0"
                    class="text-xs text-gray-500 ml-1"
                  >
                    ({{ category.gamesCount }})
                  </span>
                </RouterLink>
                <!-- 鏃犲垎绫绘椂鐨勬彁锟?-->
                <div
                  v-if="!gameCategoriesLoading && gameCategories.length === 0"
                  class="px-4 py-2 text-sm text-gray-400"
                >
                  {{ $t("layout.noCategory") }}
                </div>
              </div>
            </Transition>
          </div>
          <!-- 璧勮涓嬫媺鑿滃崟 -->
          <div
            class="relative news-menu top-nav-dropdown flex items-center h-10"
            @mouseenter="showNewsMenu = true"
            @mouseleave="showNewsMenu = false"
          >
            <button
              :class="[
                'text-base transition-colors cursor-pointer flex items-center h-full',
                routePathStartsWith('/articles')
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground hover:text-foreground',
              ]"
              @click="showNewsMenu = !showNewsMenu"
            >
              {{ $t("news") }}
            </button>
            <!-- 涓嬫媺鑿滃崟 -->
            <Transition name="dropdown">
              <div
                v-if="showNewsMenu"
                class="dropdown-content site-dropdown-panel absolute top-full left-0 mt-2 w-48 rounded-lg shadow-lg py-2 z-50"
              >
                <!-- 鍏ㄩ儴璧勮閫夐」 -->
                <RouterLink
                  to="/articles"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors font-medium border-b border-gray-700"
                  style="--stagger-index: 0"
                  @click="showNewsMenu = false"
                >
                  <span class="inline-flex items-center gap-2">
                    <Newspaper class="h-3.5 w-3.5" />
                    <span>{{ $t("layout.allNews") }}</span>
                  </span>
                </RouterLink>
                <!-- 鍔犺浇涓姸锟?-->
                <div
                  v-if="categoriesLoading"
                  class="px-4 py-2 text-sm text-gray-400"
                >
                  {{ $t("common.loading") }}
                </div>
                <!-- 鍔ㄦ€佹覆鏌撴枃绔犲垎锟?-->
                <RouterLink
                  v-for="(category, articleCategoryIndex) in articleCategories"
                  :key="category.id"
                  :to="`/articles?category=${encodeURIComponent(category.name)}`"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors"
                  :style="{
                    '--stagger-index': String(articleCategoryIndex + 1),
                  }"
                  @click="showNewsMenu = false"
                >
                  {{ resolveGameCategoryName(category) }}
                  <span
                    v-if="category.articles_count > 0"
                    class="text-xs text-gray-500 ml-1"
                  >
                    ({{ category.articles_count }})
                  </span>
                </RouterLink>
                <!-- 鏃犲垎绫绘椂鐨勬彁锟?-->
                <div
                  v-if="!categoriesLoading && articleCategories.length === 0"
                  class="px-4 py-2 text-sm text-gray-400"
                >
                  {{ $t("layout.noCategory") }}
                </div>
              </div>
            </Transition>
          </div>
          <div
            class="relative faq-menu top-nav-dropdown flex items-center h-10"
            @mouseenter="showFaqMenu = true"
            @mouseleave="showFaqMenu = false"
          >
            <button
              :class="[
                'text-base transition-colors cursor-pointer flex items-center h-full gap-1',
                routePathStartsWith('/articles') &&
                String(route.query.category || '') === FAQ_CATEGORY_NAME
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground hover:text-foreground',
              ]"
              @click="showFaqMenu = !showFaqMenu"
            >
              <HelpCircle class="h-4 w-4" /> <span>{{ $t("faq") }}</span>
            </button>
            <Transition name="dropdown">
              <div
                v-if="showFaqMenu"
                class="dropdown-content site-dropdown-panel absolute top-full left-0 mt-2 w-72 rounded-lg shadow-lg py-2 z-50"
              >
                <RouterLink
                  :to="`/articles?category=${encodeURIComponent(FAQ_CATEGORY_NAME)}`"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors font-medium border-b border-gray-700"
                  style="--stagger-index: 0"
                  @click="showFaqMenu = false"
                >
                  {{ $t("layout.faqCategory") }}
                </RouterLink>
                <div
                  v-if="faqArticlesLoading"
                  class="px-4 py-2 text-sm text-gray-400"
                >
                  {{ $t("common.loading") }}
                </div>
                <RouterLink
                  v-for="(faqArticle, faqIndex) in faqArticles"
                  :key="faqArticle.id"
                  :to="`/articles/${faqArticle.id}`"
                  class="dropdown-item menu-stagger-item block px-4 py-2 text-sm transition-colors"
                  :style="{ '--stagger-index': String(faqIndex + 1) }"
                  @click="showFaqMenu = false"
                >
                  <span
                    class="block overflow-hidden text-ellipsis whitespace-nowrap"
                    >{{ faqArticle.title }}</span
                  >
                </RouterLink>
                <div
                  v-if="!faqArticlesLoading && faqArticles.length === 0"
                  class="px-4 py-2 text-sm text-gray-400"
                >
                  {{ $t("layout.noFaqContent") }}
                </div>
              </div>
            </Transition>
          </div>
          <RouterLink
            to="/cg-wiki"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/cg-wiki')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            <span class="flex items-center gap-1">
              <span
                class="text-[10px] bg-primary text-primary-foreground px-1.5 py-0.5 rounded font-bold leading-none"
                >{{ $t("layout.newBadge") }}</span
              >
              {{ $t("layout.topNews") }}
            </span>
          </RouterLink>
          <RouterLink
            to="/tavern"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/tavern')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            <span class="flex items-center gap-1">
              <span
                class="text-[10px] bg-purple-600 text-white px-1.5 py-0.5 rounded font-bold leading-none"
                >AI</span
              >
              {{ $t("nav.tavern") }}
            </span>
          </RouterLink>
          <RouterLink
            to="/novel-story"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/novel-story')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ $t("nav.novel") }}
          </RouterLink>
          <RouterLink
            to="/plaza"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/plaza')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ $t("nav.plaza") }}
          </RouterLink>
          <RouterLink
            v-if="isDevMode"
            to="/short-drama-expert"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/short-drama-expert')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            短剧专家
          </RouterLink>
          <RouterLink
            to="/recharge-api"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/recharge-api')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            <span>API {{ $t("recharge") }}</span>
          </RouterLink>
          <RouterLink
            to="/customer-service"
            :class="[
              'text-base transition-colors flex items-center h-10',
              isRoutePath('/customer-service')
                ? 'text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground',
            ]"
          >
            {{ $t("support") }}
          </RouterLink>
        </nav>
        <Transition name="mobile-menu">
          <div
            v-if="showMobileMenu"
            class="mobile-menu-panel md:hidden mt-2 mb-3 p-3"
          >
            <div class="relative">
              <Search
                class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground"
              />
              <Input
                v-model="searchQuery"
                @keyup.enter="handleMobileSearch"
                :placeholder="$t('search')"
                class="pl-10"
              />
            </div>
            <div class="mt-3 flex flex-col gap-1.5">
              <RouterLink
                to="/"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/') ? 'mobile-menu-link-active' : '',
                ]"
                @click="closeMobileMenu"
              >
                {{ $t("home") }}
              </RouterLink>
              <button
                type="button"
                class="mobile-menu-trigger"
                @click="showMobileGameCategories = !showMobileGameCategories"
              >
                <span>{{ $t("games") }}</span>
                <span class="text-xs">{{
                  showMobileGameCategories ? "-" : "+"
                }}</span>
              </button>
              <div v-if="showMobileGameCategories" class="mobile-menu-submenu">
                <RouterLink
                  to="/games"
                  :class="[
                    'mobile-menu-sub-link',
                    routePathStartsWith('/games')
                      ? 'mobile-menu-sub-link-active'
                      : '',
                  ]"
                  @click="closeMobileMenu"
                >
                  {{ $t("allGames") }}
                </RouterLink>
                <RouterLink
                  v-for="category in gameCategories"
                  :key="`mobile-game-${category.id}`"
                  :to="`/games?category=${category.code || 'all'}`"
                  class="mobile-menu-sub-link"
                  @click="closeMobileMenu"
                >
                  {{ category.name }}
                </RouterLink>
              </div>
              <button
                type="button"
                class="mobile-menu-trigger"
                @click="showMobileNewsCategories = !showMobileNewsCategories"
              >
                <span>{{ $t("news") }}</span>
                <span class="text-xs">{{
                  showMobileNewsCategories ? "-" : "+"
                }}</span>
              </button>
              <div v-if="showMobileNewsCategories" class="mobile-menu-submenu">
                <RouterLink
                  to="/articles"
                  :class="[
                    'mobile-menu-sub-link',
                    routePathStartsWith('/articles')
                      ? 'mobile-menu-sub-link-active'
                      : '',
                  ]"
                  @click="closeMobileMenu"
                >
                  {{ $t("news") }}
                </RouterLink>
                <RouterLink
                  v-for="category in articleCategories"
                  :key="`mobile-article-${category.id}`"
                  :to="`/articles?category=${encodeURIComponent(category.name)}`"
                  class="mobile-menu-sub-link"
                  @click="closeMobileMenu"
                >
                  {{ category.name }}
                </RouterLink>
              </div>
              <button
                type="button"
                class="mobile-menu-trigger"
                @click="showMobileFaqArticles = !showMobileFaqArticles"
              >
                <span>{{ $t("faq") }}</span>
                <span class="text-xs">{{
                  showMobileFaqArticles ? "-" : "+"
                }}</span>
              </button>
              <div v-if="showMobileFaqArticles" class="mobile-menu-submenu">
                <RouterLink
                  :to="`/articles?category=${encodeURIComponent(FAQ_CATEGORY_NAME)}`"
                  class="mobile-menu-sub-link"
                  @click="closeMobileMenu"
                >
                  {{ $t("layout.faqCategory") }}
                </RouterLink>
                <RouterLink
                  v-for="faqArticle in faqArticles"
                  :key="`mobile-faq-${faqArticle.id}`"
                  :to="`/articles/${faqArticle.id}`"
                  class="mobile-menu-sub-link"
                  @click="closeMobileMenu"
                >
                  <span
                    class="block overflow-hidden text-ellipsis whitespace-nowrap"
                    >{{ faqArticle.title }}</span
                  >
                </RouterLink>
              </div>
              <RouterLink
                to="/cg-wiki"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/cg-wiki') ? 'mobile-menu-link-active' : '',
                ]"
                @click="closeMobileMenu"
              >
                {{ $t("nav.cgWiki") }}
              </RouterLink>
              <RouterLink
                to="/tavern"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/tavern') ? 'mobile-menu-link-active' : '',
                ]"
                @click="closeMobileMenu"
              >
                {{ $t("nav.tavern") }}
              </RouterLink>
              <RouterLink
                to="/novel-story"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/novel-story') ? 'mobile-menu-link-active' : '',
                ]"
                @click="closeMobileMenu"
              >
                {{ $t("nav.novel") }}
              </RouterLink>
              <RouterLink
                to="/plaza"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/plaza') ? 'mobile-menu-link-active' : '',
                ]"
                @click="closeMobileMenu"
              >
                {{ $t("nav.plaza") }}
              </RouterLink>
              <RouterLink
                v-if="isDevMode"
                to="/short-drama-expert"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/short-drama-expert')
                    ? 'mobile-menu-link-active'
                    : '',
                ]"
                @click="closeMobileMenu"
              >
                短剧专家
              </RouterLink>
              <RouterLink
                to="/recharge-api"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/recharge-api') ? 'mobile-menu-link-active' : '',
                ]"
                @click="closeMobileMenu"
              >
                API {{ $t("recharge") }}
              </RouterLink>
              <RouterLink
                to="/customer-service"
                :class="[
                  'mobile-menu-link',
                  isRoutePath('/customer-service')
                    ? 'mobile-menu-link-active'
                    : '',
                ]"
                @click="closeMobileMenu"
              >
                {{ $t("support") }}
              </RouterLink>
            </div>
          </div>
        </Transition>
      </div>
      <div
        class="route-progress"
        :class="{ active: pageProgressActive }"
        aria-hidden="true"
      >
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
    <footer
      :class="[
        'bg-card',
        isRoutePath('/') ? 'mt-0 border-t-0' : 'mt-20 border-t border-border',
      ]"
    >
      <div v-if="isRoutePath('/')" class="container mx-auto px-4">
        <GlobalPraiseTicker />
      </div>
      <div class="container mx-auto px-4 py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- 鍔ㄦ€佹覆鏌撳簳閮ㄦ澘锟?-->
          <div
            v-for="(section, idx) in effectiveFooterSections"
            :key="section.id"
          >
            <h3
              class="font-bold mb-4"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, `section_${idx}_title`)"
            >
              {{ section.title }}
            </h3>
            <!-- 濡傛灉鏈夋弿杩板垯鏄剧ず鎻忚堪锛堝叧浜庢垜浠級 -->
            <p
              v-if="section.description"
              class="text-muted-foreground text-sm"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, `section_${idx}_description`)"
            >
              {{ section.description }}
            </p>
            <!-- 濡傛灉鏈夐摼鎺ュ垯鏄剧ず閾炬帴鍒楄〃 -->
            <ul
              v-if="section.links && section.links.length > 0"
              class="space-y-2 text-sm"
            >
              <li v-for="(link, lidx) in section.links" :key="link.id">
                <RouterLink
                  v-if="!link.is_external"
                  :to="link.url"
                  class="text-muted-foreground hover:text-foreground"
                >
                  <span
                    :contenteditable="isEditMode"
                    @blur="
                      handleInlineEdit($event, `link_${idx}_${lidx}_title`)
                    "
                    >{{ link.title }}</span
                  >
                </RouterLink>
                <a
                  v-else
                  :href="link.url"
                  target="_blank"
                  class="text-muted-foreground hover:text-foreground"
                >
                  <span
                    :contenteditable="isEditMode"
                    @blur="
                      handleInlineEdit($event, `link_${idx}_${lidx}_title`)
                    "
                    >{{ link.title }}</span
                  >
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div
          v-if="footerConfig.show_copyright"
          class="border-t border-border mt-8 pt-8 text-center text-muted-foreground text-sm"
        >
          <p>{{ footerConfig.copyright_text }}</p>
        </div>
        <div class="border-t border-border mt-4 pt-5 text-center">
          <button
            type="button"
            class="footer-policy-link text-sm"
            @click="openUsagePolicyDialogPanel()"
          >
            {{ usagePolicyTitle }}
          </button>
        </div>
      </div>
    </footer>
    <DirectMessageFloat />
    <!-- Auth Dialog -->
    <AuthDialog v-model="showAuthDialog" />
    <Dialog v-model="showUsagePolicyDialog" panel-class="max-w-4xl p-0">
      <div class="usage-policy-dialog">
        <div
          class="usage-policy-dialog__header border-b border-border px-5 py-4 flex items-center justify-between gap-3"
        >
          <h3 class="text-base font-semibold text-foreground">
            {{ usagePolicyTitle }}
          </h3>
          <button
            type="button"
            class="text-sm text-muted-foreground hover:text-foreground"
            @click="showUsagePolicyDialog = false"
          >
            关闭
          </button>
        </div>
        <div class="usage-policy-dialog__content px-5 py-4 space-y-3">
          <p
            v-if="usagePolicyReason"
            class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
          >
            {{ usagePolicyReason }}
          </p>
          <div class="usage-policy-dialog__body rounded-md border border-border">
            <div
              v-if="usagePolicyLoading"
              class="usage-policy-dialog__status text-muted-foreground"
            >
              {{ $t("common.loading") }}
            </div>
            <div
              v-else-if="usagePolicyError"
              class="usage-policy-dialog__status text-red-600"
            >
              {{ usagePolicyError }}
            </div>
            <pre v-else class="usage-policy-dialog__text">{{
              usagePolicyText
            }}</pre>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Search,
  MessageCircle,
  User,
  Menu,
  Globe,
  Palette,
  MousePointer2,
  Newspaper,
  HelpCircle,
  X,
} from "lucide-vue-next";
import { useAuthStore } from "../stores/auth";
import { useThemeStore } from "../stores/theme";
import { useLanguageStore } from "../stores/language";
import {
  getArticleCategories,
  getArticles,
  type ArticleCategory,
} from "../api/articles";
import { getGameCategories } from "../api/games";
import { getFooterSections, getFooterConfig } from "../api/footer";
import type { FooterConfig, FooterLink, FooterSection } from "../api/footer";
import type { Article, GameCategoryItem } from "../types";
import type { LocaleCode } from "../i18n/locales";
import type { ThemeCursorMode } from "../theme/presets";
import { resolveGameCategoryIcon } from "../utils/iconMap";
import { stripLocalePrefix, withLocalePrefix } from "../i18n/locale-routing";
import Button from "./ui/Button.vue";
import Input from "./ui/Input.vue";
import Dialog from "./ui/Dialog.vue";
import AuthDialog from "./AuthDialog.vue";
import DirectMessageFloat from "./DirectMessageFloat.vue";
import GlobalPraiseTicker from "./GlobalPraiseTicker.vue";
import { useVisualEditor } from "../composables/useVisualEditor";
import {
  USAGE_POLICY_OPEN_EVENT,
  USAGE_POLICY_TXT_URL,
  resolveUsagePolicyTitle,
  resolveUsagePolicyTxtUrl,
} from "../utils/usagePolicy";

type CursorModeOption = {
  id: ThemeCursorMode;
  labelKey: string;
};

const authStore = useAuthStore();
const themeStore = useThemeStore();
const languageStore = useLanguageStore();
const route = useRoute();
const router = useRouter();
const normalizedRoutePath = computed(() => stripLocalePrefix(route.path));
const isDevMode = import.meta.env.DEV;

const isRoutePath = (targetPath: string): boolean => {
  return normalizedRoutePath.value === targetPath;
};

const routePathStartsWith = (prefix: string): boolean => {
  return normalizedRoutePath.value.startsWith(prefix);
};

const { isEditMode, pageConfig, handleInlineEdit } = useVisualEditor(
  "footer",
  languageStore.t("layout.footerEditorLabel"),
);

const searchQuery = ref("");
const showAuthDialog = ref(false);
const showUserMenu = ref(false);
const showLangMenu = ref(false);
const showGamesMenu = ref(false);
const showNewsMenu = ref(false);
const showFaqMenu = ref(false);
const showThemePanel = ref(false);
const showMobileMenu = ref(false);
const showMobileGameCategories = ref(false);
const showMobileNewsCategories = ref(false);
const showMobileFaqArticles = ref(false);
const themePanelRef = ref<HTMLElement | null>(null);
const pageProgressActive = ref(false);
let pageProgressTimer: ReturnType<typeof window.setTimeout> | null = null;

const cursorModes: ReadonlyArray<CursorModeOption> = [
  { id: "soft", labelKey: "layout.cursorSoft" },
  { id: "system", labelKey: "layout.cursorSystem" },
  { id: "crosshair", labelKey: "layout.cursorCrosshair" },
  { id: "neon", labelKey: "layout.cursorNeon" },
];

const buildArticleCategoryFallback = (): ArticleCategory[] => {
  return [
    {
      id: 1,
      name: languageStore.t("layout.gameNewsCategory"),
      description: "",
      sort_order: 1,
      is_active: true,
      articles_count: 0,
      created_at: "",
      updated_at: "",
    },
    {
      id: 2,
      name: languageStore.t("layout.guideCategory"),
      description: "",
      sort_order: 2,
      is_active: true,
      articles_count: 0,
      created_at: "",
      updated_at: "",
    },
    {
      id: 3,
      name: languageStore.t("layout.rechargeGuideCategory"),
      description: "",
      sort_order: 3,
      is_active: true,
      articles_count: 0,
      created_at: "",
      updated_at: "",
    },
    {
      id: 4,
      name: languageStore.t("layout.announcementCategory"),
      description: "",
      sort_order: 4,
      is_active: true,
      articles_count: 0,
      created_at: "",
      updated_at: "",
    },
  ];
};

const buildGameCategoryFallback = (): GameCategoryItem[] => {
  return [
    {
      id: "all",
      name: languageStore.t("layout.allGamesCategory"),
      nameKey: "allGames",
      icon: "🎮",
      code: "all",
    },
    {
      id: "international",
      name: languageStore.t("layout.internationalGamesCategory"),
      nameKey: "internationalGames",
      icon: "🌍",
      code: "international",
    },
    {
      id: "hongkong-taiwan",
      name: languageStore.t("layout.hongKongTaiwanGamesCategory"),
      nameKey: "hongKongTaiwanGames",
      icon: "🏮",
      code: "hongkong-taiwan",
    },
    {
      id: "southeast-asia",
      name: languageStore.t("layout.southeastAsiaGamesCategory"),
      nameKey: "southeastAsiaGames",
      icon: "🌴",
      code: "southeast-asia",
    },
  ];
};

const GAME_CATEGORY_TRANSLATION_KEYS: Record<string, string> = {
  all: "allGames",
  allgames: "allGames",
  allgamescategory: "allGames",
  international: "internationalGames",
  internationalgames: "internationalGames",
  global: "internationalGames",
  "hongkong-taiwan": "hongKongTaiwanGames",
  hongkong: "hongKongTaiwanGames",
  taiwan: "hongKongTaiwanGames",
  hk: "hongKongTaiwanGames",
  tw: "hongKongTaiwanGames",
  "southeast-asia": "southeastAsiaGames",
  southeastasia: "southeastAsiaGames",
  southeast: "southeastAsiaGames",
  sea: "southeastAsiaGames",
};

const resolveGameCategoryName = (category: Partial<GameCategoryItem>): string => {
  const candidates = [category?.nameKey, category?.code, category?.id]
    .map((item) => String(item || "").trim().toLowerCase())
    .filter(Boolean);

  for (const token of candidates) {
    const compact = token.replace(/[\s_-]+/g, "");
    const key = GAME_CATEGORY_TRANSLATION_KEYS[token] || GAME_CATEGORY_TRANSLATION_KEYS[compact];
    if (key) return languageStore.t(key);
  }

  return String(category?.name || "");
};

const articleCategories = ref<ArticleCategory[]>([]);
const categoriesLoading = ref(true);
const faqArticles = ref<Article[]>([]);
const faqArticlesLoading = ref(false);
const FAQ_CATEGORY_NAME = "常见问题";

const gameCategories = ref<GameCategoryItem[]>([]);
const gameCategoriesLoading = ref(true);

const footerSections = ref<FooterSection[]>([]);
const currentYear = new Date().getFullYear();
const footerConfig = ref<Partial<FooterConfig>>({
  copyright_text: languageStore.t("layout.copyright", {
    year: currentYear,
    company: "CYPHER GAME BUY",
  }),
  show_copyright: true,
});
const footerLoading = ref(true);
const showUsagePolicyDialog = ref(false);
const usagePolicyLoading = ref(false);
const usagePolicyText = ref("");
const usagePolicyTextLocale = ref("");
const usagePolicyError = ref("");
const usagePolicyReason = ref("");
const usagePolicyTitle = computed(() =>
  resolveUsagePolicyTitle(String(languageStore.currentLocale || "zh-CN")),
);

const pageTransitionName = ref("route-fade");
const previousRoutePath = ref(stripLocalePrefix(route.path));

const clearPageProgressTimer = () => {
  if (pageProgressTimer) {
    clearTimeout(pageProgressTimer);
    pageProgressTimer = null;
  }
};

const triggerPageProgress = (duration = 520) => {
  clearPageProgressTimer();
  pageProgressActive.value = true;
  pageProgressTimer = window.setTimeout(() => {
    pageProgressActive.value = false;
    pageProgressTimer = null;
  }, duration);
};

watch(
  () => route.fullPath,
  () => {
    closeAllMenus();
    triggerPageProgress(520);
    const currentPath = normalizedRoutePath.value;
    const prevPath = previousRoutePath.value;

    if (currentPath === prevPath) {
      pageTransitionName.value = "route-fade";
      return;
    }

    const currentDepth = currentPath.split("/").filter(Boolean).length;
    const prevDepth = prevPath.split("/").filter(Boolean).length;

    if (currentDepth > prevDepth) {
      pageTransitionName.value = "route-slide-left";
    } else if (currentDepth < prevDepth) {
      pageTransitionName.value = "route-slide-right";
    } else {
      pageTransitionName.value = "route-fade";
    }

    previousRoutePath.value = currentPath;
  },
);

const loadArticleCategories = async () => {
  try {
    categoriesLoading.value = true;
    articleCategories.value = await getArticleCategories();
  } catch (error) {
    console.error("Failed to load article categories:", error);
    articleCategories.value = buildArticleCategoryFallback();
  } finally {
    categoriesLoading.value = false;
  }
};

const loadGameCategories = async () => {
  try {
    gameCategoriesLoading.value = true;
    gameCategories.value = await getGameCategories();
  } catch (error) {
    console.error("Failed to load game categories:", error);
    gameCategories.value = buildGameCategoryFallback();
  } finally {
    gameCategoriesLoading.value = false;
  }
};

const loadFooterData = async () => {
  try {
    footerLoading.value = true;
    const [sections, config] = await Promise.all([
      getFooterSections(),
      getFooterConfig(),
    ]);
    footerSections.value = sections;
    footerConfig.value = config;
  } catch (error) {
    console.error("Failed to load footer data:", error);
  } finally {
    footerLoading.value = false;
  }
};

const requestUsagePolicyText = async (url: string): Promise<string> => {
  const response = await fetch(url, {
    cache: "no-cache",
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.text();
};

const loadUsagePolicyText = async () => {
  if (usagePolicyLoading.value) return;

  const locale = String(languageStore.currentLocale || "zh-CN").trim();
  if (usagePolicyText.value && usagePolicyTextLocale.value === locale) return;

  usagePolicyLoading.value = true;
  usagePolicyError.value = "";
  try {
    const localePolicyUrl = resolveUsagePolicyTxtUrl(locale);
    const fallbackUrl = USAGE_POLICY_TXT_URL;
    try {
      usagePolicyText.value = await requestUsagePolicyText(localePolicyUrl);
      usagePolicyTextLocale.value = locale;
    } catch (localeError) {
      if (localePolicyUrl === fallbackUrl) {
        throw localeError;
      }
      usagePolicyText.value = await requestUsagePolicyText(fallbackUrl);
      usagePolicyTextLocale.value = "zh-CN";
    }
  } catch (error) {
    console.error("Failed to load usage policy text:", error);
    usagePolicyError.value = "加载规范内容失败，请稍后重试。";
    usagePolicyTextLocale.value = "";
  } finally {
    usagePolicyLoading.value = false;
  }
};

const openUsagePolicyDialogPanel = async (reason = "") => {
  usagePolicyReason.value = String(reason || "").trim();
  showUsagePolicyDialog.value = true;
  await loadUsagePolicyText();
};

watch(
  () => languageStore.currentLocale,
  () => {
    usagePolicyText.value = "";
    usagePolicyTextLocale.value = "";
    usagePolicyError.value = "";
    if (showUsagePolicyDialog.value) {
      void loadUsagePolicyText();
    }
  },
);

const handleUsagePolicyOpenEvent = (event: Event) => {
  const customEvent = event as CustomEvent<{ reason?: string }>;
  void openUsagePolicyDialogPanel(String(customEvent.detail?.reason || ""));
};

const loadFaqArticles = async () => {
  try {
    faqArticlesLoading.value = true;
    const rows = await getArticles({ category: FAQ_CATEGORY_NAME });
    faqArticles.value = rows.slice(0, 8);
  } catch (error) {
    console.error("Failed to load FAQ articles:", error);
    faqArticles.value = [];
  } finally {
    faqArticlesLoading.value = false;
  }
};

const readOverride = (key: string): string | undefined => {
  const value = pageConfig.value?.[key];
  return typeof value === "string" ? value : undefined;
};

const effectiveFooterSections = computed<FooterSection[]>(() => {
  return footerSections.value.map((section, sectionIndex) => {
    const overrideTitle = readOverride(`section_${sectionIndex}_title`);
    const overrideDesc = readOverride(`section_${sectionIndex}_description`);

    return {
      ...section,
      title: overrideTitle ?? section.title,
      description: overrideDesc ?? section.description,
      links: (section.links || []).map(
        (link: FooterLink, linkIndex: number) => {
          const overrideLinkTitle = readOverride(
            `link_${sectionIndex}_${linkIndex}_title`,
          );

          return {
            ...link,
            title: overrideLinkTitle ?? link.title,
          };
        },
      ),
    };
  });
});

const handleLogout = async () => {
  await authStore.logout();
  closeAllMenus();
  window.alert(languageStore.t("layout.logoutSuccess"));
};

const handleSearch = () => {
  const keyword = searchQuery.value.trim();
  if (keyword) {
    router.push({
      path: "/search",
      query: { q: keyword },
    });
  }
};

const changeLanguage = async (locale: LocaleCode) => {
  const nextLocalizedPath = withLocalePrefix(route.fullPath, locale);
  await languageStore.setLocale(locale);
  if (route.fullPath !== nextLocalizedPath) {
    await router.replace(nextLocalizedPath);
  }
  showLangMenu.value = false;
  closeMobileMenu();
};

const applyThemePreset = (presetId: string) => {
  themeStore.setPreset(presetId);
};

const closeMobileMenu = () => {
  showMobileMenu.value = false;
  showMobileGameCategories.value = false;
  showMobileNewsCategories.value = false;
  showMobileFaqArticles.value = false;
};

const closeAllMenus = () => {
  showUserMenu.value = false;
  showLangMenu.value = false;
  showGamesMenu.value = false;
  showNewsMenu.value = false;
  showFaqMenu.value = false;
  showThemePanel.value = false;
  closeMobileMenu();
};

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
  if (!showMobileMenu.value) {
    showMobileGameCategories.value = false;
    showMobileNewsCategories.value = false;
    showMobileFaqArticles.value = false;
  }
};

const handleMobileSearch = () => {
  handleSearch();
  closeMobileMenu();
};

const handleViewportResize = () => {
  if (window.innerWidth >= 768) {
    closeMobileMenu();
  }
};

const handleDocumentClick = (event: MouseEvent) => {
  if (!(event.target instanceof Node)) return;

  if (themePanelRef.value && !themePanelRef.value.contains(event.target)) {
    showThemePanel.value = false;
  }
};

onMounted(() => {
  void loadArticleCategories();
  void loadGameCategories();
  void loadFaqArticles();
  void loadFooterData();
  document.addEventListener("click", handleDocumentClick);
  window.addEventListener("resize", handleViewportResize);
  window.addEventListener(
    USAGE_POLICY_OPEN_EVENT,
    handleUsagePolicyOpenEvent as EventListener,
  );
  triggerPageProgress(420);
});

onUnmounted(() => {
  document.removeEventListener("click", handleDocumentClick);
  window.removeEventListener("resize", handleViewportResize);
  window.removeEventListener(
    USAGE_POLICY_OPEN_EVENT,
    handleUsagePolicyOpenEvent as EventListener,
  );
  clearPageProgressTimer();
});
</script>
<style scoped>
.galaxy-header {
  background:
    radial-gradient(
      circle at 6% 0%,
      color-mix(in srgb, var(--primary-color) 16%, transparent) 0%,
      transparent 36%
    ),
    radial-gradient(
      circle at 94% 0%,
      color-mix(in srgb, #22c55e 14%, transparent) 0%,
      transparent 34%
    ),
    color-mix(in srgb, #ffffff 88%, #f2f8ff 12%);
  border-bottom: 1px solid color-mix(in srgb, #cfdced 72%, #ffffff 28%);
  box-shadow: 0 16px 34px -28px rgba(15, 23, 42, 0.32);
  backdrop-filter: blur(12px);
}
.galaxy-header::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    color-mix(in srgb, var(--primary-color) 55%, transparent) 52%,
    transparent 100%
  );
  opacity: 0.7;
}
.logo-badge {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, #c6d6ec 78%, #ffffff 22%);
  background: linear-gradient(160deg, #ffffff 0%, #f0f7ff 100%);
  color: #0f172a;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.04em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 22px -18px rgba(2, 132, 199, 0.52);
}
.menu-float-panel {
  transform-origin: top right;
  animation: menu-float-in 220ms cubic-bezier(0.16, 1, 0.3, 1);
  backdrop-filter: blur(12px);
}
.menu-stagger-item {
  opacity: 0;
  transform: translateY(7px) scale(0.995);
  animation: menu-stagger-in 260ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: calc(var(--stagger-index, 0) * 34ms + 24ms);
}
.top-nav {
  overflow: visible;
}
.top-nav-dropdown {
  padding-bottom: 0.5rem;
  margin-bottom: -0.5rem;
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
  background: linear-gradient(
    90deg,
    transparent 0%,
    hsl(var(--primary)) 40%,
    hsl(var(--accent)) 100%
  );
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
  background: color-mix(in srgb, #ffffff 84%, #f4f9ff 16%);
  border: 1px solid color-mix(in srgb, #d4e0f3 74%, #ffffff 26%);
  box-shadow: 0 24px 36px -30px rgba(15, 23, 42, 0.46);
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
  border-color: color-mix(
    in srgb,
    var(--primary-color) 60%,
    hsl(var(--border))
  );
  transform: translateY(-1px);
}
.theme-preset-btn.active {
  border-color: color-mix(
    in srgb,
    var(--primary-color) 80%,
    hsl(var(--border))
  );
  box-shadow: 0 0 0 1px
    color-mix(in srgb, var(--primary-color) 26%, transparent);
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
  border-color: color-mix(
    in srgb,
    var(--secondary-color) 58%,
    hsl(var(--border))
  );
  color: hsl(var(--foreground));
}
.theme-cursor-btn.active {
  color: hsl(var(--foreground));
  border-color: color-mix(
    in srgb,
    var(--secondary-color) 75%,
    hsl(var(--border))
  );
  box-shadow: 0 0 0 1px
    color-mix(in srgb, var(--secondary-color) 24%, transparent);
}
.dropdown-enter-active,
.dropdown-leave-active {
  transition:
    opacity 220ms cubic-bezier(0.16, 1, 0.3, 1),
    transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
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
.mobile-menu-panel {
  border: 1px solid color-mix(in srgb, #d4e0f3 74%, #ffffff 26%);
  border-radius: 14px;
  background: color-mix(in srgb, #ffffff 90%, #f4f9ff 10%);
  box-shadow: 0 20px 34px -28px rgba(15, 23, 42, 0.4);
}
.mobile-menu-link,
.mobile-menu-trigger {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  font-weight: 600;
  color: hsl(var(--muted-foreground));
  background: color-mix(in srgb, #ffffff 92%, #eef5ff 8%);
  border: 1px solid color-mix(in srgb, #dbe7f7 80%, #ffffff 20%);
}
.mobile-menu-link:hover,
.mobile-menu-trigger:hover {
  color: hsl(var(--foreground));
  background: color-mix(in srgb, #f5faff 78%, #ffffff 22%);
  border-color: color-mix(in srgb, #bfdbfe 72%, #ffffff 28%);
}
.mobile-menu-link-active {
  color: hsl(var(--foreground));
  border-color: color-mix(in srgb, var(--primary-color) 42%, #dbeafe);
  background: color-mix(in srgb, hsl(var(--accent) / 0.15) 56%, #ffffff 44%);
}
.mobile-menu-submenu {
  display: grid;
  gap: 6px;
  padding: 4px 0 2px 10px;
}
.mobile-menu-sub-link {
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 13px;
  color: hsl(var(--muted-foreground));
}
.mobile-menu-sub-link:hover {
  color: hsl(var(--foreground));
  background: color-mix(in srgb, #f0f7ff 80%, #ffffff 20%);
}
.mobile-menu-sub-link-active {
  color: hsl(var(--foreground));
  background: color-mix(in srgb, hsl(var(--accent) / 0.16) 58%, #ffffff 42%);
}
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition:
    opacity 200ms ease,
    transform 200ms ease;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
.mobile-menu-enter-to,
.mobile-menu-leave-from {
  opacity: 1;
  transform: translateY(0);
}
@media (prefers-reduced-motion: reduce) {
  .menu-stagger-item {
    opacity: 1;
    transform: none;
    animation: none;
  }
  .mobile-menu-enter-active,
  .mobile-menu-leave-active {
    transition: none;
  }
}
.footer-policy-link {
  color: hsl(var(--muted-foreground));
  text-decoration: underline;
  text-underline-offset: 3px;
}
.footer-policy-link:hover {
  color: hsl(var(--foreground));
}
.usage-policy-dialog {
  background: hsl(var(--card));
}
.usage-policy-dialog__body {
  max-height: min(62vh, 560px);
  overflow: auto;
}
.usage-policy-dialog__status {
  padding: 20px 16px;
  font-size: 14px;
}
.usage-policy-dialog__text {
  margin: 0;
  padding: 16px;
  white-space: pre-wrap;
  line-height: 1.65;
  font-size: 13px;
  color: hsl(var(--foreground));
}
</style>
