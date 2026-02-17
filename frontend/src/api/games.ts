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

const mapCategoryIcon = (nameOrSlug: string): string => {
  const value = (nameOrSlug || '').toLowerCase()
  if (!value) return '🎮'
  if (value === 'all' || value.includes('全部')) return '🎮'
  if (value.includes('国际') || value.includes('global') || value.includes('international')) return '🌍'
  if (value.includes('港台') || value.includes('hongkong') || value.includes('taiwan')) return '🏮'
  if (value.includes('东南亚') || value.includes('southeast') || value.includes('sea')) return '🌴'
  if (value.includes('日本') || value.includes('韩国') || value.includes('日韓') || value.includes('japan') || value.includes('korea')) return '🗾'
  if (value.includes('欧美') || value.includes('europe') || value.includes('america') || value.includes('western')) return '🛡️'
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

  const response: any = await client.get('/game-pages/categories/')
  const categories = extractList(response)
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
    console.warn('分类映射加载失败，已忽略分类筛选:', error)
    return undefined
  }
}

export const getGameCategories = async (): Promise<GameCategoryItem[]> => {
  const response: any = await client.get('/game-pages/categories/')
  const results = extractList(response)

  const allCategory: GameCategoryItem = {
    id: 'all',
    name: '全部游戏',
    nameKey: 'allGames',
    icon: '🎮',
    code: 'all',
    gamesCount: 0,
  }

  const categories = results.map((item: any) => {
    const name = String(item.name || '')
    const slug = String(item.slug || name)
    return {
      id: String(item.id),
      name,
      nameKey: slug,
      icon: mapCategoryIcon(`${name}|${slug}`),
      code: slug,
      gamesCount: Number(item.game_pages_count || 0),
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

  const response: any = await client.get('/game-pages/pages/', { params: queryParams })
  const results = extractList(response)
  return results.map(toRechargeGame)
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
  alipay: '支付宝',
  wechat: '微信支付',
  paypal: 'PayPal',
  usdt: 'USDT',
  'foreign-currency': '外币支付',
}
