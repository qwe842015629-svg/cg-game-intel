import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { locales, type LocaleCode, type TranslationKey } from '../i18n/locales'
import { i18n } from '../i18n/vue-i18n.config'

export const useLanguageStore = defineStore('language', () => {
  // 当前语言，默认简体中文
  const currentLocale = ref<LocaleCode>('zh-CN')
  
  // 从 localStorage 初始化
  const initLanguage = () => {
    const saved = localStorage.getItem('locale')
    if (saved && saved in locales) {
      currentLocale.value = saved as LocaleCode
    } else {
      // 尝试从浏览器语言检测
      const browserLang = navigator.language
      if (browserLang.startsWith('zh')) {
        currentLocale.value = browserLang.includes('TW') || browserLang.includes('HK') ? 'zh-TW' : 'zh-CN'
      } else if (browserLang.startsWith('ja')) {
        currentLocale.value = 'ja'
      } else if (browserLang.startsWith('ko')) {
        currentLocale.value = 'ko'
      } else if (browserLang.startsWith('th')) {
        currentLocale.value = 'th'
      } else if (browserLang.startsWith('vi')) {
        currentLocale.value = 'vi'
      } else if (browserLang.startsWith('fr')) {
        currentLocale.value = 'fr'
      } else if (browserLang.startsWith('de')) {
        currentLocale.value = 'de'
      } else {
        currentLocale.value = 'en'
      }
    }
  }
  
  // 切换语言
  const setLocale = (locale: LocaleCode) => {
    currentLocale.value = locale
    localStorage.setItem('locale', locale)
    // 同步更新 vue-i18n 的语言
    i18n.global.locale.value = locale
  }
  
  // 获取翻译文本（混合策略：优先使用自定义翻译，缺失时使用 vue-i18n）
  const t = (key: TranslationKey): string => {
    // 首先尝试从自定义 locales 获取
    const customTranslation = locales[currentLocale.value].translations[key]
    
    if (customTranslation && customTranslation !== key) {
      return customTranslation
    }
    
    // 如果自定义翻译不存在或等于 key，尝试使用 vue-i18n
    // 直接访问 messages 来避免类型问题
    try {
      const messages = i18n.global.messages.value[currentLocale.value] as any
      if (messages && messages[key]) {
        return messages[key]
      }
    } catch (e) {
      // 访问失败
    }
    
    // 都没有找到，返回 key
    return key
  }
  
  // 获取所有可用语言
  const availableLocales = computed(() => {
    return Object.values(locales).map(locale => ({
      code: locale.code,
      name: locale.name
    }))
  })
  
  return {
    currentLocale,
    availableLocales,
    initLanguage,
    setLocale,
    t
  }
})
