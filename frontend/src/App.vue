<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'
import client from './api/client'
import { useAuthStore } from './stores/auth'
import { useLanguageStore } from './stores/language'
import { useThemeStore } from './stores/theme'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const languageStore = useLanguageStore()

const currentLanguage = computed(() => languageStore.currentLocale)

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

onMounted(async () => {
  authStore.init()
  themeStore.init()
  languageStore.initLanguage()
  window.addEventListener('message', handleMessage)
  await loadRemoteThemeConfig()
})

onBeforeUnmount(() => {
  window.removeEventListener('message', handleMessage)
})
</script>

<template>
  <RouterView :key="currentLanguage" />
</template>
