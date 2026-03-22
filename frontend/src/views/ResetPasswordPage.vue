<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center py-12 px-4"
  >
    <div class="fixed inset-0 opacity-20 pointer-events-none">
      <div
        class="absolute inset-0"
        style="background-image: linear-gradient(rgba(0,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,255,0.1) 1px, transparent 1px); background-size: 50px 50px;"
      ></div>
    </div>

    <div class="relative max-w-md w-full">
      <div
        class="bg-slate-900/80 backdrop-blur-sm border-2 border-cyan-500/50 rounded-2xl shadow-[0_0_40px_rgba(0,255,255,0.3)] p-8"
      >
        <div class="text-center mb-8">
          <h1
            class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 mb-2"
          >
            重置密码
          </h1>
          <p class="text-cyan-200 text-sm">请输入并确认新的登录密码</p>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 bg-red-500/20 border-2 border-red-400 rounded-lg">
          <p class="text-red-200 text-sm">{{ errorMessage }}</p>
        </div>

        <div v-if="successMessage" class="mb-6 p-4 bg-cyan-500/15 border-2 border-cyan-400 rounded-lg">
          <p class="text-cyan-100 text-sm">{{ successMessage }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label class="block text-cyan-300 text-sm font-bold mb-2">新密码</label>
            <input
              v-model="newPassword"
              type="password"
              required
              placeholder="请输入新密码"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_15px_rgba(0,255,255,0.3)] transition-all"
            />
          </div>

          <div>
            <label class="block text-cyan-300 text-sm font-bold mb-2">确认密码</label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              placeholder="请再次输入新密码"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_15px_rgba(0,255,255,0.3)] transition-all"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-4 bg-gradient-to-r from-cyan-500 via-purple-600 to-pink-500 text-white font-bold text-lg rounded-lg hover:shadow-[0_0_30px_rgba(0,255,255,0.6)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">提交中...</span>
            <span v-else>确认重置</span>
          </button>
        </form>

        <div class="mt-6 text-center text-sm text-gray-400">
          <router-link to="/login" class="text-cyan-300 hover:text-cyan-200">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const router = useRouter()

const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const extractErrorMessage = (payload: any): string => {
  if (!payload) return ''
  if (typeof payload.detail === 'string' && payload.detail.trim()) return payload.detail.trim()
  for (const value of Object.values(payload)) {
    if (Array.isArray(value) && value.length > 0) {
      const text = String(value[0] || '').trim()
      if (text) return text
    }
    if (typeof value === 'string' && value.trim()) return value.trim()
  }
  return ''
}

const handleSubmit = async () => {
  const uid = String(route.params.uid || '').trim()
  const token = String(route.params.token || '').trim()
  const password = String(newPassword.value || '')
  const rePassword = String(confirmPassword.value || '')

  if (!uid || !token) {
    errorMessage.value = '重置链接无效，请重新申请找回密码'
    return
  }
  if (!password || !rePassword) {
    errorMessage.value = '请完整填写新密码'
    return
  }
  if (password !== rePassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await client.post('/auth/users/reset_password_confirm/', {
      uid,
      token,
      new_password: password,
      re_new_password: rePassword,
    })
    successMessage.value = '密码已重置成功，正在跳转登录页...'
    setTimeout(() => {
      router.push('/login')
    }, 1200)
  } catch (error: any) {
    const payload = error?.response?.data
    errorMessage.value = extractErrorMessage(payload) || '重置失败，请重新获取链接后再试'
  } finally {
    loading.value = false
  }
}
</script>
