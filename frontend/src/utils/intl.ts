export const normalizeIntlLocale = (rawLocale: unknown): string => {
  const raw = String(rawLocale || '').trim().toLowerCase()
  if (!raw) return 'zh-CN'
  if (raw.startsWith('zh')) {
    if (raw.includes('tw') || raw.includes('hk') || raw.includes('hant')) return 'zh-TW'
    return 'zh-CN'
  }
  if (raw.startsWith('ja')) return 'ja-JP'
  if (raw.startsWith('ko')) return 'ko-KR'
  if (raw.startsWith('th')) return 'th-TH'
  if (raw.startsWith('vi')) return 'vi-VN'
  if (raw.startsWith('fr')) return 'fr-FR'
  if (raw.startsWith('de')) return 'de-DE'
  if (raw.startsWith('en')) return 'en-US'
  return rawLocale ? String(rawLocale) : 'en-US'
}

const parseDateInput = (value: unknown): Date | null => {
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value
  const raw = String(value || '').trim()
  if (!raw) return null
  const date = new Date(raw)
  return Number.isNaN(date.getTime()) ? null : date
}

export const formatDateByLocale = (
  value: unknown,
  locale: unknown,
  options?: Intl.DateTimeFormatOptions,
): string => {
  const date = parseDateInput(value)
  if (!date) return String(value || '')
  const intlLocale = normalizeIntlLocale(locale)
  const fallbackOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }
  return new Intl.DateTimeFormat(intlLocale, options || fallbackOptions).format(date)
}

export const formatDateTimeByLocale = (value: unknown, locale: unknown): string => {
  return formatDateByLocale(value, locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const formatNumberByLocale = (
  value: number | string,
  locale: unknown,
  options?: Intl.NumberFormatOptions,
): string => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return String(value)
  const intlLocale = normalizeIntlLocale(locale)
  return new Intl.NumberFormat(intlLocale, options).format(numeric)
}

export const formatCurrencyByLocale = (
  value: number | string,
  locale: unknown,
  currency = 'CNY',
): string => {
  return formatNumberByLocale(value, locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  })
}

