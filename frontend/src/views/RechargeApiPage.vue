<template>
  <div class="min-h-screen py-10">
    <div class="container mx-auto px-4 max-w-7xl space-y-6">
      <section class="surface-card p-5 md:p-6">
        <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground mb-2">{{ t('rechargeApiPage.badge') }}</p>
        <h1 class="text-2xl md:text-3xl font-bold text-foreground mb-2">{{ t('rechargeApiPage.title') }}</h1>
        <p class="text-sm text-muted-foreground">
          {{ t('rechargeApiPage.subtitle') }}
        </p>
      </section>

      <section v-if="error" class="surface-card p-5 border border-red-200">
        <p class="text-sm text-red-600 break-all">{{ error }}</p>
        <p class="mt-3 text-xs text-muted-foreground">
          {{
            t('rechargeApiPage.snapshotMissingHint', {
              command: 'py -3 manage.py sync_chargex_inventory_snapshot --sleep-ms 1200',
            })
          }}
        </p>
      </section>

      <section class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="surface-card p-4">
          <p class="text-xs text-muted-foreground">{{ t('rechargeApiPage.stats.products') }}</p>
          <p class="text-2xl font-semibold text-foreground mt-1">{{ productCount }}</p>
        </div>
        <div class="surface-card p-4">
          <p class="text-xs text-muted-foreground">{{ t('rechargeApiPage.stats.inStock') }}</p>
          <p class="text-2xl font-semibold text-emerald-600 mt-1">{{ stats.in_stock }}</p>
        </div>
        <div class="surface-card p-4">
          <p class="text-xs text-muted-foreground">{{ t('rechargeApiPage.stats.outOfStock') }}</p>
          <p class="text-2xl font-semibold text-amber-600 mt-1">{{ stats.out_of_stock }}</p>
        </div>
        <div class="surface-card p-4">
          <p class="text-xs text-muted-foreground">{{ t('rechargeApiPage.stats.unknown') }}</p>
          <p class="text-2xl font-semibold text-slate-600 mt-1">{{ stats.unknown }}</p>
        </div>
      </section>

      <section class="surface-card p-4 space-y-2">
        <div class="flex flex-wrap items-center gap-2 text-xs">
          <p class="text-muted-foreground">
            {{ t('rechargeApiPage.snapshotLabel') }}:
            <span class="font-medium text-foreground">{{ formattedGeneratedAt || '-' }}</span>
          </p>
          <span class="px-2 py-0.5 rounded-full font-medium" :class="delayStatusBadgeClass">
            {{ delayStatusText }}
          </span>
          <span class="text-muted-foreground">
            {{ t('rechargeApiPage.health.snapshotAge', { age: snapshotAgeDisplay }) }}
          </span>
          <span class="text-muted-foreground">
            {{ t('rechargeApiPage.health.autoRefreshIn', { seconds: autoRefreshCountdown }) }}
          </span>
        </div>
        <p class="text-xs text-muted-foreground">
          {{ t('rechargeApiPage.health.syncStatus', { status: syncStatusText, duration: runDurationDisplay }) }}
        </p>
        <p v-if="lastSyncErrorMessage" class="text-xs text-amber-600 break-all">
          {{ t('rechargeApiPage.health.lastError', { error: lastSyncErrorMessage }) }}
        </p>
      </section>

      <section class="surface-card p-5 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">{{ t('rechargeApiPage.filters.search') }}</span>
            <input
              v-model="searchInput"
              type="text"
              :placeholder="t('rechargeApiPage.filters.searchPlaceholder')"
              class="w-full h-10 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">{{ t('rechargeApiPage.filters.inventoryStatus') }}</span>
            <select
              v-model="inventoryStatusFilter"
              class="w-full h-10 px-3 rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            >
              <option value="">{{ t('rechargeApiPage.filters.inventoryAll') }}</option>
              <option value="in_stock">{{ t('rechargeApiPage.inventoryStatus.inStock') }}</option>
              <option value="out_of_stock">{{ t('rechargeApiPage.inventoryStatus.outOfStock') }}</option>
              <option value="unknown">{{ t('rechargeApiPage.inventoryStatus.unknown') }}</option>
            </select>
          </label>

          <label class="block">
            <span class="block text-xs text-muted-foreground mb-1">{{ t('rechargeApiPage.filters.pageSize') }}</span>
            <select
              v-model.number="limit"
              class="w-full h-10 px-3 rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            >
              <option :value="30">30</option>
              <option :value="60">60</option>
              <option :value="100">100</option>
              <option :value="150">150</option>
            </select>
          </label>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button
            class="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90"
            :disabled="loading"
            @click="applyFilters"
          >
            {{ loading ? t('rechargeApiPage.actions.loading') : t('rechargeApiPage.actions.applyFilters') }}
          </button>
          <button
            class="px-4 py-2 rounded-lg border border-border text-sm font-medium text-foreground hover:bg-muted"
            :disabled="loading"
            @click="resetFilters"
          >
            {{ t('rechargeApiPage.actions.reset') }}
          </button>
        </div>
      </section>

      <section class="surface-card p-5">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
          <p class="text-sm text-muted-foreground">{{ t('rechargeApiPage.list.totalMatched', { total }) }}</p>
          <div class="flex items-center gap-2">
            <button
              class="px-3 py-1.5 rounded-md border border-border text-sm text-foreground hover:bg-muted disabled:opacity-50"
              :disabled="loading || page <= 1"
              @click="prevPage"
            >
              {{ t('rechargeApiPage.actions.prev') }}
            </button>
            <p class="text-sm text-muted-foreground">{{ t('rechargeApiPage.list.page', { page, total: totalPages || 1 }) }}</p>
            <button
              class="px-3 py-1.5 rounded-md border border-border text-sm text-foreground hover:bg-muted disabled:opacity-50"
              :disabled="loading || page >= totalPages"
              @click="nextPage"
            >
              {{ t('rechargeApiPage.actions.next') }}
            </button>
          </div>
          <p class="text-xs text-muted-foreground">{{ t('rechargeApiPage.list.mergedPages') }}</p>
        </div>

        <p v-if="loading" class="text-sm text-muted-foreground">{{ t('rechargeApiPage.list.loading') }}</p>
        <p v-else-if="!rows.length" class="text-sm text-muted-foreground">{{ t('rechargeApiPage.list.empty') }}</p>

        <div v-else class="space-y-4">
          <div class="flex items-center gap-2">
            <button
              class="px-3 py-1.5 rounded-md border border-border text-xs text-foreground hover:bg-muted"
              @click="expandAllCategories"
            >
              {{ t('rechargeApiPage.actions.expandAll') }}
            </button>
            <button
              class="px-3 py-1.5 rounded-md border border-border text-xs text-foreground hover:bg-muted"
              @click="collapseAllCategories"
            >
              {{ t('rechargeApiPage.actions.collapseAll') }}
            </button>
          </div>

          <section
            v-for="category in categoryOrder"
            :key="category.key"
            class="rounded-lg border border-border"
          >
            <button
              class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-muted/30 transition-colors"
              @click="toggleCategory(category.key)"
            >
              <div class="flex items-center gap-2">
                <p class="text-sm font-semibold text-foreground">{{ category.label }}</p>
                <span class="text-xs text-muted-foreground">
                  ({{ groupedRows[category.key].length }})
                </span>
              </div>
              <span class="text-xs text-muted-foreground">
                {{ expandedCategories[category.key] ? t('rechargeApiPage.categories.collapse') : t('rechargeApiPage.categories.expand') }}
              </span>
            </button>

            <div v-show="expandedCategories[category.key]" class="px-3 pb-3 space-y-3">
              <p
                v-if="!groupedRows[category.key].length"
                class="text-sm text-muted-foreground px-1"
              >
                {{ t('rechargeApiPage.categories.empty') }}
              </p>

              <article
                v-for="item in groupedRows[category.key]"
                :key="`${item.provider_uuid}:${item.product_id}`"
                class="rounded-lg border border-border p-4 cursor-pointer hover:bg-muted/30 transition-colors"
                @click="openProductRecharge(item)"
              >
                <div class="flex items-start gap-3">
                  <div class="min-w-0 flex-1">
                    <div class="flex flex-wrap items-center gap-2">
                      <p class="text-sm font-semibold text-foreground break-words">
                        {{ resolveProductName(item) || item.product_id }}
                      </p>
                      <span
                        class="px-2 py-0.5 rounded-full text-xs font-medium"
                        :class="inventoryBadgeClass(item.inventory_status)"
                      >
                        {{ inventoryStatusText(item.inventory_status) }}
                      </span>
                    </div>
                  </div>
                  <button
                    class="shrink-0 px-3 py-1.5 rounded-md border border-border text-xs text-foreground hover:bg-muted"
                    @click.stop="openProductRecharge(item)"
                  >
                    {{ t('rechargeApiPage.actions.recharge') }}
                  </button>
                </div>

                <div class="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                  <div class="rounded-md bg-muted/40 px-2 py-1">
                    <span class="text-muted-foreground">{{ t('rechargeApiPage.product.available') }}</span>
                    <p class="text-foreground font-semibold">{{ item.available_variations }}</p>
                  </div>
                  <div class="rounded-md bg-muted/40 px-2 py-1">
                    <span class="text-muted-foreground">{{ t('rechargeApiPage.product.totalVariations') }}</span>
                    <p class="text-foreground font-semibold">{{ item.total_variations }}</p>
                  </div>
                  <div class="rounded-md bg-muted/40 px-2 py-1">
                    <span class="text-muted-foreground">{{ t('rechargeApiPage.product.orderSupported') }}</span>
                    <p class="text-foreground font-semibold">{{ booleanText(item.order_supported) }}</p>
                  </div>
                </div>
              </article>
            </div>
          </section>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  getChargeXInventorySnapshot,
  type ChargeXInventoryProductItem,
} from '../api/recharge'

