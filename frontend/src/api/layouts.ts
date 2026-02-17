import client from './client'

export interface LayoutSection {
  id: number
  sectionKey: string
  sectionName: string
  isEnabled: boolean
  sortOrder: number
  config: Record<string, any>
  viewCount: number
}

/**
 * 获取所有启用的首页布局板块
 */
export const getHomeLayouts = async (): Promise<LayoutSection[]> => {
  const response = await client.get('/layouts/') as any
  // client 的响应拦截器已经返回了 response.data
  // 所以这里 response 就是数据本身
  return Array.isArray(response) ? response : (response.results || [])
}

/**
 * 根据section_key获取特定板块
 */
export const getLayoutByKey = async (sectionKey: string): Promise<LayoutSection> => {
  const response = await client.get(`/layouts/section/?key=${sectionKey}`) as any
  return response as LayoutSection
}

/**
 * 获取所有板块（包括禁用的）
 */
export const getAllLayouts = async (): Promise<LayoutSection[]> => {
  const response = await client.get('/layouts/all/') as any
  return response as LayoutSection[]
}
