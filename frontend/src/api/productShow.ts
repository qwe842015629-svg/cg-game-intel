import client from './client'

// TypeScript类型定义
export interface ProductShowCategory {
  id: number
  name: string
  description: string
  sort_order: number
  is_active: boolean
  shows_count: number
  created_at: string
  updated_at: string
}

export interface ProductShow {
  id: number
  title: string
  slug: string
  category: string
  game_name?: string
  excerpt: string
  content?: string
  image: string
  author_name: string
  is_top: boolean
  is_hot: boolean
  is_recommended: boolean
  view_count: number
  like_count: number
  published_at: string
  created_at: string
  updated_at?: string
}

// API函数
/**
 * 获取所有产品展示分类
 */
export const getProductShowCategories = async (): Promise<ProductShowCategory[]> => {
  const response: any = await client.get('/product-show/categories/')
  return (response.results || response) as ProductShowCategory[]
}

/**
 * 获取产品展示列表
 * @param params - 查询参数 { category, search, is_hot, is_recommended }
 */
export const getProductShows = async (params?: Record<string, any>): Promise<ProductShow[]> => {
  const response: any = await client.get('/product-show/shows/', { params })
  return (response.results || response) as ProductShow[]
}

/**
 * 获取产品展示详情
 * @param id - 展示页ID
 */
export const getProductShowDetail = async (id: string | number): Promise<ProductShow> => {
  const response: any = await client.get(`/product-show/shows/${id}/`)
  return response as ProductShow
}

/**
 * 获取热门产品展示
 */
export const getHotProductShows = async (): Promise<ProductShow[]> => {
  const response: any = await client.get('/product-show/shows/hot/')
  return response as ProductShow[]
}

/**
 * 获取推荐产品展示
 */
export const getRecommendedProductShows = async (): Promise<ProductShow[]> => {
  const response: any = await client.get('/product-show/shows/recommended/')
  return response as ProductShow[]
}
