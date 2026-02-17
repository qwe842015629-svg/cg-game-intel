import client from './client'

/**
 * 轮播图相关API
 */

// 获取轮播图列表
export const getBanners = async (): Promise<any[]> => {
  const response: any = await client.get('/banners/')
  return response.results || response
}

// 获取轮播图详情
export const getBannerDetail = async (id: number): Promise<any> => {
  const response: any = await client.get(`/banners/${id}/`)
  return response
}

// 获取默认轮播图
export const getDefaultBanner = async (): Promise<any> => {
  const response: any = await client.get('/banners/default/')
  return response
}

// 记录轮播图点击
export const clickBanner = async (id: number): Promise<any> => {
  const response: any = await client.post(`/banners/${id}/click/`)
  return response
}