type InventoryStats = {
  in_stock: number
  out_of_stock: number
  unknown: number
  failed_detail: number
  rate_limit_hit?: number
}

type ProductCategoryKey = 'game' | 'software' | 'gift_card'
type SyncStatus = 'running' | 'completed' | 'failed' | 'skipped_locked' | 'unknown'
type DelayStatus = 'fresh' | 'delayed' | 'stale' | 'unknown'

const DEFAULT_AUTO_REFRESH_SECONDS = 60
const AUTO_REFRESH_MIN_SECONDS = 30
const AUTO_REFRESH_MAX_SECONDS = 300
const MERGED_PAGES_PER_VIEW = 4

const resolveAutoRefreshSeconds = (): number => {
  const raw = Number(import.meta.env.VITE_RECHARGE_INVENTORY_AUTO_REFRESH_SEC || DEFAULT_AUTO_REFRESH_SECONDS)
  if (!Number.isFinite(raw)) return DEFAULT_AUTO_REFRESH_SECONDS
  return Math.min(AUTO_REFRESH_MAX_SECONDS, Math.max(AUTO_REFRESH_MIN_SECONDS, Math.round(raw)))
}

const loading = ref(false)
const error = ref('')
const router = useRouter()
const { t, locale } = useI18n()
const autoRefreshIntervalSeconds = resolveAutoRefreshSeconds()
const autoRefreshCountdown = ref(autoRefreshIntervalSeconds)
const autoRefreshTimerId = ref<number | null>(null)
const nowTimestamp = ref(Date.now())

