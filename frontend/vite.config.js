import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendTarget = env.VITE_BACKEND_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            const normalizedId = String(id || '').replace(/\\/g, '/')

            if (normalizedId.includes('/src/i18n/messages/')) {
              const localeMatch = normalizedId.match(/\/src\/i18n\/messages\/([^/]+)\//)
              const localeCode = localeMatch?.[1]
              if (localeCode) {
                return `i18n-messages-${localeCode}`
              }
              return 'i18n-messages'
            }

            if (normalizedId.includes('/src/i18n/locales.ts')) {
              return 'i18n-core'
            }

            if (normalizedId.includes('/node_modules/')) {
              if (normalizedId.includes('/axios/')) {
                return 'network'
              }

              if (
                normalizedId.includes('/lucide-vue-next/') ||
                normalizedId.includes('/simple-icons/')
              ) {
                return 'icons'
              }

              return 'vendor'
            }
          },
        },
      },
    },
    server: {
      port: 5176,
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
        }
      }
    }
  }
})
