import type { App } from 'vue'
import { computed } from 'vue'
import { useLanguageStore } from '../stores/language'

export default {
  install(app: App) {
    // 全局mixin提供响应式翻译
    app.mixin({
      computed: {
        // 这个 computed 属性会在 currentLocale 变化时重新计算
        $$translateKey() {
          const languageStore = useLanguageStore()
          // 访问 currentLocale 以建立响应式依赖
          return languageStore.currentLocale
        },
        $lang() {
          const languageStore = useLanguageStore()
          return languageStore.currentLocale
        }
      },
      methods: {
        $t(key: string) {
          const languageStore = useLanguageStore()
          // 访问 computed 属性以建立响应式连接
          const _ = (this as any).$$translateKey
          // 使用增强后的 t 函数，它已经包含了混合策略
          return languageStore.t(key as any)
        }
      }
    })
    
    // 全局属性：翻译函数（用于非组件上下文）
    app.config.globalProperties.$t = function(key: string) {
      const languageStore = useLanguageStore()
      return languageStore.t(key as any)
    }
  }
}
