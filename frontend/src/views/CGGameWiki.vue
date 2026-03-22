﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="wiki-galaxy min-h-screen bg-white text-slate-900 pb-20">
    <!-- Header Section -->
    <header class="wiki-galaxy-header bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm/50 backdrop-blur-md bg-white/90">
      <div class="mx-auto max-w-[1600px] px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-4">
           <div class="flex items-center gap-2">
             <span class="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-black italic text-lg shadow-blue-200 shadow-lg">CG</span>
             <h1 class="text-xl font-black tracking-tight text-slate-900">GAME INTEL <span class="text-blue-600">HUB</span></h1>
           </div>
           <div class="hidden md:flex h-6 w-px bg-slate-200 mx-2"></div>
           <div class="hidden md:flex items-center gap-2 bg-slate-100/50 p-1 rounded-lg">
             <span class="px-4 py-1.5 text-sm font-bold bg-white text-blue-600 shadow-sm ring-1 ring-black/5 rounded-md flex items-center gap-2">
               <BarChart3 class="w-4 h-4" />
               {{ t("cgWikiPage.header.rankMonitor") }}
             </span>
              <button 
                @click="triggerUpdate" 
                class="px-3 py-1.5 text-xs font-bold bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-md shadow-sm transition-colors flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="isUpdating"
              >
               <RefreshCw class="w-3.5 h-3.5" :class="{'animate-spin': isUpdating}" />
                {{ isUpdating ? t("cgWikiPage.header.updating") : t("cgWikiPage.header.update") }}
              </button>
           </div>
        </div>
        <div class="text-xs font-mono text-slate-400">
          SYNC: {{ lastUpdated || "WAITING..." }}
        </div>
      </div>
    </header>

    <!-- Marquee Section -->
    <div class="wiki-galaxy-ticker border-b border-slate-200 bg-white overflow-hidden relative group shadow-sm z-20">
      <div class="mx-auto max-w-[1600px] px-4">
        <div class="flex items-center gap-2 py-2 marquee-horizontal-wrapper overflow-hidden" :class="{ 'paused': isMarqueePaused }" @mouseenter="isMarqueePaused = true" @mouseleave="isMarqueePaused = false">
          <div class="flex items-center gap-8 whitespace-nowrap marquee-horizontal-content">
             <a 
               v-for="(item, idx) in [...strategies, ...strategies]" 
               :key="`ticker-${idx}`"
               :href="item.link" 
               target="_blank" 
               rel="noopener noreferrer"
               class="flex items-center gap-2 hover:opacity-80 transition-opacity text-sm text-slate-600 hover:text-blue-600"
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

    <main class="wiki-galaxy-main mx-auto max-w-[1600px] grid grid-cols-1 xl:grid-cols-[340px_1fr] gap-8 px-4 py-8 items-start">
      
      <!-- Left Sidebar -->
      <aside class="space-y-6 xl:sticky xl:top-24">
        <!-- Market Heat -->
        <section class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
              {{ t("cgWikiPage.sidebar.marketHeat") }}
            </h2>
          </div>
          <div class="flex justify-center mb-4">
            <div class="gauge-ring" :style="marketGaugeStyle">
              <div class="gauge-center flex-col">
                <p class="text-[10px] uppercase text-slate-400 font-bold">HEAT INDEX</p>
                <p class="text-2xl font-black text-slate-800">{{ totalHeatScore }}</p>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2">
             <div v-for="slice in marketHeat" :key="slice.region" class="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
               <div class="flex items-center gap-1.5">
                 <span class="w-2 h-2 rounded-full" :style="{ background: slice.color }"></span>
                 <span class="text-xs text-slate-600 font-medium">{{ slice.label }}</span>
               </div>
               <span class="text-xs font-bold text-slate-800">{{ slice.percent.toFixed(0) }}%</span>
             </div>
          </div>
        </section>

        <!-- Wiki Console -->
        <section class="game-console-frame p-3 rounded-[20px] bg-slate-800 shadow-xl border-b-4 border-r-4 border-slate-900 relative">
           <!-- Screen Bezel -->
           <div class="bg-[#0f172a] rounded-[12px] p-3 shadow-inner border border-slate-700 relative overflow-hidden">
             
             <!-- Screen Glare/Reflection -->
             <div class="absolute top-0 right-0 w-full h-full bg-gradient-to-bl from-white/5 to-transparent pointer-events-none z-10 rounded-[12px]"></div>
             
             <!-- Header / Status Bar -->
             <div class="flex items-center justify-between mb-2 px-1">
                <div class="flex gap-1.5">
                   <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                   <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
                </div>
                <span class="text-[11px] font-mono text-emerald-300 font-bold tracking-wide">WIKI_NET_LINK <span class="ml-1 font-black text-emerald-200">{{ t("cgWikiPage.sidebar.wikiDirect") }}</span></span>
             </div>

             <!-- CRT Screen Content -->
             <div class="bg-[#030b15] rounded-md h-[160px] overflow-hidden relative border border-emerald-500/30 shadow-[inset_0_0_14px_rgba(0,0,0,0.75)]">
                <!-- Scanline Effect -->
                <div class="absolute inset-0 z-20 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.12)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.015),rgba(0,0,255,0.03))] bg-[length:100%_4px,3px_100%]"></div>
                
                <!-- Scrolling Content -->
                <div class="wiki-scroll-container h-full">
                   <div class="wiki-scroll-content space-y-2 p-2">
                      <!-- Duplicated list for infinite scroll -->
                      <a v-for="(wiki, i) in [...famousWikis, ...famousWikis]" :key="i" :href="wiki.url" target="_blank" class="flex items-center justify-between group hover:bg-emerald-500/20 p-1.5 rounded border border-emerald-500/15 hover:border-emerald-300/70 transition-all cursor-pointer">
                         <div class="flex flex-col">
                            <span class="text-base font-black text-emerald-300 font-mono group-hover:text-emerald-100 drop-shadow-[0_0_6px_rgba(16,185,129,0.45)]">>> {{ wiki.name }}</span>
                            <span class="text-xs text-emerald-200/90 font-mono uppercase">{{ wiki.desc }}</span>
                         </div>
                         <span class="text-xs text-emerald-200 opacity-80 group-hover:opacity-100 font-mono font-bold">[GO]</span>
                      </a>
                   </div>
                </div>
             </div>

             <!-- Console Controls Decoration -->
             <div class="mt-2 flex justify-between items-center px-2">
                <div class="flex gap-1">
                   <div class="w-8 h-2 bg-slate-700 rounded-full"></div>
                   <div class="w-2 h-2 bg-slate-700 rounded-full"></div>
                </div>
                <div class="text-[9px] font-black text-slate-600 font-mono">GAME_BOY_WIKI</div>
             </div>
           </div>
        </section>

        <!-- News Feed -->
        <section class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col max-h-[600px]">
           <div class="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
             <h2 class="text-sm font-bold text-slate-800">{{ t("cgWikiPage.sidebar.newsFeed") }}</h2>
             <span class="text-[10px] px-1.5 py-0.5 bg-blue-100 text-blue-600 rounded font-bold">LIVE</span>
           </div>
           <div class="overflow-y-auto custom-scrollbar p-2 space-y-1">
              <a v-for="(item, idx) in strategies" :key="idx" :href="item.link" target="_blank" class="block p-2 rounded-lg hover:bg-slate-50 transition-colors group">
                 <div class="flex items-start justify-between gap-2">
                    <span class="text-xs font-medium text-slate-700 leading-snug group-hover:text-blue-600">{{ item.title }}</span>
                 </div>
                 <div class="mt-1.5 flex items-center justify-between">
                    <span class="text-[10px] text-slate-400">{{ item.source }} · {{ formatFeedTime(item.time) }}</span>
                 </div>
              </a>
           </div>
        </section>
      </aside>

      <!-- Main Content Area -->
      <section class="min-w-0 space-y-6">
         
         <!-- Region Select -->
         <div class="bg-white rounded-2xl border border-slate-200 p-1 shadow-sm flex flex-wrap gap-1 sticky top-20 z-20">
            <button 
              v-for="region in rankingRegions" 
              :key="region"
              @click="activeRankingRegion = region"
              class="flex-1 px-4 py-3 rounded-xl text-sm font-bold transition-all relative overflow-hidden group"
              :class="activeRankingRegion === region ? 'bg-blue-50 text-blue-600 shadow-inner' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'"
            >
              <span class="relative z-10">{{ regionLabel(region) }}</span>
              <span v-if="activeRankingRegion === region" class="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500"></span>
            </button>
         </div>

         <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <!-- Top 1 Highlight -->
            <div v-if="topGame" class="p-6 md:p-8 bg-slate-50 border-b border-slate-100 group cursor-pointer hover:bg-slate-100 transition-colors" @click="openLink(topGame.url)">
               <div class="flex items-end justify-between gap-4">
                  <div class="min-w-0">
                     <div class="flex items-center gap-2 mb-2">
                        <span class="px-2 py-0.5 bg-yellow-400 text-yellow-900 text-xs font-black rounded shadow-lg shadow-yellow-400/20">TOP 1</span>
                        <span class="px-2 py-0.5 bg-slate-100 text-slate-700 text-xs font-bold rounded">Featured</span>
                     </div>
                     <h2 class="text-2xl md:text-3xl font-black text-slate-900 mb-1 truncate">{{ topGame.title }}</h2>
                     <p class="text-slate-500 text-sm font-medium truncate">{{ topGame.author }}</p>
                  </div>
                  <button class="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg font-bold hover:bg-slate-700 transition-colors">
                     {{ t("cgWikiPage.common.viewDetails") }}
                     <ArrowRight class="w-4 h-4" />
                  </button>
               </div>
            </div>

            <!-- Ranking List (Infinite Scroll) -->
            <div class="divide-y divide-slate-100">
               <article v-for="(game, idx) in currentRanking" :key="game.id" class="p-4 hover:bg-slate-50 transition-colors flex items-center gap-4 group">
                  <div class="w-12 text-center flex-shrink-0">
                     <span class="text-xl font-black italic" :class="idx < 3 ? 'text-blue-500' : 'text-slate-300'">#{{ game.rank }}</span>
                  </div>
                  <img :src="game.icon || defaultCover" class="h-14 w-14 rounded-xl shadow-sm border border-slate-200 object-cover bg-white" loading="lazy" @error="onImageError">
                  <div class="flex-1 min-w-0">
                     <h3 class="text-base font-bold text-slate-800 group-hover:text-blue-600 transition-colors truncate">{{ game.title }}</h3>
                     <p class="text-xs text-slate-500 mt-0.5 truncate">{{ game.author }}</p>
                     <div class="mt-1.5 flex gap-2">
                        <span v-if="game.global_hot" class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-green-50 text-green-600 border border-green-100">
                          <Flame class="w-3 h-3" />
                          {{ t("cgWikiPage.common.globalHot") }}
                        </span>
                     </div>
                  </div>
                  <button @click="openLink(game.url)" class="px-3 py-1.5 rounded-lg bg-slate-50 text-slate-600 text-xs font-bold hover:bg-blue-50 hover:text-blue-600 transition-colors border border-slate-200">
                     Go
                  </button>
               </article>
            </div>
            <div class="px-4 py-3 border-t border-slate-100 text-right text-xs text-slate-400">
              {{ t("cgWikiPage.footer.dataSourceAppleStore") }}
            </div>
         </div>

      </section>

    </main>

    <div v-if="isLoading" class="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
      <div class="bg-white p-6 rounded-2xl shadow-xl border border-slate-100 flex flex-col items-center">
        <div class="loader-spin mb-3"></div>
        <span class="text-xs font-bold text-slate-500 tracking-wider">LOADING DATA...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue"
