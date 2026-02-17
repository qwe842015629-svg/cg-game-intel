import client from './client'

// TypeScript类型定义
export interface GamePageCategory {
  id: number
  name: string
  description: string
  sort_order: number
  is_active: boolean
  game_pages_count: number
  created_at: string
  updated_at: string
}

export interface GamePage {
  id: number
  title: string
  slug: string
  category: number
  category_name: string
  game?: number
  game_name?: string
  author_name: string
  cover_image?: string
  cover_image_url?: string
  excerpt: string
  content?: string
  status: 'draft' | 'published' | 'archived'
  is_top: boolean
  is_hot: boolean
  is_recommended: boolean
  view_count: number
  like_count: number
  published_at: string
  created_at: string
  updated_at: string
}

export interface GamePageDetail extends GamePage {
  category_info: GamePageCategory
  game_info?: {
    id: number
    name: string
    icon?: string
  }
}

// API函数
/**
 * 获取所有游戏页面分类
 */
export const getGamePageCategories = async (): Promise<GamePageCategory[]> => {
  const response: any = await client.get('/game-pages/categories/')
  return (response.results || response) as GamePageCategory[]
}

/**
 * 获取激活的游戏页面分类
 */
export const getActiveGamePageCategories = async (): Promise<GamePageCategory[]> => {
  const response: any = await client.get('/game-pages/categories/active/')
  return response as GamePageCategory[]
}

/**
 * 获取游戏页面列表
 * @param params - 查询参数 { category, game, status, is_top, is_hot, is_recommended, search }
 */
export const getGamePages = async (params?: Record<string, any>): Promise<GamePage[]> => {
  const response: any = await client.get('/game-pages/pages/', { params })
  return (response.results || response) as GamePage[]
}

/**
 * 获取游戏页面详情
 * @param id - 页面ID
 */
export const getGamePageDetail = async (id: string | number): Promise<GamePageDetail> => {
  const response: any = await client.get(`/game-pages/pages/${id}/`)
  return response as GamePageDetail
}

/**
 * 根据slug获取游戏页面详情
 * @param slug - 页面slug
 */
export const getGamePageBySlug = async (slug: string): Promise<GamePageDetail> => {
  const response: any = await client.get('/game-pages/pages/by_slug/', {
    params: { slug }
  })
  return response as GamePageDetail
}

/**
 * 获取置顶游戏页面
 */
export const getTopGamePages = async (): Promise<GamePage[]> => {
  const response: any = await client.get('/game-pages/pages/top_pages/')
  return response as GamePage[]
}

/**
 * 获取热门游戏页面
 */
export const getHotGamePages = async (): Promise<GamePage[]> => {
  const response: any = await client.get('/game-pages/pages/hot_pages/')
  return response as GamePage[]
}

/**
 * 获取推荐游戏页面
 */
export const getRecommendedGamePages = async (): Promise<GamePage[]> => {
  const response: any = await client.get('/game-pages/pages/recommended_pages/')
  return response as GamePage[]
}

/**
 * 根据游戏ID获取相关页面
 * @param gameId - 游戏ID
 */
export const getGamePagesByGame = async (gameId: number): Promise<GamePage[]> => {
  const response: any = await client.get('/game-pages/pages/by_game/', {
    params: { game_id: gameId }
  })
  return response as GamePage[]
}

/**
 * 点赞游戏页面
 * @param id - 页面ID
 */
export const likeGamePage = async (id: number): Promise<{ status: string; like_count: number }> => {
  const response: any = await client.post(`/game-pages/pages/${id}/like/`)
  return response as { status: string; like_count: number }
}
