﻿﻿﻿<template>
  <div class="homepage-shell relative min-h-screen">
    <!-- Subtle Grid Background -->
    <div class="fixed inset-0 pointer-events-none home-grid-overlay"></div>
    <div
      v-if="showAmbientLayer"
      class="fixed inset-0 pointer-events-none home-ambient-layer"
      :style="ambientLayerStyle"
      aria-hidden="true"
    >
      <span
        v-for="particle in ambientParticles"
        :key="particle.id"
        class="ambient-particle"
        :style="getAmbientParticleStyle(particle)"
      ></span>
    </div>
    
    <!-- 按后台排序动态渲染板块 -->
    <div 
      v-for="(section, sectionIndex) in sortedEnabledSections" 
      :key="section.sectionKey"
      class="relative group/section"
      :class="{'cursor-pointer': isEditMode}"
      :data-section-key="section.sectionKey"
      v-motion-reveal="{ delay: Math.min(sectionIndex * 70, 280), y: 26 }"
      @click="handleSectionClick(section)"
      @mouseenter="isHovering = section.sectionKey"
      @mouseleave="isHovering = null"
    >
      <!-- 编辑模式下的高亮遮罩 -->
      <div 
        v-if="isEditMode" 
        class="absolute inset-0 z-[60] border-2 border-transparent group-hover/section:border-primary pointer-events-none transition-all duration-200"
        :class="{'border-primary bg-primary/5': selectedSectionKey === section.sectionKey}"
      >
        <!-- 浮动手柄 -->
        <div 
          v-if="selectedSectionKey === section.sectionKey || isHovering === section.sectionKey"
          class="absolute top-0 left-0 -translate-y-full bg-primary flex items-center gap-1 p-1 rounded-t-lg pointer-events-auto"
        >
          <button @click.stop="moveSection(section, 'up')" class="p-1 hover:bg-black/10 rounded" title="上移"><i class="fas fa-arrow-up text-black text-xs"></i></button>
          <button @click.stop="moveSection(section, 'down')" class="p-1 hover:bg-black/10 rounded" title="下移"><i class="fas fa-arrow-down text-black text-xs"></i></button>
          <div class="w-px h-3 bg-black/10 mx-1"></div>
          <button @click.stop="copySection(section)" class="p-1 hover:bg-black/10 rounded" title="复制"><i class="fas fa-copy text-black text-xs"></i></button>
          <button @click.stop="deleteSection(section)" class="p-1 hover:bg-red-500/20 rounded" title="删除"><i class="fas fa-trash text-red-600 text-xs"></i></button>
        </div>

        <div 
          v-if="selectedSectionKey === section.sectionKey"
          class="absolute top-0 right-0 bg-primary text-primary-foreground px-2 py-1 text-xs font-bold rounded-bl-lg"
        >
          正在编辑: {{ section.sectionName }}
        </div>
      </div>

      <!-- Hero Section with Carousel -->
      <section
        v-if="section.sectionKey === 'banner_section'"
        class="relative py-12"
        :class="isLightMode ? 'bg-white' : 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900'"
      >
      <div class="container mx-auto px-4">
        <div class="relative h-[400px] md:h-[500px]">
          <!-- Carousel Slides -->
          <div class="relative w-full h-full flex items-center justify-center overflow-hidden">
            <div 
              v-for="(slide, index) in carouselSlides" 
              :key="slide.id"
              :class="getSlideClasses(index)"
            >
              <!-- Background Image -->
              <img 
                :src="slide.image" 
                :alt="slide.title"
                class="w-full h-full object-cover banner-parallax-image"
                :class="{'cursor-pointer hover:opacity-80 transition-opacity': isEditMode}"
                :style="getBannerImageStyle(index)"
                @click="handleImageClick($event, 'banner_section', 'image')"
              />
              
              <!-- Gradient Overlay -->
              <div class="absolute inset-0 bg-gradient-to-r from-black/70 via-black/50 to-transparent"></div>
              
              <!-- Content - Only show on active slide -->
              <div v-if="currentSlide === index" class="absolute inset-0 flex items-center px-6 md:px-12 carousel-content">
                <div class="max-w-xl">
                  <!-- Badge -->
                  <div class="inline-block px-3 py-1.5 rounded-full border-2 border-cyan-400 bg-cyan-500/20 mb-3 backdrop-blur-sm shadow-[0_0_15px_rgba(0,255,255,0.6)]">
                    <span class="text-cyan-300 text-xs md:text-sm font-bold tracking-wider uppercase drop-shadow-[0_0_8px_rgba(0,255,255,0.8)]">{{ slide.badge }}</span>
                  </div>
                  
                  <!-- Title -->
                  <h1 class="text-2xl md:text-4xl lg:text-5xl font-black mb-3 text-white leading-tight drop-shadow-[0_0_10px_rgba(255,0,255,0.8)]">
                    {{ slide.title }}
                  </h1>
                  
                  <!-- Description -->
                  <p class="text-sm md:text-lg text-cyan-200 mb-6 leading-relaxed drop-shadow-[0_0_5px_rgba(0,255,255,0.5)]">
                    {{ slide.description }}
                  </p>
                  
                  <!-- CTA Buttons -->
                  <div class="flex flex-col sm:flex-row gap-3">
                    <RouterLink :to="slide.primaryLink">
                      <button v-magnetic="{ strength: 0.22, max: 14 }" class="px-6 py-3 rounded-xl font-bold text-sm md:text-base tracking-wide uppercase bg-gradient-to-r from-cyan-500 to-purple-600 text-white hover:shadow-[0_0_20px_rgba(0,255,255,0.8)] hover:scale-105 transition-all duration-300 border-2 border-cyan-400">
                        {{ slide.primaryButton }}
                      </button>
                    </RouterLink>
                    <RouterLink :to="slide.secondaryLink">
                      <button v-magnetic="{ strength: 0.2, max: 12 }" class="px-6 py-3 rounded-xl font-bold text-sm md:text-base tracking-wide uppercase border-2 border-pink-500 text-pink-400 hover:bg-pink-500 hover:text-black hover:shadow-[0_0_20px_rgba(255,0,255,0.8)] transition-all duration-300">
                        {{ slide.secondaryButton }}
                      </button>
                    </RouterLink>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Navigation Arrows -->
          <button 
            @click="prevSlide"
            class="absolute left-4 top-1/2 -translate-y-1/2 z-40 p-2.5 rounded-full bg-slate-900/80 border-2 border-cyan-400 hover:bg-cyan-500/20 hover:shadow-[0_0_15px_rgba(0,255,255,0.8)] shadow-lg transition-all duration-300"
          >
            <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button 
            @click="nextSlide"
            class="absolute right-4 top-1/2 -translate-y-1/2 z-40 p-2.5 rounded-full bg-slate-900/80 border-2 border-cyan-400 hover:bg-cyan-500/20 hover:shadow-[0_0_15px_rgba(0,255,255,0.8)] shadow-lg transition-all duration-300"
          >
            <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        
        <!-- Indicators -->
        <div class="flex justify-center gap-2 mt-6">
          <button
            v-for="(slide, index) in carouselSlides"
            :key="slide.id"
            @click="goToSlide(index)"
            :class="[
              'transition-all duration-300 rounded-full',
              currentSlide === index 
                ? 'w-8 h-2 bg-cyan-400 shadow-[0_0_10px_rgba(0,255,255,0.8)]' 
                : 'w-2 h-2 bg-slate-600 hover:bg-cyan-500 hover:shadow-[0_0_8px_rgba(0,255,255,0.6)]'
            ]"
          >
          </button>
        </div>
        
        <!-- Stats -->
        <div class="grid grid-cols-3 gap-6 mt-12 text-center">
          <div class="p-4 bg-slate-900/50 border-2 border-cyan-500/50 rounded-xl shadow-[0_0_20px_rgba(0,255,255,0.3)] hover:shadow-[0_0_30px_rgba(0,255,255,0.6)] hover:border-cyan-400 transition-all backdrop-blur-sm motion-breathe">
            <div class="text-2xl md:text-3xl font-black text-cyan-400 mb-1 drop-shadow-[0_0_10px_rgba(0,255,255,0.8)]">100K+</div>
            <div class="text-cyan-200 text-sm font-medium">{{ $t('activePlayers') }}</div>
          </div>
          <div class="p-4 bg-slate-900/50 border-2 border-purple-500/50 rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.3)] hover:shadow-[0_0_30px_rgba(168,85,247,0.6)] hover:border-purple-400 transition-all backdrop-blur-sm motion-breathe motion-breathe-delay-1">
            <div class="text-2xl md:text-3xl font-black text-purple-400 mb-1 drop-shadow-[0_0_10px_rgba(168,85,247,0.8)]">500+</div>
            <div class="text-purple-200 text-sm font-medium">{{ $t('supportedGames') }}</div>
          </div>
          <div class="p-4 bg-slate-900/50 border-2 border-pink-500/50 rounded-xl shadow-[0_0_20px_rgba(236,72,153,0.3)] hover:shadow-[0_0_30px_rgba(236,72,153,0.6)] hover:border-pink-400 transition-all backdrop-blur-sm motion-breathe motion-breathe-delay-2">
            <div class="text-2xl md:text-3xl font-black text-pink-400 mb-1 drop-shadow-[0_0_10px_rgba(236,72,153,0.8)]">99.9%</div>
            <div class="text-pink-200 text-sm font-medium">{{ $t('securityRate') }}</div>
          </div>
        </div>
      </div>
    </section>

      <!-- Features Section -->
      <section v-else-if="section.sectionKey === 'features'" class="py-20 relative" :style="{ backgroundColor: 'var(--page-bg)' }">
        <div class="container mx-auto px-4 relative z-10">
          <div class="text-center mb-16">
            <div class="inline-flex items-center justify-center p-3 bg-primary/20 rounded-custom mb-4 border border-primary/30">
              {{ getSectionConfig('features', 'icon', '✨') }}
            </div>
            <!-- 使用后台配置的标题 -->
            <h2 class="text-4xl md:text-5xl font-black text-white drop-shadow-[0_0_15px_rgba(0,255,255,0.8)]">
              <span 
                class="text-primary"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'title')"
              >{{ getSectionConfig('features', 'title', $t('coreFeatures')) }}</span>
            </h2>
            <!-- 使用后台配置的副标题 -->
            <p 
              class="text-xl text-cyan-200 max-w-2xl mx-auto"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'features', 'subtitle')"
            >
              {{ getSectionConfig('features', 'subtitle', $t('experienceNextGen')) }}
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
            <!-- Feature 1 -->
            <div class="p-8 bg-slate-800/50 rounded-custom border border-slate-700 hover:border-primary transition-all group/card text-center">
              <div class="w-16 h-16 bg-primary/20 rounded-custom flex items-center justify-center mb-6 mx-auto group-hover/card:scale-110 transition-transform overflow-hidden">
                <!-- 使用后台配置的图标，如果是 emoji 则显示文本，否则显示 SVG/Image -->
                <span 
                  v-if="getSectionConfig('features', 'feature_1_icon', '⚡').length <= 2" 
                  class="text-4xl"
                >
                  {{ getSectionConfig('features', 'feature_1_icon', '⚡') }}
                </span>
                <img 
                  v-else-if="getSectionConfig('features', 'feature_1_icon', '').startsWith('http')"
                  :src="getSectionConfig('features', 'feature_1_icon', '')"
                  class="w-full h-full object-cover"
                  @click="handleImageClick($event, 'features', 'feature_1_icon')"
                />
                <svg v-else class="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <!-- 使用后台配置的特性1标题和描述 -->
              <h3 
                class="text-xl font-bold text-cyan-300 mb-4 drop-shadow-[0_0_8px_rgba(0,255,255,0.6)]"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'feature_1_title')"
              >
                {{ getSectionConfig('features', 'feature_1_title', $t('fastArrival')) }}
              </h3>
              <p 
                class="text-cyan-100/80"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'feature_1_desc')"
              >
                {{ getSectionConfig('features', 'feature_1_desc', $t('fastArrivalDesc')) }}
              </p>
            </div>

            <!-- Feature 2 -->
            <div class="p-8 bg-slate-800/50 rounded-custom border border-slate-700 hover:border-primary transition-all group/card text-center">
              <div class="w-16 h-16 bg-primary/20 rounded-custom flex items-center justify-center mb-6 mx-auto group-hover/card:scale-110 transition-transform">
                <span v-if="getSectionConfig('features', 'feature_2_icon', '🔒').length <= 2" class="text-4xl">
                  {{ getSectionConfig('features', 'feature_2_icon', '🔒') }}
                </span>
                <svg v-else class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 
                class="text-xl font-bold text-white mb-4"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'feature_2_title')"
              >
                {{ getSectionConfig('features', 'feature_2_title', $t('secureGuarantee')) }}
              </h3>
              <p 
                class="text-slate-400 leading-relaxed"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'feature_2_desc')"
              >
                {{ getSectionConfig('features', 'feature_2_desc', $t('secureGuaranteeDesc')) }}
              </p>
            </div>
            
            <!-- Feature 3 -->
            <div class="p-8 bg-slate-800/50 rounded-custom border border-slate-700 hover:border-primary transition-all group/card text-center">
              <div class="w-16 h-16 bg-primary/20 rounded-custom flex items-center justify-center mb-6 mx-auto group-hover/card:scale-110 transition-transform">
                <span v-if="getSectionConfig('features', 'feature_3_icon', '💰').length <= 2" class="text-4xl">
                  {{ getSectionConfig('features', 'feature_3_icon', '💰') }}
                </span>
                <svg v-else class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 
                class="text-xl font-bold text-white mb-4"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'feature_3_title')"
              >
                {{ getSectionConfig('features', 'feature_3_title', $t('support247')) }}
              </h3>
              <p 
                class="text-slate-400 leading-relaxed"
                :contenteditable="isEditMode"
                @blur="handleInlineEdit($event, 'features', 'feature_3_desc')"
              >
                {{ getSectionConfig('features', 'feature_3_desc', $t('support247Desc')) }}
              </p>
            </div>
          </div>
        </div>
      </section>
      <!-- Hot Games Section -->
      <section
        v-else-if="section.sectionKey === 'hot_games'"
        class="py-20 relative"
        :class="isLightMode ? 'bg-[#f6f7fb]' : 'bg-slate-950'"
      >
      <div class="container mx-auto px-4 relative">
        <div class="text-center mb-12">
          <div class="inline-flex items-center justify-center gap-3 mb-3 px-5 py-2 rounded-full bg-white border border-slate-200 shadow-sm">
            <span class="text-3xl">
              {{ getSectionConfig('hot_games', 'icon', '🔥') }}
            </span>
            <h2 class="text-3xl md:text-4xl font-black text-slate-900">
              <span>{{ getSectionConfig('hot_games', 'title', $t('hotGames')) }}</span>
            </h2>
            <svg class="w-6 h-6 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <p class="text-base md:text-lg text-slate-500 max-w-2xl mx-auto">
            {{ getSectionConfig('hot_games', 'subtitle', $t('mostPopularGamesRecharge')) }}
          </p>
          <p class="mt-3 text-cyan-500 text-lg">
            {{ $t('gamesFound') }}:
            <span class="text-green-500 font-extrabold text-xl">{{ hotGames.length }}</span>
            {{ $t('gamesUnit') }}
          </p>
        </div>

        <div :class="hotGamesContainerClass">
          <RouterLink
            v-for="(game, hotIndex) in hotGames"
            :key="game.id"
            :to="`/games/${game.slug || game.id}`"
            class="group block"
            v-tilt="{ max: 4.6, scale: 1.01 }"
            v-motion-reveal="{ delay: Math.min(hotIndex * 65, 260), y: 20 }"
          >
            <div :class="hotGameCardClass">
              <div :class="hotGameThumbClass">
                <img
                  :src="resolveGameImage(game)"
                  :data-fallbacks="getGameImageFallbackData(game)"
                  :alt="game.name"
                  class="w-full h-full object-cover"
                  @error="handleGameImageError"
                />
              </div>

              <div :class="hotGameContentClass">
                <div :class="hotGameHeaderClass">
                  <h3 :class="hotGameTitleClass">
                    {{ game.name }}
                  </h3>
                  <span
                    v-if="showHotGameDiscount && getGameDiscountLabel(game)"
                    class="inline-flex items-center rounded-full bg-rose-50 text-rose-600 px-2.5 py-1 text-xs font-semibold shrink-0"
                  >
                    {{ getGameDiscountLabel(game) }}
                  </span>
                </div>

                <p :class="hotGameMetaClass">
                  {{ game.categoryName || '国际游戏' }}
                  <span> · </span>
                  {{ game.platform || 'Android / iOS' }}
                </p>

                <div :class="hotGameActionRowClass">
                  <span
                    v-if="showHotGameRating"
                    class="inline-flex items-center rounded-full bg-amber-50 text-amber-600 px-2.5 py-1 text-xs font-semibold"
                  >
                    ⭐ {{ getGameRating(game) }}
                  </span>
                  <span class="inline-flex items-center justify-center px-5 py-2 rounded-full bg-violet-100 text-violet-700 font-bold text-sm group-hover:bg-violet-600 group-hover:text-white transition-all">
                    {{ $t('rechargeNow') || '立即充值' }}
                  </span>
                </div>
              </div>
            </div>
          </RouterLink>
        </div>

        <div v-if="showHotGamesMoreButton" class="text-center mt-10">
          <RouterLink to="/games">
            <button v-magnetic="{ strength: 0.2, max: 13 }" class="px-8 py-3 rounded-full font-bold text-base bg-violet-600 text-white hover:bg-violet-500 transition-colors">
              {{ $t('viewAllGames') }}
            </button>
          </RouterLink>
        </div>
      </div>
    </section>

      <!-- Latest News Section - 最新资讯板块 -->
      <section
        v-else-if="section.sectionKey === 'latest_news'"
        class="py-20 relative"
        :class="isLightMode ? 'bg-white' : 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900'"
      >
      <div class="container mx-auto px-4 relative">
        <div class="text-center mb-16">
          <div class="flex items-center justify-center gap-3 mb-4">
            <!-- 使用后台配置的图标 -->
            <span class="text-4xl drop-shadow-[0_0_10px_rgba(0,255,255,0.8)]">
              {{ getSectionConfig('latest_news', 'icon', '📰') }}
            </span>
            <h2 class="text-4xl md:text-5xl font-black text-white drop-shadow-[0_0_15px_rgba(0,255,255,0.8)]">
              <!-- 使用后台配置的标题 -->
              <span class="text-cyan-400">{{ getSectionConfig('latest_news', 'title', '最新资讯') }}</span>
            </h2>
            <svg class="w-8 h-8 text-pink-500 drop-shadow-[0_0_10px_rgba(236,72,153,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <!-- 使用后台配置的副标题 -->
          <p class="text-xl text-cyan-200 max-w-2xl mx-auto">
            {{ getSectionConfig('latest_news', 'subtitle', '智能推荐 · 热门阅读 · 最新发布') }}
          </p>
        </div>
        
        <!-- 加载中状态 -->
        <div v-if="newsLoading" class="flex justify-center py-12">
          <div class="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-400"></div>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="newsError" class="text-center py-12">
          <p class="text-pink-400 text-xl mb-4">❗ {{ newsError }}</p>
          <button 
            @click="loadRecommendedNews" 
            class="px-6 py-3 rounded-xl bg-cyan-500/20 border border-cyan-400 text-cyan-400 hover:bg-cyan-500/30 transition-all"
          >
            重试
          </button>
        </div>
        
        <!-- 文章列表 -->
        <div v-else-if="recommendedNews.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <RouterLink
            v-for="(article, newsIndex) in recommendedNews"
            :key="article.id"
            :to="`/articles/${article.id}`"
            class="group relative rounded-2xl overflow-hidden border-2 border-cyan-500/50 hover:border-cyan-400 hover:shadow-[0_0_30px_rgba(0,255,255,0.6)] transition-all duration-300"
            v-tilt="{ max: 4, scale: 1.008 }"
            v-motion-reveal="{ delay: Math.min(newsIndex * 60, 260), y: 18 }"
          >
            <div class="relative h-48 overflow-hidden">
              <img 
                v-if="resolveNewsCardImage(article)"
                :src="resolveNewsCardImage(article)"
                :alt="article.title"
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                @error="handleNewsCardImageError"
              />
              <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent"></div>
              
              <!-- 分类徽章 -->
              <div class="absolute top-4 left-4">
                <span class="inline-block px-3 py-1 rounded-full bg-cyan-500/20 border border-cyan-400 text-cyan-300 text-xs font-bold uppercase tracking-wider backdrop-blur-sm">
                  {{ article.category || '资讯' }}
                </span>
              </div>
              
              <!-- 热门标记 -->
              <div v-if="article.readTime" class="absolute top-4 right-4">
                <span class="inline-block px-2 py-1 rounded bg-pink-500/80 text-white text-xs font-bold backdrop-blur-sm">
                  🔥 {{ article.readTime }}
                </span>
              </div>
            </div>
            
            <div class="relative p-6 bg-slate-900/90 backdrop-blur-sm">
              <h3 class="text-lg font-bold text-cyan-300 mb-2 group-hover:text-cyan-400 transition-colors drop-shadow-[0_0_8px_rgba(0,255,255,0.6)] line-clamp-2">
                {{ article.title }}
              </h3>
              <p class="text-cyan-100/80 text-sm mb-4 line-clamp-2">{{ article.excerpt }}</p>
              <div class="flex items-center justify-between text-xs text-cyan-400">
                <span>👤 {{ article.author }}</span>
                <span>📅 {{ article.date }}</span>
              </div>
            </div>
          </RouterLink>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="text-center py-12">
          <p class="text-cyan-400 text-xl">暂无推荐资讯</p>
        </div>
        
        <!-- 查看更多按钮 -->
        <div v-if="recommendedNews.length > 0" class="text-center mt-12">
          <RouterLink to="/articles">
            <button v-magnetic="{ strength: 0.2, max: 12 }" class="px-8 py-4 rounded-xl font-bold text-lg tracking-wide uppercase border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-500 hover:text-black hover:shadow-[0_0_25px_rgba(0,255,255,0.8)] transition-all duration-300">
              查看更多资讯
            </button>
          </RouterLink>
        </div>
      </div>
    </section>

      <!-- Categories Section -->
      <section
        v-else-if="section.sectionKey === 'categories'"
        class="py-20 relative"
        :class="isLightMode ? 'bg-white' : 'bg-slate-900'"
      >
      <div class="container mx-auto px-4 relative">
        <div class="text-center mb-16">
          <div class="flex items-center justify-center gap-3 mb-4">
            <!-- 使用后台配置的图标 -->
            <span class="text-4xl drop-shadow-[0_0_10px_rgba(168,85,247,0.8)]">
              {{ getSectionConfig('categories', 'icon', '🎮') }}
            </span>
            <!-- 使用后台配置的标题 -->
            <h2 class="text-4xl md:text-5xl font-black text-white drop-shadow-[0_0_15px_rgba(168,85,247,0.8)]">
              <span class="text-purple-400">{{ getSectionConfig('categories', 'title', $t('games') + ' ' + $t('categories')) }}</span>
            </h2>
            <svg class="w-8 h-8 text-cyan-500 drop-shadow-[0_0_10px_rgba(0,255,255,0.8)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <!-- 使用后台配置的副标题 -->
          <p class="text-xl text-purple-200 max-w-2xl mx-auto">
            {{ getSectionConfig('categories', 'subtitle', $t('browseByCategory')) }}
          </p>
        </div>
        
        <div :class="categoriesContainerClass">
          <RouterLink
            v-for="(category, categoryIndex) in homepageCategories"
            :key="category.id"
            :to="`/games?category=${category.id}`"
            :class="categoriesCardClass"
            v-tilt="{ max: 3.8, scale: 1.006 }"
            v-motion-reveal="{ delay: Math.min(categoryIndex * 45, 180), y: 16 }"
          >
            <span
              v-if="showHotCategoryBadge && isHotCategory(category)"
              class="absolute top-3 right-3 rounded-full bg-rose-100 text-rose-600 text-[11px] font-bold px-2 py-0.5"
            >
              HOT
            </span>

            <div :class="categoriesCardInnerClass">
              <div v-if="showCategoryIcon" :class="categoriesIconClass">{{ category.icon }}</div>
              <div :class="categoriesTextWrapClass">
                <h3 :class="categoriesTitleClass">{{ category.name }}</h3>
                <div v-if="showCategoryGameCount" :class="categoriesCountClass">
                  {{ category.gamesCount || 0 }} {{ $t('gamesCount') }}
                </div>
              </div>
            </div>
          </RouterLink>
        </div>

        <div v-if="showCategoriesMoreButton" class="text-center mt-10">
          <RouterLink to="/games">
            <button v-magnetic="{ strength: 0.2, max: 12 }" class="px-8 py-3 rounded-full font-bold text-base border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors">
              {{ $t('viewAllGames') }}
            </button>
          </RouterLink>
        </div>
      </div>
      </section>
    </div> <!-- 关闭 v-for sortedEnabledSections -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, type CSSProperties } from 'vue'
