import client from './client'
import type { User, LoginCredentials, RegisterData } from '../types'

/**
 * 认证相关API
 */

// 登录（Mock实现）
export const login = async (credentials: LoginCredentials): Promise<{ user: User; token: string }> => {
  // TODO: 替换为真实的API调用
  // const response = await client.post('/auth/login/', credentials)
  
  // Mock响应
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const mockUser: User = {
    id: '1',
    name: '游戏玩家',
    email: credentials.email,
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${credentials.email}`,
  }
  
  const mockToken = 'mock-jwt-token-' + Date.now()
  
  return {
    user: mockUser,
    token: mockToken,
  }
}

// 注册（Mock实现）
export const register = async (data: RegisterData): Promise<{ user: User; token: string }> => {
  // TODO: 替换为真实的API调用
  // const response = await client.post('/auth/register/', data)
  
  // Mock响应
  await new Promise(resolve => setTimeout(resolve, 500))
  
  const mockUser: User = {
    id: Date.now().toString(),
    name: data.name,
    email: data.email,
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.email}`,
  }
  
  const mockToken = 'mock-jwt-token-' + Date.now()
  
  return {
    user: mockUser,
    token: mockToken,
  }
}

// 登出
export const logout = async (): Promise<void> => {
  // TODO: 如果需要服务器端登出，调用API
  // await client.post('/auth/logout/')
  
  // 清除本地存储
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User | null> => {
  // TODO: 替换为真实的API调用
  // const response = await client.get('/auth/me/')
  // return response
  
  // 从localStorage获取
  const userStr = localStorage.getItem('user')
  if (userStr) {
    return JSON.parse(userStr)
  }
  return null
}
