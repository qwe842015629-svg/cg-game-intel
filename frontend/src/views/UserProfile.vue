<template>
  <div class="min-h-screen bg-slate-50 pt-16 pb-10">
    <div class="container mx-auto max-w-6xl space-y-5 px-4">
      <section v-if="loading" class="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        {{ t('userProfile.loading') }}
      </section>

      <section
        v-else-if="pageError"
        class="rounded-xl border border-rose-200 bg-rose-50 p-6"
      >
        <p class="text-sm text-rose-700">{{ pageError }}</p>
        <button
          class="mt-3 rounded-lg border border-rose-300 bg-white px-3 py-1.5 text-xs text-rose-700 hover:bg-rose-100"
          @click="loadProfile()"
        >
          {{ t('userProfile.actions.retry') }}
        </button>
      </section>

      <template v-else-if="profileData">
        <section class="rounded-xl border border-slate-200 bg-white p-6">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div class="flex items-start gap-4">
              <img
                :src="avatarSrc"
                :alt="t('userProfile.avatarAlt')"
                class="h-16 w-16 rounded-full border border-slate-200 object-cover"
              />
              <div class="min-w-0">
                <h1 class="truncate text-2xl font-bold text-slate-900">{{ profileData.user.name }}</h1>
                <p class="text-sm text-slate-500">@{{ profileData.user.username }}</p>
                <p class="mt-2 whitespace-pre-wrap break-words text-sm text-slate-700">
                  {{ profileData.user.bio || t('userProfile.bioEmpty') }}
                </p>
                <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                  <span class="rounded-md border border-slate-200 bg-slate-100 px-2 py-1">
                    {{ t('userProfile.counts.followers', { count: profileData.follower_count }) }}
                  </span>
                  <span class="rounded-md border border-slate-200 bg-slate-100 px-2 py-1">
                    {{ t('userProfile.counts.following', { count: profileData.following_count }) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <template v-if="isOwner">
                <button
                  class="rounded-lg border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:bg-slate-100"
                  @click="openRelationModal('following')"
                >
                  {{ t('userProfile.relationships.followingEntry') }}
                </button>
                <button
                  class="rounded-lg border border-slate-300 px-3 py-2 text-xs text-slate-700 hover:bg-slate-100"
                  @click="openRelationModal('followers')"
                >
                  {{ t('userProfile.relationships.followersEntry') }}
                </button>
              </template>
              <template v-else>
                <button
                  class="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-xs text-white disabled:opacity-60"
                  :class="isFollowing ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-blue-600 hover:bg-blue-700'"
                  :disabled="actionLoading.follow"
                  @click="toggleFollow"
                >
                  <UserCheck v-if="isFollowing" class="h-3.5 w-3.5" />
                  <UserPlus v-else class="h-3.5 w-3.5" />
                  {{ isFollowing ? t('userProfile.actions.following') : t('userProfile.actions.follow') }}
                </button>
                <button
                  class="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-700 hover:bg-slate-100 disabled:opacity-60"
                  :disabled="actionLoading.dm"
                  @click="startDirectMessage"
                >
                  <MessageCircle class="h-3.5 w-3.5" />
                  {{ t('userProfile.actions.directMessage') }}
                </button>
              </template>
            </div>
          </div>
        </section>

        <section v-if="isOwner" class="rounded-xl border border-slate-200 bg-white p-6">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-base font-semibold text-slate-900">{{ t('userProfile.globalVisibility.title') }}</h2>
              <p class="mt-1 text-xs text-slate-500">{{ t('userProfile.globalVisibility.description') }}</p>
            </div>
            <select
              v-model.number="globalVisibility"
              class="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
              :disabled="actionLoading.globalVisibility"
              @change="onGlobalVisibilityChange"
            >
              <option
                v-for="option in visibilityOptions"
                :key="`global-visibility-${option.value}`"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
        </section>

        <section class="rounded-xl border border-slate-200 bg-white p-6">
          <div class="mb-4 flex items-center gap-2">
            <BookOpenText class="h-5 w-5 text-indigo-600" />
            <h2 class="text-lg font-semibold text-slate-900">{{ t('userProfile.novels.title') }}</h2>
          </div>

          <div
            v-if="profileData.novels.length === 0"
            class="rounded-lg border border-dashed border-slate-300 px-4 py-6 text-sm text-slate-500"
          >
            {{ t('userProfile.novels.empty') }}
          </div>
          <div v-else class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <article
              v-for="novel in profileData.novels"
              :key="`novel-${novel.id}`"
              class="cursor-pointer rounded-lg border border-slate-200 bg-slate-50 p-3 transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              role="button"
              tabindex="0"
              @click="openNovelPreview(novel)"
              @keydown.enter.prevent="openNovelPreview(novel)"
              @keydown.space.prevent="openNovelPreview(novel)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="truncate text-sm font-semibold text-slate-900">
                    {{ novelDisplayTitle(novel) }}
                  </h3>
                  <p class="mt-1 text-[11px] text-slate-500">
                    {{ t('userProfile.updatedAt', { time: formatDate(novel.updated_at) }) }}
                  </p>
                </div>
                <template v-if="isOwner">
                  <select
                    v-model.number="novel.visibility"
                    class="rounded border border-slate-300 bg-white px-2 py-1 text-xs"
                    :disabled="Boolean(novelVisibilityLoading[novel.id])"
                    @click.stop
                    @change="onNovelVisibilityChange(novel)"
                  >
                    <option
                      v-for="option in visibilityOptions"
                      :key="`novel-${novel.id}-visibility-${option.value}`"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </template>
                <template v-else>
                  <span class="rounded border border-slate-300 bg-white px-2 py-1 text-[11px] text-slate-600">
                    {{ visibilityLabel(novel.visibility) }}
                  </span>
                </template>
              </div>
              <p class="mt-2 line-clamp-3 whitespace-pre-wrap break-words text-xs text-slate-700">
                {{ novelDisplaySummary(novel) }}
              </p>
            </article>
          </div>
        </section>

        <section class="rounded-xl border border-slate-200 bg-white p-6">
          <div class="mb-4 flex items-center gap-2">
            <ScrollText class="h-5 w-5 text-emerald-600" />
            <h2 class="text-lg font-semibold text-slate-900">{{ t('userProfile.characters.title') }}</h2>
          </div>

          <div
            v-if="profileData.characters.length === 0"
            class="rounded-lg border border-dashed border-slate-300 px-4 py-6 text-sm text-slate-500"
          >
            {{ t('userProfile.characters.empty') }}
          </div>
          <div v-else class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <article
              v-for="character in profileData.characters"
              :key="`character-${character.id}`"
              class="cursor-pointer rounded-lg border border-slate-200 bg-slate-50 p-3 transition hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
              role="button"
              tabindex="0"
              @click="openCharacterPreview(character)"
              @keydown.enter.prevent="openCharacterPreview(character)"
              @keydown.space.prevent="openCharacterPreview(character)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex min-w-0 items-start gap-2">
                  <img
                    :src="character.avatar || fallbackAvatar(character.name)"
                    :alt="t('userProfile.characters.avatarAlt')"
                    class="h-10 w-10 rounded-full border border-slate-200 object-cover"
                  />
                  <div class="min-w-0">
                    <h3 class="truncate text-sm font-semibold text-slate-900">
                      {{ character.name || t('userProfile.characters.untitled') }}
                    </h3>
                    <p class="mt-1 text-[11px] text-slate-500">
                      {{ t('userProfile.updatedAt', { time: formatDate(character.updated_at) }) }}
                    </p>
                  </div>
                </div>
                <template v-if="isOwner">
                  <select
                    v-model.number="character.visibility"
                    class="rounded border border-slate-300 bg-white px-2 py-1 text-xs"
                    :disabled="Boolean(characterVisibilityLoading[character.id])"
                    @click.stop
                    @change="onCharacterVisibilityChange(character)"
                  >
                    <option
                      v-for="option in visibilityOptions"
                      :key="`character-${character.id}-visibility-${option.value}`"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </template>
                <template v-else>
                  <span class="rounded border border-slate-300 bg-white px-2 py-1 text-[11px] text-slate-600">
                    {{ visibilityLabel(character.visibility) }}
                  </span>
                </template>
              </div>
              <p class="mt-2 line-clamp-3 whitespace-pre-wrap break-words text-xs text-slate-700">
                {{ characterDisplayDescription(character) }}
              </p>
            </article>
          </div>
        </section>
      </template>
    </div>

    <AuthDialog v-model="showAuthDialog" />

    <div
      v-if="relationModal.open"
      class="fixed inset-0 z-40 flex items-center justify-center bg-black/30 px-4"
      @click.self="relationModal.open = false"
    >
      <div class="w-full max-w-md rounded-xl border border-slate-200 bg-white p-5 shadow-xl">
        <h3 class="text-base font-semibold text-slate-900">
          {{
            relationModal.mode === 'following'
              ? t('userProfile.relationships.followingEntry')
              : t('userProfile.relationships.followersEntry')
          }}
        </h3>
        <p class="mt-2 text-sm text-slate-600">
          {{
            relationModal.mode === 'following'
              ? t('userProfile.relationships.followingCountText', { count: relationModal.total || profileData?.following_count || 0 })
              : t('userProfile.relationships.followersCountText', { count: relationModal.total || profileData?.follower_count || 0 })
          }}
        </p>

        <div class="mt-3 max-h-80 space-y-2 overflow-y-auto">
          <p v-if="relationModal.loading" class="text-xs text-slate-500">
            {{ t('userProfile.relationships.loading') }}
          </p>
          <div v-else-if="relationModal.error" class="space-y-2">
            <p class="text-xs text-rose-600">{{ relationModal.error }}</p>
            <button
              class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-100"
              @click="loadRelationList()"
            >
              {{ t('userProfile.actions.retry') }}
            </button>
          </div>
          <p v-else-if="relationModal.items.length === 0" class="text-xs text-slate-500">
            {{ t('userProfile.relationships.empty') }}
          </p>
          <router-link
            v-for="relationUser in relationModal.items"
            :key="`relation-user-${relationModal.mode}-${relationUser.id}`"
            :to="`/user/${relationUser.id}`"
            class="flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 p-2.5 hover:bg-slate-100"
            @click="relationModal.open = false"
          >
            <img
              :src="relationUser.avatar_url || fallbackAvatar(relationUser.name || relationUser.username)"
              :alt="t('userProfile.avatarAlt')"
              class="h-10 w-10 rounded-full border border-slate-200 object-cover"
            />
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-slate-900">
                {{ relationUser.name || relationUser.username }}
              </p>
              <p class="text-[11px] text-slate-500">@{{ relationUser.username }}</p>
              <p
                v-if="String(relationUser.bio || '').trim()"
                class="mt-1 line-clamp-2 whitespace-pre-wrap break-words text-xs text-slate-600"
              >
                {{ relationUser.bio }}
              </p>
              <p class="mt-1 text-[11px] text-slate-500">
                {{ formatDate(relationUser.followed_at) }}
              </p>
            </div>
          </router-link>
        </div>

        <div class="mt-4 flex justify-end">
          <button
            class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-100"
            @click="relationModal.open = false"
          >
            {{ t('userProfile.actions.close') }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="dmDialog.open"
      class="fixed inset-0 z-40 flex items-center justify-center bg-black/30 px-4"
      @click.self="dmDialog.open = false"
    >
      <div class="flex h-[75vh] w-full max-w-xl flex-col rounded-xl border border-slate-200 bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <div>
            <h3 class="text-sm font-semibold text-slate-900">{{ t('userProfile.actions.directMessage') }}</h3>
            <p class="text-xs text-slate-500">
              {{ dmDialog.peerName || profileData?.user.name || profileData?.user.username }}
            </p>
          </div>
          <button
            class="rounded-lg border border-slate-300 px-2.5 py-1 text-xs text-slate-700 hover:bg-slate-100"
            @click="dmDialog.open = false"
          >
            {{ t('userProfile.actions.close') }}
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto bg-slate-50 p-3">
          <p v-if="dmDialog.loading" class="text-xs text-slate-500">
            {{ t('userProfile.relationships.loading') }}
          </p>
          <p v-else-if="dmDialog.messages.length === 0" class="text-xs text-slate-500">
            {{ t('userProfile.relationships.empty') }}
          </p>
          <div v-else class="space-y-2">
            <div
              v-for="message in dmDialog.messages"
              :key="`dm-message-${message.id}`"
              class="flex"
              :class="message.sender === currentUserIdNumber ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[82%] rounded-lg border px-3 py-2"
                :class="
                  message.sender === currentUserIdNumber
                    ? 'border-emerald-300 bg-emerald-50'
                    : 'border-slate-200 bg-white'
                "
              >
                <p class="whitespace-pre-wrap break-words text-sm text-slate-800">{{ message.content }}</p>
                <p class="mt-1 text-right text-[11px] text-slate-500">{{ formatDate(message.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-slate-200 p-3">
          <p v-if="dmDialog.error" class="mb-2 text-xs text-rose-600">{{ dmDialog.error }}</p>
          <textarea
            v-model="dmDialog.draft"
            class="h-20 w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm"
            :placeholder="t('userProfile.dm.placeholder')"
            @keydown.enter.exact.prevent="sendDirectMessageMessage"
          ></textarea>
          <div class="mt-2 flex justify-end">
            <button
              class="rounded-lg bg-slate-900 px-3 py-1.5 text-xs text-white hover:bg-slate-700 disabled:opacity-60"
              :disabled="dmDialog.sending || !String(dmDialog.draft || '').trim()"
              @click="sendDirectMessageMessage"
            >
              {{ dmDialog.sending ? t('userProfile.dm.sending') : t('userProfile.dm.send') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="novelPreview.open"
      class="fixed inset-0 z-40 flex items-center justify-center bg-black/35 px-4"
      @click.self="closeNovelPreview"
    >
      <div class="flex h-[80vh] w-full max-w-3xl flex-col rounded-xl border border-slate-200 bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <div class="min-w-0">
            <h3 class="truncate text-sm font-semibold text-slate-900">{{ activeNovelPreviewTitle }}</h3>
            <p class="text-xs text-slate-500">
              {{ t('userProfile.updatedAt', { time: formatDate(activeNovelPreviewUpdatedAt) }) }}
            </p>
          </div>
          <button
            class="rounded-lg border border-slate-300 px-2.5 py-1 text-xs text-slate-700 hover:bg-slate-100"
            @click="closeNovelPreview"
          >
            {{ t('userProfile.actions.close') }}
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto bg-slate-50 p-4">
          <p v-if="novelPreview.loading" class="text-xs text-slate-500">{{ t('userProfile.loading') }}</p>
          <div v-else-if="novelPreview.error" class="space-y-2">
            <p class="text-xs text-rose-600">{{ novelPreview.error }}</p>
            <button
              class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-100"
              @click="retryNovelPreview"
            >
              {{ t('userProfile.actions.retry') }}
            </button>
          </div>
          <div v-else-if="activeNovelPreview" class="space-y-4">
            <img
              v-if="String(activeNovelPreview.cover_image || '').trim()"
              :src="activeNovelPreview.cover_image"
              :alt="activeNovelPreviewTitle"
              class="max-h-64 w-full rounded-lg border border-slate-200 object-cover"
            />

            <section class="rounded-lg border border-slate-200 bg-white p-3">
              <h4 class="text-xs font-semibold text-slate-900">{{ t('userProfile.novels.title') }}</h4>
              <p class="mt-2 whitespace-pre-wrap break-words text-sm text-slate-700">
                {{ activeNovelPreviewSummary || t('userProfile.novels.summaryEmpty') }}
              </p>
            </section>

            <section class="rounded-lg border border-slate-200 bg-white p-3">
              <h4 class="text-xs font-semibold text-slate-900">Chapters</h4>
              <div v-if="activeNovelPreview.chapters.length === 0" class="mt-2 text-xs text-slate-500">
                No chapters yet.
              </div>
              <div v-else class="space-y-3">
                <article
                  v-for="chapter in activeNovelPreview.chapters"
                  :key="`novel-preview-chapter-${activeNovelPreview.id}-${chapter.chapter_no}`"
                  class="rounded-lg border border-slate-200 bg-slate-50 p-3"
                >
                  <h5 class="text-sm font-semibold text-slate-900">
                    {{ chapter.title || `Chapter ${chapter.chapter_no}` }}
                  </h5>
                  <p class="mt-2 whitespace-pre-wrap break-words text-sm text-slate-700">
                    {{ chapter.content }}
                  </p>
                </article>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="characterPreview.open"
      class="fixed inset-0 z-40 flex items-center justify-center bg-black/35 px-4"
      @click.self="closeCharacterPreview"
    >
      <div class="flex h-[76vh] w-full max-w-2xl flex-col rounded-xl border border-slate-200 bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <div class="min-w-0">
            <h3 class="truncate text-sm font-semibold text-slate-900">{{ activeCharacterPreviewName }}</h3>
            <p class="text-xs text-slate-500">
              {{ t('userProfile.updatedAt', { time: formatDate(activeCharacterPreviewUpdatedAt) }) }}
            </p>
          </div>
          <button
            class="rounded-lg border border-slate-300 px-2.5 py-1 text-xs text-slate-700 hover:bg-slate-100"
            @click="closeCharacterPreview"
          >
            {{ t('userProfile.actions.close') }}
          </button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto bg-slate-50 p-4">
          <p v-if="characterPreview.loading" class="text-xs text-slate-500">{{ t('userProfile.loading') }}</p>
          <div v-else-if="characterPreview.error" class="space-y-2">
            <p class="text-xs text-rose-600">{{ characterPreview.error }}</p>
            <button
              class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-100"
              @click="retryCharacterPreview"
            >
              {{ t('userProfile.actions.retry') }}
            </button>
          </div>
          <div v-else-if="activeCharacterPreview" class="space-y-4">
            <section class="rounded-lg border border-slate-200 bg-white p-3">
              <div class="flex items-start gap-3">
                <img
                  :src="activeCharacterPreviewAvatar"
                  :alt="activeCharacterPreviewName"
                  class="h-14 w-14 rounded-full border border-slate-200 object-cover"
                />
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-semibold text-slate-900">{{ activeCharacterPreviewName }}</p>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ activeCharacterPreviewMeta }}
                  </p>
                </div>
              </div>
            </section>

            <section class="rounded-lg border border-slate-200 bg-white p-3">
              <h4 class="text-xs font-semibold text-slate-900">Description</h4>
              <p class="mt-2 whitespace-pre-wrap break-words text-sm text-slate-700">
                {{ activeCharacterPreviewDescription || t('userProfile.characters.descriptionEmpty') }}
              </p>
            </section>

            <section
              v-if="activeCharacterPreviewFirstMessage"
              class="rounded-lg border border-slate-200 bg-white p-3"
            >
              <h4 class="text-xs font-semibold text-slate-900">First Message</h4>
              <p class="mt-2 whitespace-pre-wrap break-words text-sm text-slate-700">
                {{ activeCharacterPreviewFirstMessage }}
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div
        v-if="toast.visible"
        class="fixed right-4 top-20 z-50 rounded-lg border px-3 py-2 text-xs shadow-lg"
        :class="toastClass"
      >
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { BookOpenText, MessageCircle, ScrollText, UserCheck, UserPlus } from 'lucide-vue-next'
import AuthDialog from '../components/AuthDialog.vue'
import { useAuthStore } from '../stores/auth'
import { formatDateTimeByLocale } from '../utils/intl'
import {
  fetchDirectMessageThreadMessages,
  sendDirectMessage as sendDirectMessageApi,
  fetchUserPublicCharacterDetail,
  fetchUserPublicNovelDetail,
  fetchUserRelationList,
  type DirectMessagePayload,
  followUser,
  initDirectMessage,
  type ContentVisibility,
  type PublicProfileCharacterDetailPayload,
  type PublicProfileCharacterPayload,
  type PublicProfileNovelDetailPayload,
  type PublicProfileNovelPayload,
  type PublicUserProfilePayload,
  type UserRelationItemPayload,
  fetchUserPublicProfile,
  unfollowUser,
  updateCharacterVisibility,
  updateMyProfile,
  updateNovelVisibility,
} from '../api/profile'

type RelationMode = 'following' | 'followers'
type ToastType = 'info' | 'success' | 'error'

const route = useRoute()
const authStore = useAuthStore()
const { t, locale } = useI18n()

const loading = ref(false)
const pageError = ref('')
const profileData = ref<PublicUserProfilePayload | null>(null)
const globalVisibility = ref<ContentVisibility>(2)
const showAuthDialog = ref(false)

const actionLoading = reactive({
  follow: false,
  dm: false,
  globalVisibility: false,
})

const novelVisibilityLoading = ref<Record<number, boolean>>({})
const characterVisibilityLoading = ref<Record<number, boolean>>({})

const relationModal = reactive({
  open: false,
  mode: 'following' as RelationMode,
  loading: false,
  error: '',
  items: [] as UserRelationItemPayload[],
  total: 0,
})

const dmDialog = reactive({
  open: false,
  loading: false,
  sending: false,
  threadId: 0,
  peerName: '',
  messages: [] as DirectMessagePayload[],
  draft: '',
  error: '',
})

const novelPreview = reactive({
  open: false,
  loading: false,
  error: '',
  data: null as PublicProfileNovelDetailPayload | null,
  sourceNovel: null as PublicProfileNovelPayload | null,
})

const characterPreview = reactive({
  open: false,
  loading: false,
  error: '',
  data: null as PublicProfileCharacterDetailPayload | null,
  sourceCharacter: null as PublicProfileCharacterPayload | null,
})

const toast = reactive({
  visible: false,
  message: '',
  type: 'info' as ToastType,
})

let toastTimer: ReturnType<typeof setTimeout> | null = null

const routeUserId = computed(() => String(route.params.id || '').trim())
const currentUserId = computed(() => String(authStore.user?.id || '').trim())
const currentUserIdNumber = computed(() => Number(authStore.user?.id || 0))
const isOwner = computed(() => routeUserId.value !== '' && routeUserId.value === currentUserId.value)
const isFollowing = computed(() => Boolean(profileData.value?.is_following))

const visibilityOptions = computed(() => [
  { value: 2 as ContentVisibility, label: t('userProfile.visibility.public') },
  { value: 1 as ContentVisibility, label: t('userProfile.visibility.followers') },
  { value: 0 as ContentVisibility, label: t('userProfile.visibility.private') },
])

const avatarSrc = computed(() => {
  const avatar = String(profileData.value?.user.avatar_url || '').trim()
  if (avatar) return avatar
  return fallbackAvatar(profileData.value?.user.name || profileData.value?.user.username || 'user-profile')
})

const toastClass = computed(() => {
  if (toast.type === 'success') {
    return 'border-emerald-300 bg-emerald-50 text-emerald-700'
  }
  if (toast.type === 'error') {
    return 'border-rose-300 bg-rose-50 text-rose-700'
  }
  return 'border-slate-300 bg-white text-slate-700'
})

const activeNovelPreview = computed(() => {
  if (novelPreview.data) return novelPreview.data
  const source = novelPreview.sourceNovel
  if (!source) return null
  const userId = parseRouteUserId() || 0
  return {
    id: source.id,
    user_id: userId,
    title: novelDisplayTitle(source),
    summary: readMaybeLocalizedText((source as any)?.summary, 12000),
    cover_image: readMaybeLocalizedText((source as any)?.cover_image, 2000),
    visibility: source.visibility,
    completion_status: 'draft',
    chapter_count: 0,
    chapters: [],
    created_at: source.created_at,
    updated_at: source.updated_at,
  } as PublicProfileNovelDetailPayload
})

const activeNovelPreviewTitle = computed(() => {
  const payload = activeNovelPreview.value
  if (!payload) return t('userProfile.novels.untitled')
  return readMaybeLocalizedText(payload.title, 220) || t('userProfile.novels.untitled')
})

const activeNovelPreviewSummary = computed(() => {
  const payload = activeNovelPreview.value
  if (!payload) return ''
  return readMaybeLocalizedText(payload.summary, 12000)
})

const activeNovelPreviewUpdatedAt = computed(() => {
  const payload = activeNovelPreview.value
  return String(payload?.updated_at || '').trim()
})

const activeCharacterPreview = computed(() => {
  if (characterPreview.data) return characterPreview.data
  const source = characterPreview.sourceCharacter
  if (!source) return null
  const userId = parseRouteUserId() || 0
  return {
    id: source.id,
    post_id: source.id,
    user_id: userId,
    name: readMaybeLocalizedText((source as any)?.name, 220),
    description: readMaybeLocalizedText((source as any)?.description, 12000),
    content: readMaybeLocalizedText((source as any)?.description, 12000),
    avatar: readMaybeLocalizedText((source as any)?.avatar, 2000),
    group: '',
    gender: '',
    first_message: '',
    source_ref: String(source.source_ref || '').trim().slice(0, 128),
    visibility: source.visibility,
    created_at: source.created_at,
    updated_at: source.updated_at,
  } as PublicProfileCharacterDetailPayload
})

const activeCharacterPreviewName = computed(() => {
  const payload = activeCharacterPreview.value
  if (!payload) return t('userProfile.characters.untitled')
  return readMaybeLocalizedText(payload.name, 220) || t('userProfile.characters.untitled')
})

const activeCharacterPreviewDescription = computed(() => {
  const payload = activeCharacterPreview.value
  if (!payload) return ''
  const primary = readMaybeLocalizedText(payload.description, 12000)
  if (primary) return primary
  return readMaybeLocalizedText(payload.content, 12000)
})

const activeCharacterPreviewFirstMessage = computed(() => {
  const payload = activeCharacterPreview.value
  if (!payload) return ''
  return readMaybeLocalizedText(payload.first_message, 12000)
})

const activeCharacterPreviewAvatar = computed(() => {
  const payload = activeCharacterPreview.value
  const avatar = readMaybeLocalizedText(payload?.avatar, 2000)
  if (avatar) return avatar
  return fallbackAvatar(activeCharacterPreviewName.value || 'role-card')
})

const activeCharacterPreviewUpdatedAt = computed(() => {
  const payload = activeCharacterPreview.value
  return String(payload?.updated_at || '').trim()
})

const activeCharacterPreviewMeta = computed(() => {
  const payload = activeCharacterPreview.value
  if (!payload) return ''
  const parts: string[] = []
  const group = readMaybeLocalizedText(payload.group, 80)
  const gender = readMaybeLocalizedText(payload.gender, 80)
  const sourceRef = String(payload.source_ref || '').trim()
  if (group) parts.push(`Group: ${group}`)
  if (gender) parts.push(`Gender: ${gender}`)
  if (sourceRef) parts.push(`Ref: ${sourceRef}`)
  return parts.join(' | ')
})

const parseError = (error: any, fallbackKey: string): string => {
  const data = error?.response?.data
  if (typeof data?.detail === 'string' && data.detail.trim()) return data.detail.trim()
  if (typeof data === 'string' && data.trim()) return data.trim()
  return error?.message || t(fallbackKey)
}

const parseRouteUserId = (): number | null => {
  const id = Number(routeUserId.value)
  if (!Number.isFinite(id) || id <= 0) return null
  return id
}

const fallbackAvatar = (seed: unknown): string => {
  const safeSeed = encodeURIComponent(String(seed || 'user-profile').trim() || 'user-profile')
  return `https://api.dicebear.com/7.x/notionists/svg?seed=${safeSeed}`
}

const formatDate = (value: unknown): string => {
  const raw = String(value || '').trim()
  if (!raw) return t('userProfile.common.dash')
  return formatDateTimeByLocale(raw, locale.value)
}

const visibilityLabel = (value: unknown): string => {
  const normalized = Number(value)
  if (normalized === 0) return t('userProfile.visibility.private')
  if (normalized === 1) return t('userProfile.visibility.followers')
  return t('userProfile.visibility.public')
}

const normalizeLocaleCode = (rawLocale: string): string => {
  const value = String(rawLocale || '').trim().toLowerCase()
  if (!value) return 'zh-CN'
  if (value.startsWith('zh')) {
    if (value.includes('tw') || value.includes('hk') || value.includes('hant')) return 'zh-TW'
    return 'zh-CN'
  }
  if (value.startsWith('en')) return 'en'
  if (value.startsWith('ja')) return 'ja'
  if (value.startsWith('ko')) return 'ko'
  if (value.startsWith('fr')) return 'fr'
  if (value.startsWith('de')) return 'de'
  if (value.startsWith('vi')) return 'vi'
  if (value.startsWith('th')) return 'th'
  return 'zh-CN'
}

const localeAliasChain = (rawLocale: string): string[] => {
  const normalized = normalizeLocaleCode(rawLocale)
  const aliases = [
    normalized,
    normalized.toLowerCase(),
    normalized.replace('-', '_'),
    normalized.toLowerCase().replace('-', '_'),
    normalized.split('-', 1)[0].toLowerCase(),
  ]
  if (normalized === 'zh-CN') {
    aliases.push('zh', 'zh-cn', 'zh_cn', 'zh-hans', 'zh_hans')
  } else if (normalized === 'zh-TW') {
    aliases.push('zh', 'zh-tw', 'zh_tw', 'zh-hk', 'zh_hk', 'zh-hant', 'zh_hant')
  } else if (normalized === 'en') {
    aliases.push('en-us', 'en_us', 'en-gb', 'en_gb')
  }

  return Array.from(
    new Set(
      aliases
        .map((item) => String(item || '').trim().replace(/_/g, '-').toLowerCase())
        .filter(Boolean)
    )
  )
}

const readMaybeLocalizedText = (value: unknown, maxLen = 12000, depth = 0): string => {
  if (depth > 4) return ''

  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value.trim().slice(0, maxLen)
  if (typeof value === 'number' || typeof value === 'boolean') return String(value).trim().slice(0, maxLen)

  if (Array.isArray(value)) {
    for (const item of value) {
      const picked = readMaybeLocalizedText(item, maxLen, depth + 1)
      if (picked) return picked
    }
    return ''
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .map(([key, item]) => [String(key || '').trim().replace(/_/g, '-').toLowerCase(), item] as const)
      .filter(([key]) => Boolean(key))

    const tryPick = (aliases: string[]) => {
      for (const alias of aliases) {
        const matched = entries.find(([key]) => key === alias)
        if (!matched) continue
        const picked = readMaybeLocalizedText(matched[1], maxLen, depth + 1)
        if (picked) return picked
      }
      return ''
    }

    const primary = tryPick(localeAliasChain(locale.value))
    if (primary) return primary
    const englishFallback = tryPick(localeAliasChain('en'))
    if (englishFallback) return englishFallback
    const chineseFallback = tryPick(localeAliasChain('zh-CN'))
    if (chineseFallback) return chineseFallback

    for (const [, item] of entries) {
      const picked = readMaybeLocalizedText(item, maxLen, depth + 1)
      if (picked) return picked
    }
    return ''
  }

  return ''
}

const novelDisplayTitle = (novel: PublicProfileNovelPayload | null | undefined): string => {
  const text = readMaybeLocalizedText((novel as any)?.title, 220)
  return text || t('userProfile.novels.untitled')
}

const novelDisplaySummary = (novel: PublicProfileNovelPayload | null | undefined): string => {
  const text = readMaybeLocalizedText((novel as any)?.summary, 12000)
  return text || t('userProfile.novels.summaryEmpty')
}

const characterDisplayDescription = (character: PublicProfileCharacterPayload | null | undefined): string => {
  const text = readMaybeLocalizedText((character as any)?.description, 12000)
  return text || t('userProfile.characters.descriptionEmpty')
}

const showToast = (message: string, type: ToastType = 'info') => {
  toast.message = message
  toast.type = type
  toast.visible = true
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
  toastTimer = setTimeout(() => {
    toast.visible = false
  }, 1800)
}

const syncGlobalVisibility = () => {
  if (!profileData.value) return
  const value = Number(profileData.value.user.global_ai_visibility)
  if (value === 0 || value === 1 || value === 2) {
    globalVisibility.value = value as ContentVisibility
    return
  }
  globalVisibility.value = 2
}

const loadProfile = async () => {
  const userId = parseRouteUserId()
  if (!userId) {
    pageError.value = t('userProfile.errors.invalidUserId')
    profileData.value = null
    return
  }

  loading.value = true
  pageError.value = ''
  try {
    const payload = await fetchUserPublicProfile(userId)
    profileData.value = payload
    syncGlobalVisibility()
  } catch (error: any) {
    pageError.value = parseError(error, 'userProfile.errors.loadFailed')
  } finally {
    loading.value = false
  }
}

const toggleFollow = async () => {
  const userId = parseRouteUserId()
  if (!userId) return
  if (!authStore.isAuthenticated) {
    showAuthDialog.value = true
    showToast(t('userProfile.toast.loginRequired'), 'info')
    return
  }

  actionLoading.follow = true
  try {
    const nextState = isFollowing.value ? await unfollowUser(userId) : await followUser(userId)
    if (profileData.value) {
      profileData.value.is_following = nextState.is_following
      profileData.value.follower_count = nextState.follower_count
      profileData.value.following_count = nextState.following_count
    }
    showToast(
      nextState.is_following ? t('userProfile.toast.followed') : t('userProfile.toast.unfollowed'),
      'success'
    )
  } catch (error: any) {
    showToast(parseError(error, 'userProfile.errors.followFailed'), 'error')
  } finally {
    actionLoading.follow = false
  }
}

const startDirectMessage = async () => {
  const userId = parseRouteUserId()
  if (!userId) return

  if (!authStore.isAuthenticated) {
    showAuthDialog.value = true
    showToast(t('userProfile.toast.loginRequired'), 'info')
    return
  }

  actionLoading.dm = true
  dmDialog.open = true
  dmDialog.loading = true
  dmDialog.threadId = 0
  dmDialog.peerName = String(profileData.value?.user.name || profileData.value?.user.username || '').trim()
  dmDialog.messages = []
  dmDialog.draft = ''
  dmDialog.error = ''
  try {
    const payload = await initDirectMessage(userId)
    const threadId = Number(payload?.thread?.id || 0)
    if (!threadId) {
      throw new Error(t('userProfile.errors.dmFailed'))
    }
    dmDialog.threadId = threadId
    await loadDirectMessages()
    showToast(t('userProfile.toast.dmStarted'), 'success')
  } catch (error: any) {
    const statusCode = Number(error?.response?.status || 0)
    if (statusCode === 403) {
      showToast(t('userProfile.toast.needFollowBeforeChat'), 'error')
    } else {
      showToast(parseError(error, 'userProfile.errors.dmFailed'), 'error')
    }
    dmDialog.open = false
  } finally {
    actionLoading.dm = false
    if (!dmDialog.threadId) {
      dmDialog.loading = false
    }
  }
}

const loadDirectMessages = async () => {
  if (!dmDialog.threadId) return
  dmDialog.loading = true
  dmDialog.error = ''
  try {
    const payload = await fetchDirectMessageThreadMessages(dmDialog.threadId, 100, true)
    dmDialog.messages = Array.isArray(payload?.messages) ? payload.messages : []
  } catch (error: any) {
    dmDialog.error = parseError(error, 'userProfile.errors.dmFailed')
  } finally {
    dmDialog.loading = false
  }
}

const sendDirectMessageMessage = async () => {
  const content = String(dmDialog.draft || '').trim()
  if (!content || dmDialog.sending || !dmDialog.threadId) return

  dmDialog.sending = true
  dmDialog.error = ''
  try {
    const created = await sendDirectMessageApi(dmDialog.threadId, content)
    dmDialog.messages = [...dmDialog.messages, created]
    dmDialog.draft = ''
  } catch (error: any) {
    dmDialog.error = parseError(error, 'userProfile.errors.dmFailed')
  } finally {
    dmDialog.sending = false
  }
}

const onGlobalVisibilityChange = async () => {
  if (!isOwner.value || !profileData.value) return
  const previous = profileData.value.user.global_ai_visibility

  actionLoading.globalVisibility = true
  try {
    const updated = await updateMyProfile({ global_ai_visibility: globalVisibility.value })
    const nextVisibility = Number(updated.global_ai_visibility)
    profileData.value.user.global_ai_visibility = (nextVisibility === 0 || nextVisibility === 1 || nextVisibility === 2
      ? nextVisibility
      : globalVisibility.value) as ContentVisibility
    globalVisibility.value = profileData.value.user.global_ai_visibility
    showToast(t('userProfile.toast.globalVisibilitySaved'), 'success')
  } catch (error: any) {
    profileData.value.user.global_ai_visibility = previous
    globalVisibility.value = previous
    showToast(parseError(error, 'userProfile.errors.globalVisibilityFailed'), 'error')
  } finally {
    actionLoading.globalVisibility = false
  }
}

const withNovelLoading = async (novelId: number, runner: () => Promise<void>) => {
  novelVisibilityLoading.value = { ...novelVisibilityLoading.value, [novelId]: true }
  try {
    await runner()
  } finally {
    novelVisibilityLoading.value = { ...novelVisibilityLoading.value, [novelId]: false }
  }
}

const withCharacterLoading = async (characterId: number, runner: () => Promise<void>) => {
  characterVisibilityLoading.value = { ...characterVisibilityLoading.value, [characterId]: true }
  try {
    await runner()
  } finally {
    characterVisibilityLoading.value = { ...characterVisibilityLoading.value, [characterId]: false }
  }
}

const onNovelVisibilityChange = async (novel: PublicProfileNovelPayload) => {
  if (!isOwner.value) return
  const previous = novel.visibility
  await withNovelLoading(novel.id, async () => {
    try {
      const updated = await updateNovelVisibility(novel.id, novel.visibility)
      novel.visibility = updated.visibility
      showToast(t('userProfile.toast.itemVisibilitySaved'), 'success')
    } catch (error: any) {
      novel.visibility = previous
      showToast(parseError(error, 'userProfile.errors.itemVisibilityFailed'), 'error')
    }
  })
}

const loadNovelPreviewDetail = async () => {
  const userId = parseRouteUserId()
  const novelId = Number(novelPreview.sourceNovel?.id || 0)
  if (!userId || !novelId) return

  novelPreview.loading = true
  novelPreview.error = ''
  try {
    const payload = await fetchUserPublicNovelDetail(userId, novelId)
    novelPreview.data = payload
  } catch (error: any) {
    novelPreview.error = parseError(error, 'userProfile.errors.loadFailed')
  } finally {
    novelPreview.loading = false
  }
}

const openNovelPreview = async (novel: PublicProfileNovelPayload) => {
  novelPreview.open = true
  novelPreview.loading = false
  novelPreview.error = ''
  novelPreview.data = null
  novelPreview.sourceNovel = novel
  await loadNovelPreviewDetail()
}

const retryNovelPreview = async () => {
  await loadNovelPreviewDetail()
}

const closeNovelPreview = () => {
  novelPreview.open = false
  novelPreview.loading = false
  novelPreview.error = ''
  novelPreview.data = null
  novelPreview.sourceNovel = null
}

const loadCharacterPreviewDetail = async () => {
  const userId = parseRouteUserId()
  const characterId = Number(characterPreview.sourceCharacter?.id || 0)
  if (!userId || !characterId) return

  characterPreview.loading = true
  characterPreview.error = ''
  try {
    const payload = await fetchUserPublicCharacterDetail(userId, characterId)
    characterPreview.data = payload
  } catch (error: any) {
    characterPreview.error = parseError(error, 'userProfile.errors.loadFailed')
  } finally {
    characterPreview.loading = false
  }
}

const openCharacterPreview = async (character: PublicProfileCharacterPayload) => {
  characterPreview.open = true
  characterPreview.loading = false
  characterPreview.error = ''
  characterPreview.data = null
  characterPreview.sourceCharacter = character
  await loadCharacterPreviewDetail()
}

const retryCharacterPreview = async () => {
  await loadCharacterPreviewDetail()
}

const closeCharacterPreview = () => {
  characterPreview.open = false
  characterPreview.loading = false
  characterPreview.error = ''
  characterPreview.data = null
  characterPreview.sourceCharacter = null
}

const onCharacterVisibilityChange = async (character: PublicProfileCharacterPayload) => {
  if (!isOwner.value) return
  const previous = character.visibility
  await withCharacterLoading(character.id, async () => {
    try {
      const updated = await updateCharacterVisibility(character.id, character.visibility)
      const nextVisibility = Number(updated?.visibility)
      character.visibility = (nextVisibility === 0 || nextVisibility === 1 || nextVisibility === 2
        ? nextVisibility
        : character.visibility) as ContentVisibility
      showToast(t('userProfile.toast.itemVisibilitySaved'), 'success')
    } catch (error: any) {
      character.visibility = previous
      showToast(parseError(error, 'userProfile.errors.itemVisibilityFailed'), 'error')
    }
  })
}

const loadRelationList = async () => {
  const userId = parseRouteUserId()
  if (!userId) return

  relationModal.loading = true
  relationModal.error = ''
  try {
    const payload = await fetchUserRelationList(userId, relationModal.mode, 200)
    relationModal.items = Array.isArray(payload.items) ? payload.items : []
    relationModal.total = Number(payload.total || relationModal.items.length)
  } catch (error: any) {
    relationModal.error = parseError(error, 'userProfile.errors.loadFailed')
    relationModal.items = []
    relationModal.total = 0
  } finally {
    relationModal.loading = false
  }
}

const openRelationModal = async (mode: RelationMode) => {
  relationModal.mode = mode
  relationModal.open = true
  await loadRelationList()
}

onMounted(() => {
  loadProfile()
})

watch(
  () => route.params.id,
  () => {
    closeNovelPreview()
    closeCharacterPreview()
    loadProfile()
    if (relationModal.open) {
      loadRelationList()
    }
  }
)

watch(
  () => authStore.user?.id,
  () => {
    if (profileData.value) {
      loadProfile()
    }
  }
)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
