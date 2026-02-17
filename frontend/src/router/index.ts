import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import HomePage from '../views/HomePage.vue'
import GamesPage from '../views/GamesPage.vue'
import GameDetailPage from '../views/GameDetailPage.vue'
import ArticlesPage from '../views/ArticlesPage.vue'
import ArticleDetailPage from '../views/ArticleDetailPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import CustomerServicePage from '../views/CustomerServicePage.vue'
import AboutPage from '../views/AboutPage.vue'
import ContactPage from '../views/ContactPage.vue'
import RechargePage from '../views/RechargePage.vue'
import SearchResultsPage from '../views/SearchResultsPage.vue'
import TranslationDemo from '../views/TranslationDemo.vue'
import CorsTestPage from '../views/CorsTestPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import LoginPage from '../views/LoginPage.vue'
import ActivateAccountPage from '../views/ActivateAccountPage.vue'
import CGGameWiki from '../views/CGGameWiki.vue'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'home',
          component: HomePage,
        },
        {
          path: 'games',
          name: 'games',
          component: GamesPage,
        },
        {
          path: 'games/:id',
          name: 'game-detail',
          component: GameDetailPage,
        },
        {
          path: 'articles',
          name: 'articles',
          component: ArticlesPage,
        },
        {
          path: 'articles/:id',
          name: 'article-detail',
          component: ArticleDetailPage,
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfilePage,
        },
        {
          path: 'customer-service',
          name: 'customer-service',
          component: CustomerServicePage,
        },
        {
          path: 'about',
          name: 'about',
          component: AboutPage,
        },
        {
          path: 'contact',
          name: 'contact',
          component: ContactPage,
        },
        {
          path: 'recharge',
          name: 'recharge',
          component: RechargePage,
        },
        {
          path: 'search',
          name: 'search',
          component: SearchResultsPage,
        },
        {
          path: 'translation-demo',
          name: 'translation-demo',
          component: TranslationDemo,
        },
        {
          path: 'cors-test',
          name: 'cors-test',
          component: CorsTestPage,
        },
        {
          path: 'register',
          name: 'register',
          component: RegisterPage,
        },
        {
          path: 'login',
          name: 'login',
          component: LoginPage,
        },
        {
          path: 'activate/:uid/:token',
          name: 'activate-account',
          component: ActivateAccountPage,
        },
        {
          path: 'cg-wiki',
          name: 'cg-wiki',
          component: CGGameWiki,
        },
      ],
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return {
        ...savedPosition,
        behavior: 'smooth',
      }
    } else {
      return {
        top: 0,
        behavior: 'smooth',
      }
    }
  },
})

export default router
