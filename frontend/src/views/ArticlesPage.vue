<template>
  <div class="relative min-h-screen py-12">
    <div class="absolute inset-0 bg-gradient-to-b from-cyber-dark/30 to-cyber-blue/30"></div>
    <div class="container mx-auto px-4 relative">
      <!-- Page Header -->
      <div class="text-center mb-16">
        <!-- Breadcrumb Navigation -->
        <div v-if="currentCategory" class="flex items-center justify-center gap-2 text-sm text-cyber-neon-blue mb-4">
          <RouterLink :to="localizedPath('/articles')" class="hover:text-cyber-neon-green transition-colors">
            {{ t('articlesPage.allNews') }}
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
          >{{ getPageConfig('subtitle', t('news').toUpperCase()) }}</span>
        </h1>
        <p 
          class="text-xl text-cyber-neon-blue max-w-2xl mx-auto"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >
          {{ getPageConfig('description', currentCategory ? `${currentCategory} - ${t('latestNews')}` : t('latestNews')) }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-20">
        <div class="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyber-neon-green"></div>
        <p class="text-cyber-neon-blue mt-4 text-lg">{{ t('articlesPage.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20">
        <p class="text-cyber-neon-pink text-xl mb-4">❗ {{ error }}</p>
        <button 
          @click="loadArticles" 
          class="px-6 py-3 rounded-xl bg-cyber-neon-blue/20 border border-cyber-neon-blue text-cyber-neon-blue hover:bg-cyber-neon-blue/30 transition-all"
        >
          {{ t('articlesPage.retry') }}
        </button>
      </div>

      <!-- Articles Grid -->
      <div v-else-if="articles.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <article
          v-for="article in articles"
          :key="article.id"
          class="group relative rounded-2xl clip-corner overflow-hidden"
        >
          <div class="absolute inset-0 bg-gradient-to-br from-cyber-dark to-cyber-blue"></div>
          <RouterLink :to="localizedPath(`/articles/${article.id}`)" class="relative block">
            <img
              v-if="resolveArticleImage(article)"
              :src="resolveArticleImage(article)"
              :alt="article.title"
              class="w-full h-48 object-cover opacity-60 group-hover:opacity-80 transition-opacity"
              referrerpolicy="no-referrer"
              @error="handleCardImageError"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-cyber-dark to-transparent opacity-80"></div>
            <div class="relative p-6 pb-4">
              <div class="mb-4">
                <div class="inline-block px-3 py-1 rounded-full bg-cyber-neon-blue/20 border border-cyber-neon-blue text-cyber-neon-blue text-xs font-bold uppercase tracking-wider">
                  {{ article.category }}
                </div>
              </div>
              <h2 class="text-xl font-bold text-white mb-4 group-hover:text-cyber-neon-green transition-colors">{{ article.title }}</h2>
              <div class="flex items-center justify-between text-sm text-cyber-neon-pink">
                <span>{{ article.author }}</span>
                <div class="flex items-center gap-4">
                  <span>{{ formatArticleDate(article.date) }}</span>
                  <span>{{ article.readTime }}</span>
                </div>
              </div>
            </div>
          </RouterLink>
          <div class="relative px-6 pb-5">
            <div class="h-px bg-cyber-neon-blue/25 mb-3"></div>
            <div class="flex items-start justify-between gap-3">
              <span class="text-[11px] text-cyber-neon-blue/85 uppercase tracking-[0.2em]">{{ t('articlesPage.share') }}</span>
              <div class="flex flex-wrap justify-end gap-1.5">
                <button
                  v-for="channel in shareChannels"
                  :key="`${article.id}-${channel.key}`"
                  type="button"
                  class="share-icon-btn"
                  :title="t('articlesPage.shareTo', { channel: t(channel.labelKey) })"
                  :aria-label="t('articlesPage.shareTo', { channel: t(channel.labelKey) })"
                  :style="{ '--share-color': `#${channel.icon.hex}` }"
                  @click.stop.prevent="shareArticle(article, channel)"
                >
                  <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" aria-hidden="true">
                    <path :d="channel.icon.path" fill="currentColor" />
                  </svg>
                </button>
              </div>
            </div>
            <p v-if="shareFeedbackById[article.id]" class="mt-2 text-[11px] text-cyber-neon-green text-right">
              {{ shareFeedbackById[article.id] }}
            </p>
          </div>
          <div class="absolute inset-0 border-2 border-transparent group-hover:border-cyber-neon-green/50 rounded-2xl clip-corner transition-all duration-300 pointer-events-none"></div>
        </article>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-20">
        <p class="text-cyber-neon-blue text-xl">
          <span v-if="currentCategory">
            {{ t('articlesPage.emptyByCategory', { category: currentCategory }) }}
          </span>
          <span v-else>
            {{ t('articlesPage.emptyAll') }}
          </span>
        </p>
        <RouterLink 
          v-if="currentCategory" 
          :to="localizedPath('/articles')"
          class="inline-block mt-6 px-6 py-3 rounded-xl bg-cyber-neon-blue/20 border border-cyber-neon-blue text-cyber-neon-blue hover:bg-cyber-neon-blue/30 transition-all"
        >
          {{ t('articlesPage.viewAll') }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getArticles } from '../api/articles'
import type { Article } from '../types'
import { useVisualEditor } from '../composables/useVisualEditor'
import { withLocalePrefix } from '../i18n/locale-routing'
import { normalizeLocaleCode } from '../i18n/locale-utils'
import { formatDateByLocale } from '../utils/intl'
import {
  guardUsagePolicyContent,
  isUsagePolicyViolationError,
  openUsagePolicyDialog,
} from '../utils/usagePolicy'
import {
  siFacebook,
  siInstagram,
  siLine,
  siWechat,
  siWhatsapp,
  siX,
  siXiaohongshu,
} from 'simple-icons'

const { t, locale } = useI18n()
const route = useRoute()
const articles = ref<Article[]>([])
const loading = ref(true)
const error = ref('')
const currentCategory = ref<string>('')
const shareFeedbackById = ref<Record<string, string>>({})
const shareFeedbackTimers = new Map<string, number>()

// 可视化编辑支持
const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('articles_page', '资讯列表页')

const normalizeBaseUrl = (value: string) => value.replace(/\/+$/, '')
const BACKEND_ORIGIN = normalizeBaseUrl(
  (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim() || 'http://127.0.0.1:8000'
)
const SHARE_ORIGIN = normalizeBaseUrl(
  (import.meta.env.VITE_SHARE_ORIGIN as string | undefined)?.trim() || ''
)

const upsertMetaTag = (name: string, content: string) => {
  if (typeof document === 'undefined') return
  const selector = `meta[name="${name}"]`
  const existing = document.head.querySelector(selector) as HTMLMetaElement | null
  const target = existing ?? document.createElement('meta')
  target.setAttribute('name', name)
  target.setAttribute('content', content)
  if (!existing) document.head.appendChild(target)
}

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

const formatArticleDate = (value: unknown): string => {
  return formatDateByLocale(value, locale.value)
}

const handleCardImageError = (event: Event) => {
  const img = event.target as HTMLImageElement | null
  if (!img) return
  img.style.display = 'none'
  img.onerror = null
}

type ShareChannelKey =
  | 'facebook'
  | 'twitter'
  | 'line'
  | 'wechat'
  | 'xiaohongshu'
  | 'whatsapp'
  | 'instagram'

interface ShareChannel {
  key: ShareChannelKey
  labelKey: string
  icon: { path: string; hex: string }
  mode: 'direct' | 'copy_then_open'
  buildUrl: (payload: { url: string; title: string }) => string
  copyMessageKey?: string
}

const shareChannels = computed<ShareChannel[]>(() => [
  {
    key: 'facebook',
    labelKey: 'articlesPage.channels.facebook',
    icon: siFacebook,
    mode: 'direct',
    buildUrl: ({ url, title }) =>
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(title)}`,
  },
  {
    key: 'twitter',
    labelKey: 'articlesPage.channels.twitter',
    icon: siX,
    mode: 'direct',
    buildUrl: ({ url, title }) =>
      `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
  },
  {
    key: 'line',
    labelKey: 'articlesPage.channels.line',
    icon: siLine,
    mode: 'direct',
    buildUrl: ({ url }) => `https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(url)}`,
  },
  {
    key: 'wechat',
    labelKey: 'articlesPage.channels.wechat',
    icon: siWechat,
    mode: 'copy_then_open',
    buildUrl: () => 'https://web.wechat.com/',
    copyMessageKey: 'articlesPage.copyForWechat',
  },
  {
    key: 'xiaohongshu',
    labelKey: 'articlesPage.channels.xiaohongshu',
    icon: siXiaohongshu,
    mode: 'copy_then_open',
    buildUrl: () => 'https://www.xiaohongshu.com/explore',
    copyMessageKey: 'articlesPage.copyForXiaohongshu',
  },
  {
    key: 'whatsapp',
    labelKey: 'articlesPage.channels.whatsapp',
    icon: siWhatsapp,
    mode: 'direct',
    buildUrl: ({ url, title }) =>
      `https://api.whatsapp.com/send?text=${encodeURIComponent(`${title} ${url}`)}`,
  },
  {
    key: 'instagram',
    labelKey: 'articlesPage.channels.instagram',
    icon: siInstagram,
    mode: 'copy_then_open',
    buildUrl: () => 'https://www.instagram.com/',
    copyMessageKey: 'articlesPage.copyForInstagram',
  },
])

const localizedPath = (path: string): string => withLocalePrefix(path, normalizeLocaleCode(locale.value))

const setShareFeedback = (articleId: string, text: string) => {
  shareFeedbackById.value = {
    ...shareFeedbackById.value,
    [articleId]: text,
  }

  const existingTimer = shareFeedbackTimers.get(articleId)
  if (existingTimer) {
    window.clearTimeout(existingTimer)
  }

  const timer = window.setTimeout(() => {
    const next = { ...shareFeedbackById.value }
    delete next[articleId]
    shareFeedbackById.value = next
    shareFeedbackTimers.delete(articleId)
  }, 2600)

  shareFeedbackTimers.set(articleId, timer)
}

const copyText = async (text: string): Promise<boolean> => {
  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {
      // fallback below
    }
  }

  if (typeof document === 'undefined') return false

  try {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.setAttribute('readonly', 'true')
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    const copied = document.execCommand('copy')
    document.body.removeChild(textarea)
    return copied
  } catch {
    return false
  }
}

const openSharePage = (url: string) => {
  if (typeof window === 'undefined') return
  const popup = window.open(url, '_blank')
  if (popup) {
    popup.opener = null
  }
}

const isLikelyPrivateHost = (host: string): boolean => {
  const h = String(host || '').toLowerCase()
  if (!h) return true
  if (h === 'localhost' || h === '127.0.0.1' || h === '0.0.0.0' || h.endsWith('.local')) return true

  const ipv4 = h.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/)
  if (!ipv4) return false

  const a = Number(ipv4[1])
  const b = Number(ipv4[2])
  if (a === 10) return true
  if (a === 127) return true
  if (a === 192 && b === 168) return true
  if (a === 172 && b >= 16 && b <= 31) return true
  return false
}

const shareUrlNeedsPublicOrigin = (url: string): boolean => {
  try {
    const parsed = new URL(url)
    return isLikelyPrivateHost(parsed.hostname)
  } catch {
    return true
  }
}

const resolveShareUrl = (article: Article): string => {
  const articlePath = withLocalePrefix(`/articles/${article.id}`, normalizeLocaleCode(locale.value))
  if (SHARE_ORIGIN) return `${SHARE_ORIGIN}${articlePath}`
  if (typeof window === 'undefined') return articlePath
  return `${window.location.origin}${articlePath}`
}

const shareArticle = async (article: Article, channel: ShareChannel) => {
  const shareUrl = resolveShareUrl(article)
  const shareTitle = t('articlesPage.shareTitle', { title: article.title })
  try {
    guardUsagePolicyContent(
      {
        title: shareTitle,
        content: (article as any).content,
        summary: (article as any).summary,
        url: shareUrl,
      },
      'share'
    )
  } catch (error) {
    if (isUsagePolicyViolationError(error)) {
      setShareFeedback(String(article.id), error.message)
      openUsagePolicyDialog(error.message)
      return
    }
    throw error
  }

  const targetUrl = channel.buildUrl({ url: shareUrl, title: shareTitle })
  const isLocalOrPrivateShareUrl = shareUrlNeedsPublicOrigin(shareUrl)

  if (channel.mode === 'copy_then_open') {
    const copied = await copyText(`${shareTitle}\n${shareUrl}`)
    if (copied && channel.copyMessageKey) {
      setShareFeedback(String(article.id), t(channel.copyMessageKey))
    }
  } else if (!SHARE_ORIGIN && isLocalOrPrivateShareUrl) {
    const copied = await copyText(`${shareTitle}\n${shareUrl}`)
    if (copied) {
      setShareFeedback(String(article.id), t('articlesPage.localShareFallback'))
    }
  }

  openSharePage(targetUrl)
}

const syncArticlesSeo = () => {
  if (typeof document === 'undefined') return
  const siteName = t('siteName')
  const routeTitle = t('seo.routeTitles.articles')
  const category = String(currentCategory.value || '').trim()
  document.title = category
    ? `${category} | ${routeTitle} | ${siteName}`
    : `${routeTitle} | ${siteName}`

  const description = category
    ? t('articlesPage.categoryDescription', { category })
    : t('seo.defaultDescription')
  upsertMetaTag('description', description)
}

const loadArticles = async () => {
  try {
    loading.value = true
    error.value = ''

    const category = route.query.category as string || ''
    currentCategory.value = category

    const params = category ? { category } : undefined
    articles.value = await getArticles(params)
  } catch (err: any) {
    console.error('Failed to load articles:', err)
    error.value = t('articlesPage.loadFailed')
  } finally {
    loading.value = false
    syncArticlesSeo()
  }
}

watch(() => route.query.category, () => {
  loadArticles()
})

watch(
  () => locale.value,
  () => {
    syncArticlesSeo()
  }
)

onMounted(() => {
  loadArticles()
})

onUnmounted(() => {
  shareFeedbackTimers.forEach((timer) => window.clearTimeout(timer))
  shareFeedbackTimers.clear()
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

.share-icon-btn {
  width: 1.95rem;
  height: 1.95rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--share-color) 42%, transparent);
  background: color-mix(in srgb, var(--share-color) 15%, transparent);
  color: var(--share-color);
  transition: transform 0.2s ease, filter 0.2s ease, border-color 0.2s ease;
}

.share-icon-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.08);
  border-color: color-mix(in srgb, var(--share-color) 68%, transparent);
}
</style>
