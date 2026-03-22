import axios from 'axios'
import { API_BASE_URL } from './base'
import {
  guardUsagePolicyContent,
  isUsagePolicyViolationError,
  openUsagePolicyDialog,
  type UsagePolicyScene,
} from '../utils/usagePolicy'

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
  // Frontend uses token auth header; avoid sending session cookies to prevent CSRF checks.
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
})

const resolveRequestLocale = (): string => {
  if (typeof window === 'undefined') return 'zh-CN'
  const saved = String(window.localStorage.getItem('locale') || '').trim()
  if (saved) return saved
  return String(window.navigator?.language || 'zh-CN')
}

const normalizeApiLocale = (rawLocale: string): string => {
  const raw = String(rawLocale || '').trim().toLowerCase()
  if (!raw) return 'zh-CN'
  if (raw.startsWith('zh')) {
    if (raw.includes('tw') || raw.includes('hk') || raw.includes('hant')) return 'zh-TW'
    return 'zh-CN'
  }
  if (raw.startsWith('en')) return 'en'
  if (raw.startsWith('ja')) return 'ja'
  if (raw.startsWith('ko')) return 'ko'
  if (raw.startsWith('fr')) return 'fr'
  if (raw.startsWith('de')) return 'de'
  if (raw.startsWith('vi')) return 'vi'
  if (raw.startsWith('th')) return 'th'
  return rawLocale
}

const buildAcceptLanguageHeader = (locale: string): string => {
  switch (locale) {
    case 'zh-CN':
      return 'zh-CN,zh;q=0.9,en;q=0.6'
    case 'zh-TW':
      return 'zh-TW,zh;q=0.9,en;q=0.6'
    case 'en':
      return 'en-US,en;q=0.9'
    case 'ja':
      return 'ja-JP,ja;q=0.9,en;q=0.6'
    case 'ko':
      return 'ko-KR,ko;q=0.9,en;q=0.6'
    case 'fr':
      return 'fr-FR,fr;q=0.9,en;q=0.6'
    case 'de':
      return 'de-DE,de;q=0.9,en;q=0.6'
    case 'vi':
      return 'vi-VN,vi;q=0.9,en;q=0.6'
    case 'th':
      return 'th-TH,th;q=0.9,en;q=0.6'
    default:
      return String(locale || 'zh-CN')
  }
}

const shouldAttachLocaleParam = (url: string, method: string): boolean => {
  if (String(method || 'get').toLowerCase() !== 'get') return false

  const normalizedUrl = String(url || '').trim()
  if (!normalizedUrl) return false

  // locale is safe for all internal GET APIs; unknown query params are ignored by DRF.
  // Using explicit locale query avoids relying only on custom headers for proxy/caching cases.
  if (/^https?:\/\//i.test(normalizedUrl)) return false

  return true
}

const USAGE_POLICY_GUARD_METHODS = new Set(['post', 'put', 'patch', 'delete'])

const resolveUsagePolicyScene = (rawUrl: string): UsagePolicyScene => {
  const url = String(rawUrl || '').toLowerCase()
  if (!url) return 'generic'
  if (
    url.includes('/chat/completions') ||
    url.includes('/images/generations') ||
    url.includes('/videos/generations') ||
    url.includes('/audio/')
  ) {
    return 'ai_generation'
  }
  if (url.includes('/dm/') || url.includes('/messages/') || url.includes('/customer-service/chat/')) {
    return 'chat'
  }
  if (url.includes('/share')) return 'share'
  if (
    url.includes('/plaza-posts/') ||
    url.includes('/novel-works/') ||
    url.includes('/articles/') ||
    url.includes('/publish')
  ) {
    return 'publish'
  }
  return 'generic'
}

const parseMaybeJson = (raw: string): unknown => {
  const text = String(raw || '').trim()
  if (!text) return ''
  if (!((text.startsWith('{') && text.endsWith('}')) || (text.startsWith('[') && text.endsWith(']')))) {
    return text
  }
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

const normalizeGuardInput = (input: unknown): unknown => {
  if (typeof input === 'string') return parseMaybeJson(input)
  return input
}

client.interceptors.request.use(
  (config) => {
    const method = String(config.method || 'get').toLowerCase()
    if (USAGE_POLICY_GUARD_METHODS.has(method)) {
      const guardInput =
        config.data !== undefined || config.params !== undefined
          ? {
              data: normalizeGuardInput(config.data),
              params: normalizeGuardInput(config.params),
            }
          : undefined

      if (guardInput !== undefined) {
        try {
          guardUsagePolicyContent(guardInput, resolveUsagePolicyScene(String(config.url || '')))
        } catch (error) {
          if (isUsagePolicyViolationError(error)) {
            openUsagePolicyDialog(error.message)
          }
          return Promise.reject(error)
        }
      }
    }

    const token = localStorage.getItem('authToken') || localStorage.getItem('token')
    if (token) {
      const normalizedToken = token.trim()
      const hasScheme = /^(Token|Bearer)\s+/i.test(normalizedToken)
      config.headers.Authorization = hasScheme ? normalizedToken : `Token ${normalizedToken}`
    }

    const locale = normalizeApiLocale(resolveRequestLocale())
    config.headers['X-Locale'] = locale
    config.headers['Accept-Language'] = buildAcceptLanguageHeader(locale)

    if (shouldAttachLocaleParam(String(config.url || ''), String(config.method || 'get'))) {
      const currentParams = config.params && typeof config.params === 'object' ? config.params : {}
      if (currentParams.locale === undefined) {
        config.params = {
          ...currentParams,
          locale,
        }
      }
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
