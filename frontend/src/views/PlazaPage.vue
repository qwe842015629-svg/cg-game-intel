<template>
  <div class="min-h-[calc(100vh-64px)] bg-slate-50 text-slate-900">
    <div class="container mx-auto space-y-5 px-4 py-8">
      <section class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 class="text-2xl font-bold">{{ t('squarePage.header.title') }}</h1>
            <p class="mt-1 text-sm text-slate-600">{{ t('squarePage.header.description') }}</p>
          </div>
          <button
            class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs hover:bg-slate-100"
            @click="refreshAll"
          >
            {{ t('squarePage.header.refreshButton') }}
          </button>
        </div>
        <p class="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          {{ t('squarePage.header.complianceNotice') }}
        </p>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1 text-sm">
          <button
            class="rounded px-3 py-1.5"
            :class="composerType === 'text' ? 'bg-white shadow-sm' : ''"
            @click="composerType = 'text'"
          >
            {{ t('squarePage.composer.tabs.text') }}
          </button>
          <button
            class="rounded px-3 py-1.5"
            :class="composerType === 'role_card' ? 'bg-white shadow-sm' : ''"
            @click="composerType = 'role_card'"
          >
            {{ t('squarePage.composer.tabs.roleCard') }}
          </button>
          <button
            class="rounded px-3 py-1.5"
            :class="composerType === 'novel_work' ? 'bg-white shadow-sm' : ''"
            @click="composerType = 'novel_work'"
          >
            {{ t('squarePage.composer.tabs.novelWork') }}
          </button>
        </div>

        <div class="mt-4 space-y-3">
          <div v-if="composerType === 'text'">
            <label class="text-xs text-slate-600">{{ t('squarePage.composer.textContentLabel') }}</label>
            <textarea
              v-model="draftContent"
              class="mt-1 h-28 w-full resize-none rounded-lg border border-slate-200 px-3 py-2 text-sm"
              :placeholder="t('squarePage.composer.textContentPlaceholder')"
            ></textarea>
          </div>

          <div v-else-if="composerType === 'role_card'" class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-xs text-slate-600">{{ t('squarePage.composer.roleSelectLabel') }}</label>
              <button class="text-xs text-slate-500 hover:text-slate-700" @click="loadRoleCards">
                {{ t('squarePage.composer.reloadRoles') }}
              </button>
            </div>
            <select
              v-model="selectedRoleId"
              class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            >
              <option value="">{{ t('squarePage.composer.roleSelectPlaceholder') }}</option>
              <option v-for="role in roleCards" :key="role.id" :value="role.id">
                {{ role.name || t('squarePage.composer.roleNameFallback') }}
              </option>
            </select>
            <div
              v-if="selectedRole"
              class="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600"
            >
              <p>
                <b class="text-slate-800">{{ t('squarePage.composer.roleNameLabel') }}</b>
                {{ selectedRole.name || t('squarePage.composer.roleNameFallback') }}
              </p>
              <p>
                <b class="text-slate-800">{{ t('squarePage.composer.roleGroupLabel') }}</b>
                {{ selectedRole.group || t('squarePage.composer.roleGroupFallback') }}
              </p>
              <p class="mt-1 whitespace-pre-wrap break-words">
                {{ compactText(selectedRole.description, 180) || t('squarePage.composer.roleDescriptionFallback') }}
              </p>
            </div>
          </div>

          <div v-else class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-xs text-slate-600">{{ t('squarePage.composer.workSelectLabel') }}</label>
              <button class="text-xs text-slate-500 hover:text-slate-700" @click="loadNovelWorks">
                {{ t('squarePage.composer.reloadWorks') }}
              </button>
            </div>
            <select
              v-model.number="selectedWorkId"
              class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            >
              <option :value="0">{{ t('squarePage.composer.workSelectPlaceholder') }}</option>
              <option v-for="work in novelWorks" :key="work.id" :value="work.id">
                {{ work.title || t('squarePage.composer.workTitleFallback') }} ({{ workStatusLabel(work) }})
              </option>
            </select>
            <div
              v-if="selectedWork"
              class="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600"
            >
              <p>
                <b class="text-slate-800">{{ t('squarePage.composer.workTitleLabel') }}</b>
                {{ selectedWork.title || t('squarePage.composer.workTitleFallback') }}
              </p>
              <p>
                <b class="text-slate-800">{{ t('squarePage.composer.workChaptersLabel') }}</b>
                {{ selectedWork.chapter_count }}
              </p>
              <p>
                <b class="text-slate-800">{{ t('squarePage.composer.workStatusLabel') }}</b>
                {{ workStatusLabel(selectedWork) }}
              </p>
              <p class="mt-1 whitespace-pre-wrap break-words">
                {{ compactText(selectedWork.summary, 180) || t('squarePage.composer.workSummaryFallback') }}
              </p>
            </div>
          </div>

          <div>
            <label class="text-xs text-slate-600">{{ t('squarePage.composer.captionLabel') }}</label>
            <input
              v-model="draftCaption"
              class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
              :placeholder="t('squarePage.composer.captionPlaceholder')"
            />
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              class="rounded-lg bg-slate-900 px-4 py-2 text-sm text-white hover:bg-slate-700 disabled:opacity-60"
              :disabled="publishing"
              @click="submitPost"
            >
              {{ publishing ? t('squarePage.composer.publishingButton') : t('squarePage.composer.publishButton') }}
            </button>
            <button
              class="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-100"
              :disabled="publishing"
              @click="resetComposer"
            >
              {{ t('squarePage.composer.clearButton') }}
            </button>
          </div>

          <p v-if="composerError" class="text-xs text-rose-600">{{ composerError }}</p>
          <p v-if="composerInfo" class="text-xs text-emerald-700">{{ composerInfo }}</p>
        </div>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 class="text-lg font-semibold">{{ t('squarePage.feed.title') }}</h2>
          <div class="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1 text-xs">
            <button
              class="rounded px-2.5 py-1.5"
              :class="postFilter === 'all' ? 'bg-white shadow-sm' : ''"
              @click="postFilter = 'all'"
            >
              {{ t('squarePage.feed.filters.all') }}
            </button>
            <button
              class="rounded px-2.5 py-1.5"
              :class="postFilter === 'text' ? 'bg-white shadow-sm' : ''"
              @click="postFilter = 'text'"
            >
              {{ t('squarePage.feed.filters.text') }}
            </button>
            <button
              class="rounded px-2.5 py-1.5"
              :class="postFilter === 'role_card' ? 'bg-white shadow-sm' : ''"
              @click="postFilter = 'role_card'"
            >
              {{ t('squarePage.feed.filters.roleCard') }}
            </button>
            <button
              class="rounded px-2.5 py-1.5"
              :class="postFilter === 'novel_work' ? 'bg-white shadow-sm' : ''"
              @click="postFilter = 'novel_work'"
            >
              {{ t('squarePage.feed.filters.novelWork') }}
            </button>
          </div>
        </div>

        <p v-if="feedError" class="mb-3 text-xs text-rose-600">{{ feedError }}</p>
        <p v-if="loadingPosts" class="text-sm text-slate-500">{{ t('squarePage.feed.loading') }}</p>
        <div
          v-else-if="filteredPosts.length === 0"
          class="rounded-lg border border-dashed border-slate-300 px-4 py-8 text-center text-sm text-slate-500"
        >
          {{ t('squarePage.feed.empty') }}
        </div>

        <div v-else class="space-y-3">
          <article
            v-for="post in filteredPosts"
            :key="post.id"
            class="rounded-xl border border-slate-200 bg-slate-50 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <router-link
                :to="authorProfileTo(post)"
                class="flex min-w-0 items-center gap-2 transition-opacity hover:opacity-90"
              >
                <img
                  :src="post.author_avatar || fallbackAvatar(post.author_name)"
                  class="h-9 w-9 rounded-full border border-slate-200 object-cover"
                  :alt="t('squarePage.feed.authorAvatarAlt')"
                />
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold text-slate-800">
                    {{ post.author_name || t('squarePage.feed.anonymousUser') }}
                  </p>
                  <p class="text-[11px] text-slate-500">{{ formatDate(post.created_at) }}</p>
                </div>
              </router-link>
              <div class="flex items-center gap-2">
                <span
                  class="rounded border border-slate-200 bg-white px-2 py-1 text-[11px] text-slate-600"
                >
                  {{ postTypeLabel(post.post_type) }}
                </span>
                <button
                  v-if="post.is_owner"
                  class="text-xs text-rose-600 hover:text-rose-700"
                  @click="removePost(post)"
                >
                  {{ t('squarePage.feed.deleteButton') }}
                </button>
              </div>
            </div>

            <div
              v-if="post.post_type === 'role_card'"
              class="mt-3 rounded-lg border border-indigo-200 bg-indigo-50 p-3"
            >
              <p class="text-xs font-semibold text-indigo-700">{{ t('squarePage.feed.roleCardSynced') }}</p>
              <div class="mt-2 flex items-center gap-2">
                <img
                  :src="String(post.source_data?.avatar || post.author_avatar || fallbackAvatar(post.source_data?.name || post.author_name))"
                  class="h-10 w-10 rounded-full border border-indigo-200 object-cover"
                  :alt="t('squarePage.feed.roleCardAvatarAlt')"
                />
                <div>
                  <p class="text-sm font-medium text-indigo-900">
                    {{ String(post.source_data?.name || t('squarePage.composer.roleNameFallback')) }}
                  </p>
                  <p class="text-[11px] text-indigo-700">
                    {{ String(post.source_data?.group || t('squarePage.composer.roleGroupFallback')) }}
                  </p>
                </div>
              </div>
            </div>

            <div
              v-if="post.post_type === 'novel_work'"
              class="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3"
            >
              <p class="text-xs font-semibold text-emerald-700">{{ t('squarePage.feed.novelWorkSynced') }}</p>
              <div class="mt-2 flex gap-3">
                <img
                  v-if="String(post.source_data?.cover_image || '').trim()"
                  :src="String(post.source_data?.cover_image)"
                  class="h-16 w-12 rounded border border-emerald-200 object-cover"
                  :alt="t('squarePage.feed.novelWorkCoverAlt')"
                />
                <div class="min-w-0">
                  <p class="truncate text-sm font-medium text-emerald-900">
                    {{ String(post.source_data?.title || t('squarePage.composer.workTitleFallback')) }}
                  </p>
                  <p class="text-[11px] text-emerald-700">
                    {{
                      t('squarePage.feed.novelMeta', {
                        chapters: Number(post.source_data?.chapter_count || 0),
                        status: resolveSourceWorkStatus(post.source_data?.status),
                      })
                    }}
                  </p>
                </div>
              </div>
            </div>

            <p class="mt-3 whitespace-pre-wrap break-words text-sm text-slate-700">
              {{ post.content || t('squarePage.feed.noContent') }}
            </p>

            <div class="mt-3 flex items-center gap-3 text-xs">
              <button
                class="rounded border px-2.5 py-1.5"
                :class="
                  [
                    post.liked_by_me
                      ? 'border-rose-300 bg-rose-50 text-rose-700'
                      : 'border-slate-300 bg-white text-slate-700',
                    likeSyncing[post.id] ? 'cursor-not-allowed opacity-60' : '',
                  ]
                "
                :disabled="Boolean(likeSyncing[post.id])"
                @click="onToggleLike(post)"
              >
                {{
                  post.liked_by_me
                    ? t('squarePage.feed.likedButton', { count: post.like_count })
                    : t('squarePage.feed.likeButton', { count: post.like_count })
                }}
              </button>
              <button
                class="rounded border border-slate-300 bg-white px-2.5 py-1.5 text-slate-700"
                @click="toggleComments(post.id)"
              >
                {{ t('squarePage.feed.commentButton', { count: post.comment_count }) }}
              </button>
            </div>

            <div v-if="isCommentsOpen(post.id)" class="mt-3 rounded-lg border border-slate-200 bg-white p-3">
              <div v-if="post.comments.length === 0" class="text-xs text-slate-500">
                {{ t('squarePage.feed.noComments') }}
              </div>
              <div v-else class="space-y-2">
                <div
                  v-for="comment in post.comments"
                  :key="comment.id"
                  class="rounded border border-slate-100 bg-slate-50 px-2.5 py-2"
                >
                  <div class="flex items-center justify-between gap-2">
                    <router-link
                      v-if="commentProfileTo(comment)"
                      :to="commentProfileTo(comment) || '/plaza'"
                      class="text-xs font-medium text-slate-700 hover:underline"
                    >
                      {{ comment.author_name || t('squarePage.feed.anonymousUser') }}
                    </router-link>
                    <p v-else class="text-xs font-medium text-slate-700">
                      {{ comment.author_name || t('squarePage.feed.anonymousUser') }}
                    </p>
                    <div class="flex items-center gap-2">
                      <span class="text-[11px] text-slate-500">{{ formatDate(comment.created_at) }}</span>
                      <button
                        v-if="comment.is_owner"
                        class="text-[11px] text-rose-600 hover:text-rose-700"
                        @click="removeComment(post, comment.id)"
                      >
                        {{ t('squarePage.feed.deleteButton') }}
                      </button>
                    </div>
                  </div>
                  <p class="mt-1 whitespace-pre-wrap break-words text-xs text-slate-700">{{ comment.content }}</p>
                </div>
              </div>

              <div class="mt-2 space-y-2">
                <textarea
                  v-model="commentDrafts[post.id]"
                  class="min-h-[80px] w-full resize-y rounded border border-slate-200 px-3 py-2 text-xs"
                  :placeholder="t('squarePage.feed.commentPlaceholder')"
                ></textarea>
                <div class="flex justify-end">
                  <button
                    class="h-9 rounded bg-slate-900 px-3 text-xs text-white hover:bg-slate-700 disabled:opacity-60"
                    :disabled="commentSubmitting[post.id]"
                    @click="submitComment(post)"
                  >
                    {{
                      commentSubmitting[post.id]
                        ? t('squarePage.feed.commentSending')
                        : t('squarePage.feed.commentSend')
                    }}
                  </button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import client from '../api/client'
