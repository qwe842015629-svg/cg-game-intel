<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 relative overflow-hidden">
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(50%_42%_at_50%_0%,hsl(var(--primary)/0.14),transparent_72%)]"></div>
    <div class="pointer-events-none absolute -top-20 right-[7%] h-60 w-60 rounded-full bg-primary/10 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-20 left-[10%] h-64 w-64 rounded-full bg-secondary/10 blur-3xl"></div>
    <div class="relative max-w-md w-full">
      <div v-if="activating" class="surface-card p-8 text-center" v-motion-reveal="{ y: 20 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center mb-5 animate-pulse">
          <RefreshCw class="w-8 h-8 text-primary animate-spin" />
        </div>
        <h2 class="text-2xl font-bold text-foreground mb-3">{{ t('activateAccountPage.activatingTitle') }}</h2>
        <p class="text-muted-foreground">{{ t('activateAccountPage.activatingDescription') }}</p>
      </div>

      <div v-else-if="activationSuccess" class="surface-card p-8 text-center" v-motion-reveal="{ y: 20 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-emerald-500/15 flex items-center justify-center mb-5">
          <Check class="w-8 h-8 text-emerald-500" />
        </div>

        <h2 class="text-2xl font-bold text-foreground mb-3">{{ t('activateAccountPage.successTitle') }}</h2>

        <p class="text-muted-foreground mb-5">{{ t('activateAccountPage.successDescription') }}</p>

        <div class="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 mb-5">
          <p class="text-emerald-700 dark:text-emerald-300 text-sm">
            {{ t('activateAccountPage.successNotice') }}
          </p>
        </div>

        <div v-if="countdown > 0" class="mb-5">
          <p class="text-muted-foreground text-sm">
            {{ t('activateAccountPage.countdownRedirect', { count: countdown }) }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <router-link
            :to="localizedPath('/login')"
            v-magnetic="{ strength: 0.16, max: 9 }"
            class="px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors text-center"
          >
            {{ t('activateAccountPage.loginNow') }}
          </router-link>
          <router-link
            :to="localizedPath('/')"
            class="px-4 py-2.5 rounded-lg bg-secondary text-secondary-foreground font-semibold hover:opacity-90 transition-colors text-center"
          >
            {{ t('activateAccountPage.backHome') }}
          </router-link>
        </div>
      </div>

      <div v-else class="surface-card p-8 text-center" v-motion-reveal="{ y: 20 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-destructive/15 flex items-center justify-center mb-5">
          <X class="w-8 h-8 text-destructive" />
        </div>

        <h2 class="text-2xl font-bold text-destructive mb-3">{{ t('activateAccountPage.failedTitle') }}</h2>

        <p class="text-muted-foreground mb-5">
          {{ errorMessage || t('activateAccountPage.invalidOrExpired') }}
        </p>

        <div class="bg-destructive/10 border border-destructive/25 rounded-lg p-4 mb-5 text-left">
          <p class="text-sm text-muted-foreground">
            {{ t('activateAccountPage.reasonsTitle') }}
            <br />• {{ t('activateAccountPage.reasonExpired') }}
            <br />• {{ t('activateAccountPage.reasonUsed') }}
            <br />• {{ t('activateAccountPage.reasonFormat') }}
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <router-link
            :to="localizedPath('/register')"
            v-magnetic="{ strength: 0.16, max: 9 }"
            class="px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors text-center"
          >
            {{ t('activateAccountPage.registerAgain') }}
          </router-link>
          <router-link
            :to="localizedPath('/')"
            class="px-4 py-2.5 rounded-lg bg-secondary text-secondary-foreground font-semibold hover:opacity-90 transition-colors text-center"
          >
            {{ t('activateAccountPage.backHome') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Check, RefreshCw, X } from 'lucide-vue-next'
import client from '../api/client'
import { withLocalePrefix } from '../i18n/locale-routing'
import { normalizeLocaleCode } from '../i18n/locale-utils'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const activating = ref(true)
const activationSuccess = ref(false)
const errorMessage = ref('')
const countdown = ref(5)

let countdownTimer: number | null = null

const localizedPath = (path: string): string => withLocalePrefix(path, normalizeLocaleCode(locale.value))

const activateAccount = async () => {
  const { uid, token } = route.params

  if (!uid || !token) {
    activating.value = false
    errorMessage.value = t('activateAccountPage.errors.invalidLinkFormat')
    return
  }

  try {
    await client.post('/auth/users/activation/', {
      uid,
      token,
    })

    activationSuccess.value = true
    activating.value = false
    startCountdown()
  } catch (error: any) {
    activating.value = false

    if (error.response?.data) {
      const errors = error.response.data
      if (errors.detail) {
        errorMessage.value = errors.detail
      } else if (errors.uid) {
        errorMessage.value = t('activateAccountPage.errors.invalidUid')
      } else if (errors.token) {
        errorMessage.value = t('activateAccountPage.errors.invalidToken')
      } else {
        errorMessage.value = t('activateAccountPage.errors.activateFailedRetry')
      }
    } else {
      errorMessage.value = t('activateAccountPage.errors.networkError')
    }
  }
}

const startCountdown = () => {
  countdownTimer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
      router.push(localizedPath('/login'))
    }
  }, 1000)
}

onMounted(() => {
  activateAccount()
})

onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped></style>