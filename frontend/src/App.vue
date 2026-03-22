<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'
import client from './api/client'
import { useAuthStore } from './stores/auth'
import { useLanguageStore } from './stores/language'
import { useThemeStore } from './stores/theme'
import {
  guardUsagePolicyContent,
  isUsagePolicyViolationError,
  openUsagePolicyDialog,
  type UsagePolicyScene,
} from './utils/usagePolicy'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const languageStore = useLanguageStore()

const currentLanguage = computed(() => languageStore.currentLocale)
const FETCH_GUARD_METHODS = new Set(['POST', 'PUT', 'PATCH'])
let nativeFetch: typeof window.fetch | null = null

const handleMessage = (event: MessageEvent) => {
  const { data } = event
  if (data?.type !== 'GLOBAL_STYLE_UPDATE') return

  const variable = String(data.variable || '')
  const value = String(data.value ?? '')
  if (!variable) return

  if (variable.startsWith('--')) {
    themeStore.applyCssVariables({ [variable]: value })
    return
  }

  if (variable === 'themePreset') {
    themeStore.setPreset(value)
    return
  }

  if (variable === 'cursorMode') {
    themeStore.setCursorMode(value as any)
  }
}

const loadRemoteThemeConfig = async () => {
  try {
    const payload = (await client.get('/site-config/')) as any
    const themeConfig = payload?.themeConfig
    themeStore.applyThemeConfig(themeConfig)
  } catch (error) {
    console.error('加载远程主题配置失败:', error)
  }
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

const resolveFetchMethod = (input: RequestInfo | URL, init?: RequestInit): string => {
  const initMethod = String(init?.method || '').trim().toUpperCase()
  if (initMethod) return initMethod
  if (typeof Request !== 'undefined' && input instanceof Request) {
    return String(input.method || 'GET').toUpperCase()
  }
  return 'GET'
}

const resolveFetchUrl = (input: RequestInfo | URL): string => {
  if (typeof input === 'string') return input
  if (typeof URL !== 'undefined' && input instanceof URL) return input.toString()
  if (typeof Request !== 'undefined' && input instanceof Request) return String(input.url || '')
  return String(input || '')
}

const resolveFetchScene = (rawUrl: string): UsagePolicyScene => {
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
  if (url.includes('/plaza-posts/') || url.includes('/novel-works/') || url.includes('/publish')) {
    return 'publish'
  }
  return 'generic'
}

const readFetchPayload = async (input: RequestInfo | URL, init?: RequestInit): Promise<unknown> => {
  let body: BodyInit | null | undefined = init?.body

  if (body === undefined && typeof Request !== 'undefined' && input instanceof Request) {
    try {
      body = await input.clone().text()
    } catch {
      body = undefined
    }
  }

  if (body === undefined || body === null) return undefined
  if (typeof body === 'string') return parseMaybeJson(body)
  if (typeof URLSearchParams !== 'undefined' && body instanceof URLSearchParams) return body
  if (typeof FormData !== 'undefined' && body instanceof FormData) return body
  if (typeof Blob !== 'undefined' && body instanceof Blob) {
    try {
      return await body.text()
    } catch {
      return undefined
    }
  }
  return body
}

const installFetchUsagePolicyGuard = () => {
  if (typeof window === 'undefined' || nativeFetch) return
  nativeFetch = window.fetch.bind(window)

  window.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const method = resolveFetchMethod(input, init)
    if (FETCH_GUARD_METHODS.has(method)) {
      try {
        const payload = await readFetchPayload(input, init)
        if (payload !== undefined) {
          guardUsagePolicyContent(payload, resolveFetchScene(resolveFetchUrl(input)))
        }
      } catch (error) {
        if (isUsagePolicyViolationError(error)) {
          openUsagePolicyDialog(error.message)
        }
        return Promise.reject(error)
      }
    }

    return nativeFetch!(input, init)
  }) as typeof window.fetch
}

const uninstallFetchUsagePolicyGuard = () => {
  if (typeof window === 'undefined' || !nativeFetch) return
  window.fetch = nativeFetch
  nativeFetch = null
}

onMounted(async () => {
  authStore.init()
  themeStore.init()
  await languageStore.initLanguage()
  window.addEventListener('message', handleMessage)
  installFetchUsagePolicyGuard()
  await loadRemoteThemeConfig()
})

onBeforeUnmount(() => {
  window.removeEventListener('message', handleMessage)
  uninstallFetchUsagePolicyGuard()
})
</script>

<template>
  <RouterView :key="currentLanguage" />
</template>
