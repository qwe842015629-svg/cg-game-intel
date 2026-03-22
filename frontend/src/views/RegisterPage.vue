<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 relative overflow-hidden">
    <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(54%_44%_at_50%_0%,hsl(var(--primary)/0.13),transparent_70%)]"></div>
    <div class="pointer-events-none absolute -top-28 left-[8%] h-72 w-72 rounded-full bg-primary/10 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-24 right-[8%] h-72 w-72 rounded-full bg-secondary/10 blur-3xl"></div>
    <div class="relative max-w-md w-full">
      <!-- 注册表单 -->
      <div v-if="!registrationSuccess" class="surface-card p-8 md:p-9" v-motion-reveal="{ y: 24 }" v-tilt="{ max: 2.8, scale: 1.004 }">
        <div class="text-center mb-8">
          <h1 class="text-3xl md:text-4xl font-black text-foreground mb-2">CYPHER GAME BUY</h1>
          <p class="text-muted-foreground text-sm">创建您的游戏充值账号</p>
        </div>

        <div v-if="errorMessage" class="mb-6 p-3 rounded-lg border border-destructive/40 bg-destructive/10">
          <p class="text-destructive text-sm">{{ errorMessage }}</p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-5">
          <div>
            <label class="block text-sm font-semibold mb-2 text-foreground">用户名</label>
            <input
              v-model="form.username"
              type="text"
              required
              placeholder="请输入用户名"
              class="w-full px-4 py-3 rounded-lg bg-card border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2 text-foreground">邮箱地址</label>
            <input
              v-model="form.email"
              type="email"
              required
              placeholder="请输入邮箱地址"
              class="w-full px-4 py-3 rounded-lg bg-card border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2 text-foreground">密码</label>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="请输入密码（至少8位）"
              class="w-full px-4 py-3 rounded-lg bg-card border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold mb-2 text-foreground">确认密码</label>
            <input
              v-model="form.re_password"
              type="password"
              required
              placeholder="请再次输入密码"
              class="w-full px-4 py-3 rounded-lg bg-card border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            v-magnetic="{ strength: 0.16, max: 9 }"
            class="w-full py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">注册中...</span>
            <span v-else>立即注册</span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-muted-foreground text-sm">
            已有账号？
            <router-link to="/login" class="text-primary hover:underline font-semibold">
              立即登录
            </router-link>
          </p>
        </div>
      </div>

      <!-- 注册成功 - 待激活提示 -->
      <div v-else class="surface-card p-7 text-center" v-motion-reveal="{ y: 24 }">
        <div class="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center mb-5">
          <Check class="w-8 h-8 text-primary" />
        </div>

        <h2 class="text-2xl font-bold text-foreground mb-3">注册成功！</h2>

        <div class="mb-6 space-y-2">
          <p class="text-muted-foreground">激活邮件已发送至</p>
          <p class="text-lg font-semibold text-primary break-all">{{ form.email }}</p>
        </div>

        <div class="bg-muted/50 border border-border rounded-lg p-5 mb-5 text-left">
          <h3 class="font-semibold text-foreground mb-3">接下来该怎么做？</h3>
          <ol class="space-y-2 text-sm text-muted-foreground">
            <li>1. 打开您的邮箱 {{ form.email }}</li>
            <li>2. 找到来自 CYPHER GAME BUY 的激活邮件</li>
            <li>3. 点击邮件中的激活按钮</li>
            <li>4. 激活成功后，即可登录使用</li>
          </ol>
        </div>

        <div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 mb-5 text-left">
          <p class="text-amber-700 dark:text-amber-300 text-sm">
            没收到邮件？请检查垃圾邮件文件夹，或等待几分钟后重试。
          </p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <button
            @click="openEmail"
            v-magnetic="{ strength: 0.16, max: 9 }"
            class="px-4 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
          >
            打开邮箱
          </button>
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
import { ref } from 'vue'
import { Check } from 'lucide-vue-next'
import client from '../api/client'

const form = ref({
  username: '',
  email: '',
  password: '',
  re_password: ''
})

const loading = ref(false)
const errorMessage = ref('')
const registrationSuccess = ref(false)

const handleRegister = async () => {
  errorMessage.value = ''

  // 验证密码匹配
  if (form.value.password !== form.value.re_password) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  // 验证密码长度
  if (form.value.password.length < 8) {
    errorMessage.value = '密码长度至少为8位'
    return
  }

  loading.value = true

  try {
    await client.post('/auth/users/', form.value)
    registrationSuccess.value = true
  } catch (error: any) {
    if (error.response?.data) {
      const errors = error.response.data
      if (errors.username) {
        errorMessage.value = '用户名：' + errors.username.join(', ')
      } else if (errors.email) {
        errorMessage.value = '邮箱：' + errors.email.join(', ')
      } else if (errors.password) {
        errorMessage.value = '密码：' + errors.password.join(', ')
      } else if (errors.non_field_errors) {
        errorMessage.value = errors.non_field_errors.join(', ')
      } else if (errors.detail) {
        errorMessage.value = typeof errors.detail === 'string' ? errors.detail : JSON.stringify(errors.detail)
      } else {
        errorMessage.value = typeof errors === 'string' ? errors : JSON.stringify(errors)
      }
    } else {
      errorMessage.value = '网络错误，请检查您的网络连接'
    }
  } finally {
    loading.value = false
  }
}

const openEmail = () => {
  // 尝试打开邮箱
  const email = form.value.email
  const domain = email.split('@')[1]

  const emailUrls: Record<string, string> = {
    'qq.com': 'https://mail.qq.com',
    '163.com': 'https://mail.163.com',
    '126.com': 'https://mail.126.com',
    'gmail.com': 'https://mail.google.com',
    'outlook.com': 'https://outlook.live.com',
    'hotmail.com': 'https://outlook.live.com',
  }

  const url = emailUrls[domain] || 'https://mail.' + domain
  window.open(url, '_blank')
}
</script>

<style scoped></style>
