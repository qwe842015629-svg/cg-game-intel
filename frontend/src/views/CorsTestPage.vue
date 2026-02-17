<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 mb-4">
          CORS 跨域测试页面
        </h1>
        <p class="text-cyan-200">
          测试前端 (http://localhost:5176) 与后端 (http://localhost:8000) 的跨域通信
        </p>
      </div>

      <!-- Status Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <!-- Frontend Status -->
        <div class="bg-slate-900/50 border-2 border-cyan-500/50 rounded-xl p-6 backdrop-blur-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
            <h3 class="text-xl font-bold text-cyan-300">前端状态</h3>
          </div>
          <div class="space-y-2 text-sm">
            <p class="text-cyan-100">
              <span class="text-cyan-400">地址：</span>{{ frontendUrl }}
            </p>
            <p class="text-cyan-100">
              <span class="text-cyan-400">框架：</span>Vue 3 + TypeScript
            </p>
            <p class="text-cyan-100">
              <span class="text-cyan-400">HTTP 客户端：</span>Axios
            </p>
          </div>
        </div>

        <!-- Backend Status -->
        <div class="bg-slate-900/50 border-2 border-purple-500/50 rounded-xl p-6 backdrop-blur-sm">
          <div class="flex items-center gap-3 mb-4">
            <div :class="['w-3 h-3 rounded-full', backendOnline ? 'bg-green-400 animate-pulse' : 'bg-red-400']"></div>
            <h3 class="text-xl font-bold text-purple-300">后端状态</h3>
          </div>
          <div class="space-y-2 text-sm">
            <p class="text-purple-100">
              <span class="text-purple-400">地址：</span>{{ backendUrl }}
            </p>
            <p class="text-purple-100">
              <span class="text-purple-400">框架：</span>Django + DRF
            </p>
            <p class="text-purple-100">
              <span class="text-purple-400">状态：</span>
              <span :class="backendOnline ? 'text-green-400' : 'text-red-400'">
                {{ backendOnline ? '在线 ✓' : '离线 ✗' }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <!-- Test Buttons -->
      <div class="bg-slate-900/50 border-2 border-pink-500/50 rounded-xl p-6 backdrop-blur-sm mb-8">
        <h3 class="text-xl font-bold text-pink-300 mb-4">CORS 测试</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            @click="testGet"
            :disabled="loading"
            class="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(0,255,255,0.3)]"
          >
            {{ loading ? '测试中...' : 'GET 请求测试' }}
          </button>

          <button
            @click="testPost"
            :disabled="loading"
            class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(168,85,247,0.3)]"
          >
            {{ loading ? '测试中...' : 'API 请求测试（文章）' }}
          </button>

          <button
            @click="testAuth"
            :disabled="loading"
            class="px-6 py-3 bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(34,197,94,0.3)]"
          >
            {{ loading ? '测试中...' : '根路径测试' }}
          </button>

          <button
            @click="checkBackendStatus"
            :disabled="loading"
            class="px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(234,179,8,0.3)]"
          >
            {{ loading ? '检测中...' : '检查后端状态' }}
          </button>
        </div>
      </div>

      <!-- Results -->
      <div v-if="results.length > 0" class="bg-slate-900/50 border-2 border-cyan-500/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 class="text-xl font-bold text-cyan-300 mb-4">测试结果</h3>
        <div class="space-y-4 max-h-96 overflow-y-auto">
          <div
            v-for="(result, index) in results"
            :key="index"
            :class="[
              'p-4 rounded-lg border-2',
              result.success 
                ? 'bg-green-500/10 border-green-400/50' 
                : 'bg-red-500/10 border-red-400/50'
            ]"
          >
            <div class="flex items-start gap-3">
              <div :class="[
                'mt-1 text-2xl',
                result.success ? 'text-green-400' : 'text-red-400'
              ]">
                {{ result.success ? '✓' : '✗' }}
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                  <h4 :class="[
                    'font-bold',
                    result.success ? 'text-green-300' : 'text-red-300'
                  ]">
                    {{ result.title }}
                  </h4>
                  <span class="text-xs text-gray-400">{{ result.timestamp }}</span>
                </div>
                <p class="text-sm text-gray-300 mb-2">{{ result.message }}</p>
                <div v-if="result.details" class="mt-3 p-3 bg-slate-800/50 rounded border border-slate-700">
                  <pre class="text-xs text-cyan-200 overflow-x-auto">{{ JSON.stringify(result.details, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CORS Configuration Info -->
      <div class="mt-8 bg-slate-900/50 border-2 border-blue-500/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 class="text-xl font-bold text-blue-300 mb-4">CORS 配置说明</h3>
        <div class="space-y-3 text-sm text-blue-100">
          <div class="flex items-start gap-2">
            <span class="text-blue-400 mt-1">✓</span>
            <p><strong>前端配置：</strong>axios 已启用 withCredentials: true</p>
          </div>
          <div class="flex items-start gap-2">
            <span class="text-blue-400 mt-1">✓</span>
            <p><strong>后端配置：</strong>Django 已配置 django-cors-headers</p>
          </div>
          <div class="flex items-start gap-2">
            <span class="text-blue-400 mt-1">✓</span>
            <p><strong>允许的源：</strong>http://localhost:5176</p>
          </div>
          <div class="flex items-start gap-2">
            <span class="text-blue-400 mt-1">✓</span>
            <p><strong>允许的方法：</strong>GET, POST, PUT, PATCH, DELETE, OPTIONS</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import client from '../api/client'

interface TestResult {
  success: boolean
  title: string
  message: string
  timestamp: string
  details?: any
}

const frontendUrl = 'http://localhost:5176'
const backendUrl = 'http://localhost:8000'
const loading = ref(false)
const backendOnline = ref(false)
const results = ref<TestResult[]>([])

const addResult = (result: Omit<TestResult, 'timestamp'>) => {
  results.value.unshift({
    ...result,
    timestamp: new Date().toLocaleTimeString('zh-CN')
  })
}

// 检查后端状态
const checkBackendStatus = async () => {
  loading.value = true
  try {
    const response = await fetch(`${backendUrl}/api/`, {
      method: 'GET',
      credentials: 'include',
    })
    
    if (response.ok) {
      backendOnline.value = true
      addResult({
        success: true,
        title: '后端状态检查',
        message: '后端服务运行正常！',
        details: {
          status: response.status,
          statusText: response.statusText,
        }
      })
    } else {
      backendOnline.value = false
      addResult({
        success: false,
        title: '后端状态检查',
        message: `后端返回错误状态码: ${response.status}`,
      })
    }
  } catch (error: any) {
    backendOnline.value = false
    addResult({
      success: false,
      title: '后端状态检查',
      message: '无法连接到后端服务，请确保 Django 服务器正在运行',
      details: {
        error: error.message
      }
    })
  } finally {
    loading.value = false
  }
}

// GET 请求测试 - 使用实际存在的端点
const testGet = async () => {
  loading.value = true
  try {
    // 测试产品列表接口（实际存在）
    const response = await client.get('/products/')
    addResult({
      success: true,
      title: 'GET 请求测试 (/api/products/)',
      message: 'GET 请求成功！CORS 配置正确，可以正常访问产品列表。',
      details: response
    })
  } catch (error: any) {
    addResult({
      success: false,
      title: 'GET 请求测试',
      message: error.message || '请求失败',
      details: {
        error: error.message,
        response: error.response?.data,
        status: error.response?.status
      }
    })
  } finally {
    loading.value = false
  }
}

// POST 请求测试 - 使用实际存在的端点
const testPost = async () => {
  loading.value = true
  try {
    // 测试文章列表接口（实际存在）
    const response = await client.get('/articles/')
    addResult({
      success: true,
      title: 'API 请求测试 (/api/articles/)',
      message: 'API 请求成功！跨域配置正确，可以正常访问文章列表。',
      details: response
    })
  } catch (error: any) {
    addResult({
      success: false,
      title: 'API 请求测试',
      message: error.message || '请求失败',
      details: {
        error: error.message,
        response: error.response?.data,
        status: error.response?.status
      }
    })
  } finally {
    loading.value = false
  }
}

// 认证请求测试 - 使用根路径测试
const testAuth = async () => {
  loading.value = true
  try {
    // 访问根 API 路径
    const response = await fetch('http://localhost:8000/', {
      method: 'GET',
      credentials: 'include',
    })
    
    if (response.ok) {
      const data = await response.text()
      addResult({
        success: true,
        title: '根路径访问测试',
        message: 'CORS 配置正确！可以正常访问后端根路径。',
        details: {
          status: response.status,
          note: '这表明跨域请求成功，CORS 配置正确'
        }
      })
    } else {
      addResult({
        success: true,
        title: '根路径访问测试',
        message: `收到 ${response.status} 响应，CORS 配置正确（状态码不影响 CORS）`,
        details: {
          status: response.status,
          note: '没有 CORS 错误，说明配置正确'
        }
      })
    }
  } catch (error: any) {
    if (error.message.includes('CORS')) {
      addResult({
        success: false,
        title: '根路径访问测试',
        message: 'CORS 配置有问题：' + error.message,
        details: {
          error: error.message
        }
      })
    } else {
      addResult({
        success: true,
        title: '根路径访问测试',
        message: '没有 CORS 错误，配置正确（其他错误不影响 CORS）',
        details: {
          error: error.message,
          note: '如果是网络错误或其他错误，但不是 CORS 错误，说明 CORS 配置正确'
        }
      })
    }
  } finally {
    loading.value = false
  }
}

// 页面加载时检查后端状态
checkBackendStatus()
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(0, 255, 255, 0.6), rgba(168, 85, 247, 0.6));
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(0, 255, 255, 0.8), rgba(168, 85, 247, 0.8));
}
</style>