import { useTitle } from '@vueuse/core'
import { useI18n } from '../composables/useI18n'
import { getBanners } from '../api/banners'
import { getHomeLayouts, type LayoutSection } from '../api/layouts'
import { getSmartRecommendedArticles } from '../api/articles'
import { getGameCategories, getGames, getHotGames } from '../api/games'
import axios from 'axios'
import { useThemeStore } from '../stores/theme'
import { MOTION_MODE_CHANGE_EVENT, getCurrentMotionMode } from '../utils/motionMode'

// 使用增强的 i18n composable（混合自定义 + vue-i18n）
const { t, locale } = useI18n()
const themeStore = useThemeStore()
const isLightMode = computed(() => themeStore.theme === 'light')

interface AmbientParticle {
  id: number
  x: number
  y: number
  size: number
  duration: number
  delay: number
  drift: number
}

const seeded = (seed: number) => {
  const x = Math.sin(seed * 127.13) * 43758.5453
  return x - Math.floor(x)
}

const buildAmbientParticles = (count: number): AmbientParticle[] =>
  Array.from({ length: count }, (_, index) => {
    const seed = index + 1
    return {
      id: seed,
      x: Math.round(8 + seeded(seed * 2.1) * 84),
      y: Math.round(6 + seeded(seed * 3.7) * 88),
      size: Math.round(7 + seeded(seed * 5.9) * 15),
      duration: Number((10 + seeded(seed * 7.3) * 9).toFixed(2)),
      delay: Number((seeded(seed * 8.1) * 8).toFixed(2)),
      drift: Number((14 + seeded(seed * 11.4) * 26).toFixed(2)),
    }
  })

