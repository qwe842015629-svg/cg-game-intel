<template>
  <div v-if="authStore.isAuthenticated" class="fixed right-4 top-1/2 z-[60] -translate-y-1/2">
    <button
      class="relative inline-flex h-12 w-12 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 shadow-lg transition hover:bg-slate-50"
      :title="t('directMessageFloat.open')"
      @click="togglePanel"
    >
      <MessageCircle class="h-5 w-5" />
      <span
        v-if="totalUnreadMessages > 0"
        class="absolute -right-1 -top-1 min-w-[1.15rem] rounded-full bg-rose-500 px-1 text-center text-[10px] leading-5 text-white"
      >
        {{ unreadBadge }}
      </span>
    </button>

    <div
      v-if="open"
      class="mt-2 flex h-[72vh] w-[min(420px,calc(100vw-1rem))] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl"
    >
      <div class="flex items-center justify-between border-b border-slate-200 px-3 py-2">
        <div>
          <p class="text-sm font-semibold text-slate-900">{{ t('directMessageFloat.title') }}</p>
          <p class="text-[11px] text-slate-500">
            {{ t('directMessageFloat.unreadCount', { count: totalUnreadMessages }) }}
          </p>
        </div>
        <div class="flex items-center gap-1">
          <button
            class="rounded border border-slate-300 px-2 py-1 text-[11px] text-slate-700 hover:bg-slate-100"
            :disabled="loadingThreads"
            @click="refreshNow"
          >
            {{ t('directMessageFloat.refresh') }}
          </button>
          <button
            class="rounded border border-slate-300 px-2 py-1 text-[11px] text-slate-700 hover:bg-slate-100"
            @click="open = false"
          >
            {{ t('directMessageFloat.close') }}
          </button>
        </div>
      </div>

      <p v-if="panelError" class="border-b border-rose-100 bg-rose-50 px-3 py-2 text-xs text-rose-600">
        {{ panelError }}
      </p>

      <div class="grid min-h-0 flex-1 grid-cols-[156px_1fr]">
        <aside class="min-h-0 overflow-y-auto border-r border-slate-200 bg-slate-50 p-2">
          <p v-if="loadingThreads" class="px-1 py-2 text-xs text-slate-500">{{ t('directMessageFloat.loading') }}</p>
          <p v-else-if="threads.length === 0" class="px-1 py-2 text-xs text-slate-500">
            {{ t('directMessageFloat.emptyThreads') }}
          </p>
          <button
            v-for="item in threads"
            :key="`dm-thread-item-${item.thread.id}`"
            class="mb-1.5 flex w-full items-start gap-2 rounded-lg border p-2 text-left"
            :class="
              item.thread.id === selectedThreadId
                ? 'border-emerald-300 bg-emerald-50'
                : 'border-slate-200 bg-white hover:bg-slate-100'
            "
            @click="selectThread(item.thread.id)"
          >
            <img
              :src="item.peer.avatar_url || fallbackAvatar(item.peer.name || item.peer.username)"
              :alt="item.peer.name || item.peer.username"
              class="h-7 w-7 shrink-0 rounded-full border border-slate-200 object-cover"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-1">
                <p class="truncate text-[11px] font-medium text-slate-800">
                  {{ item.peer.name || item.peer.username || t('directMessageFloat.unknownUser') }}
                </p>
                <span
                  v-if="item.unread_count > 0"
                  class="rounded-full bg-rose-500 px-1.5 py-0.5 text-[10px] leading-none text-white"
                >
                  {{ item.unread_count > 99 ? '99+' : item.unread_count }}
                </span>
              </div>
              <p class="mt-0.5 truncate text-[10px] text-slate-500">{{ lastMessagePreview(item) }}</p>
            </div>
          </button>
        </aside>

        <section class="flex min-h-0 flex-col">
          <template v-if="selectedThread">
            <div class="border-b border-slate-200 px-3 py-2">
              <p class="truncate text-xs font-medium text-slate-800">
                {{ selectedThread.peer.name || selectedThread.peer.username || t('directMessageFloat.unknownUser') }}
              </p>
            </div>

            <div ref="messageBoxRef" class="min-h-0 flex-1 overflow-y-auto bg-slate-50 p-2.5">
              <p v-if="loadingMessages" class="text-xs text-slate-500">{{ t('directMessageFloat.loading') }}</p>
              <p v-else-if="selectedThreadMessages.length === 0" class="text-xs text-slate-500">
                {{ t('directMessageFloat.emptyMessages') }}
              </p>
              <div v-else class="space-y-2">
                <div
                  v-for="message in selectedThreadMessages"
                  :key="`dm-float-message-${message.id}`"
                  class="flex"
                  :class="message.sender === currentUserIdNumber ? 'justify-end' : 'justify-start'"
                >
                  <div
                    class="max-w-[88%] rounded-lg border px-2.5 py-1.5"
                    :class="
                      message.sender === currentUserIdNumber
                        ? 'border-emerald-300 bg-emerald-50'
                        : 'border-slate-200 bg-white'
                    "
                  >
                    <p class="whitespace-pre-wrap break-words text-xs text-slate-800">{{ message.content }}</p>
                    <p class="mt-1 text-right text-[10px] text-slate-500">{{ formatTime(message.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="border-t border-slate-200 p-2">
              <textarea
                v-model="draft"
                class="h-16 w-full resize-none rounded border border-slate-300 px-2 py-1.5 text-xs"
                :placeholder="t('directMessageFloat.placeholder')"
                @keydown.enter.exact.prevent="handleSend"
              ></textarea>
              <div class="mt-1.5 flex justify-end">
                <button
                  class="rounded bg-slate-900 px-2.5 py-1 text-[11px] text-white hover:bg-slate-700 disabled:opacity-60"
                  :disabled="sending || !String(draft || '').trim()"
                  @click="handleSend"
                >
                  {{ sending ? t('directMessageFloat.sending') : t('directMessageFloat.send') }}
                </button>
              </div>
            </div>
          </template>

          <div v-else class="flex h-full items-center justify-center p-3 text-center text-xs text-slate-500">
            {{ t('directMessageFloat.emptyThreads') }}
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { MessageCircle } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { formatDateTimeByLocale } from '../utils/intl'
import {
  fetchDirectMessageThreadMessages,
  fetchDirectMessageThreads,
  markDirectMessageThreadRead,
  sendDirectMessage as sendDirectMessageApi,
  type DirectMessagePayload,
  type DirectMessageThreadSummaryPayload,
} from '../api/profile'

const authStore = useAuthStore()
const { t, locale } = useI18n()

const open = ref(false)
const loadingThreads = ref(false)
const loadingMessages = ref(false)
const sending = ref(false)
const panelError = ref('')
const threads = ref<DirectMessageThreadSummaryPayload[]>([])
const selectedThreadId = ref(0)
const draft = ref('')
const messagesByThread = ref<Record<number, DirectMessagePayload[]>>({})
const messageBoxRef = ref<HTMLElement | null>(null)

let pollTimer: ReturnType<typeof setInterval> | null = null

const currentUserIdNumber = computed(() => Number(authStore.user?.id || 0))

const selectedThread = computed(() => {
  return threads.value.find((item) => item.thread.id === selectedThreadId.value) || null
})

const selectedThreadMessages = computed(() => {
  return messagesByThread.value[selectedThreadId.value] || []
})

const totalUnreadMessages = computed(() => {
  return threads.value.reduce((sum, item) => sum + Number(item.unread_count || 0), 0)
})

const unreadBadge = computed(() => {
  if (totalUnreadMessages.value > 99) return '99+'
  return String(totalUnreadMessages.value)
})

const parseError = (error: any, fallbackKey: string): string => {
  const data = error?.response?.data
  if (typeof data?.detail === 'string' && data.detail.trim()) return data.detail.trim()
  if (typeof data === 'string' && data.trim()) return data.trim()
  return error?.message || t(fallbackKey)
}

const fallbackAvatar = (seed: unknown): string => {
  const safeSeed = encodeURIComponent(String(seed || 'dm-user').trim() || 'dm-user')
  return `https://api.dicebear.com/7.x/notionists/svg?seed=${safeSeed}`
}

const formatTime = (value: unknown): string => {
  const raw = String(value || '').trim()
  if (!raw) return '-'
  return formatDateTimeByLocale(raw, locale.value)
}

const lastMessagePreview = (item: DirectMessageThreadSummaryPayload): string => {
  const content = String(item?.last_message?.content || '').trim()
  if (!content) return t('directMessageFloat.noMessage')
  if (content.length <= 18) return content
  return `${content.slice(0, 18)}...`
}

const scrollMessageToBottom = async () => {
  await nextTick()
  if (!messageBoxRef.value) return
  messageBoxRef.value.scrollTop = messageBoxRef.value.scrollHeight
}

const loadThreads = async (silent = false) => {
  if (!authStore.isAuthenticated) return
  if (!silent) loadingThreads.value = true
  panelError.value = ''
  try {
    const payload = await fetchDirectMessageThreads(60)
    const list = Array.isArray(payload?.threads) ? payload.threads : []
    threads.value = list

    if (!selectedThreadId.value && list.length > 0) {
      selectedThreadId.value = list[0].thread.id
    } else if (selectedThreadId.value && !list.some((item) => item.thread.id === selectedThreadId.value)) {
      selectedThreadId.value = list[0]?.thread.id || 0
    }
  } catch (error: any) {
    panelError.value = parseError(error, 'directMessageFloat.loadFailed')
  } finally {
    if (!silent) loadingThreads.value = false
  }
}

const loadMessages = async (threadId: number, markRead = false, silent = false) => {
  if (!threadId) return
  if (!silent) loadingMessages.value = true
  try {
    const payload = await fetchDirectMessageThreadMessages(threadId, 120, markRead)
    const nextMessages = Array.isArray(payload?.messages) ? payload.messages : []
    messagesByThread.value = {
      ...messagesByThread.value,
      [threadId]: nextMessages,
    }
    if (markRead) {
      await markDirectMessageThreadRead(threadId)
      await loadThreads(true)
    }
    await scrollMessageToBottom()
  } catch (error: any) {
    panelError.value = parseError(error, 'directMessageFloat.messageLoadFailed')
  } finally {
    if (!silent) loadingMessages.value = false
  }
}

const selectThread = async (threadId: number) => {
  if (!threadId) return
  selectedThreadId.value = threadId
  draft.value = ''
  await loadMessages(threadId, true)
}

const handleSend = async () => {
  const threadId = Number(selectedThreadId.value || 0)
  const content = String(draft.value || '').trim()
  if (!threadId || !content || sending.value) return

  sending.value = true
  try {
    const created = await sendDirectMessageApi(threadId, content)
    const existing = messagesByThread.value[threadId] || []
    messagesByThread.value = {
      ...messagesByThread.value,
      [threadId]: [...existing, created],
    }
    draft.value = ''
    await scrollMessageToBottom()
    await loadThreads(true)
  } catch (error: any) {
    panelError.value = parseError(error, 'directMessageFloat.sendFailed')
  } finally {
    sending.value = false
  }
}

const refreshNow = async () => {
  await loadThreads()
  if (open.value && selectedThreadId.value) {
    await loadMessages(selectedThreadId.value, true)
  }
}

const togglePanel = async () => {
  open.value = !open.value
  if (!open.value) return
  await loadThreads()
  if (selectedThreadId.value) {
    await loadMessages(selectedThreadId.value, true)
  }
}

const poll = async () => {
  if (!authStore.isAuthenticated) return
  await loadThreads(true)
  if (open.value && selectedThreadId.value) {
    await loadMessages(selectedThreadId.value, true, true)
  }
}

const startPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
  pollTimer = setInterval(() => {
    void poll()
  }, 8000)
}

const stopPolling = () => {
  if (!pollTimer) return
  clearInterval(pollTimer)
  pollTimer = null
}

watch(
  () => authStore.user?.id,
  (userId) => {
    if (userId) {
      void loadThreads(true)
      startPolling()
      return
    }

    stopPolling()
    open.value = false
    threads.value = []
    selectedThreadId.value = 0
    messagesByThread.value = {}
  },
  { immediate: true }
)

onMounted(() => {
  if (authStore.isAuthenticated) {
    void loadThreads(true)
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>
