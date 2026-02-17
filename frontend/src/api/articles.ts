import client from './client'
import type { Article } from '../types'

/**
 * 文章相关API
 */

// 文章分类类型
export interface ArticleCategory {
  id: number
  name: string
  description: string
  sort_order: number
  is_active: boolean
  articles_count: number
  created_at: string
  updated_at: string
}

// 获取文章分类列表
export const getArticleCategories = async (): Promise<ArticleCategory[]> => {
  const response: any = await client.get('/articles/categories/')
  return response.results || response
}

// 获取文章列表
export const getArticles = async (params?: {
  category?: string
  search?: string
  is_hot?: boolean
}): Promise<Article[]> => {
  const response: any = await client.get('/articles/articles/', { params })
  return response.results || response
}

// 获取文章详情
export const getArticleDetail = async (id: string): Promise<Article> => {
  const response: any = await client.get(`/articles/articles/${id}/`)
  return response as Article
}

// 获取热门文章
export const getHotArticles = async (): Promise<Article[]> => {
  const response: any = await client.get('/articles/articles/hot/')
  return response as Article[]
}

// 获取推荐文章
export const getRecommendedArticles = async (): Promise<Article[]> => {
  const response: any = await client.get('/articles/articles/recommended/')
  return response as Article[]
}

// 点赞文章
export const likeArticle = async (id: string): Promise<{ like_count: number }> => {
  const response: any = await client.post(`/articles/${id}/like/`)
  return response
}

// 获取智能推荐文章
export const getSmartRecommendedArticles = async (limit: number = 10): Promise<Article[]> => {
  const response: any = await client.get('/articles/articles/smart_recommended/', { 
    params: { limit } 
  })
  return response.results || response
}