const motionMode = ref<'standard' | 'lite' | 'reduced'>(getCurrentMotionMode())
const ambientParticles = ref<AmbientParticle[]>(buildAmbientParticles(motionMode.value === 'lite' ? 8 : 14))

const showAmbientLayer = ref(true)
const enableAmbientPointer = ref(false)
const ambientPointerX = ref(0.5)
const ambientPointerY = ref(0.5)
let ambientPointerRaf: number | null = null
let reducedMotionQuery: MediaQueryList | null = null
let finePointerQuery: MediaQueryList | null = null
const addMediaQueryListener = (query: MediaQueryList, listener: () => void) => {
  if (typeof query.addEventListener === 'function') {
    query.addEventListener('change', listener)
    return
  }
  query.addListener(listener)
}
const removeMediaQueryListener = (query: MediaQueryList, listener: () => void) => {
  if (typeof query.removeEventListener === 'function') {
    query.removeEventListener('change', listener)
    return
  }
  query.removeListener(listener)
}

const ambientLayerStyle = computed<CSSProperties>(() => ({
  '--ambient-offset-x': `${((ambientPointerX.value - 0.5) * (motionMode.value === 'lite' ? 12 : 22)).toFixed(2)}px`,
  '--ambient-offset-y': `${((ambientPointerY.value - 0.5) * (motionMode.value === 'lite' ? 9 : 18)).toFixed(2)}px`,
}))

