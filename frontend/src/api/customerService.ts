import client from './client'

/**
 * 客服相关API
 */

// 联系方式类型定义
export interface ContactMethod {
  id: number
  contact_type: string
  contact_type_display: string
  title: string
  description: string
  contact_info: string
  icon: string
  button_text: string
  button_link: string
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

// 常见问题类型定义
export interface FAQ {
  id: number
  question: string
  answer: string
  category: string
  is_active: boolean
  sort_order: number
  view_count: number
  created_at: string
  updated_at: string
}

// 客服页面配置类型定义
export interface CustomerServiceConfig {
  id: number
  page_title: string
  page_description: string
  show_contact_methods: boolean
  show_faq: boolean
  faq_title: string
  updated_at: string
}

// 获取所有联系方式
export const getContactMethods = async (): Promise<ContactMethod[]> => {
  const response: any = await client.get('/customer-service/contact-methods/')
  // 处理DRF分页器返回的数据结构
  return (response.results || response) as ContactMethod[]
}

// 获取所有常见问题
export const getFAQs = async (params?: { category?: string }): Promise<FAQ[]> => {
  const response: any = await client.get('/customer-service/faqs/', { params })
  // 处理DRF分页器返回的数据结构
  return (response.results || response) as FAQ[]
}

// 获取客服页面配置
export const getCustomerServiceConfig = async (): Promise<CustomerServiceConfig> => {
  const response: any = await client.get('/customer-service/config/current/')
  return response as CustomerServiceConfig
}
