<template>
  <div class="relative min-h-screen py-12">
    <div class="absolute inset-0 bg-gradient-to-b from-cyber-dark/30 to-cyber-blue/30"></div>
    <div class="container mx-auto px-4 relative">
      <!-- Page Header -->
      <div class="text-center mb-16">
        <h1 class="cyber-title text-5xl md:text-6xl font-black mb-6">
          <span 
            class="text-cyber-neon-green"
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'title')"
          >{{ getPageConfig('title', 'ABOUT') }}</span> 
          <span
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'subtitle')"
          >{{ getPageConfig('subtitle', 'US') }}</span>
        </h1>
        <p 
          class="text-xl text-cyber-neon-blue max-w-2xl mx-auto"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >{{ getPageConfig('description', '了解我们的使命、愿景和价值观') }}</p>
      </div>

      <!-- Hero Section -->
      <div class="relative rounded-3xl clip-corner overflow-hidden mb-20">
        <div class="absolute inset-0 bg-gradient-to-br from-cyber-dark to-cyber-blue"></div>
        <div class="relative h-96 flex items-center justify-center">
          <div class="text-center">
            <div 
              class="text-8xl cyber-title font-black mb-6 text-transparent bg-clip-text bg-gradient-to-r from-cyber-neon-green to-cyber-neon-pink animate-pulse"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'hero_text')"
            >
              {{ getPageConfig('hero_text', 'CYBERCHARGE') }}
            </div>
            <p 
              class="text-2xl text-cyber-neon-blue max-w-3xl mx-auto leading-relaxed"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'hero_subtext')"
            >
              {{ getPageConfig('hero_subtext', '未来游戏充值体验 · 安全 · 快速 · 可靠') }}
            </p>
          </div>
        </div>
        <div class="absolute inset-0 border-2 border-cyber-neon-green/20 clip-corner"></div>
      </div>

      <!-- Mission & Vision -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20">
        <!-- Mission -->
        <div class="relative rounded-2xl bg-gradient-to-br from-cyber-dark/60 to-cyber-blue/40 border border-cyber-neon-green/20 clip-corner p-8">
          <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-green/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
          <div class="relative">
            <div class="w-16 h-16 rounded-2xl bg-cyber-neon-green/20 flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-cyber-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 class="text-3xl font-black text-cyber-neon-green mb-4 drop-shadow-glow-green">使命</h2>
            <p class="text-cyber-neon-blue text-lg leading-relaxed">
              我们的使命是为全球游戏玩家提供最安全、最快捷、最可靠的游戏充值服务，
              让每一位玩家都能享受到无缝的游戏体验，不受地域和支付方式的限制。
            </p>
          </div>
        </div>

        <!-- Vision -->
        <div class="relative rounded-2xl bg-gradient-to-br from-cyber-dark/60 to-cyber-blue/40 border border-cyber-neon-pink/20 clip-corner p-8">
          <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-pink/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
          <div class="relative">
            <div class="w-16 h-16 rounded-2xl bg-cyber-neon-pink/20 flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-cyber-neon-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h2 class="text-3xl font-black text-cyber-neon-pink mb-4 drop-shadow-glow-pink">愿景</h2>
            <p class="text-cyber-neon-blue text-lg leading-relaxed">
              成为全球领先的游戏服务平台，通过技术创新和卓越服务，
              连接世界各地的玩家与游戏世界，创造无限可能的游戏体验。
            </p>
          </div>
        </div>
      </div>

      <!-- Values -->
      <div class="mb-20">
        <h2 class="text-4xl font-black text-center mb-16 text-white">
          <span class="text-cyber-neon-blue">CORE</span> VALUES
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-blue/20 clip-corner p-8 hover:border-cyber-neon-blue/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-12 h-12 rounded-xl bg-cyber-neon-blue/20 flex items-center justify-center mb-4">
                <svg class="w-6 h-6 text-cyber-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-cyber-neon-blue mb-3">安全可靠</h3>
              <p class="text-cyber-neon-blue">
                我们始终将用户的安全放在首位，采用最先进的安全技术保护每一笔交易。
              </p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-green/20 clip-corner p-8 hover:border-cyber-neon-green/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-green/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-12 h-12 rounded-xl bg-cyber-neon-green/20 flex items-center justify-center mb-4">
                <svg class="w-6 h-6 text-cyber-neon-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-cyber-neon-green mb-3">极速体验</h3>
              <p class="text-cyber-neon-blue">
                提供毫秒级的充值服务，让您的游戏体验永不断线。
              </p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-pink/20 clip-corner p-8 hover:border-cyber-neon-pink/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-pink/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-12 h-12 rounded-xl bg-cyber-neon-pink/20 flex items-center justify-center mb-4">
                <svg class="w-6 h-6 text-cyber-neon-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-cyber-neon-pink mb-3">用户至上</h3>
              <p class="text-cyber-neon-blue">
                始终以用户需求为中心，提供贴心的客户服务和个性化的体验。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Team -->
      <div class="mb-20">
        <h2 class="text-4xl font-black text-center mb-16 text-white">
          <span class="text-cyber-neon-green">OUR</span> TEAM
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-blue/20 clip-corner p-6 text-center hover:border-cyber-neon-blue/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-cyber-neon-blue to-cyber-neon-green mx-auto mb-4 flex items-center justify-center text-cyber-black font-bold text-xl">
                JD
              </div>
              <h3 class="text-lg font-bold text-white mb-2">John Doe</h3>
              <p class="text-cyber-neon-blue text-sm">CEO & Founder</p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-green/20 clip-corner p-6 text-center hover:border-cyber-neon-green/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-green/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-cyber-neon-green to-cyber-neon-pink mx-auto mb-4 flex items-center justify-center text-cyber-black font-bold text-xl">
                JS
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Jane Smith</h3>
              <p class="text-cyber-neon-blue text-sm">CTO</p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-pink/20 clip-corner p-6 text-center hover:border-cyber-neon-pink/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-pink/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-cyber-neon-pink to-cyber-neon-blue mx-auto mb-4 flex items-center justify-center text-cyber-black font-bold text-xl">
                MB
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Mike Brown</h3>
              <p class="text-cyber-neon-blue text-sm">Lead Developer</p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-blue/20 clip-corner p-6 text-center hover:border-cyber-neon-blue/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-cyber-neon-blue to-cyber-neon-green mx-auto mb-4 flex items-center justify-center text-cyber-black font-bold text-xl">
                SA
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Sarah Adams</h3>
              <p class="text-cyber-neon-blue text-sm">Product Manager</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact CTA -->
      <div class="text-center">
        <h2 class="text-4xl font-black mb-6 text-white">
          <span class="text-cyber-neon-pink">READY</span> TO GET STARTED?
        </h2>
        <p class="text-xl text-cyber-neon-blue mb-8 max-w-2xl mx-auto">
          加入我们的游戏社区，享受安全、快速、可靠的游戏充值服务
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <RouterLink to="/recharge">
            <button class="px-8 py-4 rounded-xl font-bold text-lg tracking-wide uppercase bg-gradient-to-r from-cyber-neon-green to-cyber-neon-blue text-cyber-black hover:shadow-neon-green transition-all duration-300 transform hover:-translate-y-1 clip-corner">
              开始充值
            </button>
          </RouterLink>
          <RouterLink to="/contact">
            <button class="px-8 py-4 rounded-xl font-bold text-lg tracking-wide uppercase border-2 border-cyber-neon-pink text-cyber-neon-pink hover:bg-cyber-neon-pink hover:text-cyber-black hover:shadow-neon-pink transition-all duration-300 clip-corner">
              联系我们
            </button>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useVisualEditor } from '../composables/useVisualEditor'
const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('about_page', '关于我们页')
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