const getAmbientParticleStyle = (particle: AmbientParticle): CSSProperties => ({
  left: `${particle.x}%`,
  top: `${particle.y}%`,
  width: `${particle.size}px`,
  height: `${particle.size}px`,
  '--duration': `${particle.duration}s`,
  '--drift': `${particle.drift}px`,
  animationDelay: `-${particle.delay}s`,
})

const handleAmbientPointerMove = (event: MouseEvent) => {
  if (!enableAmbientPointer.value) return
  if (ambientPointerRaf !== null) return

  ambientPointerRaf = window.requestAnimationFrame(() => {
    ambientPointerX.value = event.clientX / window.innerWidth
    ambientPointerY.value = event.clientY / window.innerHeight
    ambientPointerRaf = null
  })
}

const syncMotionPreferences = () => {
  motionMode.value = getCurrentMotionMode()

  const reducedMotion = reducedMotionQuery?.matches || motionMode.value === 'reduced'
  showAmbientLayer.value = !reducedMotion

  const supportsFinePointer = Boolean(finePointerQuery?.matches)
  const nextEnableAmbientPointer = showAmbientLayer.value && supportsFinePointer && motionMode.value !== 'lite'

  if (nextEnableAmbientPointer && !enableAmbientPointer.value) {
    window.addEventListener('mousemove', handleAmbientPointerMove, { passive: true })
  } else if (!nextEnableAmbientPointer && enableAmbientPointer.value) {
    window.removeEventListener('mousemove', handleAmbientPointerMove)
  }
  enableAmbientPointer.value = nextEnableAmbientPointer

  ambientParticles.value = buildAmbientParticles(motionMode.value === 'lite' ? 8 : 14)
}

// 首页布局配置
const homeLayouts = ref<LayoutSection[]>([])
const layoutMap = ref<Record<string, LayoutSection>>({})
const layoutLoading = ref(true)

// 可视化编辑器状态
const isEditMode = ref(false)
const selectedSectionKey = ref<string | null>(null)
const isHovering = ref<string | null>(null)

// 浏览器标题 SEO 联动
const pageTitle = useTitle('Cypher Game Buy | 游戏充值')

// 监听选中板块的 SEO 标题变化
watch(() => selectedSectionKey.value, (newKey) => {
  if (isEditMode.value && newKey && layoutMap.value[newKey]) {
    const seoTitle = layoutMap.value[newKey].config?.seo_title
    if (seoTitle) {
      pageTitle.value = `[预览] ${seoTitle}`
    }
  }
}, { immediate: true })

// 监听配置实时更新
watch(() => layoutMap.value, (newMap) => {
  if (isEditMode.value && selectedSectionKey.value) {
    const seoTitle = newMap[selectedSectionKey.value]?.config?.seo_title
    if (seoTitle) {
      pageTitle.value = `[预览] ${seoTitle}`
    }
  }
}, { deep: true })

// 加载首页布局配置
const loadLayouts = async () => {
  try {
    const layouts = await getHomeLayouts()
    homeLayouts.value = layouts
    // 创建快速查找映射
    layoutMap.value = layouts.reduce((map, layout) => {
      map[layout.sectionKey] = layout
      return map
    }, {} as Record<string, LayoutSection>)
    console.log('成功加载首页布局:', layouts.length, '个板块')
    
    // 检查是否在编辑器环境中（通过 URL 参数）
    if (window.location.search.includes('edit_mode=true')) {
      isEditMode.value = true
      console.log('编辑器模式已启用')
    }
    
    // 布局加载完成后，加载资讯数据（需要读取配置）
    loadRecommendedNews()
  } catch (err) {
    console.error('加载首页布局失败:', err)
    // 使用默认配置
    homeLayouts.value = []
  } finally {
    layoutLoading.value = false
  }
}