const generatedAt = ref('')
const syncStatus = ref<SyncStatus>('unknown')
const runDurationSeconds = ref(0)
const delayWarnSeconds = ref(600)
const delayStaleSeconds = ref(1200)
const lastSyncErrorMessage = ref('')
const productCount = ref(0)
const isComplete = ref(false)
const scannedProducts = ref(0)
const expectedProducts = ref(0)
const stats = ref<InventoryStats>({
  in_stock: 0,
  out_of_stock: 0,
  unknown: 0,
  failed_detail: 0,
})

const rows = ref<ChargeXInventoryProductItem[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(60)
const totalPages = ref(0)

const searchInput = ref('')
const inventoryStatusFilter = ref<'in_stock' | 'out_of_stock' | 'unknown' | ''>('')
const categoryOrder = computed<Array<{ key: ProductCategoryKey; label: string }>>(() => [
  { key: 'game', label: t('rechargeApiPage.categories.game') },
  { key: 'software', label: t('rechargeApiPage.categories.software') },
  { key: 'gift_card', label: t('rechargeApiPage.categories.giftCard') },
])
const expandedCategories = reactive<Record<ProductCategoryKey, boolean>>({
  game: true,
  software: true,
  gift_card: true,
})

const formattedGeneratedAt = computed(() => {
  if (!generatedAt.value) return ''
  const timestamp = Date.parse(generatedAt.value)
  if (Number.isNaN(timestamp)) return generatedAt.value
  return new Date(timestamp).toLocaleString()
})

const formatDurationShort = (rawSeconds: number | null): string => {
  if (rawSeconds === null || !Number.isFinite(rawSeconds)) return '-'
  const seconds = Math.max(0, Math.floor(rawSeconds))
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const remainSeconds = seconds % 60
  if (minutes < 60) return `${minutes}m ${remainSeconds}s`
  const hours = Math.floor(minutes / 60)
  const remainMinutes = minutes % 60
  return `${hours}h ${remainMinutes}m`
}

const snapshotAgeSeconds = computed<number | null>(() => {
  if (!generatedAt.value) return null
  const timestamp = Date.parse(generatedAt.value)
  if (Number.isNaN(timestamp)) return null
  return Math.max(0, Math.floor((nowTimestamp.value - timestamp) / 1000))
})

const snapshotAgeDisplay = computed(() => formatDurationShort(snapshotAgeSeconds.value))
const runDurationDisplay = computed(() => formatDurationShort(runDurationSeconds.value))

const delayStatus = computed<DelayStatus>(() => {
  const age = snapshotAgeSeconds.value
  if (age === null) return 'unknown'
  if (age <= delayWarnSeconds.value) return 'fresh'
  if (age <= delayStaleSeconds.value) return 'delayed'
  return 'stale'
})

const delayStatusText = computed(() => {
  if (delayStatus.value === 'fresh') return t('rechargeApiPage.health.delayFresh')
  if (delayStatus.value === 'delayed') return t('rechargeApiPage.health.delayDelayed')
  if (delayStatus.value === 'stale') return t('rechargeApiPage.health.delayStale')
  return t('rechargeApiPage.health.delayUnknown')
})

const delayStatusBadgeClass = computed(() => {
  if (delayStatus.value === 'fresh') return 'bg-emerald-100 text-emerald-700'
  if (delayStatus.value === 'delayed') return 'bg-amber-100 text-amber-700'
  if (delayStatus.value === 'stale') return 'bg-rose-100 text-rose-700'
  return 'bg-slate-100 text-slate-700'
})

const syncStatusText = computed(() => {
  if (syncStatus.value === 'running') return t('rechargeApiPage.health.syncRunning')
  if (syncStatus.value === 'completed') return t('rechargeApiPage.health.syncCompleted')
  if (syncStatus.value === 'failed') return t('rechargeApiPage.health.syncFailed')
  if (syncStatus.value === 'skipped_locked') return t('rechargeApiPage.health.syncSkippedLocked')
  return t('rechargeApiPage.health.syncUnknown')
})

const inventoryStatusText = (status: string): string => {
  if (status === 'in_stock') return t('rechargeApiPage.inventoryStatus.inStock')
  if (status === 'out_of_stock') return t('rechargeApiPage.inventoryStatus.outOfStock')
  return t('rechargeApiPage.inventoryStatus.unknown')
}

const inventoryBadgeClass = (status: string): string => {
  if (status === 'in_stock') return 'bg-emerald-100 text-emerald-700'
  if (status === 'out_of_stock') return 'bg-amber-100 text-amber-700'
  return 'bg-slate-100 text-slate-700'
}

const booleanText = (value: boolean): string => {
  return value ? t('rechargeApiPage.product.yes') : t('rechargeApiPage.product.no')
}

const giftCardKeywords = [
  'gift card',
  'giftcard',
  'voucher',
  'mycard',
  'gash',
  'itunes',
  'steam wallet',
  'razer gold',
  'apple gift',
  'amazon gift',
  '\u793c\u54c1\u5361',
  '\u79ae\u54c1\u5361',
  '\u70b9\u5361',
  '\u9ed1\u5361',
  '\u50a8\u503c\u5361',
  '\u5132\u503c\u5361',
  '\u5145\u503c\u5361',
]

const softwareKeywords = [
  'chatgpt',
  'duolingo',
  'netflix',
  'spotify',
  'youtube premium',
  'apple music',
  'canva',
  'adobe',
  'office 365',
  'microsoft 365',
  'capcut',
  'grammarly',
  'notion',
  'zoom',
  'subscription',
  '\u8f6f\u4ef6',
  '\u6703\u54e1',
  '\u4f1a\u5458',
]

const classifyProduct = (item: ChargeXInventoryProductItem): ProductCategoryKey => {
  const text = [
    item.product_name || '',
    item.product_name_cn || '',
    item.product_name_tw || '',
    item.product_name_en || '',
    item.localized_name || '',
  ]
    .join(' ')
    .toLowerCase()

  if (giftCardKeywords.some((keyword) => text.includes(keyword))) return 'gift_card'
  if (softwareKeywords.some((keyword) => text.includes(keyword))) return 'software'
  return 'game'
}

const groupedRows = computed<Record<ProductCategoryKey, ChargeXInventoryProductItem[]>>(() => {
  const groups: Record<ProductCategoryKey, ChargeXInventoryProductItem[]> = {
    game: [],
    software: [],
    gift_card: [],
  }
  for (const item of rows.value) {
    groups[classifyProduct(item)].push(item)
  }
  return groups
})

const resolveProductName = (item: ChargeXInventoryProductItem): string => {
  const localeCode = String(locale.value || '').toLowerCase()
  if (localeCode.startsWith('zh-cn') || localeCode === 'zh') {
    return item.product_name_cn || item.product_name_tw || item.localized_name || item.product_name || ''
  }
  if (localeCode.startsWith('zh-tw') || localeCode.includes('hant')) {
    return item.product_name_tw || item.product_name_cn || item.localized_name || item.product_name || ''
  }
  if (localeCode.startsWith('en')) {
    return item.product_name_en || item.localized_name || item.product_name || ''
  }
  return item.localized_name || item.product_name || item.product_name_en || ''
}

const openProductRecharge = async (item: ChargeXInventoryProductItem): Promise<void> => {
  const provider = String(item.provider_uuid || '').trim()
  const productId = String(item.product_id || '').trim()
  if (!provider || !productId) return
  await router.push({
    path: `/recharge-api/product/${encodeURIComponent(provider)}/${encodeURIComponent(productId)}`,
  })
}

const toggleCategory = (key: ProductCategoryKey): void => {
  expandedCategories[key] = !expandedCategories[key]
}

const expandAllCategories = (): void => {
  expandedCategories.game = true
  expandedCategories.software = true
  expandedCategories.gift_card = true
}

const collapseAllCategories = (): void => {
  expandedCategories.game = false
  expandedCategories.software = false
  expandedCategories.gift_card = false
}

const resetAutoRefreshCountdown = (): void => {
  autoRefreshCountdown.value = autoRefreshIntervalSeconds
}

const loadSnapshot = async (options?: { resetCountdown?: boolean }): Promise<void> => {
  if (options?.resetCountdown !== false) resetAutoRefreshCountdown()
  loading.value = true
  error.value = ''
  try {
    const basePage = (page.value - 1) * MERGED_PAGES_PER_VIEW + 1
    const firstResponse = await getChargeXInventorySnapshot({
      search: searchInput.value,
      inventory_status: inventoryStatusFilter.value,
      page: basePage,
      limit: limit.value,
    })

    const sourceTotalPages = Number(firstResponse.total_pages || 0)
    const extraRequests: Promise<Awaited<ReturnType<typeof getChargeXInventorySnapshot>>>[] = []
    for (let offset = 1; offset < MERGED_PAGES_PER_VIEW; offset += 1) {
      const targetPage = basePage + offset
      if (sourceTotalPages > 0 && targetPage > sourceTotalPages) break
      extraRequests.push(
        getChargeXInventorySnapshot({
          search: searchInput.value,
          inventory_status: inventoryStatusFilter.value,
          page: targetPage,
          limit: limit.value,
        })
      )
    }

    const extraResponses = extraRequests.length ? await Promise.all(extraRequests) : []
    const mergedItems = [firstResponse, ...extraResponses].flatMap((response) => response.items || [])

    generatedAt.value = firstResponse.generated_at
    syncStatus.value = firstResponse.sync_status || 'unknown'
    runDurationSeconds.value = Number(firstResponse.run_duration_seconds || 0)
    delayWarnSeconds.value = Number(firstResponse.health?.delay_warn_seconds || 600)
    delayStaleSeconds.value = Number(firstResponse.health?.delay_stale_seconds || 1200)
    lastSyncErrorMessage.value = String(firstResponse.last_error?.message || '')
    productCount.value = firstResponse.product_count
    isComplete.value = firstResponse.is_complete
    scannedProducts.value = firstResponse.scanned_products
    expectedProducts.value = firstResponse.expected_products
    stats.value = firstResponse.stats
    rows.value = mergedItems
    total.value = firstResponse.total
    totalPages.value = Math.max(1, Math.ceil(sourceTotalPages / MERGED_PAGES_PER_VIEW))
    nowTimestamp.value = Date.now()
  } catch (err: any) {
    const data = err?.response?.data || {}
    error.value = String(data.message || data.detail || err?.message || t('rechargeApiPage.errors.loadSnapshotFailed'))
    rows.value = []
    total.value = 0
    totalPages.value = 0
    syncStatus.value = 'unknown'
    runDurationSeconds.value = 0
    lastSyncErrorMessage.value = ''
    isComplete.value = false
    scannedProducts.value = 0
    expectedProducts.value = 0
  } finally {
    loading.value = false
  }
}

const handleAutoRefreshTick = (): void => {
  nowTimestamp.value = Date.now()
  if (document.visibilityState !== 'visible') return
  if (loading.value) return
  if (autoRefreshCountdown.value > 1) {
    autoRefreshCountdown.value -= 1
    return
  }
  resetAutoRefreshCountdown()
  void loadSnapshot({ resetCountdown: false })
}

const startAutoRefreshTimer = (): void => {
  if (autoRefreshTimerId.value !== null) return
  autoRefreshTimerId.value = window.setInterval(handleAutoRefreshTick, 1000)
}

const stopAutoRefreshTimer = (): void => {
  if (autoRefreshTimerId.value === null) return
  window.clearInterval(autoRefreshTimerId.value)
  autoRefreshTimerId.value = null
}

const handleVisibilityChange = (): void => {
  nowTimestamp.value = Date.now()
  if (document.visibilityState !== 'visible') return
  if (loading.value) return
  resetAutoRefreshCountdown()
  void loadSnapshot({ resetCountdown: false })
}

const applyFilters = async (): Promise<void> => {
  page.value = 1
  await loadSnapshot()
}

const resetFilters = async (): Promise<void> => {
  searchInput.value = ''
  inventoryStatusFilter.value = ''
  page.value = 1
  limit.value = 60
  await loadSnapshot()
}

const prevPage = async (): Promise<void> => {
  if (page.value <= 1) return
  page.value -= 1
  await loadSnapshot()
}

const nextPage = async (): Promise<void> => {
  if (page.value >= totalPages.value) return
  page.value += 1
  await loadSnapshot()
}

onMounted(async () => {
  document.addEventListener('visibilitychange', handleVisibilityChange)
  startAutoRefreshTimer()
  await loadSnapshot()
})

onBeforeUnmount(() => {
  stopAutoRefreshTimer()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>
