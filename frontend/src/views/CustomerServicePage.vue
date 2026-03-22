<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mx-auto max-w-4xl">
      <h1
        class="mb-8 text-3xl font-bold"
        :contenteditable="isEditMode"
        @blur="handleInlineEdit($event, 'page_title')"
      >
        {{ getPageConfig('page_title', pageConfigData.page_title || t('customerServicePage.pageTitle')) }}
      </h1>
      <p
        v-if="getPageConfig('page_description', pageConfigData.page_description || t('customerServicePage.pageDescription'))"
        class="mb-8 text-muted-foreground"
        :contenteditable="isEditMode"
        @blur="handleInlineEdit($event, 'page_description')"
      >
        {{ getPageConfig('page_description', pageConfigData.page_description || t('customerServicePage.pageDescription')) }}
      </p>

      <div v-if="pageConfigData.show_contact_methods" class="mb-12 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div v-for="method in contactMethods" :key="method.id" class="rounded-lg border border-border bg-card p-6">
          <component :is="getIconComponent(method.icon)" class="mb-4 h-12 w-12 text-primary" />
          <h3 class="mb-2 text-lg font-bold">{{ method.title }}</h3>
          <p class="mb-4 text-muted-foreground">{{ method.description }}</p>

          <Button
            v-if="method.contact_type === 'online_chat'"
            variant="default"
            @click="supportChatOpen = true"
          >
            {{ method.button_text || t('customerServicePage.startChat') }}
          </Button>

          <Button
            v-else-if="isImageButton(method)"
            variant="outline"
            @click="openQrDialog(method)"
          >
            {{ method.button_text || t('customerServicePage.buttonFallback') }}
          </Button>

          <Button
            v-else-if="method.button_link && method.button_link !== '#'"
            variant="outline"
            @click="openMethodLink(method)"
          >
            {{ method.button_text || t('customerServicePage.buttonFallback') }}
          </Button>

          <Button v-else variant="outline" disabled>
            {{ method.button_text || t('customerServicePage.buttonFallback') }}
          </Button>
        </div>
      </div>

      <Dialog v-model="qrDialogOpen">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-foreground">{{ qrDialogTitle }}</h3>
            <button
              type="button"
              class="text-muted-foreground transition-colors hover:text-foreground"
              @click="qrDialogOpen = false"
            >
              {{ t('customerServicePage.close') }}
            </button>
          </div>
          <div class="rounded-xl border border-border bg-card p-3">
            <img
              :src="qrDialogImage"
              :alt="qrDialogTitle"
              class="mx-auto max-h-[70vh] w-full rounded-lg bg-white object-contain"
            />
          </div>
          <p class="text-center text-sm text-muted-foreground">{{ qrDialogTip }}</p>
        </div>
      </Dialog>

      <SupportChatDialog v-model="supportChatOpen" />

      <div v-if="pageConfigData.show_faq" class="rounded-lg border border-border bg-card p-6">
        <h2
          class="mb-6 text-2xl font-bold"
          :contenteditable="isEditMode"
          @blur="handleInlineEdit($event, 'faq_title')"
        >
          {{ getPageConfig('faq_title', pageConfigData.faq_title || t('customerServicePage.faqTitle')) }}
        </h2>

        <div v-if="loadingFAQs" class="py-8 text-center">
          <p class="text-muted-foreground">{{ t('customerServicePage.loading') }}</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="(faq, index) in faqs"
            :key="faq.id"
            :class="['pb-4', index < faqs.length - 1 ? 'border-b border-border' : '']"
          >
            <h3 class="mb-2 font-semibold">{{ faq.question }}</h3>
            <p class="text-muted-foreground">{{ faq.answer }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Mail, MessageCircle, MessageSquare, Phone } from 'lucide-vue-next'
import Button from '../components/ui/Button.vue'
import Dialog from '../components/ui/Dialog.vue'
import SupportChatDialog from '../components/customer/SupportChatDialog.vue'
import { getContactMethods, getCustomerServiceConfig, getFAQs } from '../api/customerService'
import type { ContactMethod, CustomerServiceConfig, FAQ } from '../api/customerService'
import { useVisualEditor } from '../composables/useVisualEditor'
import { withLocalePrefix } from '../i18n/locale-routing'
import { normalizeLocaleCode } from '../i18n/locale-utils'

const { isEditMode, getPageConfig, handleInlineEdit } = useVisualEditor('customer_service', '客服中心页面')
const { t, locale } = useI18n()

const contactMethods = ref<ContactMethod[]>([])
const faqs = ref<FAQ[]>([])
const pageConfigData = ref<Partial<CustomerServiceConfig>>({
  page_title: '',
  page_description: '',
  show_contact_methods: true,
  show_faq: true,
  faq_title: '',
})
const loadingFAQs = ref(true)

const qrDialogOpen = ref(false)
const qrDialogImage = ref('')
const qrDialogTitle = ref(t('customerServicePage.qrDefaultTitle'))
const qrDialogTip = ref(t('customerServicePage.qrDefaultTip'))

const supportChatOpen = ref(false)

const normalizeBase = (value: string) => value.replace(/\/+$/, '')
const BACKEND_ORIGIN = normalizeBase(
  (import.meta.env.VITE_BACKEND_TARGET as string | undefined)?.trim() || 'http://127.0.0.1:8000'
)

const getIconComponent = (iconName: string) => {
  const icons: Record<string, any> = {
    MessageCircle,
    Mail,
    Phone,
    MessageSquare,
  }
  return icons[iconName] || MessageCircle
}

const isImageLink = (value: string) => /\.(png|jpe?g|gif|webp|svg)(\?.*)?$/i.test(value)

const resolveButtonLink = (raw: string): string => {
  const value = String(raw || '').trim()
  if (!value || value === '#') return ''
  if (/^https?:\/\//i.test(value)) return value
  if (value.startsWith('//')) return `https:${value}`
  if (value.startsWith('mailto:') || value.startsWith('tel:')) return value
  if (value.startsWith('/media/')) return `${BACKEND_ORIGIN}${value}`
  if (value.startsWith('media/')) return `${BACKEND_ORIGIN}/${value}`
  return value
}

const isImageButton = (method: ContactMethod): boolean => {
  const resolved = resolveButtonLink(method.button_link)
  return Boolean(resolved) && (isImageLink(resolved) || resolved.includes('/media/'))
}

const openQrDialog = (method: ContactMethod) => {
  const resolved = resolveButtonLink(method.button_link)
  if (!resolved) return
  qrDialogImage.value = resolved
  qrDialogTitle.value = method.title || t('customerServicePage.qrDefaultTitle')
  qrDialogTip.value = method.description || t('customerServicePage.qrDefaultTip')
  qrDialogOpen.value = true
}

const openMethodLink = (method: ContactMethod) => {
  const resolved = resolveButtonLink(method.button_link)
  if (!resolved) return
  if (/^https?:\/\//i.test(resolved)) {
    window.open(resolved, '_blank', 'noopener,noreferrer')
    return
  }
  if (resolved.startsWith('/')) {
    window.location.href = withLocalePrefix(resolved, normalizeLocaleCode(locale.value))
    return
  }
  window.location.href = resolved
}

const loadData = async () => {
  try {
    const config = await getCustomerServiceConfig()
    pageConfigData.value = config

    if (config.show_contact_methods) {
      contactMethods.value = await getContactMethods()
    }

    if (config.show_faq) {
      loadingFAQs.value = true
      faqs.value = await getFAQs()
    }
  } catch (error) {
    console.error(t('customerServicePage.loadErrorLog'), error)
  } finally {
    loadingFAQs.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
