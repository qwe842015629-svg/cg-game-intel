import axios from 'axios'
import { API_BASE_URL } from './base'

const normalizeBase = (value: string) => value.replace(/\/+$/, '')
const preferredBackendTarget =
  (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim() || 'http://127.0.0.1:8000'

const directApiTargets = Array.from(
  new Set(
    [preferredBackendTarget, 'http://127.0.0.1:8000', 'http://localhost:8000']
      .filter((value): value is string => Boolean(value))
      .map((value) => normalizeBase(value))
      .map((value) => (value.endsWith('/api') ? value : `${value}/api`))
  )
)

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken') || localStorage.getItem('token')
    if (token) {
      const normalizedToken = token.trim()
      const hasScheme = /^(Token|Bearer)\s+/i.test(normalizedToken)
      config.headers.Authorization = hasScheme ? normalizedToken : `Token ${normalizedToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

const shouldRetryWithDirectApi = (error: any) => {
  if (!import.meta.env.DEV) return false

  const config = error?.config
  if (!config || config._directFallbackRetried) return false

  const requestUrl = String(config.url || '')
  if (requestUrl.startsWith('http://') || requestUrl.startsWith('https://')) return false

  const method = String(config.method || 'get').toLowerCase()
  if (method !== 'get') return false

  const status = error?.response?.status
  if (status !== 500) return false

  const responseData = error?.response?.data
  const responseText =
    typeof responseData === 'string' ? responseData : JSON.stringify(responseData || {})

  if (!responseText || responseText === '{}') return true

  return (
    responseText.includes('Error occurred while trying to proxy') ||
    responseText.includes('ECONNREFUSED') ||
    responseText.includes('connect ECONNREFUSED') ||
    responseText.includes('socket hang up') ||
    responseText.includes('proxy error')
  )
}

const retryWithDirectApi = async (error: any) => {
  const config = error?.config
  if (!config) return null

  for (const directBaseUrl of directApiTargets) {
    try {
      const response = await axios.request({
        ...config,
        baseURL: directBaseUrl,
        _directFallbackRetried: true,
      })
      return response.data
    } catch {
      // keep trying next target
    }
  }

  return null
}

client.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (shouldRetryWithDirectApi(error)) {
      const retriedResult = await retryWithDirectApi(error)
      if (retriedResult !== null) {
        console.warn('代理请求失败，已自动切换为直连后端地址')
        return retriedResult
      }

      console.error(`后端服务不可达，已尝试地址: ${directApiTargets.join(', ')}`)
    }

    if (error.response) {
      const responseData = error.response.data
      const responseText =
        typeof responseData === 'string' ? responseData : JSON.stringify(responseData || {})

      switch (error.response.status) {
        case 401:
          localStorage.removeItem('authToken')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          break
        case 403:
          console.error('没有权限访问')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器错误:', responseText.slice(0, 500))
          break
        default:
          console.error('请求失败:', responseText.slice(0, 500))
      }
    } else if (error.request) {
      console.error('网络错误，请检查后端服务是否已启动（默认端口 8000）')
    } else {
      console.error('请求失败:', error.message)
    }

    return Promise.reject(error)
  }
)

export default client
