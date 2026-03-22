<template>
  <Dialog
    v-model="visible"
    :modal="false"
    panel-class="!m-0 !ml-auto !mr-4 !h-[86vh] !w-[min(520px,calc(100vw-1rem))] !max-w-none !rounded-2xl !p-0 !overflow-hidden"
  >
    <div class="flex h-full w-full flex-col bg-background">
      <header class="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <h3 class="text-lg font-semibold text-foreground">在线客服</h3>
          <p class="text-xs text-muted-foreground">AI优先接待</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusBadgeClass">
            {{ session?.status_display || '连接中' }}
          </span>
          <button
            type="button"
            class="text-xs text-muted-foreground transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="clearing || loading"
            @click="clearChatHistory"
          >
            {{ clearing ? '清空中...' : '清空记录' }}
          </button>
          <button
            type="button"
            class="text-sm text-muted-foreground transition-colors hover:text-foreground"
            @click="visible = false"
          >
            关闭
          </button>
        </div>
      </header>

      <div class="flex min-h-0 flex-1 flex-col">
        <section class="flex min-h-0 flex-1 flex-col">
          <div ref="messageListRef" class="flex-1 overflow-y-auto bg-muted/20 p-4">
            <div v-if="showKnowledgePanel" class="mb-4 rounded-xl border border-border bg-card/90 p-3">
              <div class="space-y-4">
                <section>
                  <h4 class="mb-2 text-sm font-semibold text-foreground">常见问题索引</h4>
                  <div class="space-y-2">
                    <button
                      v-for="faq in faqList"
                      :key="faq.id"
                      type="button"
                      class="w-full rounded-lg border border-border bg-card px-3 py-2 text-left text-xs text-foreground transition-colors hover:bg-muted"
                      @click="fillDraft(faq.question || '')"
                    >
                      {{ faq.question }}
                    </button>
                  </div>
                </section>

                <section>
                  <h4 class="mb-2 text-sm font-semibold text-foreground">站内内容索引</h4>
                  <div class="space-y-2 text-xs text-muted-foreground">
                    <p v-if="gameList.length">热门游戏：{{ gameList.map((item) => item.title).join(' / ') }}</p>
                    <p v-if="articleList.length">热门资讯：{{ articleList.map((item) => item.title).join(' / ') }}</p>
                    <p v-if="!gameList.length && !articleList.length">暂未同步到索引数据</p>
                  </div>
                </section>
              </div>
            </div>
            <div v-if="messages.length === 0" class="py-10 text-center text-sm text-muted-foreground">
              {{ loading ? '正在连接客服系统...' : '开始输入消息即可对话' }}
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="message in messages"
                :key="message.id"
                class="max-w-[85%] rounded-xl border px-3 py-2 text-sm"
                :class="messageBubbleClass(message.sender_type)"
              >
                <p class="whitespace-pre-wrap break-words text-foreground">{{ message.content }}</p>
                <p class="mt-1 text-[11px] text-muted-foreground">
                  {{ message.sender_name || message.sender_type_display }} · {{ formatTime(message.created_at) }}
                </p>
              </div>
            </div>
          </div>

          <div class="border-t border-border bg-card p-3">
            <p v-if="errorText" class="mb-2 text-xs text-red-500">{{ errorText }}</p>
            <textarea
              v-model="draft"
              class="min-h-[84px] w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground outline-none focus:border-primary"
              placeholder="请输入问题，按 Enter 发送（Shift+Enter 换行）"
              @keydown.enter.exact.prevent="submitMessage"
            />
            <div class="mt-2 flex flex-wrap items-center justify-between gap-2">
              <p class="text-xs text-muted-foreground">
                {{ showHandoffTrigger ? '如需人工处理，可手动确认转接。' : '按 Enter 发送，AI将优先协助处理。' }}
              </p>
              <div class="flex items-center gap-2">
                <button
                  v-if="showHandoffTrigger"
                  type="button"
                  class="text-xs text-muted-foreground underline underline-offset-2 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="handoffing || !session || session.status !== 'ai'"
                  @click="handoffToHuman"
                >
                  {{ handoffing ? '转接中...' : '转人工' }}
                </button>
                <button
                  v-if="showResumeAiTrigger"
                  type="button"
                  class="text-xs text-muted-foreground underline underline-offset-2 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="resumingAi || !session || session.status !== 'human'"
                  @click="resumeToAi"
                >
                  {{ resumingAi ? '处理中...' : '结束人工' }}
                </button>
                <Button
                  size="sm"
                  :disabled="sending || !draft.trim() || !session || session.status === 'closed'"
                  @click="submitMessage"
                >
                  {{ sending ? '发送中...' : session?.status === 'closed' ? '会话已关闭' : '发送' }}
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import Button from '../ui/Button.vue'
import Dialog from '../ui/Dialog.vue'
import {
  getChatKnowledge,
  getChatMessages,
  handoffChatToHuman,
  initChatSession,
  resumeChatToAi,
  sendChatMessage,
  type ChatKnowledgeResponse,
  type ChatMessage,
  type ChatSession,
} from '../../api/customerChat'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const VISITOR_TOKEN_KEY = 'customer_chat_visitor_token'
const SESSION_ID_KEY = 'customer_chat_session_id'

