import { createI18n } from 'vue-i18n'
import { locales, type LocaleCode } from './locales'

// 将现有的 locales 转换为 vue-i18n 格式
const messages: Record<string, any> = {}

Object.keys(locales).forEach((key) => {
  const localeCode = key as LocaleCode
  messages[localeCode] = locales[localeCode].translations
})

// 创建 vue-i18n 实例
export const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: localStorage.getItem('locale') || 'zh-CN', // 默认语言
  fallbackLocale: 'zh-CN', // 回退语言
  messages,
  globalInjection: true, // 全局注入 $t
  missingWarn: false, // 关闭缺失警告
  fallbackWarn: false, // 关闭回退警告
})

export default i18n
