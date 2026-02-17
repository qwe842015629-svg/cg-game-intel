<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <section class="border-b border-gray-200 bg-white">
      <div class="mx-auto max-w-[1500px] px-4 pb-8 pt-12 md:px-6">
        <span class="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-[11px] tracking-wider text-blue-600 font-semibold">
          CG GAME INTEL ENGINE V2
        </span>
        <div class="mt-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 class="text-3xl font-black tracking-tight md:text-5xl text-gray-900">CG 游戏百事通</h1>
            <p class="mt-3 max-w-3xl text-sm leading-relaxed text-gray-500 md:text-base">
              聚合全球榜单、开服情报、热门攻略和 Wiki 雷达，支持 CN/US/JP 榜单切换并自动标记「全球热门」。
            </p>
          </div>
          <span class="text-xs text-gray-400">数据更新：{{ lastUpdated || "未同步" }}</span>
        </div>
      </div>
    </section>

    <!-- Top Horizontal Ticker (Marquee) -->
    <div class="border-b border-gray-200 bg-white overflow-hidden relative group shadow-sm z-10">
      <div class="mx-auto max-w-[1600px] px-4 md:px-6">
        <div class="flex items-center gap-2 py-2 marquee-horizontal-wrapper overflow-hidden" :class="{ 'paused': isMarqueePaused }" @mouseenter="isMarqueePaused = true" @mouseleave="isMarqueePaused = false">
          <div class="flex items-center gap-8 whitespace-nowrap marquee-horizontal-content">
             <a 
               v-for="(item, idx) in [...strategies, ...strategies]" 
               :key="`ticker-${idx}`"
               :href="item.link" 
               target="_blank" 
               rel="noopener noreferrer"
               class="flex items-center gap-2 hover:opacity-80 transition-opacity text-sm text-gray-600 hover:text-blue-600"
             >
               <span 
                 class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase"
                 :class="sourceColorMap[item.source] || sourceColorMap['default']"
               >
                 {{ item.source }}
               </span>
               <span class="font-medium">{{ item.title }}</span>
             </a>
          </div>
        </div>
      </div>
    </div>

    <main class="mx-auto grid max-w-[1600px] grid-cols-1 gap-6 px-4 py-6 md:px-6 xl:grid-cols-[300px_minmax(0,1fr)_340px] h-[calc(100vh-220px)] min-h-[750px]">
      <aside class="space-y-6 flex flex-col h-full overflow-hidden">
        <section class="panel-card p-5 flex-shrink-0">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-gray-800">市场晴雨表</h2>
            <span class="text-[11px] text-gray-400">海外手游热度分布</span>
          </div>
          <div class="mt-4 flex justify-center">
            <div class="gauge-ring" :style="marketGaugeStyle">
              <div class="gauge-center">
                <p class="text-[10px] uppercase tracking-wider text-gray-400">Heat</p>
                <p class="text-xl font-black text-gray-800">{{ totalHeatScore }}</p>
              </div>
            </div>
          </div>
          <ul class="mt-4 space-y-2">
            <li v-for="slice in marketHeat" :key="slice.region" class="heat-row" :style="{ borderColor: `${slice.color}66` }">
              <div class="flex items-center gap-2">
                <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: slice.color }"></span>
                <span class="text-xs text-gray-600">{{ slice.label }}</span>
              </div>
              <span class="text-xs font-semibold text-gray-800">{{ slice.percent.toFixed(1) }}%</span>
            </li>
          </ul>
        </section>

        <section class="panel-card p-5 flex-1 flex flex-col min-h-0">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-bold text-gray-800">开服时间轴</h2>
            <span class="text-[11px] text-gray-400">纵向卡片流</span>
          </div>
          <div class="relative flex-1 overflow-auto pr-1 timeline-scroll">
            <div class="absolute bottom-1 left-[9px] top-1 w-px bg-gray-200"></div>
            <article v-for="item in timelineReleases" :key="item.id" class="timeline-item group hover:border-blue-300 hover:bg-blue-50/30 transition-colors">
              <span class="timeline-dot"></span>
              <img :src="item.thumbnail || defaultCover" :alt="item.title" class="h-10 w-10 rounded-lg border border-gray-200 bg-gray-100 object-cover" @error="onImageError" />
              <div class="min-w-0 flex-1">
                <h3 class="truncate text-sm font-semibold text-gray-800 group-hover:text-blue-600">{{ item.title }}</h3>
                <p class="mt-1 truncate text-[11px] text-gray-500">{{ item.genre }} · {{ item.publisher || "未知发行商" }}</p>
                <p class="mt-1 text-[10px] text-blue-500 font-medium">{{ formatRelease(item.release_date) }} · {{ releasePhase(item.release_date) }}</p>
              </div>
              <button type="button" class="mini-btn" @click="openLink(item.game_url)">详情</button>
            </article>
          </div>
        </section>
      </aside>

      <section class="panel-card p-5 md:p-6 flex flex-col h-full overflow-hidden">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4 flex-shrink-0">
          <div class="flex items-center gap-2">
            <h2 class="text-lg font-black md:text-xl text-gray-900">全球榜单竞技场</h2>
            <button 
              type="button" 
              class="p-1 hover:bg-gray-100 rounded-full transition-colors"
              @click="loadData"
              title="手动更新榜单"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 hover:text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          <div class="tab-wrap">
            <button
              v-for="region in rankingRegions"
              :key="region"
              type="button"
              class="tab-btn"
              :class="{ active: activeRankingRegion === region }"
              @click="activeRankingRegion = region"
            >
              {{ regionLabelMap[region] }}
            </button>
          </div>
        </div>

        <article v-if="topGame" class="top-spotlight mb-5 flex-shrink-0" :style="spotlightStyle">
          <div class="absolute inset-0 bg-white/90 backdrop-blur-sm"></div>
          <div class="relative z-10 flex flex-col gap-3 p-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p class="text-xs uppercase tracking-[0.2em] text-blue-600 font-bold">Top 1 Featured</p>
              <h3 class="mt-2 text-2xl font-black md:text-3xl text-gray-900">{{ topGame.title }}</h3>
              <p class="mt-1 text-sm text-gray-500">{{ topGame.author || "未知发行商" }}</p>
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <span class="badge-rank">#{{ topGame.rank }}</span>
                <span v-if="topGame.global_hot" class="badge-global">全球热门</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <img :src="topGame.icon || defaultCover" :alt="topGame.title" class="h-16 w-16 rounded-2xl border border-gray-200 object-cover shadow-md" @error="onImageError" />
              <button type="button" class="mini-btn text-blue-600 border-blue-200 hover:bg-blue-50" @click="openLink(topGame.url)">查看详情</button>
            </div>
          </div>
        </article>

        <div :key="activeRankingRegion" class="flex-1 overflow-y-auto pr-2 custom-scrollbar relative min-h-0">
          <TransitionGroup name="rank-stagger" tag="div" class="space-y-3">
            <article
              v-for="(game, index) in currentRanking"
              :key="`${activeRankingRegion}-${game.id}-${game.rank}`"
              class="rank-row group"
              :class="{ 'rank-row-top3': game.rank <= 3 }"
              :style="{ '--stagger-delay': `${Math.min(index * 20, 1000)}ms`, '--from-x': index % 2 === 0 ? '-26px' : '26px' }"
            >
              <div class="rank-no" :class="{ top: game.rank <= 3 }">{{ game.rank }}</div>
              <img :src="game.icon || defaultCover" :alt="game.title" loading="lazy" class="h-10 w-10 rounded-lg border border-gray-200 bg-gray-50 object-cover group-hover:scale-105 transition-transform" @error="onImageError" />
              <div class="min-w-0 flex-1">
                <h4 class="truncate text-sm font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">{{ game.title }}</h4>
                <p class="truncate text-[11px] text-gray-500">{{ game.author || "未知" }}</p>
              </div>
              <span v-if="game.global_hot" class="global-tag">全球热门</span>
              <button type="button" class="mini-btn" @click="openLink(game.url)">跳转</button>
            </article>
          </TransitionGroup>
        </div>
      </section>

      <aside class="space-y-6 flex flex-col h-full overflow-hidden">
        <section class="panel-card p-5 flex-1 flex flex-col min-h-0 overflow-hidden">
          <div class="flex items-center justify-between mb-4 flex-shrink-0">
            <h2 class="text-base font-bold text-gray-800">海内外游戏热榜</h2>
            <div class="flex items-center gap-2">
               <span class="text-[10px] text-gray-400">实时滚动</span>
               <button 
                 type="button" 
                 class="p-1 hover:bg-gray-100 rounded-full transition-colors"
                 @click="loadData"
                 title="手动更新情报"
               >
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-gray-400 hover:text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                 </svg>
               </button>
            </div>
          </div>
          
          <div class="flex-1 overflow-y-auto pr-1 custom-scrollbar space-y-2 min-h-0">
              <a
                v-for="(item, idx) in strategies"
                :key="`list-${idx}`"
                :href="item.link"
                target="_blank"
                rel="noopener noreferrer"
                class="block group/item border-b border-gray-100 pb-2 last:border-0 hover:bg-gray-50 p-2 rounded-md transition-colors"
              >
                <div class="flex flex-col gap-1.5">
                  <div class="flex items-center justify-between">
                     <span 
                       class="px-1.5 py-0.5 rounded-[4px] text-[10px] font-bold shadow-sm"
                       :class="sourceColorMap[item.source] || sourceColorMap['default']"
                     >
                       {{ item.source }}
                     </span>
                     <span class="text-[10px] text-gray-400 font-mono">{{ item.time.substring(5) }}</span>
                  </div>
                  <h3 class="text-[13px] leading-snug font-medium text-gray-700 group-hover/item:text-blue-600 transition-colors line-clamp-2">
                      {{ item.title }}
                  </h3>
                  <div class="flex justify-end mt-0.5 opacity-0 group-hover/item:opacity-100 transition-opacity">
                    <span class="text-[10px] text-blue-500 flex items-center gap-0.5 cursor-pointer hover:underline">
                      阅读原文 
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </span>
                  </div>
                </div>
              </a>
          </div>
        </section>

        <section class="panel-card p-0 h-[200px] flex-shrink-0 flex flex-col overflow-hidden bg-gray-900 border-gray-800">
          <div class="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
            <h2 class="text-xs font-bold text-gray-300 font-mono">TERMINAL > WIKI_LOG</h2>
            <span class="text-[10px] text-gray-500 animate-pulse">● LIVE</span>
          </div>
          <div class="terminal-screen flex-1">
            <p v-for="(line, idx) in terminalLines" :key="`term-${idx}-${line.link}`" class="terminal-line">
              <span class="terminal-time">[{{ formatTerminalTime(line.time) }}]</span>
              <a :href="line.link" target="_blank" rel="noopener noreferrer" class="hover:underline hover:text-white transition-colors">{{ line.title }}</a>
            </p>
            <p v-if="terminalLines.length === 0" class="terminal-line text-gray-600">[WAITING] Connecting to Wiki feed...</p>
            <p class="terminal-cursor">_</p>
          </div>
        </section>
      </aside>
    </main>

    <div v-if="isLoading" class="fixed inset-0 z-40 grid place-items-center bg-white/80 backdrop-blur-sm">
      <div class="rounded-xl border border-gray-200 bg-white shadow-xl px-5 py-4 text-center">
        <div class="loader-spin mx-auto"></div>
        <p class="mt-3 text-xs text-gray-500">情报引擎加载中...</p>
      </div>
    </div>

    <div v-if="loadError && !isLoading" class="mx-auto max-w-[1500px] px-4 pb-6 md:px-6">
      <div class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
        {{ loadError }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { useLanguageStore } from "../stores/language"

type RankingRegion = "CN" | "US" | "JP" | "HK" | "TW" | "SEA"

interface RankingGame {
  id: string
  rank: number
  title: string
  icon: string
  author: string
  url: string
  global_hot: boolean
  global_hot_regions: string[]
}

interface ReleaseGame {
  id: string
  title: string
  thumbnail: string
  genre: string
  publisher?: string
  release_date: string
  game_url: string
}

interface StrategyFeedItem {
  title: string
  link: string
  is_high_value: boolean
  weight_score: number
  time: string
  source: string
  source_icon?: string
  image?: string
}

interface WikiFeedItem {
  title: string
  link: string
  time: string
  source?: string
}

interface HubPayload {
  last_updated: string
  rankings: Record<RankingRegion, RankingGame[]>
  new_releases: ReleaseGame[]
  strategies: StrategyFeedItem[]
  wiki_radar: WikiFeedItem[]
}

interface LegacyRawGame {
  id: string
  title: string
  thumbnail?: string
  icon?: string
  game_url?: string
  genre?: string
  publisher?: string
  release_date?: string
}

interface LegacyPayload {
  last_updated: string
  hot_games?: LegacyRawGame[]
  new_releases?: Record<string, LegacyRawGame[]>
}

const languageStore = useLanguageStore()
const rankingRegions: RankingRegion[] = ["CN", "US", "JP", "HK", "TW", "SEA"]
const regionLabelMap: Record<RankingRegion, string> = { 
  CN: "中国区", 
  US: "美国区", 
  JP: "日本区",
  HK: "香港区",
  TW: "台湾区",
  SEA: "东南亚"
}
const colorMap: Record<RankingRegion, string> = { 
  CN: "#22d3ee", 
  US: "#f59e0b", 
  JP: "#34d399",
  HK: "#e879f9",
  TW: "#818cf8",
  SEA: "#facc15"
}

const sourceColorMap: Record<string, string> = {
  "巴哈姆特": "tag-emerald",
  "机核网": "tag-red",
  "触乐": "tag-amber",
  "爱玩网": "tag-rose",
  "游研社": "tag-indigo",
  "4Gamers": "tag-green",
  "Yahoo电竞": "tag-purple",
  "DoNews游戏": "tag-blue",
  "游民星空": "tag-orange",
  "default": "tag-slate"
}

const defaultCover = "https://placehold.co/96x96/0f172a/94a3b8?text=GAME"

const keywordWeights: Record<string, number> = {
  "tier list": 4,
  meta: 3,
  build: 3,
  guide: 2,
  best: 1,
  reroll: 2,
  codes: 1,
}

const genreAliasMap: Record<string, string> = {
  "Role Playing": "角色扮演",
  RolePlaying: "角色扮演",
  Action: "动作",
  Adventure: "冒险",
  Strategy: "策略",
  Casual: "休闲",
  Shooter: "射击",
}

const titleAliasById: Record<string, string> = {
  "com.miHoYo.GenshinImpact": "原神",
  "com.blizzard.diablo.immortal": "暗黑破坏神：不朽",
  "com.levelinfinite.sgameGlobal": "王者荣耀国际服",
}

const rankings = ref<Record<RankingRegion, RankingGame[]>>({ CN: [], US: [], JP: [], HK: [], TW: [], SEA: [] })
const newReleases = ref<ReleaseGame[]>([])
const strategies = ref<StrategyFeedItem[]>([])
const wikiRadar = ref<WikiFeedItem[]>([])
const activeRankingRegion = ref<RankingRegion>("CN")
const lastUpdated = ref("")
const isLoading = ref(true)
const isMarqueePaused = ref(false)
const loadError = ref("")
const terminalLines = ref<WikiFeedItem[]>([])
const terminalPointer = ref(0)
let terminalTimer: ReturnType<typeof setInterval> | null = null

const rankingTotal = computed(() => rankingRegions.reduce((sum, region) => sum + (rankings.value[region]?.length || 0), 0))
const highValueCount = computed(() => strategies.value.filter((item) => item.is_high_value).length)
const currentRanking = computed(() => rankings.value[activeRankingRegion.value] || [])
const topGame = computed(() => currentRanking.value[0] || null)
const timelineReleases = computed(() =>
  [...newReleases.value].sort((a, b) => parseDate(b.release_date).getTime() - parseDate(a.release_date).getTime()).slice(0, 12)
)

const marketHeat = computed(() => {
  const raw = rankingRegions.map((region) => {
    const score = (rankings.value[region] || []).reduce((sum, game) => sum + Math.max(16 - game.rank, 1) + (game.global_hot ? 6 : 0), 0)
    return { region, label: regionLabelMap[region], score, percent: 0, color: colorMap[region] }
  })
  const total = raw.reduce((sum, row) => sum + row.score, 0)
  if (total <= 0) return raw
  return raw.map((row) => ({ ...row, percent: (row.score / total) * 100 }))
})

const totalHeatScore = computed(() => Math.round(marketHeat.value.reduce((sum, row) => sum + row.score, 0)))

const marketGaugeStyle = computed(() => {
  if (!totalHeatScore.value) return { background: "conic-gradient(#334155 0 100%)" }
  let cursor = 0
  const parts = marketHeat.value.map((row) => {
    const start = cursor
    cursor += row.percent
    return `${row.color} ${start}% ${cursor}%`
  })
  return { background: `conic-gradient(${parts.join(", ")})` }
})

const spotlightStyle = computed(() => {
  if (!topGame.value) return {}
  return {
    backgroundImage: `linear-gradient(120deg, rgba(255, 255, 255, 0.95), rgba(243, 244, 246, 0.85)), url(${topGame.value.icon || defaultCover})`,
    backgroundPosition: "center",
    backgroundSize: "cover",
  }
})

const parseDate = (value: string): Date => {
  if (!value) return new Date(0)
  const normalized = value.includes(" ") ? value.replace(" ", "T") : value
  const date = new Date(normalized)
  return Number.isNaN(date.getTime()) ? new Date(0) : date
}

const formatRelease = (value: string): string => {
  const date = parseDate(value)
  return date.getTime() ? date.toLocaleDateString("zh-CN", { month: "2-digit", day: "2-digit" }) : "日期待定"
}

const formatFeedTime = (value: string): string => {
  const date = parseDate(value)
  return date.getTime()
    ? date.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false })
    : "刚刚"
}