const loading = ref(false)
const sending = ref(false)
const handoffing = ref(false)
const resumingAi = ref(false)
const clearing = ref(false)
const errorText = ref('')
const draft = ref('')

const knowledge = ref<ChatKnowledgeResponse | null>(null)
const session = ref<ChatSession | null>(null)
const messages = ref<ChatMessage[]>([])
const visitorToken = ref('')
const messageListRef = ref<HTMLElement | null>(null)
let pollTimer: number | null = null

const showKnowledgePanel = computed(() => knowledge.value?.agent?.show_knowledge_panel !== false)
const faqList = computed(() => (knowledge.value?.faqs || []).slice(0, 6))
const gameList = computed(() => (knowledge.value?.games || []).slice(0, 5))
const articleList = computed(() => (knowledge.value?.articles || []).slice(0, 5))

const statusBadgeClass = computed(() => {
  if (session.value?.status === 'human') return 'bg-emerald-100 text-emerald-700'
  if (session.value?.status === 'closed') return 'bg-slate-200 text-slate-700'
  return 'bg-cyan-100 text-cyan-700'
})

const transferKeywords = computed(() => {
  const fromConfig = (knowledge.value?.agent?.transfer_keywords || [])
    .map((item) => String(item || '').trim().toLowerCase())
    .filter(Boolean)
  const defaults = ['转人工', '人工客服', '真人客服', '人工']
  return Array.from(new Set([...fromConfig, ...defaults]))
})

const hasTransferIntentInDraft = computed(() => {
  const text = String(draft.value || '').trim().toLowerCase()
  if (!text) return false
  return transferKeywords.value.some((keyword) => keyword && text.includes(keyword))
})

const showHandoffTrigger = computed(() => {
  if (!session.value || session.value.status !== 'ai') return false
  return hasTransferIntentInDraft.value
})

const showResumeAiTrigger = computed(() => {
  return !!session.value && session.value.status === 'human'
})

const createVisitorToken = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID().replace(/-/g, '')
  }
  return `${Date.now()}_${Math.random().toString(36).slice(2)}`
}

const ensureVisitorToken = () => {
  const cached = localStorage.getItem(VISITOR_TOKEN_KEY)
  if (cached) {
    visitorToken.value = cached
    return cached
  }
  const token = createVisitorToken()
  localStorage.setItem(VISITOR_TOKEN_KEY, token)
  visitorToken.value = token
  return token
}

const mergeMessages = (incoming: ChatMessage[]) => {
  if (!incoming.length) return
  const merged = new Map<number, ChatMessage>()
  for (const item of messages.value) {
    merged.set(item.id, item)
  }
  for (const item of incoming) {
    merged.set(item.id, item)
  }
  messages.value = Array.from(merged.values()).sort((a, b) => a.id - b.id)
}

const latestMessageId = computed(() => {
  if (!messages.value.length) return 0
  return messages.value[messages.value.length - 1].id
})

const scrollToBottom = async () => {
  await nextTick()
  if (!messageListRef.value) return
  messageListRef.value.scrollTop = messageListRef.value.scrollHeight
}

const formatTime = (value: string) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

const messageBubbleClass = (senderType: string) => {
  if (senderType === 'user') return 'ml-auto border-cyan-200 bg-cyan-50'
  if (senderType === 'ai') return 'mr-auto border-sky-200 bg-sky-50'
  if (senderType === 'agent') return 'mr-auto border-emerald-200 bg-emerald-50'
  return 'mx-auto border-slate-200 bg-slate-100'
}

