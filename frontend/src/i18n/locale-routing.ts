import type { LocaleCode } from './locales'
import { normalizeLocaleCode, SUPPORTED_LOCALE_CODES } from './locale-utils'

const escapeRegExp = (value: string): string => {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const localeVariants = Array.from(
  new Set([
    ...SUPPORTED_LOCALE_CODES,
    ...SUPPORTED_LOCALE_CODES.map((code) => code.toLowerCase()),
  ])
)

export const LOCALE_ROUTE_PATTERN = localeVariants.map(escapeRegExp).join('|')

const LOCALE_PREFIX_REGEX = new RegExp(`^/(${LOCALE_ROUTE_PATTERN})(?=/|$)`)

const splitPath = (rawPath: string): { pathname: string; query: string; hash: string } => {
  const pathWithSlash = rawPath.startsWith('/') ? rawPath : `/${rawPath}`
  const [pathAndQuery, hash = ''] = pathWithSlash.split('#', 2)
  const [pathname = '/', query = ''] = pathAndQuery.split('?', 2)
  return {
    pathname: pathname || '/',
    query: query ? `?${query}` : '',
    hash: hash ? `#${hash}` : '',
  }
}

export const stripLocalePrefix = (rawPath: string): string => {
  const pathWithSlash = rawPath.startsWith('/') ? rawPath : `/${rawPath}`
  const stripped = pathWithSlash.replace(LOCALE_PREFIX_REGEX, '')
  return stripped || '/'
}

export const extractLocaleFromPath = (rawPath: string): LocaleCode | null => {
  const pathWithSlash = rawPath.startsWith('/') ? rawPath : `/${rawPath}`
  const match = pathWithSlash.match(LOCALE_PREFIX_REGEX)
  if (!match) return null
  return normalizeLocaleCode(match[1])
}

export const withLocalePrefix = (rawPath: string, locale: LocaleCode): string => {
  const { pathname, query, hash } = splitPath(rawPath)
  const basePath = stripLocalePrefix(pathname)
  const localizedPath = basePath === '/' ? `/${locale}` : `/${locale}${basePath}`
  return `${localizedPath}${query}${hash}`
}
