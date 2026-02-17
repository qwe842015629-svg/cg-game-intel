<template>
  <div v-if="loading" class="min-h-screen py-20 flex items-center justify-center">
    <div class="text-center">
      <div class="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-primary"></div>
      <p class="text-muted-foreground mt-4">加载中...</p>
    </div>
  </div>

  <div v-else-if="article && !error" class="min-h-screen py-8 md:py-10">
    <div class="container mx-auto px-4 max-w-[1540px]">
      <button
        @click="router.back()"
        v-magnetic="{ strength: 0.16, max: 10 }"
        class="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg border border-border bg-card text-foreground hover:bg-muted transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回
      </button>

      <div class="article-layout mt-6">
        <aside class="article-sidebar article-sidebar-left">
          <div class="sidebar-sticky surface-card p-4">
            <div class="sidebar-title">文章目录</div>
            <nav class="toc-nav">
              <a
                v-for="item in tocItems"
                :key="item.id"
                :href="`#${item.id}`"
                :class="[
                  'toc-link',
                  item.level === 3 ? 'level-3' : '',
                  activeHeadingId === item.id ? 'active' : '',
                ]"
                @click.prevent="scrollToHeading(item.id)"
              >
                {{ item.text }}
              </a>
              <p v-if="tocItems.length === 0" class="toc-empty">本篇暂无可用目录，建议刷新后重试。</p>
            </nav>
          </div>
        </aside>

        <article class="surface-card article-main overflow-hidden" v-motion-reveal="{ y: 22 }">
          <div class="p-6 md:p-8 border-b border-border">
            <div class="inline-flex items-center px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold mb-4">
              {{ article.category || '资讯' }}
            </div>

            <h1 class="text-3xl md:text-4xl font-bold text-foreground leading-tight mb-5">
              {{ article.title }}
            </h1>

            <div class="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span>作者：{{ article.author || '官方编辑' }}</span>
              <span>{{ article.date }}</span>
              <span>阅读时长：{{ article.readTime || '约 3 分钟' }}</span>
            </div>
          </div>

          <div v-if="heroImageSrc" class="aspect-[16/5.8] bg-muted">
            <img
              :src="heroImageSrc"
              :alt="article.title"
              class="w-full h-full object-cover"
              @error="handleHeroImageError"
            />
          </div>

          <div class="p-6 md:p-8">
            <div
              class="article-content text-foreground/90 leading-8 text-[15px] md:text-base"
              v-html="renderedArticleHtml"
            ></div>

            <div v-if="article.tags && article.tags.length > 0" class="mt-8 flex flex-wrap gap-2">
              <span
                v-for="tag in article.tags"
                :key="tag"
                class="inline-flex items-center px-3 py-1 rounded-full border border-border bg-muted text-xs text-foreground"
              >
                # {{ tag }}
              </span>
            </div>
          </div>
        </article>

        <aside class="article-sidebar article-sidebar-right">
          <div class="sidebar-sticky sidebar-stack">
            <section class="surface-card p-4">
              <h3 class="sidebar-title">热门游戏</h3>
              <div v-if="sidebarLoading && hotGames.length === 0" class="sidebar-loading">加载中...</div>
              <div v-else-if="hotGames.length === 0" class="sidebar-empty">暂无热门游戏</div>
              <RouterLink
                v-for="game in hotGames"
                :key="`hot-${game.id}`"
                :to="`/games/${game.id}`"
                class="sidebar-list-item"
              >
                <img :src="resolveGameThumb(game)" :alt="game.name || '热门游戏'" class="sidebar-thumb" @error="handleSidebarImageError" />
                <div class="sidebar-item-copy">
                  <p class="sidebar-item-title">{{ game.name || game.title || '未命名游戏' }}</p>
                  <p class="sidebar-item-sub">点击查看充值详情</p>
                </div>
              </RouterLink>
            </section>

            <section class="surface-card p-4">
              <h3 class="sidebar-title">新增文章</h3>
              <div v-if="sidebarLoading && latestArticles.length === 0" class="sidebar-loading">加载中...</div>
              <div v-else-if="latestArticles.length === 0" class="sidebar-empty">暂无新增文章</div>
              <RouterLink
                v-for="item in latestArticles"
                :key="`latest-${item.id}`"
                :to="`/articles/${item.id}`"
                class="sidebar-list-item"
              >
                <img :src="resolveArticleThumb(item)" :alt="item.title || '新增文章'" class="sidebar-thumb" @error="handleSidebarImageError" />
                <div class="sidebar-item-copy">
                  <p class="sidebar-item-title">{{ item.title || '未命名文章' }}</p>
                  <p class="sidebar-item-sub">{{ item.date || '最新发布' }}</p>
                </div>
              </RouterLink>
            </section>
          </div>
        </aside>
      </div>
    </div>
  </div>

  <div v-else class="min-h-screen py-20 flex items-center justify-center">
    <div class="text-center surface-card px-8 py-10 max-w-md">
      <div class="text-4xl font-bold text-foreground mb-3">404</div>
      <h2 class="text-xl font-semibold text-foreground mb-2">文章不存在</h2>
      <p class="text-muted-foreground mb-6">{{ error || '抱歉，未找到该文章。' }}</p>
      <RouterLink
        to="/articles"
        class="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
      >
        返回资讯列表
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticleDetail, getArticles } from '../api/articles'
import { getHotGames } from '../api/games'
import type { Article, RechargeGame } from '../types'

