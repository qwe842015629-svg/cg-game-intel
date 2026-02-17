import { computed } from 'vue'
import { useI18n as useVueI18n } from 'vue-i18n'
import { useLanguageStore } from '../stores/language'

/**
 * 混合 i18n composable
 * 优先使用自定义翻译，缺失时使用 vue-i18n
 */
export function useI18n() {
  const languageStore = useLanguageStore()
  const vueI18n = useVueI18n()
  
  // 当前语言
  const locale = computed({
    get: () => languageStore.currentLocale,
    set: (value) => languageStore.setLocale(value)
  })
  
  // 混合翻译函数
  const t = (key: string) => {
    // 使用 languageStore 的增强 t 函数，已包含混合策略
    return languageStore.t(key as any)
  }
  
  // 直接使用 vue-i18n 的翻译（可选）
  const ti = (key: string) => {
    return vueI18n.t(key)
  }
  
  return {
    locale,
    t,
    ti,
    availableLocales: languageStore.availableLocales
  }
}
