import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { locales, type LocaleCode } from '../i18n/locales'
import { ensureLocaleMessages, i18n } from '../i18n/vue-i18n.config'
import { normalizeLocaleCode, resolveInitialLocale } from '../i18n/locale-utils'

const syncI18nLocale = async (locale: LocaleCode): Promise<void> => {
  await ensureLocaleMessages(locale)
  i18n.global.locale.value = locale
}

export const useLanguageStore = defineStore('language', () => {
  const currentLocale = ref<LocaleCode>(resolveInitialLocale())

  const initLanguage = async () => {
    const locale = resolveInitialLocale()
    currentLocale.value = locale
    await syncI18nLocale(locale)

    if (typeof window !== 'undefined') {
      window.localStorage.setItem('locale', locale)
    }
  }

  const setLocale = async (locale: LocaleCode) => {
    const normalized = normalizeLocaleCode(locale)
    currentLocale.value = normalized

    if (typeof window !== 'undefined') {
      window.localStorage.setItem('locale', normalized)
    }

    await syncI18nLocale(normalized)
  }

  const t = (key: string, params?: Record<string, unknown>): string => {
    const customTranslations = locales[currentLocale.value]?.translations as Record<string, string>
    const customValue = customTranslations?.[key]

    if (typeof customValue === 'string' && customValue.length > 0 && !params) {
      return customValue
    }

    const translated = i18n.global.t(key as string, params as any)
    return typeof translated === 'string' ? translated : String(translated)
  }

  const availableLocales = computed(() => {
    return Object.values(locales).map((locale) => ({
      code: locale.code,
      name: locale.name,
    }))
  })

  return {
    currentLocale,
    availableLocales,
    initLanguage,
    setLocale,
    t,
  }
})