interface TocItem {
  id: string
  text: string
  level: 2 | 3
}

const route = useRoute()
const router = useRouter()

const article = ref<Article | null>(null)
const loading = ref(true)
const error = ref('')
const sidebarLoading = ref(false)
const renderedArticleHtml = ref('')
const tocItems = ref<TocItem[]>([])
const activeHeadingId = ref('')
const hotGames = ref<RechargeGame[]>([])
const latestArticles = ref<Article[]>([])
const heroImageSrc = ref('')
const heroImageFallbackQueue = ref<string[]>([])

let headingObserver: IntersectionObserver | null = null

const normalizeBaseUrl = (value: string) => value.replace(/\/+$/, '')
const BACKEND_ORIGIN = normalizeBaseUrl(
  (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim() || 'http://127.0.0.1:8000'
)

const escapeHtml = (value: string): string =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const slugifyHeading = (value: string): string => {
  const normalized = String(value || '')
    .toLowerCase()
    .trim()
    .replace(/[\s]+/g, '-')
    .replace(/[^a-z0-9\u4e00-\u9fff\-_]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
  return normalized || 'section'
}

const stripHeadingNumber = (value: string): string =>
  String(value || '')
    .replace(/^\s*\d+(?:\.\d+)*[.)銆乗-\s]+/, '')
    .trim()

const normalizeImageUrl = (raw: unknown): string => {
  const value = String(raw || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  if (value.startsWith('//')) return `https:${value}`
  if (value.startsWith('/')) return `${BACKEND_ORIGIN}${value}`
  return value
}

const resolveGameThumb = (game: RechargeGame): string =>
  normalizeImageUrl(game?.image)

const resolveArticleThumb = (item: Article): string => {
  const record = item as Article & { cover_image?: string }
  return normalizeImageUrl(record.image || record.cover_image)
}

const extractFirstImageFromHtml = (html: string): string => {
  const match = String(html || '').match(/<img[^>]+src=["']([^"']+)["']/i)
  return normalizeImageUrl(match?.[1] || '')
}

const dedupeStringList = (items: string[]): string[] => {
  const seen = new Set<string>()
  const output: string[] = []
  for (const raw of items) {
    const value = String(raw || '').trim()
    if (!value) continue
    if (seen.has(value)) continue
    seen.add(value)
    output.push(value)
  }
  return output
}

const resetHeroImageByCandidates = (contentHtml = '') => {
  const articleRecord = (article.value || {}) as Article & { cover_image?: string }
  const candidates = dedupeStringList([
    normalizeImageUrl(articleRecord.image),
    normalizeImageUrl(articleRecord.cover_image),
    extractFirstImageFromHtml(contentHtml || renderedArticleHtml.value),
  ])
  heroImageSrc.value = candidates[0] || ''
  heroImageFallbackQueue.value = candidates.slice(1)
}

const handleHeroImageError = (event: Event) => {
  const img = event.target as HTMLImageElement | null
  if (!img) return
  const next = heroImageFallbackQueue.value.shift()
  if (next) {
    heroImageSrc.value = next
    img.src = next
    return
  }
  heroImageSrc.value = ''
  img.onerror = null
}

const handleSidebarImageError = (event: Event) => {
  const img = event.target as HTMLImageElement | null
  if (!img) return
  img.style.display = 'none'
  img.onerror = null
}

const stopHeadingObserver = () => {
  if (headingObserver) {
    headingObserver.disconnect()
    headingObserver = null
  }
}

const updateActiveHeadingByPosition = () => {
  if (typeof window === 'undefined' || tocItems.value.length === 0) return
  const offset = 146
  let current = tocItems.value[0].id
  for (const item of tocItems.value) {
    const el = document.getElementById(item.id)
    if (!el) continue
    if (el.getBoundingClientRect().top <= offset) {
      current = item.id
    }
  }
  activeHeadingId.value = current
}

const setupHeadingObserver = async () => {
  if (typeof window === 'undefined' || tocItems.value.length === 0) return
  await nextTick()
  stopHeadingObserver()

  const headingEls = tocItems.value
    .map((item) => document.getElementById(item.id))
    .filter(Boolean) as HTMLElement[]

  if (headingEls.length === 0) return

  if (!('IntersectionObserver' in window)) {
    activeHeadingId.value = tocItems.value[0].id
    return
  }

  headingObserver = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
      if (visible.length > 0) {
        activeHeadingId.value = (visible[0].target as HTMLElement).id
      } else {
        updateActiveHeadingByPosition()
      }
    },
    {
      root: null,
      rootMargin: '-120px 0px -62% 0px',
      threshold: [0, 0.15, 1],
    }
  )

  headingEls.forEach((el) => headingObserver?.observe(el))
}