import { ArrowRight, BarChart3, Flame, RefreshCw } from "lucide-vue-next"
import { useI18n } from "../composables/useI18n"

const { t, locale } = useI18n()
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
  strategies: StrategyFeedItem[]
  wiki_radar: WikiFeedItem[]
}

interface NewReleaseFeedItem {
  id?: string
  title?: string
  url?: string
  link?: string
  source?: string
  platform?: string
  region?: string
  status?: string
  release_date?: string
}

const rankingRegions: RankingRegion[] = ["CN", "US", "JP", "HK", "TW", "SEA"]
const regionLabelKeyMap: Record<RankingRegion, string> = {
  CN: "cgWikiPage.regions.cn",
  US: "cgWikiPage.regions.us",
  JP: "cgWikiPage.regions.jp",
  HK: "cgWikiPage.regions.hk",
  TW: "cgWikiPage.regions.tw",
  SEA: "cgWikiPage.regions.sea",
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
  "IGN中国": "tag-red",
  "机核": "tag-amber",
  "游研社": "tag-indigo",
  "3DM": "tag-blue",
  "游民星空": "tag-orange",
  "巴哈姆特": "tag-emerald",
  "default": "tag-slate"
}

const defaultCover = "https://placehold.co/96x96/0f172a/94a3b8?text=GAME"

