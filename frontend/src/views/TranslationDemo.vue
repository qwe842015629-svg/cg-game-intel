<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900 py-12">
    <div class="container mx-auto px-4 max-w-4xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-black text-cyan-300 mb-4 drop-shadow-[0_0_15px_rgba(0,255,255,0.8)]">
          {{ $t('siteName') }} - 翻译演示
        </h1>
        <p class="text-cyan-200">测试翻译API功能</p>
      </div>

      <!-- Translation Stats -->
      <div v-if="stats" class="bg-slate-900/50 border-2 border-cyan-500/50 rounded-xl p-6 mb-6 backdrop-blur-sm">
        <h3 class="text-xl font-bold text-cyan-300 mb-4">翻译额度统计</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-sm text-cyan-200/70 mb-1">可用字符数</div>
            <div class="text-3xl font-black text-cyan-400">{{ stats.available.toLocaleString() }}</div>
          </div>
          <div>
            <div class="text-sm text-cyan-200/70 mb-1">已使用字符数</div>
            <div class="text-3xl font-black text-purple-400">{{ stats.used.toLocaleString() }}</div>
          </div>
        </div>
      </div>

      <!-- Single Translation -->
      <div class="bg-slate-900/50 border-2 border-purple-500/50 rounded-xl p-6 mb-6 backdrop-blur-sm">
        <h3 class="text-xl font-bold text-purple-300 mb-4">单文本翻译</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-cyan-200 mb-2 text-sm font-bold">原文</label>
            <textarea
              v-model="singleText"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-cyan-100 placeholder-cyan-400/50 focus:outline-none focus:border-cyan-400 min-h-[100px]"
              placeholder="输入要翻译的文本..."
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-cyan-200 mb-2 text-sm font-bold">目标语言</label>
              <select
                v-model="singleTargetLang"
                class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-cyan-100 focus:outline-none focus:border-cyan-400"
              >
                <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                  {{ lang.native_name }} ({{ lang.name }})
                </option>
              </select>
            </div>
            <div>
              <label class="block text-cyan-200 mb-2 text-sm font-bold">操作</label>
              <button
                @click="handleSingleTranslate"
                :disabled="loading || !singleText"
                class="w-full px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-[0_0_20px_rgba(0,255,255,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ loading ? '翻译中...' : '翻译' }}
              </button>
            </div>
          </div>

          <div v-if="singleResult">
            <label class="block text-cyan-200 mb-2 text-sm font-bold">译文</label>
            <div class="w-full px-4 py-3 bg-slate-800/50 border-2 border-green-500/50 rounded-lg text-green-100 min-h-[100px]">
              {{ singleResult }}
            </div>
          </div>
        </div>
      </div>

      <!-- Batch Translation -->
      <div class="bg-slate-900/50 border-2 border-pink-500/50 rounded-xl p-6 mb-6 backdrop-blur-sm">
        <h3 class="text-xl font-bold text-pink-300 mb-4">批量翻译</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-cyan-200 mb-2 text-sm font-bold">批量文本（每行一条）</label>
            <textarea
              v-model="batchTexts"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-cyan-100 placeholder-cyan-400/50 focus:outline-none focus:border-cyan-400 min-h-[150px]"
              placeholder="输入要翻译的文本，每行一条..."
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-cyan-200 mb-2 text-sm font-bold">目标语言</label>
              <select
                v-model="batchTargetLang"
                class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-cyan-100 focus:outline-none focus:border-cyan-400"
              >
                <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                  {{ lang.native_name }} ({{ lang.name }})
                </option>
              </select>
            </div>
            <div>
              <label class="block text-cyan-200 mb-2 text-sm font-bold">操作</label>
              <button
                @click="handleBatchTranslate"
                :disabled="loading || !batchTexts"
                class="w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-[0_0_20px_rgba(236,72,153,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ loading ? '批量翻译中...' : '批量翻译' }}
              </button>
            </div>
          </div>

          <div v-if="batchResults.length > 0">
            <label class="block text-cyan-200 mb-2 text-sm font-bold">译文</label>
            <div class="space-y-2">
              <div
                v-for="(result, index) in batchResults"
                :key="index"
                class="px-4 py-2 bg-slate-800/50 border-2 border-green-500/50 rounded-lg text-green-100"
              >
                {{ result }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Multi-language Translation -->
      <div class="bg-slate-900/50 border-2 border-blue-500/50 rounded-xl p-6 backdrop-blur-sm">
        <h3 class="text-xl font-bold text-blue-300 mb-4">多语种翻译</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-cyan-200 mb-2 text-sm font-bold">原文</label>
            <textarea
              v-model="multiText"
              class="w-full px-4 py-3 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg text-cyan-100 placeholder-cyan-400/50 focus:outline-none focus:border-cyan-400 min-h-[100px]"
              placeholder="输入要翻译成多种语言的文本..."
            ></textarea>
          </div>

          <div>
            <label class="block text-cyan-200 mb-2 text-sm font-bold">选择目标语言（多选）</label>
            <div class="grid grid-cols-3 gap-2">
              <label
                v-for="lang in languages"
                :key="lang.code"
                class="flex items-center gap-2 px-3 py-2 bg-slate-800/50 border-2 border-cyan-500/50 rounded-lg cursor-pointer hover:border-cyan-400"
              >
                <input
                  type="checkbox"
                  :value="lang.code"
                  v-model="multiTargetLangs"
                  class="rounded"
                />
                <span class="text-cyan-100 text-sm">{{ lang.native_name }}</span>
              </label>
            </div>
          </div>

          <button
            @click="handleMultiTranslate"
            :disabled="loading || !multiText || multiTargetLangs.length === 0"
            class="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-lg hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? '多语种翻译中...' : '翻译为多种语言' }}
          </button>

          <div v-if="Object.keys(multiResults).length > 0">
            <label class="block text-cyan-200 mb-2 text-sm font-bold">译文</label>
            <div class="space-y-2">
              <div
                v-for="(text, langCode) in multiResults"
                :key="langCode"
                class="px-4 py-3 bg-slate-800/50 border-2 border-green-500/50 rounded-lg"
              >
                <div class="text-sm text-green-400 mb-1">{{ getLanguageName(langCode) }}</div>
                <div class="text-green-100">{{ text }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mt-6 bg-red-900/50 border-2 border-red-500 rounded-xl p-4 backdrop-blur-sm">
        <div class="flex items-center gap-2">
          <AlertCircle class="w-5 h-5 text-red-400" />
          <span class="text-red-200">{{ error }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AlertCircle } from 'lucide-vue-next'
import {
  translateText,
  translateBatch,
  translateMultiLanguage,
  getSupportedLanguages,
  getTranslationStats,
  type Language,
  type TranslationStats
} from '../services/translationApi'

const loading = ref(false)
const error = ref('')

// Stats
const stats = ref<TranslationStats | null>(null)

// Languages
const languages = ref<Language[]>([])

// Single translation
const singleText = ref('Hello, world!')
const singleTargetLang = ref('zh-CN')
const singleResult = ref('')

// Batch translation
const batchTexts = ref('Hello\nWorld\nGood morning')
const batchTargetLang = ref('ja')
const batchResults = ref<string[]>([])

// Multi-language translation
const multiText = ref('Welcome to our website')
const multiTargetLangs = ref<string[]>(['ja', 'ko', 'fr'])
const multiResults = ref<Record<string, string>>({})

const handleSingleTranslate = async () => {
  if (!singleText.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await translateText(singleText.value, singleTargetLang.value)
    singleResult.value = result
  } catch (e: any) {
    error.value = e.message || '翻译失败'
  } finally {
    loading.value = false
  }
}

const handleBatchTranslate = async () => {
  if (!batchTexts.value) return
  
  const texts = batchTexts.value.split('\n').filter(t => t.trim())
  if (texts.length === 0) return
  
  loading.value = true
  error.value = ''
  
  try {
    const results = await translateBatch(texts, batchTargetLang.value)
    batchResults.value = results
  } catch (e: any) {
    error.value = e.message || '批量翻译失败'
  } finally {
    loading.value = false
  }
}

const handleMultiTranslate = async () => {
  if (!multiText.value || multiTargetLangs.value.length === 0) return
  
  loading.value = true
  error.value = ''
  
  try {
    const results = await translateMultiLanguage(multiText.value, multiTargetLangs.value)
    multiResults.value = results
  } catch (e: any) {
    error.value = e.message || '多语种翻译失败'
  } finally {
    loading.value = false
  }
}

const getLanguageName = (code: string): string => {
  const lang = languages.value.find(l => l.code === code)
  return lang ? `${lang.native_name} (${lang.name})` : code
}

const loadInitialData = async () => {
  try {
    // Load supported languages
    languages.value = await getSupportedLanguages()
    
    // Load translation stats
    stats.value = await getTranslationStats()
  } catch (e: any) {
    console.error('Failed to load initial data:', e)
  }
}

onMounted(() => {
  loadInitialData()
})
</script>