const formatTerminalTime = (value: string): string => {
  const date = parseDate(value)
  return date.getTime()
    ? date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false })
    : "00:00:00"
}

const releasePhase = (value: string): string => {
  const d = parseDate(value)
  if (!d.getTime()) return "持续更新"
  const diff = Math.floor((Date.now() - d.getTime()) / (24 * 60 * 60 * 1000))
  if (diff < 0) return `预计 ${Math.abs(diff)} 天后开服`
  if (diff <= 3) return "新服冲榜期"
  if (diff <= 10) return "活跃窗口"
  return "稳定运营"
}

const inferTitleFromId = (id: string): string => {
  const tail = (id || "").split(".").pop() || id || "game"
  return tail.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/[_-]/g, " ").replace(/\s+/g, " ").trim()
}

const normalizeTitle = (id: string, title: string): string => {
  if (titleAliasById[id]) return titleAliasById[id]
  return title || inferTitleFromId(id)
}

const normalizeGenre = (genre: string): string => {
  if (!genre) return "综合"
  return genreAliasMap[genre] || genre
}

const keywordWeight = (text: string): number => {
  const lower = text.toLowerCase()
  return Object.entries(keywordWeights).reduce((sum, [key, weight]) => (lower.includes(key) ? sum + weight : sum), 0)
}

