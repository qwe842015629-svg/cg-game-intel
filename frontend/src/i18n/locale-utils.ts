import { locales, type LocaleCode } from './locales'

export const DEFAULT_LOCALE: LocaleCode = 'en'
export const SUPPORTED_LOCALE_CODES = Object.keys(locales) as LocaleCode[]

const SUPPORTED_LOCALE_SET = new Set<LocaleCode>(SUPPORTED_LOCALE_CODES)
const GEO_LOCALE_CACHE_KEY = 'geo_locale_cache_v1'
const GEO_LOCALE_CACHE_TTL_MS = 24 * 60 * 60 * 1000

const COUNTRY_LOCALE_MAP: Record<string, LocaleCode> = {
  CN: 'zh-CN',
  SG: 'zh-CN',
  TW: 'zh-TW',
  HK: 'zh-TW',
  MO: 'zh-TW',
  JP: 'ja',
  KR: 'ko',
  TH: 'th',
  VN: 'vi',
  FR: 'fr',
  DE: 'de',
  AT: 'de',
  LI: 'de',
  LU: 'de',
}

type GeoLocaleCache = {
  country: string
  locale: LocaleCode
  ts: number
}

let geoLocalePending: Promise<LocaleCode> | null = null

export const isLocaleCode = (value: unknown): value is LocaleCode => {
  return typeof value === 'string' && SUPPORTED_LOCALE_SET.has(value as LocaleCode)
}

export const normalizeLocaleCode = (raw: unknown): LocaleCode => {
  const value = String(raw ?? '').trim()
  if (isLocaleCode(value)) return value

  const lower = value.toLowerCase()
  if (lower.startsWith('zh')) {
    if (lower.includes('tw') || lower.includes('hk') || lower.includes('hant')) return 'zh-TW'
    return 'zh-CN'
  }
  if (lower.startsWith('ja')) return 'ja'
  if (lower.startsWith('ko')) return 'ko'
  if (lower.startsWith('th')) return 'th'
  if (lower.startsWith('vi')) return 'vi'
  if (lower.startsWith('fr')) return 'fr'
  if (lower.startsWith('de')) return 'de'
  if (lower.startsWith('en')) return 'en'
  return DEFAULT_LOCALE
}

const resolveLocaleByCountry = (rawCountryCode: unknown): LocaleCode => {
  const code = String(rawCountryCode ?? '').trim().toUpperCase()
  if (!code) return DEFAULT_LOCALE
  return COUNTRY_LOCALE_MAP[code] ?? DEFAULT_LOCALE
}

const readGeoLocaleCache = (): LocaleCode | null => {
  if (typeof window === 'undefined') return null

  try {
    const raw = window.localStorage.getItem(GEO_LOCALE_CACHE_KEY)
    if (!raw) return null
    const payload = JSON.parse(raw) as Partial<GeoLocaleCache>
    const locale = payload?.locale
    const ts = Number(payload?.ts ?? 0)

    if (!isLocaleCode(locale)) return null
    if (!Number.isFinite(ts) || ts <= 0) return null
    if (Date.now() - ts > GEO_LOCALE_CACHE_TTL_MS) return null

    return locale
  } catch {
    return null
  }
}

const writeGeoLocaleCache = (country: string, locale: LocaleCode): void => {
  if (typeof window === 'undefined') return
  try {
    const payload: GeoLocaleCache = { country, locale, ts: Date.now() }
    window.localStorage.setItem(GEO_LOCALE_CACHE_KEY, JSON.stringify(payload))
  } catch {
    // Ignore storage failures (private mode / quota exceeded)
  }
}

const fetchCountryCodeByIp = async (): Promise<string | null> => {
  try {
    const response = await window.fetch('https://ipapi.co/country/', {
      method: 'GET',
      cache: 'no-store',
    })
    if (!response.ok) return null
    const rawText = (await response.text()).trim().toUpperCase()
    if (!/^[A-Z]{2}$/.test(rawText)) return null
    return rawText
  } catch {
    return null
  }
}

export const resolveIpLocale = async (): Promise<LocaleCode> => {
  if (typeof window === 'undefined') return DEFAULT_LOCALE

  const cachedLocale = readGeoLocaleCache()
  if (cachedLocale) return cachedLocale

  if (!geoLocalePending) {
    geoLocalePending = (async () => {
      const countryCode = await fetchCountryCodeByIp()
      const locale = resolveLocaleByCountry(countryCode)
      if (countryCode) {
        writeGeoLocaleCache(countryCode, locale)
      }
      return locale
    })().finally(() => {
      geoLocalePending = null
    })
  }

  return geoLocalePending
}

export const resolvePreferredLocale = async (): Promise<LocaleCode> => {
  if (typeof window === 'undefined') return DEFAULT_LOCALE

  const savedLocale = window.localStorage.getItem('locale')
  if (isLocaleCode(savedLocale)) return savedLocale

  return resolveIpLocale()
}

export const resolveInitialLocale = (): LocaleCode => {
  if (typeof window === 'undefined') return DEFAULT_LOCALE
  const savedLocale = window.localStorage.getItem('locale')
  if (isLocaleCode(savedLocale)) return savedLocale
  return normalizeLocaleCode(window.navigator?.language)
}