import {
  createPlazaComment,
  createPlazaPost,
  deletePlazaComment,
  deletePlazaPost,
  ensurePlazaClientId,
  fetchPlazaPosts,
  togglePlazaLike,
  type PlazaComment,
  type PlazaPost,
  type PlazaPostType,
} from '../api/plaza'
import { useAuthStore } from '../stores/auth'
import {
  guardUsagePolicyContent,
  isUsagePolicyViolationError,
  openUsagePolicyDialog,
} from '../utils/usagePolicy'

interface TavernRoleCard {
  id: string
  name: string
  description: string
  group: string
  avatar: string
  firstMessage: string
  systemPrompt: string
}

interface NovelWorkItem {
  id: number
  title: string
  summary: string
  cover_image: string
  chapter_count: number
  completion_status: 'draft' | 'completed'
}

interface LikeSnapshot {
  liked: boolean
  like_count: number
}

const { t, locale } = useI18n()
const authStore = useAuthStore()
const plazaClientId = ensurePlazaClientId()

const composerType = ref<PlazaPostType>('text')
const draftContent = ref('')
const draftCaption = ref('')
const selectedRoleId = ref('')
const selectedWorkId = ref(0)
const publishing = ref(false)
const composerError = ref('')
const composerInfo = ref('')

const postFilter = ref<'all' | PlazaPostType>('all')
const loadingPosts = ref(false)
const feedError = ref('')
const posts = ref<PlazaPost[]>([])

