import {
  createRouter,
  createWebHistory,
  type RouteLocationNormalized,
  type RouteRecordRaw,
} from 'vue-router'
import Layout from '../components/Layout.vue'
import { ensureLocaleMessages, i18n } from '../i18n/vue-i18n.config'
import type { LocaleCode } from '../i18n/locales'
import {
  DEFAULT_LOCALE,
  normalizeLocaleCode,
  resolveInitialLocale,
  resolvePreferredLocale,
} from '../i18n/locale-utils'
import { LOCALE_ROUTE_PATTERN, withLocalePrefix } from '../i18n/locale-routing'
import { syncLocaleSeoTags } from '../i18n/seo'

type ChildRouteConfig = {
  path: string
  name?: string
  component: RouteRecordRaw['component']
}

const HomePage = () => import('../views/HomePage.vue')
const GamesPage = () => import('../views/GamesPage.vue')
const GameDetailPage = () => import('../views/GameDetailPage.vue')
const ArticlesPage = () => import('../views/ArticlesPage.vue')
const ArticleDetailPage = () => import('../views/ArticleDetailPage.vue')
const ProfilePage = () => import('../views/ProfilePage.vue')
const CustomerServicePage = () => import('../views/CustomerServicePage.vue')
const AboutPage = () => import('../views/AboutPage.vue')
const ContactPage = () => import('../views/ContactPage.vue')
const RechargePage = () => import('../views/RechargePage.vue')
const RechargeApiPage = () => import('../views/RechargeApiPage.vue')
const RechargeApiProductPage = () => import('../views/RechargeApiProductPage.vue')
const RechargeGuidePage = () => import('../views/RechargeGuidePage.vue')
const SearchResultsPage = () => import('../views/SearchResultsPage.vue')
const TranslationDemo = () => import('../views/TranslationDemo.vue')
const CorsTestPage = () => import('../views/CorsTestPage.vue')
const RegisterPage = () => import('../views/RegisterPage.vue')
const LoginPage = () => import('../views/LoginPage.vue')
const ForgotPasswordPage = () => import('../views/ForgotPasswordPage.vue')
const ResetPasswordPage = () => import('../views/ResetPasswordPage.vue')
const ActivateAccountPage = () => import('../views/ActivateAccountPage.vue')
const CGGameWiki = () => import('../views/CGGameWiki.vue')
const CypherTavern = () => import('../views/CypherTavern.vue')
const NovelStoryPage = () => import('../views/NovelStoryPage.vue')
const PlazaPage = () => import('../views/PlazaPage.vue')
const ShortDramaExpertPage = () => import('../views/ShortDramaExpertPage.vue')
const UserProfilePage = () => import('../views/UserProfile.vue')
const I18nQuickDemoPage = () => import('../views/I18nQuickDemoPage.vue')
const NotFoundPage = () => import('../views/NotFoundPage.vue')

const childRouteConfigs: ChildRouteConfig[] = [
  { path: '', name: 'home', component: HomePage },
  { path: 'games', name: 'games', component: GamesPage },
  { path: 'games/:id', name: 'game-detail', component: GameDetailPage },
  { path: 'articles', name: 'articles', component: ArticlesPage },
  { path: 'articles/:id', name: 'article-detail', component: ArticleDetailPage },
  { path: 'profile', name: 'profile', component: ProfilePage },
  { path: 'customer-service', name: 'customer-service', component: CustomerServicePage },
  { path: 'about', name: 'about', component: AboutPage },
  { path: 'contact', name: 'contact', component: ContactPage },
  { path: 'recharge', name: 'recharge', component: RechargePage },
  { path: 'recharge-api', name: 'recharge-api', component: RechargeApiPage },
  {
    path: 'recharge-api/product/:providerUuid/:productId',
    name: 'recharge-api-product',
    component: RechargeApiProductPage,
  },
  { path: 'recharge-guide', name: 'recharge-guide', component: RechargeGuidePage },
  { path: 'search', name: 'search', component: SearchResultsPage },
  { path: 'translation-demo', name: 'translation-demo', component: TranslationDemo },
  { path: 'i18n-demo', name: 'i18n-demo', component: I18nQuickDemoPage },
  { path: 'cors-test', name: 'cors-test', component: CorsTestPage },
  { path: 'register', name: 'register', component: RegisterPage },
  { path: 'login', name: 'login', component: LoginPage },
  { path: 'forgot-password', name: 'forgot-password', component: ForgotPasswordPage },
  { path: 'password-reset/:uid/:token', name: 'password-reset', component: ResetPasswordPage },
  { path: 'activate/:uid/:token', name: 'activate-account', component: ActivateAccountPage },
  { path: 'cg-wiki', name: 'cg-wiki', component: CGGameWiki },
  { path: 'tavern', name: 'tavern', component: CypherTavern },
  { path: 'novel-story', name: 'novel-story', component: NovelStoryPage },
  { path: 'plaza', name: 'plaza', component: PlazaPage },
  { path: 'user/:id', name: 'user-profile', component: UserProfilePage },
  { path: '404', name: 'not-found', component: NotFoundPage },
]

