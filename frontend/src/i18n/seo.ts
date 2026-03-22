import type { RouteLocationNormalizedLoaded } from 'vue-router'
import type { LocaleCode } from './locales'
import { DEFAULT_LOCALE, SUPPORTED_LOCALE_CODES } from './locale-utils'
import { stripLocalePrefix, withLocalePrefix } from './locale-routing'
import { i18n } from './vue-i18n.config'

const MANAGED_LINK_ATTR = 'data-i18n-seo-link'
const MANAGED_META_ATTR = 'data-i18n-seo-meta'
const HOME_TITLE_OVERRIDE: Partial<Record<LocaleCode, string>> = {
  'zh-CN': 'Cypher Game Buy|你的全球手游买手',
}

const hreflangMap: Partial<Record<LocaleCode, string>> = {
  'zh-CN': 'zh-Hans',
  'zh-TW': 'zh-Hant',
}

const toHreflang = (locale: LocaleCode): string => {
  return hreflangMap[locale] ?? locale.toLowerCase()
}

const normalizeSeoPath = (rawPath: string): string => {
  const withoutHash = rawPath.split('#', 1)[0] || '/'
  const withoutQuery = withoutHash.split('?', 1)[0] || '/'
  return withoutQuery.startsWith('/') ? withoutQuery : `/${withoutQuery}`
}

const buildAbsoluteUrl = (path: string): string => {
  return new URL(path, window.location.origin).toString()
}

const appendManagedLink = (attrs: Record<string, string>): void => {
  const link = document.createElement('link')
  Object.entries(attrs).forEach(([key, value]) => link.setAttribute(key, value))
  link.setAttribute(MANAGED_LINK_ATTR, 'true')
  document.head.appendChild(link)
}

const upsertManagedMeta = (name: string, content: string): void => {
  const selector = `meta[name="${name}"][${MANAGED_META_ATTR}="true"]`
  const existing = document.head.querySelector(selector) as HTMLMetaElement | null
  const meta = existing ?? document.createElement('meta')

  meta.setAttribute('name', name)
  meta.setAttribute('content', content)
  meta.setAttribute(MANAGED_META_ATTR, 'true')

  if (!existing) {
    document.head.appendChild(meta)
  }
}

const resolveRouteTitleKey = (normalizedPath: string): string => {
  if (normalizedPath === '/') return 'seo.routeTitles.home'
  if (normalizedPath === '/games') return 'seo.routeTitles.games'
  if (normalizedPath.startsWith('/games/')) return 'seo.routeTitles.gameDetail'
  if (normalizedPath === '/articles') return 'seo.routeTitles.articles'
  if (normalizedPath.startsWith('/articles/')) return 'seo.routeTitles.articleDetail'
  if (normalizedPath === '/profile') return 'seo.routeTitles.profile'
  if (normalizedPath === '/customer-service') return 'seo.routeTitles.customerService'
  if (normalizedPath === '/about') return 'seo.routeTitles.about'
  if (normalizedPath === '/contact') return 'seo.routeTitles.contact'
  if (normalizedPath === '/recharge') return 'seo.routeTitles.recharge'
  if (normalizedPath === '/recharge-guide') return 'seo.routeTitles.rechargeGuide'
  if (normalizedPath === '/search') return 'seo.routeTitles.search'
  if (normalizedPath === '/translation-demo') return 'seo.routeTitles.translationDemo'
  if (normalizedPath === '/i18n-demo') return 'seo.routeTitles.i18nDemo'
  if (normalizedPath === '/register') return 'seo.routeTitles.register'
  if (normalizedPath === '/login') return 'seo.routeTitles.login'
  if (normalizedPath.startsWith('/activate/')) return 'seo.routeTitles.activate'
  if (normalizedPath === '/404') return 'seo.routeTitles.notFound'
  if (normalizedPath === '/cg-wiki') return 'seo.routeTitles.cgWiki'
  if (normalizedPath === '/tavern') return 'seo.routeTitles.tavern'
  if (normalizedPath === '/novel-story') return 'seo.routeTitles.novelStory'
  if (normalizedPath === '/plaza') return 'seo.routeTitles.plaza'
  return 'seo.routeTitles.default'
}

const safeTranslate = (key: string, fallback = ''): string => {
  const translated = i18n.global.t(key)
  if (typeof translated === 'string' && translated.trim().length > 0 && translated !== key) {
    return translated
  }
  return fallback
}

const syncDocumentMeta = (normalizedPath: string, locale: LocaleCode): void => {
  const overrideTitle = normalizedPath === '/' ? HOME_TITLE_OVERRIDE[locale] : ''
  const siteName = safeTranslate('siteName', 'CYPHER GAME BUY')
  const pageTitle = safeTranslate(resolveRouteTitleKey(normalizedPath), siteName)
  document.title = overrideTitle || (pageTitle === siteName ? siteName : `${pageTitle} | ${siteName}`)

  const description = safeTranslate('seo.defaultDescription')
  const keywords = safeTranslate('seo.defaultKeywords')

  if (description) upsertManagedMeta('description', description)
  if (keywords) upsertManagedMeta('keywords', keywords)
}

export const syncLocaleSeoTags = (
  route: RouteLocationNormalizedLoaded,
  activeLocale: LocaleCode
): void => {
  if (typeof window === 'undefined') return

  const managedLinks = document.head.querySelectorAll(`link[${MANAGED_LINK_ATTR}="true"]`)
  managedLinks.forEach((node) => node.remove())

  const normalizedPath = normalizeSeoPath(stripLocalePrefix(route.path || '/'))
  const canonicalPath = withLocalePrefix(normalizedPath, activeLocale)

  document.documentElement.setAttribute('lang', activeLocale)
  syncDocumentMeta(normalizedPath, activeLocale)

  SUPPORTED_LOCALE_CODES.forEach((locale) => {
    const localizedPath = withLocalePrefix(normalizedPath, locale)
    appendManagedLink({
      rel: 'alternate',
      hreflang: toHreflang(locale),
      href: buildAbsoluteUrl(localizedPath),
    })
  })

  appendManagedLink({
    rel: 'alternate',
    hreflang: 'x-default',
    href: buildAbsoluteUrl(withLocalePrefix(normalizedPath, DEFAULT_LOCALE)),
  })

  appendManagedLink({
    rel: 'canonical',
    href: buildAbsoluteUrl(canonicalPath),
  })
}
