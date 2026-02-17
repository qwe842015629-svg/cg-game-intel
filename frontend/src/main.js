import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18nPlugin from './plugins/i18n'
import { i18n } from './i18n/vue-i18n.config'
import { motionRevealDirective } from './directives/motionReveal'
import { magneticHoverDirective } from './directives/magneticHover'
import { tiltSpotlightDirective } from './directives/tiltSpotlight'
import { initMotionMode } from './utils/motionMode'
import './assets/main.css'

initMotionMode()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(i18nPlugin)
app.directive('motion-reveal', motionRevealDirective)
app.directive('magnetic', magneticHoverDirective)
app.directive('tilt', tiltSpotlightDirective)

app.mount('#app')