// 检查板块是否启用
const isSectionEnabled = (sectionKey: string): boolean => {
  return layoutMap.value[sectionKey]?.isEnabled ?? true // 默认启用
}

// 获取板块配置
const getSectionConfig = (sectionKey: string, configKey: string, defaultValue: any = null): any => {
  return layoutMap.value[sectionKey]?.config?.[configKey] ?? defaultValue
}

// 获取排序后的启用板块列表
const sortedEnabledSections = computed(() => {
  return homeLayouts.value
    .filter(layout => layout.isEnabled)
    .sort((a, b) => a.sortOrder - b.sortOrder)
})

const parseBooleanConfig = (sectionKey: string, configKey: string, defaultValue: boolean) => {
  const rawValue = getSectionConfig(sectionKey, configKey, defaultValue)
  if (typeof rawValue === 'boolean') return rawValue
  if (typeof rawValue === 'number') return rawValue !== 0
  if (typeof rawValue === 'string') {
    const normalized = rawValue.trim().toLowerCase()
    if (['1', 'true', 'yes', 'on'].includes(normalized)) return true
    if (['0', 'false', 'no', 'off'].includes(normalized)) return false
  }
  return defaultValue
}

const parseNumberConfig = (sectionKey: string, configKey: string, defaultValue: number) => {
  const rawValue = Number(getSectionConfig(sectionKey, configKey, defaultValue))
  return Number.isFinite(rawValue) ? rawValue : defaultValue
}

const hotGamesLayout = computed<'grid' | 'list'>(() => {
  const rawLayout = String(getSectionConfig('hot_games', 'layout', 'grid') || '')
    .trim()
    .toLowerCase()
  return rawLayout === 'list' ? 'list' : 'grid'
})

const showHotGameRating = computed(() => parseBooleanConfig('hot_games', 'show_game_rating', true))
const showHotGameDiscount = computed(() => parseBooleanConfig('hot_games', 'show_discount', true))
const showHotGamesMoreButton = computed(() => parseBooleanConfig('hot_games', 'show_more_button', true))

const hotGamesContainerClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'space-y-4'
    : 'grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6'
)

const hotGameCardClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'rounded-2xl border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-all duration-300 flex items-center gap-4'
    : 'rounded-2xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 text-center h-full'
)

const hotGameThumbClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'w-16 h-16 rounded-2xl overflow-hidden bg-slate-100 shadow shrink-0'
    : 'w-24 h-24 mx-auto mb-4 rounded-3xl overflow-hidden bg-slate-100 shadow'
)

const hotGameContentClass = computed(() =>
  hotGamesLayout.value === 'list' ? 'flex-1 min-w-0 text-left' : ''
)

const hotGameHeaderClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'flex items-start justify-between gap-3'
    : 'flex items-center justify-center gap-2 mb-1'
)

const hotGameTitleClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'text-lg font-black text-slate-900 line-clamp-1 group-hover:text-violet-700 transition-colors'
    : 'text-2xl font-black text-slate-900 mb-2 line-clamp-1 group-hover:text-violet-700 transition-colors'
)

const hotGameMetaClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'text-slate-500 text-sm mt-1 line-clamp-1'
    : 'text-slate-500 text-sm mb-5 line-clamp-1'
)

const hotGameActionRowClass = computed(() =>
  hotGamesLayout.value === 'list'
    ? 'mt-3 flex items-center justify-between gap-3'
    : 'mt-1 flex items-center justify-center gap-3'
)

const getGameDiscountLabel = (game: any): string => {
  const textCandidates = [game?.discount_label, game?.discountText, game?.promo_text, game?.promotion]
  for (const candidate of textCandidates) {
    const value = String(candidate || '').trim()
    if (value) return value
  }

  const numericDiscount = Number(game?.discount ?? game?.discount_percent)
  if (Number.isFinite(numericDiscount) && numericDiscount > 0) {
    return `-${Math.round(numericDiscount)}%`
  }

  return ''
}

const getGameRating = (game: any): string => {
  const explicitRating = Number(game?.rating ?? game?.score ?? game?.stars)
  if (Number.isFinite(explicitRating) && explicitRating > 0) {
    return explicitRating.toFixed(1)
  }

  const viewCount = Number(game?.view_count || 0)
  if (Number.isFinite(viewCount) && viewCount > 0) {
    const derivedRating = Math.min(5, 4.2 + Math.log10(viewCount + 1) * 0.2)
    return derivedRating.toFixed(1)
  }

  return game?.is_hot ? '4.9' : '4.8'
}

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

const getGameImageCandidates = (game: any): string[] => {
  const unique = new Set<string>()
  const candidates = [game?.icon_image_url, game?.icon_external_url, game?.image, game?.banner_image_url]

  for (const candidate of candidates) {
    const value = normalizeImageUrl(candidate)
    if (value) unique.add(value)
  }

  return Array.from(unique)
}

const getGameImageFallbackData = (game: any): string => {
  const candidates = getGameImageCandidates(game)
  return JSON.stringify(candidates.slice(1))
}

const resolveGameImage = (game: any): string => {
  const candidates = getGameImageCandidates(game)
  return candidates[0] || ''
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
  img.style.display = 'none'
  img.onerror = null
}

const resolveNewsCardImage = (article: any): string => {
  const cover = normalizeImageUrl(article?.cover_image)
  const image = normalizeImageUrl(article?.image)
  return cover || image
}

const handleNewsCardImageError = (event: Event) => {
  const img = event.target as HTMLImageElement | null
  if (!img) return
  img.style.display = 'none'
  img.onerror = null
}

const categoriesLayoutStyle = computed<'card' | 'icon' | 'list' | 'grid'>(() => {
  const rawStyle = String(getSectionConfig('categories', 'layout_style', 'card') || '')
    .trim()
    .toLowerCase()
  if (rawStyle === 'icon' || rawStyle === 'list' || rawStyle === 'grid') return rawStyle
  return 'card'
})

const categoriesColumns = computed(() => {
  const rawColumns = Math.round(parseNumberConfig('categories', 'columns', 4))
  return Math.min(6, Math.max(3, rawColumns))
})

const categoriesGridColumnsClass = computed(() => {
  if (categoriesColumns.value === 3) return 'grid-cols-2 md:grid-cols-3'
  if (categoriesColumns.value === 5) return 'grid-cols-2 md:grid-cols-3 xl:grid-cols-5'
  if (categoriesColumns.value >= 6) return 'grid-cols-2 md:grid-cols-3 xl:grid-cols-6'
  return 'grid-cols-2 md:grid-cols-4'
})

const showCategoryIcon = computed(() => parseBooleanConfig('categories', 'show_category_icon', true))
const showCategoryGameCount = computed(() => parseBooleanConfig('categories', 'show_game_count', true))
const showHotCategoryBadge = computed(() => parseBooleanConfig('categories', 'show_hot_badge', true))
const showAllCategory = computed(() => parseBooleanConfig('categories', 'show_all_category', true))
const showCategoriesMoreButton = computed(() => parseBooleanConfig('categories', 'show_more_button', false))
const enableCategoryHoverEffect = computed(() => parseBooleanConfig('categories', 'enable_hover_effect', true))

const categoriesDisplayCount = computed(() => {
  const rawDisplayCount = Math.round(parseNumberConfig('categories', 'display_count', 8))
  return Math.max(1, rawDisplayCount)
})

const homepageCategories = computed(() => {
  const items = [...gameCategories.value]
  const filtered = showAllCategory.value
    ? items
    : items.filter((category) => String(category.id) !== 'all' && String(category.code || '') !== 'all')
  return filtered.slice(0, categoriesDisplayCount.value)
})

const categoriesContainerClass = computed(() => {
  if (categoriesLayoutStyle.value === 'list') {
    return 'grid grid-cols-1 md:grid-cols-2 gap-4'
  }
  return `grid ${categoriesGridColumnsClass.value} gap-6`
})

