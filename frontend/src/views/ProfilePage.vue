<template>
  <div class="min-h-screen relative pt-16 pb-10 bg-gray-50">
    <div class="container mx-auto px-4 max-w-6xl">
      <div class="mb-8 text-center">
        <h1
          class="text-4xl md:text-5xl font-bold text-gray-800 mb-2"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'title')"
        >
          {{ getPageConfig('title', t('profilePage.title')) }}
        </h1>
        <p
          class="text-gray-500 text-base"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'description')"
        >
          {{ getPageConfig('description', t('profilePage.description')) }}
        </p>
      </div>

      <div v-if="!authStore.isAuthenticated" class="text-center py-16 bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="mb-6 inline-block p-5 bg-gray-50 rounded-full">
          <User class="w-14 h-14 text-gray-400 mx-auto" />
        </div>
        <h2 class="text-xl md:text-2xl font-semibold text-gray-800 mb-3">{{ t('profilePage.auth.title') }}</h2>
        <p class="text-gray-600 mb-6 max-w-md mx-auto text-sm">{{ t('profilePage.auth.description') }}</p>
        <button
          @click="showAuthDialog = true"
          class="px-6 py-2.5 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition-colors"
        >
          {{ t('profilePage.auth.loginRegister') }}
        </button>
      </div>

      <div v-else class="space-y-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:p-8">
          <div class="flex flex-col md:flex-row md:items-center gap-6">
            <div class="flex-shrink-0">
              <img
                :src="avatarPreview || '/api/placeholder/120/120'"
                :alt="t('profilePage.avatar.alt')"
                class="w-24 h-24 rounded-full border-2 border-gray-200 object-cover"
              />
              <div class="mt-3 flex gap-2">
                <label
                  class="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-md bg-blue-600 text-white cursor-pointer hover:bg-blue-700"
                >
                  <ImagePlus class="w-3.5 h-3.5" />
                  <span>{{ t('profilePage.avatar.upload') }}</span>
                  <input type="file" accept="image/*" class="hidden" @change="handleAvatarChange" />
                </label>
                <button
                  type="button"
                  class="text-xs px-3 py-1.5 rounded-md bg-gray-100 text-gray-600 hover:bg-gray-200"
                  @click="removeAvatar"
                >
                  {{ t('profilePage.avatar.remove') }}
                </button>
              </div>
            </div>

            <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.displayName') }}</label>
                <input v-model="form.name" type="text" class="w-full border border-gray-200 rounded-md px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.gender') }}</label>
                <input
                  v-model="form.gender"
                  type="text"
                  class="w-full border border-gray-200 rounded-md px-3 py-2"
                  :placeholder="t('profilePage.form.genderPlaceholder')"
                />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.firstName') }}</label>
                <input v-model="form.first_name" type="text" class="w-full border border-gray-200 rounded-md px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.lastName') }}</label>
                <input v-model="form.last_name" type="text" class="w-full border border-gray-200 rounded-md px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.phone') }}</label>
                <input v-model="form.phone" type="text" class="w-full border border-gray-200 rounded-md px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.visibility') }}</label>
                <select v-model="form.ai_content_visibility" class="w-full border border-gray-200 rounded-md px-3 py-2">
                  <option value="private">{{ t('profilePage.form.visibilityPrivate') }}</option>
                  <option value="members">{{ t('profilePage.form.visibilityMembers') }}</option>
                  <option value="public">{{ t('profilePage.form.visibilityPublic') }}</option>
                </select>
              </div>
            </div>
          </div>

          <div class="mt-4">
            <label class="block text-sm text-gray-600 mb-1">{{ t('profilePage.form.bio') }}</label>
            <textarea
              v-model="form.bio"
              rows="4"
              maxlength="500"
              class="w-full border border-gray-200 rounded-md px-3 py-2"
              :placeholder="t('profilePage.form.bioPlaceholder')"
            />
          </div>

          <div class="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              class="px-5 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
              :disabled="saving || loading"
              @click="saveProfile"
            >
              {{ saving ? t('profilePage.form.saving') : t('profilePage.form.save') }}
            </button>
            <button
              type="button"
              class="px-5 py-2 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
              :disabled="loading"
              @click="loadDashboard"
            >
              {{ t('profilePage.form.refresh') }}
            </button>
            <RouterLink :to="localizedPath('/novel-story')" class="px-5 py-2 rounded-md bg-emerald-100 text-emerald-700 hover:bg-emerald-200">
              {{ t('profilePage.form.toNovel') }}
            </RouterLink>
            <RouterLink :to="localizedPath('/plaza')" class="px-5 py-2 rounded-md bg-indigo-100 text-indigo-700 hover:bg-indigo-200">
              {{ t('profilePage.form.toPlaza') }}
            </RouterLink>
          </div>

          <p v-if="message" class="mt-3 text-sm text-emerald-600">{{ message }}</p>
          <p v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-3xl font-semibold text-gray-800">{{ dashboard?.stats?.novel_draft_count || 0 }}</div>
            <p class="text-sm text-gray-500 mt-1">{{ t('profilePage.stats.novelDrafts') }}</p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-3xl font-semibold text-gray-800">{{ dashboard?.stats?.novel_work_count || 0 }}</div>
            <p class="text-sm text-gray-500 mt-1">{{ t('profilePage.stats.novelWorks') }}</p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-3xl font-semibold text-gray-800">{{ dashboard?.stats?.role_card_count || 0 }}</div>
            <p class="text-sm text-gray-500 mt-1">{{ t('profilePage.stats.roleCards') }}</p>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 p-4 text-center">
            <div class="text-3xl font-semibold text-gray-800">{{ dashboard?.stats?.ai_content_count || 0 }}</div>
            <p class="text-sm text-gray-500 mt-1">{{ t('profilePage.stats.aiContentTotal') }}</p>
          </div>
        </div>

        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <div class="flex items-center gap-2 mb-3">
            <BookOpenText class="w-5 h-5 text-blue-600" />
            <h3 class="text-lg font-semibold text-gray-800">{{ t('profilePage.novels.title') }}</h3>
          </div>
          <p class="text-xs text-gray-500 mb-4">{{ t('profilePage.novels.scopeHint') }}</p>
          <div v-if="!(dashboard?.novel_works?.length || dashboard?.novel_drafts?.length)" class="text-sm text-gray-500 py-4">
            {{ t('profilePage.novels.empty') }}
          </div>

          <div v-if="dashboard?.novel_drafts?.length" class="mb-4">
            <h4 class="text-sm font-medium text-gray-700 mb-2">{{ t('profilePage.novels.draftsTitle') }}</h4>
            <div class="space-y-2">
              <div
                v-for="item in dashboard.novel_drafts"
                :key="`draft-${item.id}`"
                class="border border-gray-100 rounded-md px-3 py-2"
              >
                <p class="text-sm font-medium text-gray-800">{{ item.title || t('profilePage.novels.draftTitleFallback', { id: item.id }) }}</p>
                <p class="text-xs text-gray-500">
                  {{ t('profilePage.novels.draftMeta', { count: item.state_key_count, updatedAt: formatDate(item.updated_at) }) }}
                </p>
              </div>
            </div>
          </div>

          <div v-if="dashboard?.novel_works?.length">
            <h4 class="text-sm font-medium text-gray-700 mb-2">{{ t('profilePage.novels.worksTitle') }}</h4>
            <div class="space-y-2">
              <div
                v-for="item in dashboard.novel_works"
                :key="`work-${item.id}`"
                class="border border-gray-100 rounded-md px-3 py-2"
              >
                <p class="text-sm font-medium text-gray-800">{{ item.title || t('profilePage.novels.workTitleFallback', { id: item.id }) }}</p>
                <p class="text-xs text-gray-500 line-clamp-2">{{ item.summary || t('profilePage.novels.summaryEmpty') }}</p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ t('profilePage.novels.workMeta', {
                    chapters: item.chapter_count,
                    images: item.character_image_count,
                    status: formatWorkStatus(item.completion_status),
                    updatedAt: formatDate(item.updated_at),
                  }) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg border border-gray-200 p-6">
          <div class="flex items-center gap-2 mb-3">
            <ScrollText class="w-5 h-5 text-indigo-600" />
            <h3 class="text-lg font-semibold text-gray-800">{{ t('profilePage.roleCards.title') }}</h3>
          </div>
          <div v-if="!dashboard?.role_cards?.length" class="text-sm text-gray-500 py-4">{{ t('profilePage.roleCards.empty') }}</div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              v-for="card in dashboard.role_cards"
              :key="`card-${card.id}`"
              class="border border-gray-100 rounded-md p-3"
            >
              <div class="flex items-start gap-3">
                <img
                  :src="card.avatar || fallbackAvatar(card.name)"
                  :alt="t('profilePage.roleCards.avatarAlt')"
                  class="w-10 h-10 rounded-full object-cover border border-gray-200"
                />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ card.name }}</p>
                  <p class="text-xs text-gray-500 truncate">
                    {{ t('profilePage.roleCards.meta', {
                      group: card.group || t('profilePage.common.dash'),
                      gender: card.gender || t('profilePage.common.dash'),
                    }) }}
                  </p>
                  <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ card.description || t('profilePage.roleCards.descEmpty') }}</p>
                  <p class="text-[11px] text-gray-400 mt-1">
                    {{ t('profilePage.roleCards.updatedAt', { updatedAt: formatDate(card.updated_at) }) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <AuthDialog v-model="showAuthDialog" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { BookOpenText, ImagePlus, ScrollText, User } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
import AuthDialog from '../components/AuthDialog.vue'
import { useAuthStore } from '../stores/auth'
import { useVisualEditor } from '../composables/useVisualEditor'
import { withLocalePrefix } from '../i18n/locale-routing'
import { normalizeLocaleCode } from '../i18n/locale-utils'
import { formatDateTimeByLocale } from '../utils/intl'
import {
  fetchMyDashboard,
  type UserDashboardPayload,
  type UserProfilePayload,
  updateMyProfile,
  updateMyProfileWithAvatar,
} from '../api/profile'

const { t, locale } = useI18n()
const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('profile_page', '个人中心页')
const authStore = useAuthStore()

const showAuthDialog = ref(false)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const message = ref('')

const dashboard = ref<UserDashboardPayload | null>(null)
const avatarPreview = ref('')
const avatarFile = ref<File | null>(null)
const shouldRemoveAvatar = ref(false)

const form = reactive({
  name: '',
  first_name: '',
  last_name: '',
  phone: '',
  gender: '',
  bio: '',
  ai_content_visibility: 'private' as 'private' | 'members' | 'public',
})

const localizedPath = (path: string): string => withLocalePrefix(path, normalizeLocaleCode(locale.value))
const normalizeText = (value: unknown) => String(value || '').trim()
const ALLOWED_VISIBILITY = new Set(['private', 'members', 'public'])

const normalizeVisibility = (value: unknown): 'private' | 'members' | 'public' => {
  const normalized = normalizeText(value)
  return ALLOWED_VISIBILITY.has(normalized) ? (normalized as 'private' | 'members' | 'public') : 'private'
}

const parseRequestError = (err: any): string => {
  const data = err?.response?.data
  if (!data) {
    return err?.message || t('profilePage.messages.saveFailed')
  }

  if (typeof data?.detail === 'string' && data.detail.trim()) {
    return data.detail.trim()
  }

  if (typeof data === 'string') {
    return data.trim() || err?.message || t('profilePage.messages.saveFailed')
  }

  if (Array.isArray(data)) {
    const first = data.find((item) => typeof item === 'string' && item.trim())
    if (first) return first.trim()
  }

  if (typeof data === 'object') {
    for (const [field, value] of Object.entries(data)) {
      if (Array.isArray(value) && value.length > 0) {
        const first = String(value[0] || '').trim()
        if (first) return `${field}: ${first}`
      }
      const text = String(value || '').trim()
      if (text) return `${field}: ${text}`
    }
  }

  return err?.message || t('profilePage.messages.saveFailed')
}

const fallbackAvatar = (seed: unknown) => {
  const safeSeed = encodeURIComponent(normalizeText(seed) || 'profile-user')
  return `https://api.dicebear.com/7.x/notionists/svg?seed=${safeSeed}`
}

const formatDate = (value: unknown): string => {
  const raw = normalizeText(value)
  if (!raw) return t('profilePage.common.dash')
  return formatDateTimeByLocale(raw, locale.value)
}

const formatWorkStatus = (value: unknown): string => {
  const raw = normalizeText(value)
  if (!raw) return t('profilePage.novels.statusUnknown')

  const normalized = raw.toLowerCase()
  if (normalized === '2' || normalized === 'completed' || normalized === 'complete' || normalized === 'finished' || normalized === '已完结' || normalized === '完结') {
    return t('profilePage.novels.statusCompleted')
  }
  if (normalized === '1' || normalized === 'ongoing' || normalized === 'in_progress' || normalized === 'running' || normalized === '连载中' || normalized === '连载') {
    return t('profilePage.novels.statusOngoing')
  }
  return raw
}

const fillForm = (data: UserProfilePayload) => {
  form.name = normalizeText(data.name)
  form.first_name = normalizeText(data.first_name)
  form.last_name = normalizeText(data.last_name)
  form.phone = normalizeText(data.phone)
  form.gender = normalizeText(data.gender)
  form.bio = normalizeText(data.bio)
  form.ai_content_visibility = normalizeVisibility(data.ai_content_visibility)
  avatarPreview.value = normalizeText(data.avatar_url)
  avatarFile.value = null
  shouldRemoveAvatar.value = false
}

const loadDashboard = async () => {
  if (!authStore.isAuthenticated) return
  loading.value = true
  error.value = ''
  message.value = ''
  try {
    const payload = await fetchMyDashboard(20)
    dashboard.value = payload
    fillForm(payload.profile)
    authStore.applyProfilePayload(payload.profile)
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || t('profilePage.messages.loadFailed')
  } finally {
    loading.value = false
  }
}

const handleAvatarChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const allowedTypes = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif'])
  if (!allowedTypes.has(file.type)) {
    error.value = t('profilePage.avatar.invalidType')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = t('profilePage.avatar.tooLarge')
    return
  }

  avatarFile.value = file
  shouldRemoveAvatar.value = false
  avatarPreview.value = URL.createObjectURL(file)
  error.value = ''
}

const removeAvatar = () => {
  avatarFile.value = null
  avatarPreview.value = ''
  shouldRemoveAvatar.value = true
}

const saveProfile = async () => {
  if (!authStore.isAuthenticated) return
  saving.value = true
  error.value = ''
  message.value = ''

  const payload = {
    name: normalizeText(form.name).slice(0, 80),
    first_name: normalizeText(form.first_name).slice(0, 30),
    last_name: normalizeText(form.last_name).slice(0, 30),
    phone: normalizeText(form.phone).slice(0, 20),
    gender: normalizeText(form.gender).slice(0, 20),
    bio: normalizeText(form.bio).slice(0, 500),
    sandbox_enabled: true,
    ai_content_visibility: normalizeVisibility(form.ai_content_visibility),
    remove_avatar: shouldRemoveAvatar.value,
  }

  try {
    const updated = avatarFile.value
      ? await updateMyProfileWithAvatar(payload, avatarFile.value)
      : await updateMyProfile(payload)

    authStore.applyProfilePayload(updated)
    if (dashboard.value) {
      dashboard.value.profile = updated
    }
    fillForm(updated)
    message.value = t('profilePage.messages.profileSaved')
  } catch (err: any) {
    error.value = parseRequestError(err)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadDashboard()
  }
})

watch(
  () => authStore.isAuthenticated,
  (loggedIn) => {
    if (loggedIn) {
      loadDashboard()
    } else {
      dashboard.value = null
      avatarPreview.value = ''
    }
  }
)
</script>