const roleCards = ref<TavernRoleCard[]>([])
const novelWorks = ref<NovelWorkItem[]>([])

const commentDrafts = ref<Record<number, string>>({})
const commentSubmitting = ref<Record<number, boolean>>({})
const openedComments = ref<Record<number, boolean>>({})
const likeSnapshots = ref<Record<number, LikeSnapshot>>({})
const likeDebounceTimers = ref<Record<number, number>>({})
const likeSyncing = ref<Record<number, boolean>>({})

const TAVERN_CUSTOM_PERSONAS_KEY = 'cypher_tavern_custom_personas'
const NOVEL_CLIENT_KEY = 'novel_story_client_id'
const LIKE_DEBOUNCE_MS = 320

const LOCAL_BLOCKED_TERMS = [
  'porn',
  'nsfw',
  'nude',
  'hentai',
  'sex',
  'gambling',
  'casino',
  'betting',
  'drug',
  'cocaine',
  'heroin',
  'meth',
  'terror',
  'explosive',
  'gun trafficking',
  'human trafficking',
  'money laundering',
  '\u8272\u60c5',
  '\u8d4c\u535a',
  '\u6bd2\u54c1',
  '\u5438\u6bd2',
  '\u6050\u6016\u88ad\u51fb',
  '\u8bc8\u9a97',
  '\u6d17\u94b1',
  '\u4eba\u53e3\u8d29\u5356',
]