const categoriesCardClass = computed(() => {
  const hoverClass = enableCategoryHoverEffect.value
    ? 'hover:-translate-y-1 hover:shadow-md hover:border-violet-300'
    : ''

  if (categoriesLayoutStyle.value === 'list') {
    return `group relative p-4 rounded-xl bg-white border border-slate-200 transition-all duration-300 ${hoverClass}`
  }
  if (categoriesLayoutStyle.value === 'icon') {
    return `group relative p-6 rounded-2xl bg-white border border-slate-200 transition-all duration-300 text-center ${hoverClass}`
  }
  if (categoriesLayoutStyle.value === 'grid') {
    return `group relative p-4 rounded-xl bg-white border border-slate-200 transition-all duration-300 text-center ${hoverClass}`
  }
  return `group relative p-6 rounded-2xl bg-white border border-slate-200 transition-all duration-300 text-center ${hoverClass}`
})

const categoriesCardInnerClass = computed(() =>
  categoriesLayoutStyle.value === 'list' ? 'flex items-center gap-3' : 'relative'
)

const categoriesIconClass = computed(() => {
  if (categoriesLayoutStyle.value === 'list') return 'text-3xl shrink-0'
  if (categoriesLayoutStyle.value === 'icon') return 'text-6xl mb-3'
  if (categoriesLayoutStyle.value === 'grid') return 'text-4xl mb-2'
  return 'text-5xl mb-3'
})

const categoriesTextWrapClass = computed(() =>
  categoriesLayoutStyle.value === 'list' ? 'text-left min-w-0' : 'text-center'
)

const categoriesTitleClass = computed(() =>
  categoriesLayoutStyle.value === 'list'
    ? 'text-base font-bold text-slate-800 line-clamp-1'
    : 'text-lg font-bold text-slate-800 mb-1 line-clamp-1'
)

const categoriesCountClass = computed(() =>
  categoriesLayoutStyle.value === 'list'
    ? 'text-sm text-slate-500'
    : 'text-sm text-slate-500'
)

const isHotCategory = (category: any) => Number(category?.gamesCount || 0) >= 8

// 轮播图数据 - 从 API 获取
const carouselSlides = ref<any[]>([])
const loading = ref(true)

// 最新资讯数据
const recommendedNews = ref<any[]>([])
const newsLoading = ref(false)
const newsError = ref('')
const hotGamesSource = ref<any[]>([])
const gameCategories = ref<any[]>([])

// 加载轮播图
const loadBanners = async () => {
  try {
    loading.value = true
    const banners = await getBanners()
    // 处理图片 URL
    carouselSlides.value = banners.map(banner => ({
      ...banner,
      image: banner.image || `https://images.unsplash.com/photo-${banner.id}542751371-adc38448a05e?w=1920&h=600&fit=crop`,
      // 如果后台返回的字段名不同，这里进行映射
      primaryButton: banner.primaryButton || t('startRechargeNow'),
      secondaryButton: banner.secondaryButton || t('viewDetails'),
    }))
    console.log('成功加载轮播图:', banners.length)
  } catch (err) {
    console.error('加载轮播图失败:', err)
    // 如果 API 失败，使用默认数据
    carouselSlides.value = getDefaultSlides()
  } finally {
    loading.value = false
  }
}

// 加载热门游戏（优先走热门专用接口，确保与后台热门开关联动）
const loadHotGames = async () => {
  try {
    const hotGames = await getHotGames()
    hotGamesSource.value = hotGames.length > 0 ? hotGames : await getGames()
    console.log('成功加载热门游戏:', hotGamesSource.value.length)
  } catch (err) {
    console.error('加载热门游戏失败:', err)
    hotGamesSource.value = []
  }
}

// 加载首页分类（从后端分类接口同步）
const loadHomepageGameCategories = async () => {
  try {
    const categories = await getGameCategories()
    gameCategories.value = categories
    console.log('成功加载首页游戏分类:', categories.length)
  } catch (err) {
    console.error('加载首页游戏分类失败:', err)
    gameCategories.value = [
      { id: 'all', name: '全部游戏', icon: '🎮', gamesCount: 0 },
    ]
  }
}

// 加载推荐资讯
const loadRecommendedNews = async () => {
  try {
    newsLoading.value = true
    newsError.value = ''
    // 从后台配置读取显示数量，默认为6篇
    const displayCount = getSectionConfig('latest_news', 'display_count', 6)
    // 调用智能推荐API，获取配置数量的推荐文章
    const articles = await getSmartRecommendedArticles(displayCount)
    // 格式化数据以匹配模板需求
    recommendedNews.value = articles.map((article: any) => ({
      id: article.id,
      title: article.title,
      excerpt: article.excerpt || article.summary || article.content?.substring(0, 100) || '暂无摘要',
      author: article.author_name || article.author || '游戏充值网',
      date: new Date(article.published_at || article.created_at).toLocaleDateString('zh-CN'),
      category: article.category?.name || article.category || '资讯',
      cover_image: normalizeImageUrl(article.cover_image),
      image: normalizeImageUrl(article.image || article.cover_image),
      readTime: article.view_count ? `${article.view_count}次阅读` : null
    }))
    console.log('成功加载推荐资讯:', articles.length, '篇（配置数量:', displayCount, '）')
  } catch (err) {
    console.error('加载推荐资讯失败:', err)
    newsError.value = '加载资讯失败，请稍后再试'
  } finally {
    newsLoading.value = false
  }
}

// 默认轮播图数据（API 失败时使用）
const getDefaultSlides = () => [
  {
    id: 1,
    title: t('carouselTitle1'),
    description: t('carouselDesc1'),
    badge: t('carouselBadgeHotSale'),
    image: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1920&h=600&fit=crop',
    primaryButton: t('startRechargeNow'),
    secondaryButton: t('viewDetails'),
    primaryLink: '/recharge',
    secondaryLink: '/games/1'
  },
  {
    id: 2,
    title: t('carouselTitle2'),
    description: t('carouselDesc2'),
    badge: t('carouselBadgeNewArrival'),
    image: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1920&h=600&fit=crop',
    primaryButton: t('startNow'),
    secondaryButton: t('learnMore'),
    primaryLink: '/recharge',
    secondaryLink: '/games/3'
  },
  {
    id: 3,
    title: t('carouselTitle3'),
    description: t('carouselDesc3'),
    badge: t('carouselBadgeBestSeller'),
    image: 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=1920&h=600&fit=crop',
    primaryButton: t('grabNow'),
    secondaryButton: t('browseMore'),
    primaryLink: '/recharge',
    secondaryLink: '/games/2'
  },
  {
    id: 4,
    title: t('carouselTitle4'),
    description: t('carouselDesc4'),
    badge: t('carouselBadgeSpecialOffer'),
    image: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=1920&h=600&fit=crop',
    primaryButton: t('immediateRecharge'),
    secondaryButton: t('viewActivity'),
    primaryLink: '/recharge',
    secondaryLink: '/games/4'
  }
]

const currentSlide = ref(0)
let autoPlayInterval: number | null = null
const heroParallaxOffset = ref(0)
let heroParallaxRaf: number | null = null

const updateHeroParallax = () => {
  const scrollY = window.scrollY || window.pageYOffset || 0
  if (motionMode.value === 'lite') {
    heroParallaxOffset.value = Math.min(34, scrollY * 0.07)
    return
  }
  heroParallaxOffset.value = Math.min(56, scrollY * 0.12)
}

const handleWindowScroll = () => {
  if (heroParallaxRaf !== null) return
  heroParallaxRaf = window.requestAnimationFrame(() => {
    updateHeroParallax()
    heroParallaxRaf = null
  })
}

// 计算每个轮播项相对于当前项的位置
const getSlidePosition = (index: number) => {
  const total = carouselSlides.value.length
  const diff = (index - currentSlide.value + total) % total
  
  if (diff === 0) return 'center' // 当前项
  if (diff === 1) return 'right' // 右侧
  if (diff === total - 1) return 'left' // 左侧
  return 'hidden' // 隐藏
}