const buildRenderedArticle = (raw: unknown): { html: string; toc: TocItem[] } => {
  if (raw == null) return { html: '', toc: [] }

  const rawText = typeof raw === 'string' ? raw : String(raw)
  if (!rawText.trim()) return { html: '', toc: [] }

  const hasHtmlTag = /<[a-z][\s\S]*>/i.test(rawText)
  const html = hasHtmlTag ? rawText : escapeHtml(rawText).replace(/\n/g, '<br />')

  if (typeof window === 'undefined' || typeof DOMParser === 'undefined') {
    return { html, toc: [] }
  }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(`<div>${html}</div>`, 'text/html')
    const root = doc.body.firstElementChild as HTMLElement | null
    if (!root) return { html, toc: [] }

    root
      .querySelectorAll('script,style,iframe,object,embed,link,meta,form,input,button,textarea,select')
      .forEach((node) => node.remove())

    const safeUrlPattern = /^(https?:|mailto:|tel:|\/|#|\/\/|data:image\/)/i
    root.querySelectorAll('*').forEach((el) => {
      Array.from(el.attributes).forEach((attr) => {
        const name = attr.name.toLowerCase()
        const value = attr.value.trim()
        if (name.startsWith('on') || name === 'style') {
          el.removeAttribute(attr.name)
          return
        }
        if (name === 'src' || name === 'href') {
          if (!value || /^javascript:/i.test(value) || !safeUrlPattern.test(value)) {
            el.removeAttribute(attr.name)
          }
        }
      })

      if (el.tagName.toLowerCase() === 'a') {
        el.setAttribute('target', '_blank')
        el.setAttribute('rel', 'noopener noreferrer nofollow')
      }
    })

    const figures = root.querySelectorAll('.seo-media-gallery figure')
    const maxFigures = 16
    if (figures.length > maxFigures) {
      for (let i = maxFigures; i < figures.length; i += 1) {
        figures[i].remove()
      }
    }

    const summaryBlocks = root.querySelectorAll('.seo-summary')
    if (summaryBlocks.length > 1) {
      for (let i = 1; i < summaryBlocks.length; i += 1) {
        summaryBlocks[i].remove()
      }
    }

    const metadataBlocks = root.querySelectorAll('.seo-metadata')
    if (metadataBlocks.length > 1) {
      for (let i = 1; i < metadataBlocks.length; i += 1) {
        metadataBlocks[i].remove()
      }
    }

    if (summaryBlocks.length > 0) {
      root.querySelectorAll('p,div,section').forEach((el) => {
        if (el.closest('.seo-summary')) return
        const text = String(el.textContent || '').replace(/\s+/g, ' ').trim()
        if (/^摘要[:：]/.test(text)) {
          el.remove()
        }
      })
    }

    if (metadataBlocks.length > 0) {
      root.querySelectorAll('p,div,section').forEach((el) => {
        if (el.closest('.seo-metadata')) return
        const text = String(el.textContent || '').replace(/\s+/g, ' ').trim()
        if (/(關鍵詞|关键词)/.test(text) && /(發佈日期|發布日期|发布日期)/.test(text)) {
          el.remove()
        }
      })
    }

    let h2Index = 0
    let h3Index = 0
    const seenHeadingText = new Set<string>()
    const toc: TocItem[] = []
    root.querySelectorAll('h2, h3').forEach((node) => {
      const tagName = node.tagName.toLowerCase()
      const level = tagName === 'h2' ? 2 : 3
      const rawText = String(node.textContent || '').replace(/\s+/g, ' ').trim()
      const baseText = stripHeadingNumber(rawText)
      if (!baseText) return

      let numbered = baseText
      if (level === 2) {
        h2Index += 1
        h3Index = 0
        numbered = `${h2Index}. ${baseText}`
      } else {
        if (h2Index <= 0) h2Index = 1
        h3Index += 1
        numbered = `${h2Index}.${h3Index} ${baseText}`
      }

      const dedupeKey = numbered.toLowerCase()
      if (seenHeadingText.has(dedupeKey)) return
      seenHeadingText.add(dedupeKey)

      node.textContent = numbered
      const id = `sec-${level === 2 ? `${h2Index}` : `${h2Index}-${h3Index}`}-${slugifyHeading(baseText)}`
      node.setAttribute('id', id)
      toc.push({ id, text: numbered, level })
    })

    return { html: root.innerHTML, toc }
  } catch (err) {
    console.error('鏂囩珷 HTML 娓呮礂澶辫触锛屽凡闄嶇骇涓虹函鏂囨湰娓叉煋:', err)
    return { html: escapeHtml(rawText).replace(/\n/g, '<br />'), toc: [] }
  }
}