const normalizeRankingEntry = (entry: any, rank: number): RankingGame => ({
  id: String(entry?.id || `${entry?.title || "game"}-${rank}`),
  rank: Number(entry?.rank || rank),
  title: normalizeTitle(String(entry?.id || ""), String(entry?.title || "")),
  icon: String(entry?.icon || ""),
  author: String(entry?.author || entry?.artist || "未知"),
  url: String(entry?.url || entry?.link || ""),
  global_hot: Boolean(entry?.global_hot),
  global_hot_regions: Array.isArray(entry?.global_hot_regions) ? entry.global_hot_regions : [],
})

const applyGlobalHot = (raw: Record<RankingRegion, RankingGame[]>): Record<RankingRegion, RankingGame[]> => {
  const buckets: Record<string, Set<RankingRegion>> = {}
  rankingRegions.forEach((region) => {
    raw[region]?.forEach((game) => {
      const key = game.title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, "")
      if (!key) return
      if (!buckets[key]) buckets[key] = new Set<RankingRegion>()
      buckets[key].add(region)
    })
  })
  const resolve = (game: RankingGame): RankingGame => {
    const key = game.title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, "")
    const regions = key ? Array.from(buckets[key] || []) : []
    return { ...game, global_hot: game.global_hot || regions.length >= 2, global_hot_regions: regions }
  }
  
  const result = {} as Record<RankingRegion, RankingGame[]>
  rankingRegions.forEach(region => {
    result[region] = (raw[region] || []).map(resolve)
  })
  return result
}