const famousWikis = [
  { name: "Fandom", url: "https://www.fandom.com/", desc: "全球最大维基平台" },
  { name: "BWiki", url: "https://wiki.biligame.com/", desc: "B站游戏WIKI" },
  { name: "灰机Wiki", url: "https://www.huijiwiki.com/", desc: "硬核数据资料库" },
  { name: "萌娘百科", url: "https://zh.moegirl.org.cn/", desc: "万物皆可萌" },
  { name: "Liquipedia", url: "https://liquipedia.net/", desc: "电竞赛事百科" },
  { name: "Fextralife", url: "https://fextralife.com/", desc: "魂系/RPG百科" },
  { name: "Bulbapedia", url: "https://bulbapedia.bulbagarden.net/", desc: "宝可梦百科" },
  { name: "UESP", url: "https://en.uesp.net/", desc: "上古卷轴百科" },
  { name: "NGA", url: "https://bbs.nga.cn/", desc: "精英玩家论坛" },
  { name: "巴哈姆特", url: "https://forum.gamer.com.tw/", desc: "华人最大ACG社群" },
]

const rankings = ref<Record<RankingRegion, RankingGame[]>>({ CN: [], US: [], JP: [], HK: [], TW: [], SEA: [] })
const strategies = ref<StrategyFeedItem[]>([])
const wikiRadar = ref<WikiFeedItem[]>([])
const activeRankingRegion = ref<RankingRegion>("CN")
const lastUpdated = ref("")
const isLoading = ref(true)
const isUpdating = ref(false)
const isMarqueePaused = ref(false)
const loadError = ref("")
const terminalLines = ref<WikiFeedItem[]>([])
const terminalPointer = ref(0)
let terminalTimer: ReturnType<typeof setInterval> | null = null