const scrollToHeading = (id: string) => {
  if (typeof window === 'undefined') return
  const target = document.getElementById(id)
  if (!target) return
  const y = target.getBoundingClientRect().top + window.scrollY - 112
  window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' })
  activeHeadingId.value = id
}

const loadSidebarData = async () => {
  try {
    sidebarLoading.value = true
    const [hotRows, latestRows] = await Promise.all([
      getHotGames().catch(() => [] as RechargeGame[]),
      getArticles().catch(() => [] as Article[]),
    ])

    hotGames.value = hotRows.slice(0, 8)
    const currentId = String(article.value?.id || '')
    latestArticles.value = latestRows
      .filter((item) => String(item.id || '') !== currentId)
      .slice(0, 8)
  } finally {
    sidebarLoading.value = false
  }
}

const loadArticle = async () => {
  try {
    loading.value = true
    error.value = ''
    const rawId = route.params.id
    const id = Array.isArray(rawId) ? rawId[0] : String(rawId || '')
    article.value = await getArticleDetail(id)
    const rendered = buildRenderedArticle(article.value?.content)
    renderedArticleHtml.value = rendered.html
    tocItems.value = rendered.toc
    activeHeadingId.value = rendered.toc[0]?.id || ''
    resetHeroImageByCandidates(rendered.html)
    await setupHeadingObserver()
    await loadSidebarData()
  } catch (err: any) {
    console.error('鍔犺浇鏂囩珷澶辫触:', err)
    error.value = '鏂囩珷涓嶅瓨鍦ㄦ垨鍔犺浇澶辫触'
    article.value = null
    renderedArticleHtml.value = ''
    tocItems.value = []
    hotGames.value = []
    latestArticles.value = []
    heroImageSrc.value = ''
    heroImageFallbackQueue.value = []
    stopHeadingObserver()
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    loadArticle()
  }
)