// 获取轮播项的类名
const getSlideClasses = (index: number) => {
  const position = getSlidePosition(index)
  return [
    'carousel-slide absolute rounded-2xl overflow-hidden shadow-2xl',
    `carousel-slide--${position}`
  ]
}

// Carousel functions
const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % carouselSlides.value.length
}

const prevSlide = () => {
  currentSlide.value = currentSlide.value === 0 
    ? carouselSlides.value.length - 1 
    : currentSlide.value - 1
}

const goToSlide = (index: number) => {
  currentSlide.value = index
}

const getBannerImageStyle = (index: number) => {
  const active = currentSlide.value === index
  const offset = active ? heroParallaxOffset.value : heroParallaxOffset.value * 0.45
  const scale = motionMode.value === 'lite'
    ? (active ? 1.03 : 1.02)
    : (active ? 1.06 : 1.035)
  return {
    transform: `translate3d(0, ${offset}px, 0) scale(${scale})`,
  }
}

// Auto play
const startAutoPlay = () => {
  autoPlayInterval = window.setInterval(() => {
    nextSlide()
  }, 5000) // Change slide every 5 seconds
}

const stopAutoPlay = () => {
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval)
    autoPlayInterval = null
  }
}

// 处理板块点击（编辑器模式）
const handleSectionClick = (section: LayoutSection) => {
  if (!isEditMode.value) return
  
  selectedSectionKey.value = section.sectionKey
  console.log('选中板块:', section.sectionName, section.config)
  
  // 发送消息给父窗口，确保数据是纯对象而不是 Proxy
  if (window.parent) {
    const sectionData = JSON.parse(JSON.stringify({
      id: section.id,
      name: section.sectionName,
      key: section.sectionKey,
      originalKey: (section as any).section_key || section.sectionKey,
      config: section.config || {}
    }))
    
    window.parent.postMessage({
      type: 'SECTION_SELECTED',
      section: sectionData
    }, '*')
  }
}

// 移动板块
const moveSection = (section: LayoutSection, direction: 'up' | 'down') => {
  const index = homeLayouts.value.findIndex(l => l.sectionKey === section.sectionKey)
  if (index === -1) return
  
  const newLayouts = [...homeLayouts.value]
  if (direction === 'up' && index > 0) {
    [newLayouts[index], newLayouts[index-1]] = [newLayouts[index-1], newLayouts[index]]
  } else if (direction === 'down' && index < newLayouts.length - 1) {
    [newLayouts[index], newLayouts[index+1]] = [newLayouts[index+1], newLayouts[index]]
  }
  
  // 重新计算所有 sortOrder
  newLayouts.forEach((l, i) => l.sortOrder = i)
  homeLayouts.value = newLayouts
  
  // 通知父级更新排序列表
  if (window.parent) {
    window.parent.postMessage({
      type: 'LAYOUT_ORDER_CHANGED',
      order: newLayouts.map(l => ({ sectionKey: l.sectionKey, sortOrder: l.sortOrder }))
    }, '*')
  }
}

// 删除板块
const deleteSection = (section: LayoutSection) => {
  if (!confirm(`确定要移除“${section.sectionName}”板块吗？`)) return
  homeLayouts.value = homeLayouts.value.filter(l => l.sectionKey !== section.sectionKey)
  if (selectedSectionKey.value === section.sectionKey) selectedSectionKey.value = null
  
  if (window.parent) {
    window.parent.postMessage({
      type: 'SECTION_DELETED',
      sectionKey: section.sectionKey
    }, '*')
  }
}

// 复制板块 (仅预览)
const copySection = (section: LayoutSection) => {
  const newSection = JSON.parse(JSON.stringify(section))
  newSection.sectionKey = `${section.sectionKey}_copy_${Date.now()}`
  newSection.sectionName = `${section.sectionName} (副本)`
  homeLayouts.value.push(newSection)
}

// 处理内联文字编辑
const handleInlineEdit = (event: FocusEvent, sectionKey: string, configKey: string) => {
  if (!isEditMode.value) return
  const newText = (event.target as HTMLElement).innerText
  
  // 更新本地数据
  if (layoutMap.value[sectionKey]) {
    layoutMap.value[sectionKey].config[configKey] = newText
  }
  
  // 通知父窗口更新右侧面板输入框
  if (window.parent) {
    window.parent.postMessage({
      type: 'CONFIG_UPDATE_FROM_INLINE',
      sectionKey: sectionKey,
      config: { [configKey]: newText }
    }, '*')
  }
}

// 处理图片点击编辑
const handleImageClick = (event: MouseEvent, sectionKey: string, configKey: string) => {
  if (!isEditMode.value) return
  event.preventDefault()
  event.stopPropagation()
  
  const currentUrl = (event.target as HTMLImageElement).src
  const newUrl = window.prompt('请输入新的图片 URL (或者稍后在右侧面板上传):', currentUrl)
  
  if (newUrl && newUrl !== currentUrl) {
    // 更新本地数据
    if (layoutMap.value[sectionKey]) {
      layoutMap.value[sectionKey].config[configKey] = newUrl
    }
    
    // 通知父窗口
    if (window.parent) {
      window.parent.postMessage({
        type: 'CONFIG_UPDATE_FROM_INLINE',
        sectionKey: sectionKey,
        config: { [configKey]: newUrl }
      }, '*')
    }
  }
}