const normalizeHubPayload = (payload: any): HubPayload => {
  const rawRankings = {} as Record<RankingRegion, RankingGame[]>
  rankingRegions.forEach(region => {
    rawRankings[region] = (payload?.rankings?.[region] || []).map((row: any, idx: number) => normalizeRankingEntry(row, idx + 1))
  })

  return {
    last_updated: String(payload?.last_updated || ""),
    rankings: applyGlobalHot(rawRankings),
    new_releases: (payload?.new_releases || []).map((row: any, idx: number) => ({
      id: String(row?.id || `release-${idx + 1}`),
      title: normalizeTitle(String(row?.id || ""), String(row?.title || "")),
      thumbnail: String(row?.thumbnail || row?.icon || ""),
      genre: normalizeGenre(String(row?.genre || "Game")),
      publisher: String(row?.publisher || ""),
      release_date: String(row?.release_date || ""),
      game_url: String(row?.game_url || row?.url || ""),
    })),
    strategies: (payload?.strategies || []).map((row: any) => {
      const score = Number(row?.weight_score || keywordWeight(String(row?.title || "")))
      return {
        title: String(row?.title || "未命名攻略"),
        link: String(row?.link || "#"),
        is_high_value: Boolean(row?.is_high_value ?? score >= 3),
        weight_score: score,
        time: String(row?.time || ""),
        source: String(row?.source || "Feed"),
        source_icon: String(row?.source_icon || ""),
        image: String(row?.image || "")
      }
    }),
    wiki_radar: (payload?.wiki_radar || []).map((row: any) => ({
      title: String(row?.title || "Wiki 动态"),
      link: String(row?.link || "#"),
      time: String(row?.time || ""),
      source: String(row?.source || "Wiki"),
    })),
  }
}