const handleWindowScroll = () => {
  updateActiveHeadingByPosition()
}

onMounted(() => {
  loadArticle()
  window.addEventListener('scroll', handleWindowScroll, { passive: true })
})

onUnmounted(() => {
  stopHeadingObserver()
  window.removeEventListener('scroll', handleWindowScroll)
})
</script>

<style scoped>
.article-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}

.article-sidebar {
  display: none;
}

.article-main {
  min-width: 0;
}

.sidebar-sticky {
  position: fixed;
  top: 112px;
  z-index: 18;
  overflow: visible;
  max-height: none;
}

.sidebar-stack {
  display: grid;
  gap: 0.95rem;
}

.sidebar-title {
  font-size: 1.02rem;
  font-weight: 700;
  color: hsl(var(--foreground));
  margin-bottom: 0.7rem;
}

.toc-nav {
  display: grid;
  gap: 0.35rem;
  max-height: 52vh;
  overflow-y: auto;
  padding-right: 0.28rem;
  overscroll-behavior: contain;
  scrollbar-width: thin;
}

.toc-nav::-webkit-scrollbar {
  width: 8px;
}

.toc-nav::-webkit-scrollbar-thumb {
  background: hsl(var(--border));
  border-radius: 999px;
}

.toc-link {
  display: block;
  padding: 0.52rem 0.6rem;
  border-radius: 0.55rem;
  border: 1px solid transparent;
  color: hsl(var(--muted-foreground));
  font-size: 0.86rem;
  line-height: 1.48;
  transition: all 0.2s ease;
}

.toc-link:hover {
  color: hsl(var(--foreground));
  border-color: hsl(var(--border));
  background: hsl(var(--muted) / 0.46);
}

.toc-link.level-3 {
  padding-left: 1.15rem;
  font-size: 0.8rem;
}

.toc-link.active {
  color: hsl(var(--foreground));
  border-color: hsl(var(--primary) / 0.32);
  background: hsl(var(--primary) / 0.12);
}

.toc-empty,
.sidebar-loading,
.sidebar-empty {
  font-size: 0.84rem;
  color: hsl(var(--muted-foreground));
  line-height: 1.58;
}

