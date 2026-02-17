const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()

const stripTrailingSlash = (value: string) => value.replace(/\/+$/, '')

const buildApiBaseUrl = () => {
  if (!rawBaseUrl) return '/api'

  const normalized = stripTrailingSlash(rawBaseUrl)
  if (normalized.endsWith('/api')) return normalized

  return `${normalized}/api`
}

export const API_BASE_URL = buildApiBaseUrl()

export const buildApiUrl = (path: string) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalizedPath}`
}