const convertLegacyToHub = (legacy: LegacyPayload): HubPayload => {
  // Legacy mapping (approximate)
  const map: Partial<Record<RankingRegion, string>> = { CN: "hktw", US: "us", JP: "sea", HK: "hktw", TW: "hktw", SEA: "sea" }
  const rankingRaw = {} as Record<RankingRegion, RankingGame[]>
  
  rankingRegions.forEach((region) => {
    const legacyKey = map[region]
    const list = legacyKey ? (legacy?.new_releases?.[legacyKey] || []) : []
    rankingRaw[region] = list.slice(0, 15).map((game, idx) =>
      normalizeRankingEntry(
        {
          id: game.id,
          rank: idx + 1,
          title: game.title,
          icon: game.icon || game.thumbnail,
          author: game.publisher || "未知",
          url: game.game_url,
          genre: game.genre || "Game",
        },
        idx + 1
      )
    )
  })

  const mergedReleases = [
    ...(legacy?.new_releases?.hktw || []),
    ...(legacy?.new_releases?.us || []),
    ...(legacy?.new_releases?.sea || []),
  ]

  const legacyStrategies: StrategyFeedItem[] = (legacy?.hot_games || []).slice(0, 16).map((game) => {
    const gameTitle = normalizeTitle(String(game.id || ""), String(game.title || ""))
    const title = `${gameTitle || "Game"} Tier List Build Guide`
    const score = keywordWeight(title)
    return {
      title,
      link: `https://www.google.com/search?q=${encodeURIComponent((gameTitle || "game") + " Tier List Build Guide")}`,
      is_high_value: score >= 3,
      weight_score: score,
      time: legacy.last_updated || new Date().toISOString(),
      source: "LegacyHub",
    }
  })

  return normalizeHubPayload({
    last_updated: legacy.last_updated,
    rankings: rankingRaw,
    new_releases: mergedReleases,
    strategies: legacyStrategies,
    wiki_radar: legacyStrategies.slice(0, 8).map((row) => ({ title: `Wiki Mirror: ${row.title}`, link: row.link, time: row.time, source: "LegacyFallback" })),
  })
}

