<template>
  <Dialog v-model="isOpen">
    <!-- 注册成功 - 待激活提示 -->
    <div v-if="registrationSuccess" class="space-y-4">
      <!-- 成功图标 -->
      <div class="text-center mb-4">
        <div class="w-16 h-16 mx-auto bg-gradient-to-br from-green-400 to-cyan-400 rounded-full flex items-center justify-center shadow-[0_0_30px_rgba(34,197,94,0.6)] animate-bounce">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
          </svg>
        </div>
      </div>

      <h2 class="text-2xl font-bold text-center text-green-400">🎉 注册成功！</h2>
      
      <div class="text-center space-y-3">
        <p class="text-sm text-muted-foreground">
          激活邮件已发送至
        </p>
        <p class="text-lg font-bold text-cyan-400">
          {{ registerForm.email }}
        </p>
      </div>

      <!-- 操作指南 -->
      <div class="bg-cyan-500/10 border-2 border-cyan-500/30 rounded-xl p-4 space-y-3">
        <h3 class="text-sm font-bold text-cyan-300 flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          接下来该怎么做？
        </h3>
        <ol class="space-y-2 text-xs text-cyan-100">
          <li class="flex items-start gap-2">
            <span class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold">1</span>
            <span>打开您的邮箱 <strong class="text-cyan-300">{{ registerForm.email }}</strong></span>
          </li>
          <li class="flex items-start gap-2">
            <span class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold">2</span>
            <span>找到来自 <strong class="text-cyan-300">CYPHER GAME BUY</strong> 的激活邮件</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold">3</span>
            <span>点击邮件中的 <strong class="text-cyan-300">激活按钮</strong></span>
          </li>
          <li class="flex items-start gap-2">
            <span class="flex-shrink-0 w-5 h-5 bg-cyan-500 text-black rounded-full flex items-center justify-center text-xs font-bold">4</span>
            <span>激活成功后，即可登录使用</span>
          </li>
        </ol>
      </div>

      <!-- 提示信息 -->
      <div class="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
        <p class="text-yellow-300 text-xs flex items-start gap-2">
          <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>
            <strong>没收到邮件？</strong><br/>
            请检查垃圾邮件文件夹，或等待几分钟后重试
          </span>
        </p>
      </div>

      <!-- 操作按钮 -->
      <div class="grid grid-cols-2 gap-3">
        <Button @click="openEmail" class="w-full">
          📧 打开邮箱
        </Button>
        <Button @click="closeActivationDialog" variant="outline" class="w-full">
          关闭
        </Button>
      </div>
    </div>

    <!-- 原有的登录/注册表单 -->
    <div v-else class="space-y-4">
      <h2 class="text-2xl font-bold">账号登录</h2>
      
      <Tabs :tabs="['登录', '注册']" v-model="activeTab">
        <!-- Login Tab -->
        <div v-if="activeTab === '登录'" class="space-y-4 pt-4">
          <div>
            <label class="block text-sm font-medium mb-2">邮箱</label>
            <Input
              v-model="loginForm.email"
              type="email"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">密码</label>
            <Input
              v-model="loginForm.password"
              type="password"
              placeholder="••••••••"
            />
          </div>
          <Button @click="handleLogin" class="w-full">登录</Button>
        </div>

        <!-- Register Tab -->
        <div v-if="activeTab === '注册'" class="space-y-4 pt-4">
          <div>
            <label class="block text-sm font-medium mb-2">用户名</label>
            <Input
              v-model="registerForm.name"
              placeholder="您的昵称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">邮箱</label>
            <Input
              v-model="registerForm.email"
              type="email"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">密码</label>
            <Input
              v-model="registerForm.password"
              type="password"
              placeholder="••••••••"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-2">确认密码</label>
            <Input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="••••••••"
            />
          </div>
          <Button @click="handleRegister" class="w-full">注册</Button>
        </div>
      </Tabs>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import Dialog from './ui/Dialog.vue'
import Tabs from './ui/Tabs.vue'
import Input from './ui/Input.vue'
import Button from './ui/Button.vue'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const authStore = useAuthStore()
const isOpen = ref(props.modelValue)
const activeTab = ref('登录')

const loginForm = ref({
  email: '',
  password: '',
})

const registerForm = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const registrationSuccess = ref(false)
const errorMessage = ref('')

watch(() => props.modelValue, (val) => {
  isOpen.value = val
})

watch(isOpen, (val) => {
  emit('update:modelValue', val)
  // 关闭弹窗时重置注册成功状态
  if (!val) {
    registrationSuccess.value = false
    errorMessage.value = ''
  }
})

const handleLogin = async () => {
  try {
    await authStore.login(loginForm.value)
    alert('登录成功！')
    isOpen.value = false
    loginForm.value = { email: '', password: '' }
  } catch (error: any) {
    if (error.response?.data) {
      const errors = error.response.data
      if (errors.non_field_errors) {
        alert(errors.non_field_errors.join(', '))
      } else if (errors.detail) {
        alert(errors.detail)
      } else {
        alert('邮箱或密码错误')
      }
    } else {
      alert('登录失败，请检查您的凭据')
    }
  }
}

const handleRegister = async () => {
  errorMessage.value = ''
  
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  if (registerForm.value.password.length < 8) {
    alert('密码长度至少为8位')
    return
  }
  
  try {
    await authStore.register(registerForm.value)
    // 显示注册成功提示
    registrationSuccess.value = true
  } catch (error: any) {
    if (error.response?.data) {
      const errors = error.response.data
      if (errors.username) {
        alert('用户名：' + errors.username.join(', '))
      } else if (errors.email) {
        alert('邮箱：' + errors.email.join(', '))
      } else if (errors.password) {
        alert('密码：' + errors.password.join(', '))
      } else {
        alert('注册失败，请稍后重试')
      }
    } else {
      alert('注册失败，请重试')
    }
  }
}

const openEmail = () => {
  const email = registerForm.value.email
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

const closeActivationDialog = () => {
  isOpen.value = false
  registrationSuccess.value = false
  registerForm.value = { name: '', email: '', password: '', confirmPassword: '' }
}
</script>

<style scoped>
/* 激活成功动画 */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce {
  animation: bounce 1s ease-in-out infinite;
}

/* 霸道气流荧光效果 */
.shadow-neon-green {
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.6);
}
</style>