const rankingTotal = computed(() => rankingRegions.reduce((sum, region) => sum + (rankings.value[region]?.length || 0), 0))
const currentRanking = computed(() => rankings.value[activeRankingRegion.value] || [])
const topGame = computed(() => currentRanking.value[0] || null)
const regionLabel = (region: RankingRegion): string => {
  // Ensure reactivity when locale switches.
  void locale.value
  return t(regionLabelKeyMap[region])
}

const marketHeat = computed(() => {
  const raw = rankingRegions.map((region) => {
    const score = (rankings.value[region] || []).reduce((sum, game) => sum + Math.max(16 - game.rank, 1) + (game.global_hot ? 6 : 0), 0)
    return { region, label: regionLabel(region), score, percent: 0, color: colorMap[region] }
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

const parseDate = (dateStr: string): Date => {
  if (!dateStr) return new Date()
  let safeStr = dateStr.replace(/-/g, "/") 
  let d = new Date(safeStr)
  if (!isNaN(d.getTime())) return d
  d = new Date(dateStr)
  if (!isNaN(d.getTime())) return d
  return new Date()
}

const formatFeedTime = (value: string): string => {
  if (!value) return ""
  try {
    const date = new Date(value)
    if (isNaN(date.getTime())) return value
    const month = (date.getMonth() + 1).toString().padStart(2, "0")
    const day = date.getDate().toString().padStart(2, "0")
    const hours = date.getHours().toString().padStart(2, "0")
    const minutes = date.getMinutes().toString().padStart(2, "0")
    return `${month}/${day} ${hours}:${minutes}`
  } catch (e) {
    return value
  }
}

const formatTerminalTime = (value: string): string => {
  const date = parseDate(value)
  const localeCode = String(locale.value || "en-US")
  return date.getTime()
    ? date.toLocaleTimeString(localeCode, { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false })
    : "00:00:00"
}

const inferTitleFromId = (id: string): string => {
  const tail = (id || "").split(".").pop() || id || "game"
  return tail.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/[_-]/g, " ").replace(/\s+/g, " ").trim()
}

const normalizeTitle = (id: string, title: string): string => {
  return title || inferTitleFromId(id)
}

const normalizeRankingEntry = (entry: any, rank: number): RankingGame => ({
  id: String(entry?.id || `${entry?.title || "game"}-${rank}`),
  rank: Number(entry?.rank || rank),
  title: normalizeTitle(String(entry?.id || ""), String(entry?.title || "")),
  icon: String(entry?.icon || ""),
  author: String(entry?.author || entry?.artist || t("cgWikiPage.common.unknownAuthor")),
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
  const normalizeStrategyRow = (row: any): StrategyFeedItem | null => {
    const title = String(row?.title || row?.name || "").trim()
    if (!title) return null
    const link = String(row?.link || row?.url || "").trim()
    const source = String(row?.source || row?.platform || row?.region || "Feed").trim()
    const time = String(row?.time || row?.published || row?.release_date || payload?.last_updated || "")
    return {
      title,
      link: link || "#",
      is_high_value: Boolean(row?.is_high_value),
      weight_score: Number(row?.weight_score || 0),
      time,
      source,
      source_icon: String(row?.source_icon || ""),
      image: String(row?.image || row?.icon || ""),
    }
  }

  const normalizeWikiRadarRow = (row: any): WikiFeedItem | null => {
    const title = String(row?.title || "").trim()
    if (!title) return null
    return {
      title,
      link: String(row?.link || row?.url || "#").trim() || "#",
      time: String(row?.time || row?.published || payload?.last_updated || ""),
      source: String(row?.source || "Wiki").trim() || "Wiki",
    }
  }

  const dedupeStrategies = (items: StrategyFeedItem[]): StrategyFeedItem[] => {
    const seen = new Set<string>()
    const output: StrategyFeedItem[] = []
    for (const item of items) {
      const key = `${item.title}|${item.link}|${item.source}`.toLowerCase()
      if (!key.trim() || seen.has(key)) continue
      seen.add(key)
      output.push(item)
    }
    return output
  }

  const rawStrategies = (payload?.strategies || payload?.news_feed || payload?.intel_feed || [])
    .map(normalizeStrategyRow)
    .filter(Boolean) as StrategyFeedItem[]

  const releaseFallback = (payload?.new_releases || [])
    .map((row: NewReleaseFeedItem) =>
      normalizeStrategyRow({
        title: row?.status ? `${String(row.title || "").trim()} · ${String(row.status).trim()}` : row?.title,
        link: row?.url || row?.link || "",
        source: row?.source || row?.platform || row?.region || "Release",
        time: row?.release_date || payload?.last_updated || "",
        image: row?.icon || "",
      })
    )
    .filter(Boolean) as StrategyFeedItem[]

  const wikiRadarFallback = (payload?.wiki_radar || [])
    .map((row: any) =>
      normalizeStrategyRow({
        title: row?.title,
        link: row?.link || row?.url || "",
        source: row?.source || "Wiki",
        time: row?.time || payload?.last_updated || "",
      })
    )
    .filter(Boolean) as StrategyFeedItem[]

  const strategyCandidates = rawStrategies.length
    ? rawStrategies
    : releaseFallback.length
      ? releaseFallback
      : wikiRadarFallback

  const normalizedStrategies = dedupeStrategies(strategyCandidates)
    .sort((a, b) => parseDate(b.time).getTime() - parseDate(a.time).getTime())
    .slice(0, 80)

  const normalizedWikiRadar = (payload?.wiki_radar || [])
    .map(normalizeWikiRadarRow)
    .filter(Boolean) as WikiFeedItem[]

  const wikiRadarWithFallback = normalizedWikiRadar.length
    ? normalizedWikiRadar
    : releaseFallback.slice(0, 12).map((item) => ({
        title: item.title,
        link: item.link,
        time: item.time,
        source: item.source,
      }))

  const rawRankings = {} as Record<RankingRegion, RankingGame[]>
  rankingRegions.forEach(region => {
    rawRankings[region] = (payload?.rankings?.[region] || []).map((row: any, idx: number) => normalizeRankingEntry(row, idx + 1))
  })

  return {
    last_updated: String(payload?.last_updated || ""),
    rankings: applyGlobalHot(rawRankings),
    strategies: normalizedStrategies,
    wiki_radar: wikiRadarWithFallback,
  }
}

const applyPayload = (payload: HubPayload): void => {
  rankings.value = payload.rankings || { CN: [], US: [], JP: [], HK: [], TW: [], SEA: [] }
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

const triggerUpdate = async (): Promise<void> => {
  if (isUpdating.value) return
  isUpdating.value = true
  
  try {
    // 尝试调用后端更新接口
    // 注意：这里假设后端已在 main/urls.py 中添加了 'wiki-update/' 路由
    // 如果没有，或者跨域失败，这个请求会出错
    let apiUrl = "/api/wiki-update/"
    if (!window.location.hostname.includes("localhost")) {
        // 生产环境可能需要完整路径或不同处理，暂时保持相对路径
    }
    
    const response = await fetch(apiUrl)
    
    if (response.ok) {
       // 更新成功后，重新加载数据
       // 等待一小会儿确保文件写入完成
       await new Promise(r => setTimeout(r, 1000))
       await loadData()
    } else {
       console.warn("API update failed, trying fallback reload")
       // 如果API调用失败（例如没有后端支持），至少重新加载数据
       await loadData()
    }
  } catch (e) {
    console.error("Update failed", e)
    // 出错也尝试重载
    await loadData()
  } finally {
    isUpdating.value = false
  }
}

const loadData = async (): Promise<void> => {
  isLoading.value = true
  loadError.value = ""
  try {
    loadError.value = ""
    isLoading.value = true
    const timestamp = new Date().getTime()
    const remoteCandidates = [
      `https://raw.githubusercontent.com/qwe842015629-svg/cg-game-intel/master/frontend/public/data/game_hub.json?t=${timestamp}`,
      `https://raw.githubusercontent.com/qwe842015629-svg/cypher-frontend/main/frontend/public/data/game_hub.json?t=${timestamp}`,
      `https://raw.githubusercontent.com/qwe842015629-svg/cypher-frontend/main/public/data/game_hub.json?t=${timestamp}`,
    ]
    const candidates = [`/data/game_hub.json?t=${timestamp}`, ...remoteCandidates]

    let loaded = false
    let lastError: unknown = null
    for (const dataUrl of candidates) {
      try {
        const response = await fetch(dataUrl, { cache: "no-store" })
        if (!response.ok) throw new Error(`Status ${response.status}`)
        const data = await response.json()
        applyPayload(normalizeHubPayload(data))
        loaded = true
        break
      } catch (error) {
        lastError = error
      }
    }

    if (!loaded) throw lastError || new Error("All wiki feed sources failed")
  } catch (error) {
    console.warn("Failed to load wiki hub data from all sources", error)
    loadError.value = t("cgWikiPage.errors.loadFailed")
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  void loadData()
})

onUnmounted(() => {
  if (terminalTimer) clearInterval(terminalTimer)
})
</script>

<style scoped>
.wiki-galaxy {
  background:
    radial-gradient(circle at 7% 0%, color-mix(in srgb, var(--primary-color) 15%, transparent) 0%, transparent 30%),
    radial-gradient(circle at 95% 4%, color-mix(in srgb, #22c55e 14%, transparent) 0%, transparent 30%),
    linear-gradient(180deg, #f8fbff 0%, #f5f9ff 100%);
}

.wiki-galaxy-header {
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--primary-color) 14%, transparent) 0%, transparent 52%),
    linear-gradient(180deg, color-mix(in srgb, #ffffff 90%, #f4f8ff 10%) 0%, #ffffff 100%) !important;
  border-bottom-color: #d6e3f4 !important;
  box-shadow: 0 16px 32px -30px rgba(15, 23, 42, 0.35);
}

.wiki-galaxy-ticker {
  border-color: #d9e5f4 !important;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%) !important;
}

.wiki-galaxy-main {
  max-width: 1600px;
}

.wiki-galaxy :deep(section.bg-white),
.wiki-galaxy :deep(div.bg-white.rounded-2xl),
.wiki-galaxy :deep(.bg-white.rounded-2xl.border) {
  border-color: #d4e2f4 !important;
  background:
    radial-gradient(120% 90% at 0% -14%, color-mix(in srgb, var(--primary-color) 9%, transparent) 0%, transparent 56%),
    linear-gradient(160deg, #ffffff 0%, #f7fbff 100%) !important;
  box-shadow: 0 20px 38px -30px rgba(15, 23, 42, 0.28) !important;
}

.wiki-galaxy :deep(button) {
  border-radius: 12px;
  border: 1px solid #d0def0;
  background: linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
  color: #0f172a;
  font-weight: 600;
  box-shadow: 0 10px 22px -20px rgba(15, 23, 42, 0.38);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.wiki-galaxy :deep(button:hover:not(:disabled)) {
  transform: translateY(-1px);
  border-color: #8fd3ff;
  box-shadow: 0 16px 28px -20px rgba(3, 105, 161, 0.38);
}

.wiki-galaxy :deep(button.bg-slate-900),
.wiki-galaxy :deep(button.bg-blue-600) {
  background: linear-gradient(180deg, #22b1f0 0%, #0284c7 100%) !important;
  border-color: transparent !important;
  color: #ffffff !important;
}

.wiki-galaxy :deep(article) {
  border-radius: 14px;
}

.wiki-galaxy :deep(.text-slate-500),
.wiki-galaxy :deep(.text-slate-600) {
  color: #55657d !important;
}

.wiki-galaxy :deep(.text-slate-700),
.wiki-galaxy :deep(.text-slate-800),
.wiki-galaxy :deep(.text-slate-900) {
  color: #0f172a !important;
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
  animation: scroll-left 360s linear infinite;
  padding-left: 100%;
}

.marquee-horizontal-wrapper.paused .marquee-horizontal-content {
  animation-play-state: paused;
}

@keyframes scroll-left {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}

.wiki-scroll-content {
  animation: scroll-vertical 20s linear infinite;
}

@keyframes scroll-vertical {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

.wiki-scroll-container:hover .wiki-scroll-content {
  animation-play-state: paused;
}
</style>