const applyPayload = (payload: HubPayload): void => {
  rankings.value = payload.rankings || { CN: [], US: [], JP: [], HK: [], TW: [], SEA: [] }
  newReleases.value = payload.new_releases || []
  strategies.value = payload.strategies || []
  wikiRadar.value = payload.wiki_radar || []
  lastUpdated.value = formatFeedTime(payload.last_updated)
}

const pushTerminalLine = (): void => {
  if (!wikiRadar.value.length) return
  const line = wikiRadar.value[terminalPointer.value % wikiRadar.value.length]
  terminalLines.value = [...terminalLines.value, line].slice(-10)
  terminalPointer.value += 1
}

const resetTerminal = (): void => {
  terminalLines.value = []
  terminalPointer.value = 0
  for (let i = 0; i < Math.min(4, wikiRadar.value.length); i += 1) pushTerminalLine()
  if (terminalTimer) clearInterval(terminalTimer)
  terminalTimer = setInterval(pushTerminalLine, 5000)
}

watch(wikiRadar, () => resetTerminal(), { deep: false })

const onImageError = (event: Event): void => {
  const target = event.target as HTMLImageElement
  if (target && target.src !== defaultCover) target.src = defaultCover
}

const openLink = (url: string): void => {
  if (!url || url === "#") return
  window.open(url, "_blank", "noopener,noreferrer")
}

