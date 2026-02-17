<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 relative overflow-hidden">
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(50%_42%_at_50%_0%,hsl(var(--primary)/0.14),transparent_72%)]"></div>
    <div class="pointer-events-none absolute -top-20 right-[7%] h-60 w-60 rounded-full bg-primary/10 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-20 left-[10%] h-64 w-64 rounded-full bg-secondary/10 blur-3xl"></div>
    <div class="relative max-w-md w-full">
      <!-- 激活中 -->
      <div v-if="activating" class="surface-card p-8 text-center" v-motion-reveal="{ y: 20 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center mb-5 animate-pulse">
          <svg class="w-8 h-8 text-primary animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-foreground mb-3">正在激活您的账号...</h2>
        <p class="text-muted-foreground">请稍候，这只需要几秒钟</p>
      </div>

      <!-- 激活成功 -->
      <div v-else-if="activationSuccess" class="surface-card p-8 text-center" v-motion-reveal="{ y: 20 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-emerald-500/15 flex items-center justify-center mb-5">
          <svg class="w-8 h-8 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold text-foreground mb-3">激活成功！</h2>

        <p class="text-muted-foreground mb-5">您的账号已成功激活，现在可以登录使用了</p>

        <div class="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 mb-5">
          <p class="text-emerald-700 dark:text-emerald-300 text-sm">
            账号激活完成，您可以使用所有功能。
          </p>
        </div>

        <div v-if="countdown > 0" class="mb-5">
          <p class="text-muted-foreground text-sm">
            {{ countdown }} 秒后自动跳转到登录页...
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <router-link
            to="/login"
            v-magnetic="{ strength: 0.16, max: 9 }"
            class="px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors text-center"
          >
            立即登录
          </router-link>
          <router-link
            to="/"
            class="px-4 py-2.5 rounded-lg bg-secondary text-secondary-foreground font-semibold hover:opacity-90 transition-colors text-center"
          >
            返回首页
          </router-link>
        </div>
      </div>

      <!-- 激活失败 -->
      <div v-else class="surface-card p-8 text-center" v-motion-reveal="{ y: 20 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-destructive/15 flex items-center justify-center mb-5">
          <svg class="w-8 h-8 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold text-destructive mb-3">激活失败</h2>

        <p class="text-muted-foreground mb-5">
          {{ errorMessage || '激活链接无效或已过期' }}
        </p>

        <div class="bg-destructive/10 border border-destructive/25 rounded-lg p-4 mb-5 text-left">
          <p class="text-sm text-muted-foreground">
            可能的原因：
            <br />• 激活链接已过期（24小时有效期）
            <br />• 激活链接已被使用
            <br />• 链接格式不正确
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <router-link
            to="/register"
            v-magnetic="{ strength: 0.16, max: 9 }"
            class="px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors text-center"
          >
            重新注册
          </router-link>
          <router-link
            to="/"
            class="px-4 py-2.5 rounded-lg bg-secondary text-secondary-foreground font-semibold hover:opacity-90 transition-colors text-center"
          >
            返回首页
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const router = useRouter()

const activating = ref(true)
const activationSuccess = ref(false)
const errorMessage = ref('')
const countdown = ref(5)

let countdownTimer: number | null = null

const activateAccount = async () => {
  const { uid, token } = route.params

  if (!uid || !token) {
    activating.value = false
    errorMessage.value = '激活链接格式不正确'
    return
  }

  try {
    await client.post('/auth/users/activation/', {
      uid: uid,
      token: token
    })

    activationSuccess.value = true
    activating.value = false

    // 开始倒计时
    startCountdown()
  } catch (error: any) {
    activating.value = false

    if (error.response?.data) {
      const errors = error.response.data
      if (errors.detail) {
        errorMessage.value = errors.detail
      } else if (errors.uid) {
        errorMessage.value = '用户ID无效'
      } else if (errors.token) {
        errorMessage.value = '激活令牌无效或已过期'
      } else {
        errorMessage.value = '激活失败，请重试'
      }
    } else {
      errorMessage.value = '网络错误，请检查您的网络连接'
    }
  }
}

const startCountdown = () => {
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
      router.push('/login')
    }
  }, 1000)
}

onMounted(() => {
  activateAccount()
})
</script>

<style scoped></style>