const selectedRole = computed(() => roleCards.value.find((item) => item.id === selectedRoleId.value) || null)
const selectedWork = computed(() => novelWorks.value.find((item) => item.id === selectedWorkId.value) || null)
const filteredPosts = computed(() => {
  if (postFilter.value === 'all') return posts.value
  return posts.value.filter((item) => item.post_type === postFilter.value)
})

const normalizeText = (value: unknown) => String(value || '').trim()

function parseOwnerUserId(ownerKey: unknown): number | null {
  const matched = normalizeText(ownerKey).match(/^user:(\d+)$/)
  if (!matched) return null

  const parsed = Number(matched[1])
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null
}

function resolvePostAuthorId(post: PlazaPost): number | null {
  const direct = Number((post as any).author_id || 0)
  if (Number.isInteger(direct) && direct > 0) return direct
  return parseOwnerUserId(post.owner_key)
}

function authorProfileTo(post: PlazaPost): string {
  const authorId = resolvePostAuthorId(post)
  return authorId ? `/user/${authorId}` : '/plaza'
}

function resolveCommentAuthorId(comment: PlazaComment): number | null {
  const direct = Number((comment as any).author_id || 0)
  if (Number.isInteger(direct) && direct > 0) return direct
  return parseOwnerUserId(comment.owner_key)
}