const loadData = async (): Promise<void> => {
  isLoading.value = true
  loadError.value = ""
  try {
    const response = await fetch("/data/game_hub.json", { cache: "no-store" })
    if (response.ok) {
      applyPayload(normalizeHubPayload(await response.json()))
    } else {
      throw new Error(`game_hub.json: ${response.status}`)
    }
  } catch (error) {
    console.warn("game_hub.json 加载失败，尝试回退到 games_sync.json", error)
    try {
      const response = await fetch("/data/games_sync.json", { cache: "no-store" })
      if (!response.ok) throw new Error(`games_sync.json: ${response.status}`)
      applyPayload(convertLegacyToHub((await response.json()) as LegacyPayload))
      loadError.value = "当前显示的是兼容回退数据（games_sync.json）。"
    } catch (fallbackError) {
      console.error("CG 游戏百事通数据加载失败", fallbackError)
      loadError.value = "数据加载失败，请稍后刷新或检查同步任务。"
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (languageStore.currentLocale !== "zh-CN") languageStore.setLocale("zh-CN")
  void loadData()
})

onUnmounted(() => {
  if (terminalTimer) clearInterval(terminalTimer)
})
</script>

<style scoped>
.cg-hub-bg {
  /* Removed dark gradients */
}

.hero-metric {
  border: 1px solid rgba(226, 232, 240, 1);
  border-radius: 12px;
  padding: 10px 12px;
  background: #fff;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.metric-label {
  font-size: 11px;
  color: #64748b;
}

.metric-value {
  margin-top: 4px;
  font-size: 1.35rem;
  line-height: 1.2;
  font-weight: 800;
  color: #1e293b;
}

.panel-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.panel-glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.gauge-ring {
  width: 170px;
  height: 170px;
  border-radius: 999px;
  padding: 14px;
  box-shadow: inset 0 0 0 1px rgba(226, 232, 240, 0.8), 0 0 24px rgba(59, 130, 246, 0.1);
}

.gauge-center {
  width: 100%;
  height: 100%;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: radial-gradient(circle, #fff, #f8fafc);
  border: 1px solid #e2e8f0;
}

.heat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #f1f5f9;
  border-radius: 10px;
  padding: 8px 10px;
  background: #f8fafc;
}

.timeline-scroll::-webkit-scrollbar {
  width: 6px;
}

.timeline-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 999px;
}

.timeline-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px 10px 10px 22px;
  background: #fff;
  transition: all 0.2s ease;
}