// 处理来自父窗口（Django Admin）的可视化布局消息
const handleMessage = (event: MessageEvent) => {
  const { data } = event
  
  if (data.type === 'LAYOUT_UPDATE' && data.order) {
    console.log('收到布局更新预览消息:', data.order)
    const newLayouts = [...homeLayouts.value]
    data.order.forEach((item: any) => {
      const layout = newLayouts.find(l => l.sectionKey === item.sectionKey)
      if (layout) {
        layout.sortOrder = item.sortOrder
        layout.isEnabled = item.isEnabled
      }
    })
    homeLayouts.value = newLayouts
  } 
  else if (data.type === 'CONFIG_UPDATE' && data.sectionKey && data.config) {
    console.log('收到组件配置更新预览:', data.sectionKey, data.config)
    // 实时更新本地映射中的配置
    if (layoutMap.value[data.sectionKey]) {
      layoutMap.value[data.sectionKey].config = {
        ...layoutMap.value[data.sectionKey].config,
        ...data.config
      }
    }
  }
  else if (data.type === 'GLOBAL_STYLE_UPDATE' && data.variable && data.value) {
    console.log('收到全局样式更新:', data.variable, data.value)
    document.documentElement.style.setProperty(data.variable, data.value)
  }
  else if (data.type === 'SELECT_SECTION_BY_KEY' && data.sectionKey) {
    const section = homeLayouts.value.find(l => l.sectionKey === data.sectionKey)
    if (section) {
      handleSectionClick(section)
      // 滚动到对应位置
      const el = document.querySelector(`[data-section-key="${data.sectionKey}"]`)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}

// 加载全局配置
const loadGlobalConfig = async () => {
  try {
    const response = await axios.get('/api/site-config/')
    const payload = response.data

    if (payload && typeof payload === 'object' && payload.themeConfig) {
      themeStore.applyThemeConfig(payload.themeConfig)
    }

    if (Array.isArray(payload) && payload.length > 0 && payload[0]?.config) {
      Object.entries(payload[0].config).forEach(([key, value]) => {
        document.documentElement.style.setProperty(key, String(value))
      })
      return
    }

    if (payload && typeof payload === 'object') {
      if (payload.primaryColor) {
        document.documentElement.style.setProperty('--primary-color', payload.primaryColor)
      }
      if (payload.secondaryColor) {
        document.documentElement.style.setProperty('--secondary-color', payload.secondaryColor)
      }
    }
  } catch (err) {
    console.error('加载全局配置失败:', err)
  }
}

onMounted(() => {
  reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  finePointerQuery = window.matchMedia('(hover: hover) and (pointer: fine)')
  addMediaQueryListener(reducedMotionQuery, syncMotionPreferences)
  addMediaQueryListener(finePointerQuery, syncMotionPreferences)
  window.addEventListener(MOTION_MODE_CHANGE_EVENT, syncMotionPreferences)
  syncMotionPreferences()

  updateHeroParallax()
  loadGlobalConfig()
  loadLayouts()  // 加载布局配置
  loadBanners()  // 加载轮播图
  loadHotGames()
  loadHomepageGameCategories()
  startAutoPlay()
  window.addEventListener('scroll', handleWindowScroll, { passive: true })
  window.addEventListener('message', handleMessage)
})

onUnmounted(() => {
  stopAutoPlay()
  window.removeEventListener('mousemove', handleAmbientPointerMove)
  window.removeEventListener(MOTION_MODE_CHANGE_EVENT, syncMotionPreferences)
  if (reducedMotionQuery) removeMediaQueryListener(reducedMotionQuery, syncMotionPreferences)
  if (finePointerQuery) removeMediaQueryListener(finePointerQuery, syncMotionPreferences)
  window.removeEventListener('scroll', handleWindowScroll)
  window.removeEventListener('message', handleMessage)
  if (heroParallaxRaf !== null) {
    window.cancelAnimationFrame(heroParallaxRaf)
    heroParallaxRaf = null
  }
  if (ambientPointerRaf !== null) {
    window.cancelAnimationFrame(ambientPointerRaf)
    ambientPointerRaf = null
  }
})

// 热门游戏 - 根据后台配置的数量显示
const hotGames = computed(() => {
  const rawCount = Number(getSectionConfig('hot_games', 'display_count', 8))
  const displayCount = Number.isFinite(rawCount) && rawCount > 0 ? rawCount : 8
  return hotGamesSource.value.slice(0, displayCount)
})
</script>

<style scoped>
/* Carousel slide base styles */
.carousel-slide {
  transition: all 700ms cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity, width, height;
}

.carousel-content {
  animation: carousel-content-in 520ms cubic-bezier(0.22, 1, 0.36, 1);
}

.carousel-content :deep(h1) {
  animation: carousel-content-in 560ms cubic-bezier(0.22, 1, 0.36, 1);
}

.carousel-content :deep(p) {
  animation: carousel-content-in 620ms cubic-bezier(0.22, 1, 0.36, 1);
}

.banner-parallax-image {
  transition: transform 720ms cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}

@keyframes carousel-content-in {
  0% {
    opacity: 0;
    transform: translateY(14px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Center slide (current) */
.carousel-slide--center {
  transform: translateX(-50%) scale(1);
  left: 50%;
  top: 0;
  width: 85%;
  height: 100%;
  z-index: 30;
  opacity: 1;
}

/* Left side slide */
.carousel-slide--left {
  transform: translateY(-50%) scale(0.85);
  left: 5%;
  top: 50%;
  width: 40%;
  height: 85%;
  z-index: 10;
  opacity: 0.4;
}

/* Right side slide */
.carousel-slide--right {
  transform: translateY(-50%) scale(0.85);
  right: 5%;
  left: auto;
  top: 50%;
  width: 40%;
  height: 85%;
  z-index: 10;
  opacity: 0.4;
}

/* Hidden slide */
.carousel-slide--hidden {
  transform: translateX(-50%) scale(0.8);
  left: 50%;
  top: 0;
  width: 85%;
  height: 100%;
  z-index: 0;
  opacity: 0;
  pointer-events: none;
}

/* Responsive adjustments for desktop */
@media (min-width: 768px) {
  .carousel-slide--center {
    width: 70%;
  }
  
  .carousel-slide--left,
  .carousel-slide--right {
    width: 35%;
  }
  
  .carousel-slide--hidden {
    width: 70%;
  }
}

/* Carousel indicator animation */
button:focus {
  outline: none;
}

.home-grid-overlay {
  opacity: 0.08;
  background-image:
    linear-gradient(to right, hsl(var(--border) / 0.36) 1px, transparent 1px),
    linear-gradient(to bottom, hsl(var(--border) / 0.36) 1px, transparent 1px);
  background-size: 44px 44px;
}

html.dark .home-grid-overlay {
  opacity: 0.12;
}

.home-ambient-layer {
  z-index: 0;
  overflow: hidden;
  transform: translate3d(var(--ambient-offset-x, 0px), var(--ambient-offset-y, 0px), 0);
  transition: transform 380ms cubic-bezier(0.22, 1, 0.36, 1);
}

.ambient-particle {
  position: absolute;
  border-radius: 999px;
  background:
    radial-gradient(
      circle at 35% 35%,
      color-mix(in srgb, var(--primary-color) 22%, white 78%) 0%,
      color-mix(in srgb, var(--secondary-color) 18%, transparent) 56%,
      transparent 100%
    );
  opacity: 0.2;
  animation: ambient-float var(--duration, 12s) ease-in-out infinite;
  will-change: transform, opacity;
}

@keyframes ambient-float {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(0.92);
    opacity: 0.12;
  }
  50% {
    transform: translate3d(calc(var(--drift, 24px) * -0.5), calc(var(--drift, 24px) * -1), 0) scale(1.05);
    opacity: 0.28;
  }
}

/* 骨架屏占位动画 */
@keyframes skeleton-loading {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}

.skeleton {
  background: linear-gradient(90deg, hsl(var(--muted) / 0.45) 25%, hsl(var(--muted) / 0.7) 50%, hsl(var(--muted) / 0.45) 75%);
  background-size: 400% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.homepage-shell :deep([class*='shadow-[0_0_']) {
  box-shadow: var(--surface-shadow) !important;
}

.homepage-shell :deep([class*='drop-shadow-[0_0_']) {
  filter: none !important;
}

.homepage-shell :deep([class*='bg-slate-900/50']),
.homepage-shell :deep([class*='bg-slate-900/80']),
.homepage-shell :deep([class*='bg-slate-800/50']),
.homepage-shell :deep([class*='bg-slate-800/30']) {
  background-color: hsl(var(--card) / 0.9) !important;
  border-color: hsl(var(--border)) !important;
}

.homepage-shell :deep([class*='bg-gradient-to-r']),
.homepage-shell :deep([class*='bg-gradient-to-l']),
.homepage-shell :deep([class*='bg-gradient-to-t']),
.homepage-shell :deep([class*='bg-gradient-to-b']),
.homepage-shell :deep([class*='bg-gradient-to-br']),
.homepage-shell :deep([class*='bg-gradient-to-tr']),
.homepage-shell :deep([class*='bg-gradient-to-bl']),
.homepage-shell :deep([class*='bg-gradient-to-tl']) {
  background-image: none !important;
}

.homepage-shell :deep([class*='border-cyan-']),
.homepage-shell :deep([class*='border-purple-']),
.homepage-shell :deep([class*='border-pink-']),
.homepage-shell :deep([class*='border-blue-']) {
  border-color: hsl(var(--border)) !important;
}

.homepage-shell :deep([class*='bg-cyan-500/']),
.homepage-shell :deep([class*='bg-purple-500/']),
.homepage-shell :deep([class*='bg-pink-500/']) {
  background-color: hsl(var(--accent) / 0.14) !important;
}

.homepage-shell :deep([class*='text-cyan-']),
.homepage-shell :deep([class*='text-purple-']),
.homepage-shell :deep([class*='text-pink-']),
.homepage-shell :deep(.text-white) {
  color: hsl(var(--foreground)) !important;
}

.homepage-shell :deep(.text-slate-400),
.homepage-shell :deep(.text-slate-500) {
  color: hsl(var(--muted-foreground)) !important;
}

html:not(.dark) .homepage-shell :deep(section) {
  background-color: #ffffff !important;
}

.homepage-shell :deep(button[class*='from-cyan-']),
.homepage-shell :deep(button[class*='to-purple-']),
.homepage-shell :deep(button[class*='to-pink-']) {
  background: hsl(var(--primary)) !important;
  border-color: hsl(var(--primary)) !important;
  color: hsl(var(--primary-foreground)) !important;
  box-shadow: none !important;
}

@media (prefers-reduced-motion: reduce) {
  .home-ambient-layer {
    display: none !important;
  }

  .banner-parallax-image {
    transform: none !important;
  }
}
</style>