const stopPolling = () => {
  if (pollTimer !== null) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

const startPolling = () => {
  stopPolling()
  pollTimer = window.setInterval(() => {
    refreshMessages(true)
  }, 3000)
}

const fillDraft = (question: string) => {
  if (!question) return
  draft.value = question
}

const refreshMessages = async (silent = false) => {
  if (!session.value?.session_id) return
  try {
    const response = await getChatMessages({
      sessionId: session.value.session_id,
      visitorToken: visitorToken.value,
      sinceId: latestMessageId.value,
    })
    session.value = response.session
    if (response.messages.length) {
      mergeMessages(response.messages)
      await scrollToBottom()
    }
    errorText.value = ''
  } catch (error: any) {
    if (!silent) {
      errorText.value = error?.response?.data?.detail || '消息同步失败，请稍后重试'
    }
  }
}

const bootstrapChat = async () => {
  loading.value = true
  errorText.value = ''
  try {
    if (!knowledge.value) {
      knowledge.value = await getChatKnowledge()
    }
    const token = ensureVisitorToken()
    const cachedSessionId = localStorage.getItem(SESSION_ID_KEY) || ''
    const response = await initChatSession({
      visitor_token: token,
      session_id: cachedSessionId,
      source_page: window.location.pathname,
    })
    visitorToken.value = response.visitor_token
    localStorage.setItem(VISITOR_TOKEN_KEY, response.visitor_token)
    localStorage.setItem(SESSION_ID_KEY, response.session.session_id)
    session.value = response.session
    messages.value = response.messages || []
    await scrollToBottom()
    startPolling()
  } catch (error: any) {
    errorText.value = error?.response?.data?.detail || '客服服务暂时不可用'
  } finally {
    loading.value = false
  }
}

const submitMessage = async () => {
  const content = draft.value.trim()
  if (!content || !session.value?.session_id || sending.value) return
  sending.value = true
  try {
    const response = await sendChatMessage({
      sessionId: session.value.session_id,
      visitorToken: visitorToken.value,
      content,
    })
    draft.value = ''
    session.value = response.session
    mergeMessages(response.messages || [])
    errorText.value = ''
    await scrollToBottom()
  } catch (error: any) {
    errorText.value = error?.response?.data?.detail || '发送失败，请稍后重试'
  } finally {
    sending.value = false
  }
}

const handoffToHuman = async () => {
  if (!session.value?.session_id || handoffing.value) return
  handoffing.value = true
  try {
    const response = await handoffChatToHuman({
      sessionId: session.value.session_id,
      visitorToken: visitorToken.value,
    })
    session.value = response.session
    await refreshMessages(true)
    errorText.value = ''
  } catch (error: any) {
    errorText.value = error?.response?.data?.detail || '转人工失败，请稍后重试'
  } finally {
    handoffing.value = false
  }
}

const resumeToAi = async () => {
  if (!session.value?.session_id || resumingAi.value) return
  resumingAi.value = true
  try {
    const response = await resumeChatToAi({
      sessionId: session.value.session_id,
      visitorToken: visitorToken.value,
    })
    session.value = response.session
    mergeMessages(response.messages || [])
    await refreshMessages(true)
    errorText.value = ''
  } catch (error: any) {
    errorText.value = error?.response?.data?.detail || '结束人工失败，请稍后重试'
  } finally {
    resumingAi.value = false
  }
}

const clearChatHistory = async () => {
  if (clearing.value) return
  if (!window.confirm('确定清空当前聊天记录并开始新会话吗？')) return
  clearing.value = true
  try {
    stopPolling()
    localStorage.removeItem(SESSION_ID_KEY)
    session.value = null
    messages.value = []
    draft.value = ''
    errorText.value = ''
    await bootstrapChat()
  } catch (error: any) {
    errorText.value = error?.response?.data?.detail || '清空失败，请稍后重试'
  } finally {
    clearing.value = false
  }
}

watch(
  () => visible.value,
  async (opened) => {
    if (opened) {
      await bootstrapChat()
      return
    }
    stopPolling()
  }
)

onBeforeUnmount(() => {
  stopPolling()
})
</script>