.timeline-dot {
  position: absolute;
  left: 6px;
  top: 50%;
  width: 8px;
  height: 8px;
  margin-top: -4px;
  border-radius: 999px;
  background: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.tab-wrap {
  display: inline-flex;
  gap: 6px;
  padding: 4px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f1f5f9;
}

.tab-btn {
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 5px 12px;
  font-size: 12px;
  color: #64748b;
  transition: all 0.2s ease;
}

.tab-btn.active {
  color: #2563eb;
  border-color: #bfdbfe;
  background: #eff6ff;
  font-weight: 600;
}

.top-spotlight {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.badge-rank {
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 9px;
  backdrop-filter: blur(4px);
}

.badge-global,
.global-tag {
  border-radius: 999px;
  border: 1px solid #bbf7d0;
  background: #f0fdf4;
  color: #16a34a;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 9px;
}

.rank-row {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 9px 10px;
  background: #fff;
  transition: all 0.2s ease;
}

.rank-row-top3 {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.rank-no {
  width: 28px;
  text-align: center;
  font-family: "JetBrains Mono", "Courier New", monospace;
  font-size: 13px;
  font-weight: 800;
  color: #94a3b8;
}

.rank-no.top {
  color: #3b82f6;
}

.mini-btn {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #64748b;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  transition: all 0.2s ease;
}

.mini-btn:hover {
  border-color: #93c5fd;
  color: #2563eb;
  background: #eff6ff;
}

.rank-stagger-enter-active {
  transition: opacity 0.45s ease, transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1);
  transition-delay: var(--stagger-delay, 0ms);
}

.rank-stagger-enter-from {
  opacity: 0;
  transform: translate3d(var(--from-x, 24px), 18px, 0) scale(0.96);
}

.strategy-waterfall {
  column-count: 2;
  column-gap: 10px;
}

.strategy-card {
  display: inline-block;
  width: 100%;
  margin-bottom: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
  background: #fff;
  break-inside: avoid;
}

.strategy-high {
  border-color: #d8b4fe;
  box-shadow: 0 0 0 1px #e9d5ff;
}

.terminal-card {
  /* Keep terminal somewhat dark/techy but cleaner */
}

.terminal-screen {
  /* border: 1px solid #333; */
  /* background: #111; */
  /* padding: 12px; */
  /* overflow: auto; */
  font-family: "Courier New", Courier, monospace;
}

.terminal-line {
  display: flex;
  gap: 8px;
  font-size: 11px;
  line-height: 1.45;
  color: #d1d5db; /* Light gray text on dark terminal */
}

.terminal-time {
  color: #67e8f9;
  flex-shrink: 0;
}

.terminal-cursor {
  margin-top: 6px;
  color: #4ade80;
  animation: terminal-caret 0.95s step-end infinite;
}

@keyframes terminal-caret {
  50% {
    opacity: 0;
  }
}

.loader-spin {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 2px solid #cbd5e1;
  border-top-color: #3b82f6;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.tag-emerald { @apply border border-emerald-200 bg-emerald-50 text-emerald-600; }
.tag-red { @apply border border-red-200 bg-red-50 text-red-600; }
.tag-amber { @apply border border-amber-200 bg-amber-50 text-amber-600; }
.tag-rose { @apply border border-rose-200 bg-rose-50 text-rose-600; }
.tag-indigo { @apply border border-indigo-200 bg-indigo-50 text-indigo-600; }
.tag-green { @apply border border-green-200 bg-green-50 text-green-600; }
.tag-purple { @apply border border-purple-200 bg-purple-50 text-purple-600; }
.tag-blue { @apply border border-blue-200 bg-blue-50 text-blue-600; }
.tag-orange { @apply border border-orange-200 bg-orange-50 text-orange-600; }
.tag-slate { @apply border border-slate-200 bg-slate-50 text-slate-600; }

.marquee-horizontal-wrapper {
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
}

.marquee-horizontal-content {
  display: inline-flex;
  animation: scroll-left 240s linear infinite;
  padding-left: 100%;
}

.marquee-horizontal-wrapper.paused .marquee-horizontal-content {
  animation-play-state: paused;
}

@keyframes scroll-left {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}

@media (max-width: 1440px) {
  .strategy-waterfall {
    column-count: 1;
  }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 999px;
  border: 1px solid #fff;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>