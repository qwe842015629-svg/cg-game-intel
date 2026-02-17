﻿﻿import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'

export function useVisualEditor(sectionKey: string, sectionName: string) {
  const route = useRoute()
  const isEditMode = ref(false)
  const pageConfig = ref<Record<string, any>>({})

  const getPageConfig = (key: string, defaultValue: any) => {
    return pageConfig.value[key] !== undefined ? pageConfig.value[key] : defaultValue
  }

  const handleInlineEdit = (event: FocusEvent, configKey: string) => {
    if (!isEditMode.value) return
    const target = event.target as HTMLElement
    const newValue = target.innerText.trim()

    if (pageConfig.value[configKey] === newValue) return

    pageConfig.value[configKey] = newValue

    if (window.parent) {
      window.parent.postMessage(
        {
          type: 'CONFIG_UPDATE_FROM_INLINE',
          sectionKey,
          config: { [configKey]: newValue },
        },
        '*'
      )
    }
  }

  const handleImageClick = (event: MouseEvent, configKey: string) => {
    if (!isEditMode.value) return
    event.preventDefault()
    event.stopPropagation()

    const target = event.currentTarget as HTMLElement
    const img = target.querySelector('img')
    const currentUrl = img ? img.src : ''

    const newUrl = window.prompt('请输入新的图片 URL:', currentUrl)

    if (newUrl !== null && newUrl !== currentUrl) {
      pageConfig.value[configKey] = newUrl
      if (window.parent) {
        window.parent.postMessage(
          {
            type: 'CONFIG_UPDATE_FROM_INLINE',
            sectionKey,
            config: { [configKey]: newUrl },
          },
          '*'
        )
      }
    }
  }

  const reportSection = () => {
    if (isEditMode.value && window.parent) {
      window.parent.postMessage(
        {
          type: 'SECTION_SELECTED',
          section: {
            key: sectionKey,
            name: sectionName,
            config: pageConfig.value,
          },
        },
        '*'
      )
    }
  }

  const loadConfig = async () => {
    try {
      const data = (await client.get(`/layouts/section/?key=${sectionKey}`)) as any
      if (data?.config) {
        pageConfig.value = data.config
        reportSection()
      }
    } catch (err) {
      console.error('Failed to load section config:', err)
    }
  }

  const onMessage = (event: MessageEvent) => {
    const { data } = event
    if (data.type === 'CONFIG_UPDATE' && data.sectionKey === sectionKey) {
      pageConfig.value = { ...pageConfig.value, ...data.config }
    } else if (data.type === 'SELECT_SECTION_BY_KEY' && data.sectionKey === sectionKey) {
      reportSection()
    }
  }

  onMounted(() => {
    isEditMode.value = route.query.edit_mode === 'true'
    loadConfig()

    if (isEditMode.value) {
      window.addEventListener('message', onMessage)
    }
  })

  onUnmounted(() => {
    window.removeEventListener('message', onMessage)
  })

  return {
    isEditMode,
    pageConfig,
    getPageConfig,
    handleInlineEdit,
    handleImageClick,
    reportSection,
  }
}