.sidebar-list-item {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 0.65rem;
  align-items: center;
  padding: 0.45rem;
  border-radius: 0.68rem;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.sidebar-list-item:hover {
  border-color: hsl(var(--border));
  background: hsl(var(--muted) / 0.4);
}

.sidebar-thumb {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 0.55rem;
  border: 1px solid hsl(var(--border));
  background: hsl(var(--muted));
}

.sidebar-item-copy {
  min-width: 0;
}

.sidebar-item-title {
  color: hsl(var(--foreground));
  font-size: 0.83rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sidebar-item-sub {
  color: hsl(var(--muted-foreground));
  font-size: 0.74rem;
  margin-top: 0.2rem;
}

@media (min-width: 1280px) {
  .article-layout {
    grid-template-columns: 250px minmax(0, 1fr) 280px;
    gap: 1.2rem;
  }

  .article-sidebar {
    display: block;
  }

  .article-sidebar-left .sidebar-sticky {
    width: 250px;
    left: max(16px, calc((100vw - 1540px) / 2 + 16px));
    max-height: calc(100vh - 128px);
    overflow: hidden;
  }

  .article-sidebar-right .sidebar-sticky {
    width: 280px;
    right: max(16px, calc((100vw - 1540px) / 2 + 16px));
    max-height: calc(100vh - 128px);
    overflow-y: auto;
    overscroll-behavior: contain;
    scrollbar-width: thin;
  }

  .article-sidebar-right .sidebar-sticky::-webkit-scrollbar {
    width: 8px;
  }

  .article-sidebar-right .sidebar-sticky::-webkit-scrollbar-thumb {
    background: hsl(var(--border));
    border-radius: 999px;
  }
}

.article-content :deep(a) {
  color: hsl(var(--primary));
  text-decoration: underline;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3) {
  color: hsl(var(--foreground));
  line-height: 1.4;
  margin: 1.15em 0 0.6em;
}

.article-content :deep(h2) {
  font-size: 1.28rem;
  scroll-margin-top: 118px;
}

.article-content :deep(h3) {
  font-size: 1.08rem;
  scroll-margin-top: 118px;
}

.article-content :deep(p) {
  margin: 0.75em 0;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 0.7em 0;
  padding-left: 1.25rem;
}

.article-content :deep(li) {
  margin: 0.35em 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  border: 1px solid hsl(var(--border));
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid hsl(var(--border));
  padding: 0.55rem 0.65rem;
  text-align: left;
}

.article-content :deep(th) {
  background: hsl(var(--muted));
  color: hsl(var(--foreground));
  font-weight: 600;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.7rem;
  margin: 0.9rem 0;
}

.article-content :deep(blockquote) {
  border-left: 3px solid hsl(var(--primary));
  padding-left: 0.8rem;
  color: hsl(var(--muted-foreground));
  margin: 0.9rem 0;
}

.article-content :deep(code) {
  background: hsl(var(--muted));
  padding: 0.1rem 0.35rem;
  border-radius: 0.25rem;
}

.article-content :deep(pre) {
  background: hsl(var(--muted));
  padding: 0.8rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

.article-content :deep(.seo-article-shell) {
  display: block;
}

.article-content :deep(.seo-article-header h1) {
  margin-top: 0.1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.55rem;
  border-bottom: 2px solid hsl(var(--primary) / 0.35);
}

.article-content :deep(.seo-summary) {
  margin: 0.8rem 0 1.1rem;
  padding: 0.85rem 1rem;
  border-left: 4px solid hsl(var(--primary));
  border-radius: 0.45rem;
  background: hsl(var(--muted) / 0.55);
  color: hsl(var(--foreground));
}

.article-content :deep(.seo-media-block) {
  margin-top: 1.35rem;
}

.article-content :deep(.seo-media-gallery) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.8rem;
  margin-top: 0.7rem;
}

.article-content :deep(.seo-media-item) {
  margin: 0;
  border: 1px solid hsl(var(--border));
  border-radius: 0.65rem;
  overflow: hidden;
  background: hsl(var(--card));
}

.article-content :deep(.seo-media-item img) {
  margin: 0;
  width: 100%;
  height: 145px;
  object-fit: cover;
  border-radius: 0;
}

.article-content :deep(.seo-media-item figcaption) {
  padding: 0.45rem 0.55rem;
  font-size: 0.78rem;
  color: hsl(var(--muted-foreground));
}

.article-content :deep(.seo-inline-media) {
  margin: 0.9rem 0 1.1rem;
}

.article-content :deep(.seo-inline-media img) {
  width: 100%;
  max-height: 460px;
  object-fit: cover;
  border: 1px solid hsl(var(--border));
}

.article-content :deep(.seo-inline-media figcaption) {
  margin-top: 0.3rem;
  font-size: 0.78rem;
  color: hsl(var(--muted-foreground));
}

.article-content :deep(.seo-quick-facts) {
  margin-top: 1.25rem;
}

.article-content :deep(.seo-quick-facts-table th) {
  width: 130px;
}

.article-content :deep(.seo-metadata) {
  margin-top: 1.2rem;
  padding: 0.8rem 0.95rem;
  border: 1px solid hsl(var(--border));
  border-radius: 0.65rem;
  background: hsl(var(--muted) / 0.5);
}

.article-content :deep(.seo-metadata p) {
  margin: 0.3rem 0;
}

.article-content :deep(.seo-internal-link) {
  margin-top: 1rem;
  padding-top: 0.65rem;
  border-top: 1px dashed hsl(var(--border));
}
</style>