function commentProfileTo(comment: PlazaComment): string | null {
  const authorId = resolveCommentAuthorId(comment)
  return authorId ? `/user/${authorId}` : null
}

function compactText(value: unknown, max = 180): string {
  const text = normalizeText(value).replace(/\s+/g, ' ')
  if (!text) return ''
  return text.length > max ? `${text.slice(0, max)}...` : text
}

function postTypeLabel(type: PlazaPostType): string {
  if (type === 'role_card') return t('squarePage.feed.filters.roleCard')
  if (type === 'novel_work') return t('squarePage.feed.filters.novelWork')
  return t('squarePage.feed.filters.text')
}

function workStatusLabel(work: NovelWorkItem): string {
  return work.completion_status === 'completed'
    ? t('squarePage.workStatus.completed')
    : t('squarePage.workStatus.draft')
}

function resolveSourceWorkStatus(value: unknown): string {
  const raw = normalizeText(value)
  if (!raw) return t('squarePage.workStatus.draft')

  const lowered = raw.toLowerCase()
  if (['completed', 'complete', 'finished', 'done'].includes(lowered)) {
    return t('squarePage.workStatus.completed')
  }
  if (['draft', 'ongoing', 'serializing', 'in_progress'].includes(lowered)) {
    return t('squarePage.workStatus.draft')
  }
  if (['\u5df2\u5b8c\u7ed3', '\u5b8c\u7ed3', '\u5df2\u5b8c\u6210'].includes(raw)) {
    return t('squarePage.workStatus.completed')
  }
  if (['\u521b\u4f5c\u4e2d', '\u8fde\u8f7d\u4e2d', '\u8349\u7a3f'].includes(raw)) {
    return t('squarePage.workStatus.draft')
  }

  return raw
}

function fallbackAvatar(seed: unknown): string {
  const safeSeed = encodeURIComponent(normalizeText(seed) || 'plaza-user')
  return `https://api.dicebear.com/7.x/notionists/svg?seed=${safeSeed}`
}

function formatDate(value: string): string {
  const raw = normalizeText(value)
  if (!raw) return t('squarePage.common.dash')

  const date = new Date(raw)
  if (Number.isNaN(date.getTime())) return raw

  const localeCode = normalizeText(locale.value) || 'en-US'
  try {
    return date.toLocaleString(localeCode, { hour12: false })
  } catch {
    return date.toLocaleString('en-US', { hour12: false })
  }
}

function getBlockedTerm(input: string): string {
  const lowered = normalizeText(input).toLowerCase()
  if (!lowered) return ''
  for (const term of LOCAL_BLOCKED_TERMS) {
    if (lowered.includes(term.toLowerCase())) return term
  }
  return ''
}

