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
          >{{ getPageConfig('title', t('aboutPage.title')) }}</span> 
          <span
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'subtitle')"
          >{{ getPageConfig('subtitle', t('aboutPage.subtitle')) }}</span>
        </h1>
        <p 
          class="text-xl text-cyber-neon-blue max-w-2xl mx-auto"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >{{ getPageConfig('description', t('aboutPage.description')) }}</p>
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
              {{ getPageConfig('hero_text', t('aboutPage.heroText')) }}
            </div>
            <p 
              class="text-2xl text-cyber-neon-blue max-w-3xl mx-auto leading-relaxed"
              :contenteditable="isEditMode"
              @blur="handleInlineEdit($event, 'hero_subtext')"
            >
              {{ getPageConfig('hero_subtext', t('aboutPage.heroSubtext')) }}
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
              <Zap class="w-8 h-8 text-cyber-neon-green" />
            </div>
            <h2 class="text-3xl font-black text-cyber-neon-green mb-4 drop-shadow-glow-green">{{ t('aboutPage.missionTitle') }}</h2>
            <p class="text-cyber-neon-blue text-lg leading-relaxed">
              {{ t('aboutPage.missionDescription') }}
            </p>
          </div>
        </div>

        <!-- Vision -->
        <div class="relative rounded-2xl bg-gradient-to-br from-cyber-dark/60 to-cyber-blue/40 border border-cyber-neon-pink/20 clip-corner p-8">
          <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-pink/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
          <div class="relative">
            <div class="w-16 h-16 rounded-2xl bg-cyber-neon-pink/20 flex items-center justify-center mb-6">
              <Eye class="w-8 h-8 text-cyber-neon-pink" />
            </div>
            <h2 class="text-3xl font-black text-cyber-neon-pink mb-4 drop-shadow-glow-pink">{{ t('aboutPage.visionTitle') }}</h2>
            <p class="text-cyber-neon-blue text-lg leading-relaxed">
              {{ t('aboutPage.visionDescription') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Values -->
      <div class="mb-20">
        <h2 class="text-4xl font-black text-center mb-16 text-white">
          <span class="text-cyber-neon-blue">{{ t('aboutPage.corePrefix') }}</span> {{ t('aboutPage.coreSuffix') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-blue/20 clip-corner p-8 hover:border-cyber-neon-blue/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-12 h-12 rounded-xl bg-cyber-neon-blue/20 flex items-center justify-center mb-4">
                <ShieldCheck class="w-6 h-6 text-cyber-neon-blue" />
              </div>
              <h3 class="text-xl font-bold text-cyber-neon-blue mb-3">{{ t('aboutPage.values.secureTitle') }}</h3>
              <p class="text-cyber-neon-blue">
                {{ t('aboutPage.values.secureDescription') }}
              </p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-green/20 clip-corner p-8 hover:border-cyber-neon-green/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-green/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-12 h-12 rounded-xl bg-cyber-neon-green/20 flex items-center justify-center mb-4">
                <Rocket class="w-6 h-6 text-cyber-neon-green" />
              </div>
              <h3 class="text-xl font-bold text-cyber-neon-green mb-3">{{ t('aboutPage.values.fastTitle') }}</h3>
              <p class="text-cyber-neon-blue">
                {{ t('aboutPage.values.fastDescription') }}
              </p>
            </div>
          </div>

          <div class="group relative rounded-2xl bg-cyber-dark/60 border border-cyber-neon-pink/20 clip-corner p-8 hover:border-cyber-neon-pink/50 transition-all duration-300">
            <div class="absolute inset-0 bg-gradient-to-br from-cyber-neon-pink/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 clip-corner"></div>
            <div class="relative">
              <div class="w-12 h-12 rounded-xl bg-cyber-neon-pink/20 flex items-center justify-center mb-4">
                <Heart class="w-6 h-6 text-cyber-neon-pink" />
              </div>
              <h3 class="text-xl font-bold text-cyber-neon-pink mb-3">{{ t('aboutPage.values.userTitle') }}</h3>
              <p class="text-cyber-neon-blue">
                {{ t('aboutPage.values.userDescription') }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Team -->
      <div class="mb-20">
        <h2 class="text-4xl font-black text-center mb-16 text-white">
          <span class="text-cyber-neon-green">{{ t('aboutPage.teamPrefix') }}</span> {{ t('aboutPage.teamSuffix') }}
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
          <span class="text-cyber-neon-pink">{{ t('aboutPage.cta.titlePrefix') }}</span> {{ t('aboutPage.cta.titleSuffix') }}
        </h2>
        <p class="text-xl text-cyber-neon-blue mb-8 max-w-2xl mx-auto">
          {{ t('aboutPage.cta.description') }}
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <RouterLink :to="localizedPath('/recharge')">
            <button class="px-8 py-4 rounded-xl font-bold text-lg tracking-wide uppercase bg-gradient-to-r from-cyber-neon-green to-cyber-neon-blue text-cyber-black hover:shadow-neon-green transition-all duration-300 transform hover:-translate-y-1 clip-corner">
              {{ t('aboutPage.cta.recharge') }}
            </button>
          </RouterLink>
          <RouterLink :to="localizedPath('/contact')">
            <button class="px-8 py-4 rounded-xl font-bold text-lg tracking-wide uppercase border-2 border-cyber-neon-pink text-cyber-neon-pink hover:bg-cyber-neon-pink hover:text-cyber-black hover:shadow-neon-pink transition-all duration-300 clip-corner">
              {{ t('aboutPage.cta.contact') }}
            </button>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Eye, Heart, Rocket, ShieldCheck, Zap } from 'lucide-vue-next'
import { useVisualEditor } from '../composables/useVisualEditor'
import { withLocalePrefix } from '../i18n/locale-routing'
import { normalizeLocaleCode } from '../i18n/locale-utils'

const { t, locale } = useI18n()
const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('about_page', '关于我们页')
const localizedPath = (path: string): string => withLocalePrefix(path, normalizeLocaleCode(locale.value))
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