if (import.meta.env.DEV) {
  childRouteConfigs.splice(Math.max(childRouteConfigs.length - 1, 0), 0, {
    path: 'short-drama-expert',
    name: 'short-drama-expert',
    component: ShortDramaExpertPage,
  })
}

const buildChildren = (includeNames: boolean): RouteRecordRaw[] => {
  return childRouteConfigs.map((routeConfig) => {
    const baseRoute: RouteRecordRaw = {
      path: routeConfig.path,
      component: routeConfig.component,
    }

    if (includeNames && routeConfig.name) {
      baseRoute.name = routeConfig.name
    }

    return baseRoute
  })
}

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: `/:locale(${LOCALE_ROUTE_PATTERN})`,
      component: Layout,
      children: buildChildren(false),
    },
    {
      path: '/',
      component: Layout,
      children: buildChildren(true),
    },
    {
      path: `/:locale(${LOCALE_ROUTE_PATTERN})/:pathMatch(.*)*`,
      redirect: (to) => {
        const rawLocale = Array.isArray(to.params.locale) ? to.params.locale[0] : to.params.locale
        return withLocalePrefix('/404', normalizeLocaleCode(rawLocale))
      },
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: () => withLocalePrefix('/404', resolveInitialLocale()),
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return {
        ...savedPosition,
        behavior: 'smooth',
      }
    }

    return {
      top: 0,
      behavior: 'smooth',
    }
  },
})

const readRouteLocale = (to: RouteLocationNormalized): string | null => {
  const rawLocale = to.params.locale
  if (Array.isArray(rawLocale)) return rawLocale[0] ?? null
  return typeof rawLocale === 'string' ? rawLocale : null
}

const applyLocale = async (locale: LocaleCode): Promise<void> => {
  await ensureLocaleMessages(locale)
  i18n.global.locale.value = locale

  if (typeof window !== 'undefined') {
    window.localStorage.setItem('locale', locale)
  }
}

router.beforeEach(async (to) => {
  if (to.matched.length === 0) {
    return true
  }

  const routeLocale = readRouteLocale(to)
  const preferredLocale =
    typeof window === 'undefined' ? DEFAULT_LOCALE : await resolvePreferredLocale()
  const targetLocale = normalizeLocaleCode(routeLocale ?? preferredLocale)
  const canonicalPath = withLocalePrefix(to.path, targetLocale)

  if (!routeLocale || to.path !== canonicalPath) {
    await applyLocale(targetLocale)
    return {
      path: canonicalPath,
      query: to.query,
      hash: to.hash,
      replace: true,
    }
  }

  await applyLocale(targetLocale)
  return true
})

router.afterEach((to) => {
  const routeLocale = readRouteLocale(to)
  const activeLocale = normalizeLocaleCode(routeLocale ?? i18n.global.locale.value ?? DEFAULT_LOCALE)
  syncLocaleSeoTags(to, activeLocale)

  if (typeof window !== 'undefined' && typeof (window as any).gtag === 'function') {
    ;(window as any).gtag('event', 'page_view', {
      send_to: 'G-C6198LC1GN',
      page_title: document.title,
      page_location: window.location.href,
      page_path: to.fullPath,
    })
  }
})

export default router