function extractErrorMessage(error: any): string {
  const data = error?.response?.data
  if (!data) return error?.message || t('squarePage.errors.requestFailed')
  if (typeof data === 'string') return data
  if (typeof data?.detail === 'string') return data.detail
  if (typeof data?.message === 'string') return data.message

  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value) && value.length > 0) return `${key}: ${String(value[0])}`
    if (typeof value === 'string') return `${key}: ${value}`
  }
  return error?.message || t('squarePage.errors.requestFailed')
}

function ensureNovelClientId(): string {
  try {
    const existing = normalizeText(localStorage.getItem(NOVEL_CLIENT_KEY)).slice(0, 64)
    if (existing) return existing
    localStorage.setItem(NOVEL_CLIENT_KEY, plazaClientId)
    return plazaClientId
  } catch {
    return plazaClientId
  }
}

function normalizePost(raw: any): PlazaPost {
  const comments = Array.isArray(raw?.comments)
    ? raw.comments.map((item: any) => ({
        ...item,
        author_id: Number(item?.author_id || 0) || parseOwnerUserId(item?.owner_key),
      }))
    : []

  return {
    ...raw,
    author_id: Number(raw?.author_id || 0) || parseOwnerUserId(raw?.owner_key),
    comments,
    like_count: Number(raw?.like_count || 0),
    comment_count: Number(raw?.comment_count || 0),
    liked_by_me: Boolean(raw?.liked_by_me),
    is_owner: Boolean(raw?.is_owner),
  }
}

async function loadPosts() {
  loadingPosts.value = true
  feedError.value = ''
  try {
    const payload = await fetchPlazaPosts(plazaClientId)
    posts.value = payload.map((item) => normalizePost(item))
  } catch (error: any) {
    feedError.value = extractErrorMessage(error) || t('squarePage.errors.feedLoadFailed')
  } finally {
    loadingPosts.value = false
  }
}

