import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import {
  DEFAULT_THEME_PRESET,
  THEME_PRESET_MAP,
  THEME_PRESETS,
  type ThemeCursorMode,
} from '../theme/presets'

type ThemeMode = 'light' | 'dark'

const THEME_MODE_KEY = 'theme_mode'
const THEME_PRESET_KEY = 'theme_preset'
const THEME_CURSOR_KEY = 'theme_cursor_mode'

const isHexColor = (value: string) => /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(value)

const hexToHslTokens = (hex: string): string | null => {
  const normalized = hex.replace('#', '').trim()
  if (!/^[0-9a-f]{3}$|^[0-9a-f]{6}$/i.test(normalized)) return null

  const full = normalized.length === 3 ? normalized.split('').map((char) => `${char}${char}`).join('') : normalized
  const r = parseInt(full.slice(0, 2), 16) / 255
  const g = parseInt(full.slice(2, 4), 16) / 255
  const b = parseInt(full.slice(4, 6), 16) / 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const delta = max - min

  let h = 0
  if (delta !== 0) {
    if (max === r) h = ((g - b) / delta) % 6
    else if (max === g) h = (b - r) / delta + 2
    else h = (r - g) / delta + 4
  }

  h = Math.round(h * 60)
  if (h < 0) h += 360

  const l = (max + min) / 2
  const s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1))

  return `${h} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<ThemeMode>('light')
  const preset = ref<string>(DEFAULT_THEME_PRESET)
  const cursorMode = ref<ThemeCursorMode>('soft')

  const presetOptions = computed(() => THEME_PRESETS)

  const applyThemeMode = (mode: ThemeMode) => {
    if (typeof document === 'undefined') return
    document.documentElement.classList.toggle('dark', mode === 'dark')
  }

  const applyCursorMode = (mode: ThemeCursorMode) => {
    if (typeof document === 'undefined') return
    document.documentElement.setAttribute('data-cursor-mode', mode)
  }

  const applyCssVariables = (variables: Record<string, string>) => {
    if (typeof document === 'undefined') return
    const root = document.documentElement
    Object.entries(variables).forEach(([key, value]) => {
      root.style.setProperty(key, String(value))
    })
  }

  const applyPreset = (presetId: string) => {
    const resolved = THEME_PRESET_MAP[presetId] || THEME_PRESET_MAP[DEFAULT_THEME_PRESET]
    preset.value = resolved.id

    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme-preset', resolved.id)
    }

    applyCssVariables(resolved.vars)
  }

  const setTheme = (newTheme: ThemeMode) => {
    theme.value = newTheme
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  const setPreset = (presetId: string) => {
    applyPreset(presetId)
  }

  const setCursorMode = (mode: ThemeCursorMode) => {
    cursorMode.value = mode
    applyCursorMode(mode)
  }

  const applyThemeConfig = (themeConfig?: Record<string, any>) => {
    if (!themeConfig || typeof themeConfig !== 'object') return

    const configPreset = String(themeConfig.themePreset || '').trim()
    const configCursor = String(themeConfig.cursorMode || '').trim() as ThemeCursorMode

    if (configPreset) {
      applyPreset(configPreset)
    }
    if (configCursor && ['system', 'soft', 'crosshair', 'neon'].includes(configCursor)) {
      setCursorMode(configCursor)
    }

    const cssVars: Record<string, string> = {}
    Object.entries(themeConfig).forEach(([key, rawValue]) => {
      if (!key.startsWith('--')) return
      cssVars[key] = String(rawValue)
    })
    applyCssVariables(cssVars)

    const primaryHex = cssVars['--primary-color']
    if (primaryHex && isHexColor(primaryHex)) {
      const hsl = hexToHslTokens(primaryHex)
      if (hsl) {
        applyCssVariables({ '--primary': hsl, '--ring': hsl })
      }
    }

    const secondaryHex = cssVars['--secondary-color']
    if (secondaryHex && isHexColor(secondaryHex)) {
      const hsl = hexToHslTokens(secondaryHex)
      if (hsl) {
        applyCssVariables({ '--secondary': hsl, '--accent': hsl })
      }
    }

    const pageBg = cssVars['--page-bg']
    if (pageBg && isHexColor(pageBg)) {
      const hsl = hexToHslTokens(pageBg)
      if (hsl) {
        applyCssVariables({ '--theme-light-background': hsl })
      }
    }
  }

  watch(
    theme,
    (newTheme) => {
      applyThemeMode(newTheme)
      localStorage.setItem(THEME_MODE_KEY, newTheme)
    },
    { immediate: true }
  )

  watch(
    preset,
    (newPreset) => {
      localStorage.setItem(THEME_PRESET_KEY, newPreset)
    },
    { immediate: true }
  )

  watch(
    cursorMode,
    (newMode) => {
      applyCursorMode(newMode)
      localStorage.setItem(THEME_CURSOR_KEY, newMode)
    },
    { immediate: true }
  )

  const init = () => {
    const savedTheme = localStorage.getItem(THEME_MODE_KEY) as ThemeMode | null
    const savedPreset = localStorage.getItem(THEME_PRESET_KEY)
    const savedCursorMode = localStorage.getItem(THEME_CURSOR_KEY) as ThemeCursorMode | null

    if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
      theme.value = savedTheme
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      theme.value = 'dark'
    } else {
      theme.value = 'light'
    }

    if (savedPreset && THEME_PRESET_MAP[savedPreset]) {
      applyPreset(savedPreset)
    } else {
      applyPreset(DEFAULT_THEME_PRESET)
    }

    if (savedCursorMode && ['system', 'soft', 'crosshair', 'neon'].includes(savedCursorMode)) {
      cursorMode.value = savedCursorMode
    } else {
      cursorMode.value = 'soft'
    }
  }

  return {
    theme,
    preset,
    cursorMode,
    presetOptions,
    init,
    setTheme,
    toggleTheme,
    setPreset,
    setCursorMode,
    applyThemeConfig,
    applyCssVariables,
  }
})
