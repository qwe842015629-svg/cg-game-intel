import client from './client'

/**
 * 页面底部相关API
 */

// 底部板块类型定义
export interface FooterSection {
  id: number
  section_type: string
  section_type_display: string
  title: string
  description: string
  is_active: boolean
  sort_order: number
  links: FooterLink[]
  created_at: string
  updated_at: string
}

// 底部链接类型定义
export interface FooterLink {
  id: number
  title: string
  url: string
  icon: string
  is_external: boolean
  is_active: boolean
  sort_order: number
}

// 底部配置类型定义
export interface FooterConfig {
  id: number
  copyright_text: string
  show_copyright: boolean
  updated_at: string
}

// 获取所有底部板块
export const getFooterSections = async (): Promise<FooterSection[]> => {
  const response: any = await client.get('/footer/sections/')
  // 处理DRF分页器返回的数据结构
  return (response.results || response) as FooterSection[]
}

// 获取底部配置
export const getFooterConfig = async (): Promise<FooterConfig> => {
  const response: any = await client.get('/footer/config/current/')
  return response as FooterConfig
}