function loadRoleCards() {
  try {
    const raw = localStorage.getItem(TAVERN_CUSTOM_PERSONAS_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    if (!Array.isArray(parsed)) {
      roleCards.value = []
      return
    }

    roleCards.value = parsed.map((item: any, index: number) => ({
      id: normalizeText(item?.id) || `role_${index}_${Date.now()}`,
      name: normalizeText(item?.name) || t('squarePage.composer.roleNameFallback'),
      description: normalizeText(item?.description),
      group: normalizeText(item?.group) || t('squarePage.composer.roleGroupFallback'),
      avatar: normalizeText(item?.avatar),
      firstMessage: normalizeText(item?.firstMessage),
      systemPrompt: normalizeText(item?.systemPrompt),
    }))
  } catch {
    roleCards.value = []
  }
}

async function loadNovelWorks() {
  try {
    const payload: any = await client.get('/novel-works/', {
      params: { client_id: ensureNovelClientId() },
    })
    novelWorks.value = (Array.isArray(payload) ? payload : [])
      .map((item: any) => ({
        id: Number(item?.id || 0),
        title: normalizeText(item?.title),
        summary: normalizeText(item?.summary),
        cover_image: normalizeText(item?.cover_image),
        chapter_count: Array.isArray(item?.chapters) ? item.chapters.length : 0,
        completion_status:
          String(item?.extra_meta?.completion_status || '').toLowerCase() === 'completed'
            ? 'completed'
            : 'draft',
      }))
      .filter((item: NovelWorkItem) => item.id > 0)
  } catch {
    novelWorks.value = []
  }
}

function resetComposer() {
  draftContent.value = ''
  draftCaption.value = ''
  composerError.value = ''
  composerInfo.value = ''
}

async function submitPost() {
  composerError.value = ''
  composerInfo.value = ''

  let content = ''
  let sourceRef = ''
  let sourceData: Record<string, any> = {}

  if (composerType.value === 'text') {
    content = normalizeText(draftContent.value)
    if (!content) {
      composerError.value = t('squarePage.errors.textRequired')
      return
    }
  }

  if (composerType.value === 'role_card') {
    if (!selectedRole.value) {
      composerError.value = t('squarePage.errors.roleRequired')
      return
    }
    sourceRef = selectedRole.value.id
    sourceData = {
      source: 'tavern_role_card',
      id: selectedRole.value.id,
      name: selectedRole.value.name,
      description: selectedRole.value.description,
      group: selectedRole.value.group,
      avatar: selectedRole.value.avatar,
      firstMessage: selectedRole.value.firstMessage,
    }
    content =
      normalizeText(draftCaption.value) ||
      t('squarePage.composer.autoContent.roleCard', {
        name: selectedRole.value.name || t('squarePage.composer.roleNameFallback'),
      })
  }

  if (composerType.value === 'novel_work') {
    if (!selectedWork.value) {
      composerError.value = t('squarePage.errors.workRequired')
      return
    }
    sourceRef = String(selectedWork.value.id)
    sourceData = {
      source: 'novel_work',
      id: selectedWork.value.id,
      title: selectedWork.value.title,
      summary: selectedWork.value.summary,
      chapter_count: selectedWork.value.chapter_count,
      status: workStatusLabel(selectedWork.value),
      cover_image: selectedWork.value.cover_image,
    }
    content =
      normalizeText(draftCaption.value) ||
      t('squarePage.composer.autoContent.novelWork', {
        title: selectedWork.value.title || t('squarePage.composer.workTitleFallback'),
      })
  }

  const blockTerm = getBlockedTerm(`${content}\n${JSON.stringify(sourceData)}`)
  if (blockTerm) {
    composerError.value = t('squarePage.errors.blockedContent', { term: blockTerm })
    return
  }

  try {
    guardUsagePolicyContent(
      {
        content,
        source_data: sourceData,
      },
      'publish'
    )
  } catch (error) {
    if (isUsagePolicyViolationError(error)) {
      composerError.value = error.message
      openUsagePolicyDialog(error.message)
      return
    }
    throw error
  }

  publishing.value = true
  try {
    const created = await createPlazaPost({
      client_id: plazaClientId,
      author_name: normalizeText(authStore.user?.name) || t('squarePage.common.visitor'),
      author_avatar:
        normalizeText(authStore.user?.avatar) || fallbackAvatar(authStore.user?.name || plazaClientId),
      content: content.slice(0, 1200),
      post_type: composerType.value,
      source_ref: sourceRef.slice(0, 128),
      source_data: sourceData,
    })
    posts.value = [normalizePost(created), ...posts.value]
    resetComposer()
    composerInfo.value = t('squarePage.composer.publishSuccess')
  } catch (error: any) {
    composerError.value = extractErrorMessage(error) || t('squarePage.errors.publishFailed')
  } finally {
    publishing.value = false
  }
}

async function removePost(post: PlazaPost) {
  if (!window.confirm(t('squarePage.feed.confirmDeletePost'))) return

  feedError.value = ''
  try {
    await deletePlazaPost(post.id, plazaClientId)
    posts.value = posts.value.filter((item) => item.id !== post.id)
  } catch (error: any) {
    feedError.value = extractErrorMessage(error) || t('squarePage.errors.deletePostFailed')
  }
}

async function onToggleLike(post: PlazaPost) {
  const postId = post.id
  if (likeSyncing.value[postId]) return

  if (!likeSnapshots.value[postId]) {
    likeSnapshots.value = {
      ...likeSnapshots.value,
      [postId]: {
        liked: Boolean(post.liked_by_me),
        like_count: Number(post.like_count || 0),
      },
    }
  }

  const nextLiked = !post.liked_by_me
  post.liked_by_me = nextLiked
  post.like_count = Math.max(0, Number(post.like_count || 0) + (nextLiked ? 1 : -1))

  const timerId = likeDebounceTimers.value[postId]
  if (typeof timerId === 'number') {
    window.clearTimeout(timerId)
  }

  likeDebounceTimers.value = {
    ...likeDebounceTimers.value,
    [postId]: window.setTimeout(() => {
      void flushLikeChange(postId)
    }, LIKE_DEBOUNCE_MS),
  }
}

async function flushLikeChange(postId: number) {
  const post = posts.value.find((item) => item.id === postId)
  const snapshot = likeSnapshots.value[postId]
  const timerId = likeDebounceTimers.value[postId]

  if (typeof timerId === 'number') {
    window.clearTimeout(timerId)
  }
  const timers = { ...likeDebounceTimers.value }
  delete timers[postId]
  likeDebounceTimers.value = timers

  if (!post || !snapshot) {
    return
  }

  if (post.liked_by_me === snapshot.liked) {
    const snapshots = { ...likeSnapshots.value }
    delete snapshots[postId]
    likeSnapshots.value = snapshots
    return
  }

  likeSyncing.value = { ...likeSyncing.value, [postId]: true }
  try {
    const result = await togglePlazaLike(postId, plazaClientId)
    post.like_count = Number(result.like_count || 0)
    post.liked_by_me = Boolean(result.liked)
  } catch (error: any) {
    post.like_count = snapshot.like_count
    post.liked_by_me = snapshot.liked
    feedError.value = extractErrorMessage(error) || t('squarePage.errors.likeFailed')
  } finally {
    const snapshots = { ...likeSnapshots.value }
    delete snapshots[postId]
    likeSnapshots.value = snapshots

    const syncing = { ...likeSyncing.value }
    delete syncing[postId]
    likeSyncing.value = syncing
  }
}

function toggleComments(postId: number) {
  openedComments.value = {
    ...openedComments.value,
    [postId]: !openedComments.value[postId],
  }
}

function isCommentsOpen(postId: number): boolean {
  return Boolean(openedComments.value[postId])
}

async function submitComment(post: PlazaPost) {
  const current = normalizeText(commentDrafts.value[post.id])
  if (!current) return

  const blockTerm = getBlockedTerm(current)
  if (blockTerm) {
    feedError.value = t('squarePage.errors.blockedComment', { term: blockTerm })
    return
  }

  try {
    guardUsagePolicyContent(current, 'publish')
  } catch (error) {
    if (isUsagePolicyViolationError(error)) {
      feedError.value = error.message
      openUsagePolicyDialog(error.message)
      return
    }
    throw error
  }

  commentSubmitting.value = { ...commentSubmitting.value, [post.id]: true }
  feedError.value = ''
  try {
    const created = await createPlazaComment(post.id, {
      client_id: plazaClientId,
      author_name: normalizeText(authStore.user?.name) || t('squarePage.common.visitor'),
      author_avatar:
        normalizeText(authStore.user?.avatar) || fallbackAvatar(authStore.user?.name || plazaClientId),
      content: current.slice(0, 500),
    })
    const normalizedCreated: PlazaComment = {
      ...created,
      author_id: Number((created as any)?.author_id || 0) || parseOwnerUserId((created as any)?.owner_key),
    }
    post.comments = [...(Array.isArray(post.comments) ? post.comments : []), normalizedCreated]
    post.comment_count = post.comments.length
    commentDrafts.value = { ...commentDrafts.value, [post.id]: '' }
    openedComments.value = { ...openedComments.value, [post.id]: true }
  } catch (error: any) {
    feedError.value = extractErrorMessage(error) || t('squarePage.errors.commentFailed')
  } finally {
    commentSubmitting.value = { ...commentSubmitting.value, [post.id]: false }
  }
}

async function removeComment(post: PlazaPost, commentId: number) {
  if (!window.confirm(t('squarePage.feed.confirmDeleteComment'))) return

  feedError.value = ''
  try {
    const result = await deletePlazaComment(post.id, commentId, plazaClientId)
    post.comments = (post.comments || []).filter((item) => item.id !== commentId)
    post.comment_count = Number(result.comment_count || post.comments.length)
  } catch (error: any) {
    feedError.value = extractErrorMessage(error) || t('squarePage.errors.deleteCommentFailed')
  }
}

async function refreshAll() {
  await Promise.all([loadPosts(), loadNovelWorks()])
  loadRoleCards()
}

onMounted(async () => {
  loadRoleCards()
  await Promise.all([loadPosts(), loadNovelWorks()])

  if (!selectedRoleId.value && roleCards.value.length > 0) {
    selectedRoleId.value = roleCards.value[0].id
  }
  if (!selectedWorkId.value && novelWorks.value.length > 0) {
    selectedWorkId.value = novelWorks.value[0].id
  }
})

onBeforeUnmount(() => {
  Object.values(likeDebounceTimers.value).forEach((timerId) => {
    if (typeof timerId === 'number') {
      window.clearTimeout(timerId)
    }
  })
})
</script>

