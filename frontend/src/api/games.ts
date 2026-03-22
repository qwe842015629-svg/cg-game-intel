import client from './client'
import type { RechargeGame, GameCategoryItem } from '../types'

const normalizeBase = (value: string) => value.replace(/\/+$/, '')
const BACKEND_ORIGIN = normalizeBase(
  (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim() || 'http://127.0.0.1:8000'
)

const extractList = (response: any): any[] => {
  if (Array.isArray(response)) return response
  if (Array.isArray(response?.results)) return response.results
  return []
}

const fetchAllPaginatedResults = async (
  path: string,
  params?: Record<string, any>
): Promise<any[]> => {
  const firstResponse: any = await client.get(path, { params })
  if (Array.isArray(firstResponse)) return firstResponse

  const firstRows = extractList(firstResponse)
  if (!Array.isArray(firstResponse?.results)) return firstRows

  const allRows: any[] = [...firstRows]
  const countRaw = Number(firstResponse?.count)
  const totalCount = Number.isFinite(countRaw) && countRaw >= 0 ? countRaw : null

  let page = 1
  let next = firstResponse?.next
  const MAX_PAGES = 200

  while (page < MAX_PAGES) {
    const hasNextByCount = totalCount !== null && allRows.length < totalCount
    if (!next && !hasNextByCount) break

    page += 1
    const response: any = await client.get(path, {
      params: {
        ...(params || {}),
        page,
      },
    })

    if (Array.isArray(response)) {
      if (!response.length) break
      allRows.push(...response)
      break
    }

    const rows = extractList(response)
    if (!rows.length) break
    allRows.push(...rows)
    next = response?.next
  }

  return allRows
}

const toPositiveInt = (value: unknown, fallback: number): number => {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback
}

const toAbsoluteUrl = (raw: any): string => {
  const value = String(raw || '').trim()
  if (!value) return ''

  if (/^https?:\/\//i.test(value)) return value
  if (value.startsWith('//')) return `https:${value}`
  if (value.startsWith('/')) return `${BACKEND_ORIGIN}${value}`
  return value
}

const pickFirstText = (...values: any[]): string => {
  for (const value of values) {
    const normalized = String(value || '').trim()
    if (normalized) return normalized
  }
  return ''
}

const normalizeCategoryToken = (value: unknown): string =>
  String(value || '').trim().toLowerCase()

const CATEGORY_KEY_BY_TOKEN: Record<string, string> = {
  all: 'allGames',
  allgames: 'allGames',
  allgamescategory: 'allGames',
  international: 'internationalGames',
  internationalgames: 'internationalGames',
  global: 'internationalGames',
  'hongkong-taiwan': 'hongKongTaiwanGames',
  hongkong: 'hongKongTaiwanGames',
  taiwan: 'hongKongTaiwanGames',
  hk: 'hongKongTaiwanGames',
  tw: 'hongKongTaiwanGames',
  'southeast-asia': 'southeastAsiaGames',
  southeastasia: 'southeastAsiaGames',
  southeast: 'southeastAsiaGames',
  sea: 'southeastAsiaGames',
}

const resolveCategoryNameKey = (slugOrName: unknown): string => {
  const raw = normalizeCategoryToken(slugOrName)
  if (!raw) return ''

  const compact = raw.replace(/[\s_-]+/g, '')
  if (CATEGORY_KEY_BY_TOKEN[raw]) return CATEGORY_KEY_BY_TOKEN[raw]
  if (CATEGORY_KEY_BY_TOKEN[compact]) return CATEGORY_KEY_BY_TOKEN[compact]

  if (raw.includes('\u5168\u90e8')) return 'allGames'
  if (raw.includes('\u56fd\u9645') || raw.includes('\u5168\u7403')) return 'internationalGames'
  if (raw.includes('\u6e2f\u53f0') || raw.includes('\u9999\u6e2f') || raw.includes('\u53f0\u6e7e')) {
    return 'hongKongTaiwanGames'
  }
  if (raw.includes('\u4e1c\u5357\u4e9a')) return 'southeastAsiaGames'

  return ''
}

const mapCategoryIcon = (nameOrSlug: string): string => {
  const key = resolveCategoryNameKey(nameOrSlug)
  if (key === 'internationalGames') return '🌍'
  if (key === 'hongKongTaiwanGames') return '🏮'
  if (key === 'southeastAsiaGames') return '🌴'
  return '🎮'
}

const toRechargeGame = (item: any): RechargeGame =>
  ({
    ...item,
    id: String(item.id ?? ''),
    slug: item.slug || '',
    name: item.title || item.name || '',
    title: item.title || item.name || '',
    categoryName: item.category_name || '',
    category_name: item.category_name || '',
    icon_external_url: toAbsoluteUrl(item.icon_external_url),
    icon_image_url: toAbsoluteUrl(item.icon_image_url),
    banner_image_url: toAbsoluteUrl(item.banner_image_url),
    image: pickFirstText(
      toAbsoluteUrl(item.icon_image_url),
      toAbsoluteUrl(item.icon_external_url),
      toAbsoluteUrl(item.icon_image),
      toAbsoluteUrl(item.banner_image_url)
    ),
    hot: Boolean(item.is_hot),
    platform: item.platform || '',
    description: item.description || '',
    tags: Array.isArray(item.tags) ? item.tags : [],
  }) as RechargeGame

let categorySlugIdCache: Record<string, string> | null = null

const buildCategorySlugIdCache = async () => {
  if (categorySlugIdCache) return categorySlugIdCache

  const categories = await fetchAllPaginatedResults('/game-pages/categories/')
  const cache: Record<string, string> = {}

  categories.forEach((item: any) => {
    const id = String(item.id ?? '')
    if (!id) return

    if (item.slug) cache[String(item.slug)] = id
    if (item.name) cache[String(item.name)] = id
  })

  categorySlugIdCache = cache
  return cache
}

const resolveCategoryParam = async (rawCategory: string): Promise<string | undefined> => {
  if (!rawCategory || rawCategory === 'all') return undefined
  if (/^\d+$/.test(rawCategory)) return rawCategory

  try {
    const mapping = await buildCategorySlugIdCache()
    return mapping[rawCategory]
  } catch (error) {
    console.warn('Category mapping load failed, ignore category filter:', error)
    return undefined
  }
}

export const getGameCategories = async (): Promise<GameCategoryItem[]> => {
  const results = await fetchAllPaginatedResults('/game-pages/categories/')

  const parseGameCount = (item: any): number => {
    const rawValue = item?.game_pages_count ?? item?.games_count ?? item?.count ?? 0
    const parsed = Number(rawValue)
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 0
  }

  const totalGamesCount = results.reduce((sum: number, item: any) => sum + parseGameCount(item), 0)

  const allCategory: GameCategoryItem = {
    id: 'all',
    name: 'All Games',
    nameKey: 'allGames',
    icon: '🎮',
    code: 'all',
    gamesCount: totalGamesCount,
  }

  const categories = results.map((item: any) => {
    const name = String(item.name || '')
    const slug = String(item.slug || name)
    const nameKey = resolveCategoryNameKey(`${slug}|${name}`) || slug

    return {
      id: String(item.id),
      name,
      nameKey,
      icon: mapCategoryIcon(`${name}|${slug}`),
      code: slug,
      gamesCount: parseGameCount(item),
    } as GameCategoryItem
  })

  return [allCategory, ...categories]
}

export const getGames = async (params?: {
  category?: string
  search?: string
  is_hot?: boolean
}): Promise<RechargeGame[]> => {
  const queryParams: Record<string, any> = { ...params }

  if (typeof queryParams.category === 'string') {
    const resolvedCategory = await resolveCategoryParam(queryParams.category)
    if (resolvedCategory) {
      queryParams.category = resolvedCategory
    } else {
      delete queryParams.category
    }
  }

  const results = await fetchAllPaginatedResults('/game-pages/pages/', queryParams)
  return results.map(toRechargeGame)
}

export interface PaginatedGamesResult {
  items: RechargeGame[]
  total: number
  page: number
  pageSize: number
  hasNext: boolean
}

export const getGamesPage = async (
  params?: {
    category?: string
    search?: string
    is_hot?: boolean
  },
  pagination?: {
    page?: number
    pageSize?: number
    page_size?: number
  }
): Promise<PaginatedGamesResult> => {
  const queryParams: Record<string, any> = { ...(params || {}) }

  if (typeof queryParams.category === 'string') {
    const resolvedCategory = await resolveCategoryParam(queryParams.category)
    if (resolvedCategory) {
      queryParams.category = resolvedCategory
    } else {
      delete queryParams.category
    }
  }

  const requestedPage = toPositiveInt(pagination?.page, 1)
  const requestedPageSize = toPositiveInt(pagination?.pageSize ?? pagination?.page_size, 24)

  queryParams.page = requestedPage
  queryParams.page_size = requestedPageSize

  const response: any = await client.get('/game-pages/pages/', { params: queryParams })

  if (Array.isArray(response)) {
    const rows = response.map(toRechargeGame)
    return {
      items: rows,
      total: rows.length,
      page: requestedPage,
      pageSize: rows.length || requestedPageSize,
      hasNext: false,
    }
  }

  const rows = extractList(response).map(toRechargeGame)
  const countRaw = Number(response?.count)
  const total = Number.isFinite(countRaw) && countRaw >= 0 ? countRaw : rows.length
  const responsePageSize = toPositiveInt(response?.page_size ?? response?.limit, rows.length || requestedPageSize)
  const hasNext = Boolean(response?.next) || (rows.length > 0 && total > requestedPage * responsePageSize)

  return {
    items: rows,
    total,
    page: requestedPage,
    pageSize: responsePageSize,
    hasNext,
  }
}

export const getGameDetail = async (id: string): Promise<RechargeGame> => {
  const isId = /^\d+$/.test(id)

  const response: any = isId
    ? await client.get(`/game-pages/pages/${id}/`)
    : await client.get('/game-pages/pages/by_slug/', { params: { slug: id } })

  return toRechargeGame(response)
}

export const getHotGames = async (): Promise<RechargeGame[]> => {
  const response: any = await client.get('/game-pages/pages/hot_pages/')
  const results = extractList(response)
  return results.map(toRechargeGame)
}

export const paymentMethodLabels: Record<string, string> = {
  alipay: 'Alipay',
  wechat: 'WeChat Pay',
  paypal: 'PayPal',
  usdt: 'USDT',
  'foreign-currency': 'Foreign Currency',
}
