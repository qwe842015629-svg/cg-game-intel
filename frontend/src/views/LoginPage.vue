﻿<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center py-12 px-4">
    <!-- 背景网格 -->
    <div class="fixed inset-0 opacity-20 pointer-events-none">
      <div class="absolute inset-0" style="background-image: linear-gradient(rgba(0,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px); background-size: 50px 50px;"></div>
    </div>

    <div class="relative max-w-md w-full">
      <div class="bg-slate-900/80 backdrop-blur-sm border-2 border-cyan-500/50 rounded-2xl shadow-[0_0_40px_rgba(0,255,255,0.3)] p-8">
        <!-- Logo -->
        <div class="text-center mb-8">
          <h1 
            class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 mb-2"
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'site_name')"
          >
            {{ getPageConfig('site_name', 'CYPHER GAME BUY') }}
          </h1>
          <p 
            class="text-cyan-200 text-sm"
            :contenteditable="isEditMode"
            @blur="handleInlineEdit($event, 'login_tip')"
          >{{ getPageConfig('login_tip', '登录您的游戏充值账号') }}</p>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="mb-6 p-4 bg-red-500/20 border-2 border-red-400 rounded-lg">
          <p class="text-red-300 text-sm">{{ errorMessage }}</p>
          <button
            v-if="canResendActivation"
            type="button"
            class="mt-3 text-sm text-cyan-300 hover:text-cyan-200 underline disabled:opacity-60"
            :disabled="resendLoading"
            @click="handleResendActivation"
          >
            <span v-if="resendLoading">正在重发激活邮件...</span>
            <span v-else>重新发送激活邮件</span>
          </button>
        </div>

        <div v-if="infoMessage" class="mb-6 p-4 bg-cyan-500/15 border-2 border-cyan-400 rounded-lg">
          <p class="text-cyan-100 text-sm">{{ infoMessage }}</p>
        </div>

        <!-- 登录表单 -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- 邮箱/用户名 -->
          <div>
            <label class="block text-cyan-300 text-sm font-bold mb-2">
              邮箱地址
            </label>
            <input
              v-model="form.email"
              type="email"
              required
              placeholder="请输入邮箱地址"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_15px_rgba(0,255,255,0.3)] transition-all"
            />
          </div>

          <!-- 密码 -->
          <div>
            <label class="block text-cyan-300 text-sm font-bold mb-2">
              密码
            </label>
            <input
              v-model="form.password"
              type="password"
              required
              placeholder="请输入密码"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_15px_rgba(0,255,255,0.3)] transition-all"
            />
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-4 bg-gradient-to-r from-cyan-500 via-purple-600 to-pink-500 text-white font-bold text-lg rounded-lg hover:shadow-[0_0_30px_rgba(0,255,255,0.6)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">登录中...</span>
            <span v-else>⚡ 立即登录</span>
          </button>
        </form>

        <!-- 其他链接 -->
        <div class="mt-6 space-y-3 text-center">
          <p class="text-gray-400">
            还没有账号？
            <router-link to="/register" class="text-cyan-400 hover:text-cyan-300 font-bold">
              立即注册
            </router-link>
          </p>
          <p class="text-gray-400 text-sm">
            <router-link to="/forgot-password" class="text-purple-400 hover:text-purple-300">
              忘记密码？
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'
import { useVisualEditor } from '../composables/useVisualEditor'

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('login_page', '登录页')

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')
const infoMessage = ref('')
const canResendActivation = ref(false)
const resendLoading = ref(false)

const extractNonFieldErrors = (errors: any): string[] => {
  if (!errors) return []
  if (Array.isArray(errors.non_field_errors)) {
    return errors.non_field_errors.map((item: unknown) => String(item || '').trim()).filter(Boolean)
  }
  return []
}

const detectInactiveError = (errors: any): boolean => {
  const nonFieldErrors = extractNonFieldErrors(errors)
  const rawCode = errors?.code
  const codeValues = Array.isArray(rawCode) ? rawCode : [rawCode]
  const hasInactiveCode = codeValues
    .map((item) => String(item || '').trim().toLowerCase())
    .some((item) => item === 'inactive_account')
  if (hasInactiveCode) return true
  return nonFieldErrors.some((message) => /未激活|inactive/i.test(message))
}

const handleResendActivation = async () => {
  const email = String(form.value.email || '').trim()
  if (!email) {
    errorMessage.value = '请先输入注册邮箱'
    return
  }

  resendLoading.value = true
  infoMessage.value = ''
  try {
    await client.post('/auth/users/resend_activation/', { email })
    infoMessage.value = '激活邮件已重新发送，请检查邮箱和垃圾邮件文件夹。'
    canResendActivation.value = false
  } catch (error: any) {
    const detail = error?.response?.data?.detail
    errorMessage.value = detail ? String(detail) : '重发激活邮件失败，请稍后重试'
  } finally {
    resendLoading.value = false
  }
}

const handleLogin = async () => {
  errorMessage.value = ''
  infoMessage.value = ''
  canResendActivation.value = false
  loading.value = true

  try {
    await authStore.login({
      email: String(form.value.email || '').trim(),
      password: String(form.value.password || ''),
    })
    // 跳转到首页
    router.push('/')
  } catch (error: any) {
    if (error.response?.data) {
      const errors = error.response.data
      canResendActivation.value = detectInactiveError(errors)
      if (errors.non_field_errors) {
        errorMessage.value = errors.non_field_errors.join(', ')
      } else if (errors.detail) {
        errorMessage.value = errors.detail
      } else {
        errorMessage.value = '邮箱或密码错误'
      }
    } else {
      errorMessage.value = '网络错误，请检查您的网络连接'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
input:focus {
  animation: glow 1.5s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    box-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
  }
  to {
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.6);
  }
}
</style>
