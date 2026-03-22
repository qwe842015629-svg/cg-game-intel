<template>
  <div class="min-h-screen py-10">
    <div class="container mx-auto px-4 max-w-5xl space-y-5">
      <section class="surface-card p-5">
        <button
          class="mb-3 px-3 py-1.5 rounded-md border border-border text-sm text-foreground hover:bg-muted"
          @click="goBack"
        >
          {{ t('rechargeApiProductPage.backToInventory') }}
        </button>
        <h1 class="text-2xl font-bold text-foreground">{{ displayProductName || t('rechargeApiProductPage.defaultTitle') }}</h1>
        <p class="mt-2 text-xs text-muted-foreground break-all">{{ t('rechargeApiProductPage.productIdLabel') }}: {{ productId }}</p>
      </section>

      <section v-if="loadingDetail" class="surface-card p-5">
        <p class="text-sm text-muted-foreground">{{ t('rechargeApiProductPage.loadingDetail') }}</p>
      </section>

      <section v-else-if="detailError" class="surface-card p-5 border border-red-200">
        <p class="text-sm text-red-600 break-all">{{ detailError }}</p>
      </section>

      <template v-else-if="detail">
        <section class="surface-card p-5 space-y-3">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div class="rounded-md bg-muted/40 px-3 py-2">
              <p class="text-xs text-muted-foreground">{{ t('rechargeApiProductPage.metrics.orderSupported') }}</p>
              <p class="font-semibold text-foreground">{{ detail.order_supported ? t('rechargeApiProductPage.metrics.yes') : t('rechargeApiProductPage.metrics.no') }}</p>
            </div>
            <div class="rounded-md bg-muted/40 px-3 py-2">
              <p class="text-xs text-muted-foreground">{{ t('rechargeApiProductPage.metrics.balanceProduct') }}</p>
              <p class="font-semibold text-foreground">{{ detail.is_balance ? t('rechargeApiProductPage.metrics.yes') : t('rechargeApiProductPage.metrics.no') }}</p>
            </div>
            <div class="rounded-md bg-muted/40 px-3 py-2">
              <p class="text-xs text-muted-foreground">{{ t('rechargeApiProductPage.metrics.availableVariations') }}</p>
              <p class="font-semibold text-foreground">{{ availableVariations.length }}</p>
            </div>
            <div class="rounded-md bg-muted/40 px-3 py-2">
              <p class="text-xs text-muted-foreground">{{ t('rechargeApiProductPage.metrics.totalVariations') }}</p>
              <p class="font-semibold text-foreground">{{ detail.variations.length }}</p>
            </div>
          </div>
        </section>

        <section class="surface-card p-5">
          <h2 class="text-lg font-semibold text-foreground mb-3">{{ t('rechargeApiProductPage.sections.selectDenomination') }}</h2>
          <p
            v-if="!availableVariations.length"
            class="mb-3 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-700"
          >
            {{ t('rechargeApiProductPage.hints.noSellableVariations') }}
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              v-for="variation in availableVariations"
              :key="variation.variation_id"
              class="rounded-lg border p-3 text-left transition-colors"
              :class="
                selectedVariationId === variation.variation_id
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:bg-muted'
              "
              @click="selectedVariationId = variation.variation_id"
            >
              <p class="font-semibold text-foreground">{{ resolveVariationName(variation) || variation.variation_id }}</p>
              <p class="text-sm text-muted-foreground mt-1">{{ formatPrice(variation.price) }}</p>
            </button>
          </div>
        </section>

        <section v-if="detail.fields.length" class="surface-card p-5">
          <h2 class="text-lg font-semibold text-foreground mb-3">{{ t('rechargeApiProductPage.sections.accountInfo') }}</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label v-for="field in detail.fields" :key="field.name" class="block">
              <span class="block text-sm text-foreground mb-2">
                {{ field.label || field.name }}
                <span v-if="field.required" class="text-red-500">*</span>
              </span>

              <select
                v-if="field.type === 'select' && field.options.length"
                v-model="dynamicFieldValues[field.name]"
                class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
              >
                <option value="">{{ t('rechargeApiProductPage.form.pleaseSelect') }}</option>
                <option v-for="option in field.options" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>

              <input
                v-else
                v-model="dynamicFieldValues[field.name]"
                :type="resolveInputType(field.type)"
                :placeholder="field.placeholder || field.name"
                class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
              />

              <p v-if="field.description" class="mt-1 text-xs text-muted-foreground">
                {{ field.description }}
              </p>
            </label>
          </div>
        </section>

        <section v-if="detail.is_balance" class="surface-card p-5">
          <h2 class="text-lg font-semibold text-foreground mb-3">{{ t('rechargeApiProductPage.sections.rechargeAmount') }}</h2>
          <input
            v-model="rechargeAmount"
            type="number"
            min="1"
            :placeholder="t('rechargeApiProductPage.form.rechargeAmountPlaceholder')"
            class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
        </section>

        <section class="surface-card p-5">
          <button
            class="w-full h-12 rounded-lg font-semibold transition-colors"
            :class="
              canSubmit
                ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                : 'bg-muted text-muted-foreground cursor-not-allowed'
            "
            :disabled="!canSubmit"
            @click="handleSubmit"
          >
            {{ submitting ? t('rechargeApiProductPage.actions.submitting') : t('rechargeApiProductPage.actions.startWechatPay') }}
          </button>

          <p v-if="submitError" class="mt-3 text-sm text-red-600 break-all">{{ submitError }}</p>

          <div v-if="wechatPaySession" class="mt-4 rounded-lg border border-emerald-200 bg-emerald-50/50 p-4">
            <p class="text-sm font-semibold text-emerald-700">
              {{ t('rechargeApiProductPage.payment.title', { orderNo: wechatPaySession.out_trade_no }) }}
            </p>
            <p class="mt-1 text-xs text-emerald-700/90">
              {{ t('rechargeApiProductPage.payment.hint') }}
            </p>

            <div class="mt-3 flex flex-col md:flex-row items-start gap-4">
              <img
                :src="wechatQrImageUrl"
                :alt="t('rechargeApiProductPage.payment.qrAlt')"
                class="h-44 w-44 rounded-md border border-emerald-200 bg-white p-2"
              />
              <div class="min-w-0 flex-1 space-y-2">
                <p class="text-xs text-emerald-800">
                  {{
                    t('rechargeApiProductPage.payment.statusLine', {
                      status: wechatPayStatusText,
                    })
                  }}
                </p>
                <p class="text-xs text-emerald-700 break-all">
                  {{ t('rechargeApiProductPage.payment.codeUrl') }}: {{ wechatPaySession.code_url }}
                </p>
                <div class="flex flex-wrap items-center gap-2 pt-1">
                  <button
                    class="px-3 py-1.5 rounded-md border border-emerald-300 text-xs text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                    :disabled="wechatPayChecking"
                    @click="checkWechatPayStatus(false)"
                  >
                    {{ wechatPayChecking ? t('rechargeApiProductPage.payment.checking') : t('rechargeApiProductPage.actions.checkPayStatus') }}
                  </button>
                  <button
                    class="px-3 py-1.5 rounded-md border border-emerald-300 text-xs text-emerald-700 hover:bg-emerald-100"
                    @click="clearWechatPaySession"
                  >
                    {{ t('rechargeApiProductPage.actions.clearPaySession') }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="createdOrder" class="mt-3 rounded-lg border border-border p-3 bg-muted/30">
            <p class="text-sm font-semibold text-foreground">{{ t('rechargeApiProductPage.order.title', { orderNo: createdOrder.out_trade_no }) }}</p>
            <p class="text-xs text-muted-foreground mt-1">
              {{
                t('rechargeApiProductPage.order.statusLine', {
                  status: createdOrder.status,
                  externalStatus: createdOrder.external_status || '-',
                })
              }}
            </p>
            <p v-if="createdOrder.error_message" class="text-xs text-red-500 mt-1">
              {{ createdOrder.error_message }}
            </p>
            <button
              class="mt-2 px-3 py-1.5 rounded-md border border-border text-xs hover:bg-muted"
              @click="refreshCreatedOrder"
            >
              {{ t('rechargeApiProductPage.actions.refreshOrderStatus') }}
            </button>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { formatCurrencyByLocale } from '../utils/intl'
import {
  createRechargeInventoryWechatPay,
  getChargeXInventoryProductDetail,
  getRechargeInventoryWechatPayStatus,
  getRechargeOrder,
  type ChargeXInventoryProductDetailResponse,
  type ChargeXInventoryVariation,
  type RechargeInventoryWechatPayCreateResponse,
  type RechargeOrderItem,
} from '../api/recharge'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t, locale } = useI18n()

const providerUuid = computed(() => String(route.params.providerUuid || '').trim())
const productId = computed(() => String(route.params.productId || '').trim())

const loadingDetail = ref(false)
const detailError = ref('')
const detail = ref<ChargeXInventoryProductDetailResponse | null>(null)

const selectedVariationId = ref('')
const dynamicFieldValues = reactive<Record<string, string>>({})
const rechargeAmount = ref('')

const submitting = ref(false)
const submitError = ref('')
const createdOrder = ref<RechargeOrderItem | null>(null)
const wechatPaySession = ref<RechargeInventoryWechatPayCreateResponse | null>(null)
const wechatPayChecking = ref(false)
const wechatPayStatus = ref<
  'success' | 'notpay' | 'userpaying' | 'closed' | 'payerror' | 'revoked' | 'refund' | 'unknown'
>('unknown')
const wechatPayPollTimer = ref<number | null>(null)

const displayProductName = computed(() => {
  if (!detail.value) return ''
  const lang = String(locale.value || '').toLowerCase()
  if (lang.startsWith('zh-cn') || lang === 'zh') {
    return detail.value.product_name_cn || detail.value.product_name_tw || detail.value.localized_name
  }
  if (lang.startsWith('zh-tw') || lang.includes('hant')) {
    return detail.value.product_name_tw || detail.value.product_name_cn || detail.value.localized_name
  }
  if (lang.startsWith('en')) {
    return detail.value.product_name_en || detail.value.localized_name || detail.value.product_name
  }
  return detail.value.localized_name || detail.value.product_name || detail.value.product_name_en
})

const availableVariations = computed(() => {
  return (detail.value?.variations || []).filter((row) => row.is_available)
})

const isWechatPayTerminal = (statusText: string): boolean => {
  return ['success', 'closed', 'payerror', 'revoked', 'refund'].includes(
    String(statusText || '').toLowerCase()
  )
}

const wechatQrImageUrl = computed(() => {
  const codeUrl = String(wechatPaySession.value?.code_url || '').trim()
  if (!codeUrl) return ''
  return `https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(
    codeUrl
  )}`
})

const wechatPayStatusText = computed(() => {
  const statusText = String(wechatPayStatus.value || '').toLowerCase()
  if (statusText === 'success') return t('rechargeApiProductPage.payment.status.success')
  if (statusText === 'notpay') return t('rechargeApiProductPage.payment.status.notpay')
  if (statusText === 'userpaying') return t('rechargeApiProductPage.payment.status.userpaying')
  if (statusText === 'closed') return t('rechargeApiProductPage.payment.status.closed')
  if (statusText === 'payerror') return t('rechargeApiProductPage.payment.status.payerror')
  if (statusText === 'revoked') return t('rechargeApiProductPage.payment.status.revoked')
  if (statusText === 'refund') return t('rechargeApiProductPage.payment.status.refund')
  return t('rechargeApiProductPage.payment.status.unknown')
})

const missingRequiredFields = computed(() => {
  const fields = detail.value?.fields || []
  return fields
    .filter((field) => field.required)
    .filter((field) => {
      const value = String(dynamicFieldValues[field.name] || '').trim()
      return !value
    })
    .map((field) => field.name)
})

const canSubmit = computed(() => {
  if (submitting.value) return false
  if (wechatPaySession.value && !isWechatPayTerminal(wechatPayStatus.value)) return false
  if (!detail.value || !detail.value.order_supported) return false
  if (!selectedVariationId.value) return false
  if (missingRequiredFields.value.length > 0) return false
  if (detail.value.is_balance && !(Number(rechargeAmount.value) > 0)) return false
  if (!authStore.isAuthenticated) return true
  return true
})

const resolveInputType = (fieldType: string): string => {
  const normalized = String(fieldType || '').toLowerCase()
  if (normalized === 'email') return 'email'
  if (normalized === 'tel') return 'tel'
  if (normalized === 'number') return 'number'
  return 'text'
}

const resolveVariationName = (variation: ChargeXInventoryVariation): string => {
  const lang = String(locale.value || '').toLowerCase()
  if (lang.startsWith('zh-cn') || lang === 'zh') {
    return variation.name_cn || variation.name_tw || variation.localized_name || variation.name
  }
  if (lang.startsWith('zh-tw') || lang.includes('hant')) {
    return variation.name_tw || variation.name_cn || variation.localized_name || variation.name
  }
  if (lang.startsWith('en')) {
    return variation.name_en || variation.localized_name || variation.name
  }
  return variation.localized_name || variation.name || variation.variation_id
}

const formatPrice = (value: string): string => {
  const number = Number(value || 0)
  return formatCurrencyByLocale(number, locale.value, 'USD')
}

const parseApiError = (error: any): string => {
  const data = error?.response?.data || {}
  if (typeof data.message === 'string' && data.message) {
    if (data.error_code) return `${data.error_code}: ${data.message}`
    return data.message
  }
  if (typeof data.detail === 'string' && data.detail) return data.detail
  return String(error?.message || t('rechargeApiProductPage.errors.createOrderFailed'))
}

const buildIdempotencyKey = (): string => {
  const random = Math.random().toString(36).slice(2, 10)
  return `inv_${Date.now()}_${random}`
}

const applyFieldDefaults = (): void => {
  Object.keys(dynamicFieldValues).forEach((key) => delete dynamicFieldValues[key])
  for (const field of detail.value?.fields || []) {
    dynamicFieldValues[field.name] = ''
  }
}

const stopWechatPayPolling = (): void => {
  if (wechatPayPollTimer.value === null) return
  window.clearInterval(wechatPayPollTimer.value)
  wechatPayPollTimer.value = null
}

const startWechatPayPolling = (): void => {
  stopWechatPayPolling()
  wechatPayPollTimer.value = window.setInterval(() => {
    void checkWechatPayStatus(true)
  }, 3000)
}

const clearWechatPaySession = (): void => {
  stopWechatPayPolling()
  wechatPaySession.value = null
  wechatPayStatus.value = 'unknown'
  wechatPayChecking.value = false
}

const checkWechatPayStatus = async (silent: boolean): Promise<void> => {
  const outTradeNo = String(wechatPaySession.value?.out_trade_no || '').trim()
  if (!outTradeNo) return
  if (wechatPayChecking.value) return

  wechatPayChecking.value = true
  try {
    const result = await getRechargeInventoryWechatPayStatus(outTradeNo)
    wechatPayStatus.value = result.pay_status || 'unknown'
    if (result.order?.out_trade_no) {
      createdOrder.value = result.order
    }

    if (isWechatPayTerminal(result.pay_status)) {
      stopWechatPayPolling()
      if (result.pay_status === 'success') {
        submitError.value = ''
      } else if (!silent) {
        submitError.value =
          result.trade_state_desc || t('rechargeApiProductPage.errors.wechatPayNotCompleted')
      }
    }
  } catch (error: any) {
    if (!silent) {
      submitError.value = parseApiError(error)
    }
  } finally {
    wechatPayChecking.value = false
  }
}

const loadDetail = async (): Promise<void> => {
  if (!providerUuid.value || !productId.value) {
    detailError.value = t('rechargeApiProductPage.errors.missingIdentifiers')
    return
  }

  loadingDetail.value = true
  detailError.value = ''
  try {
    const response = await getChargeXInventoryProductDetail({
      provider_uuid: providerUuid.value,
      product_id: productId.value,
    })
    detail.value = response
    const firstAvailable = (response.variations || []).find((row) => row.is_available)
    selectedVariationId.value = firstAvailable?.variation_id || ''
    applyFieldDefaults()
  } catch (error: any) {
    detailError.value = parseApiError(error)
    detail.value = null
  } finally {
    loadingDetail.value = false
  }
}

const handleSubmit = async (): Promise<void> => {
  submitError.value = ''
  if (!detail.value) return

  if (!authStore.isAuthenticated) {
    await router.push('/login')
    return
  }
  if (!canSubmit.value) return

  const payload: Record<string, any> = {
    provider_uuid: providerUuid.value,
    product_id: productId.value,
    variation_id: selectedVariationId.value,
    quantity: 1,
    idempotency_key: buildIdempotencyKey(),
    dynamic_fields: {},
  }

  for (const field of detail.value.fields || []) {
    const value = String(dynamicFieldValues[field.name] || '').trim()
    if (value) payload.dynamic_fields[field.name] = value
  }

  if (detail.value.is_balance) {
    payload.recharge_amount = Number(rechargeAmount.value || 0)
  }

  submitting.value = true
  try {
    clearWechatPaySession()
    const paymentSession = await createRechargeInventoryWechatPay(payload)
    wechatPaySession.value = paymentSession
    wechatPayStatus.value = paymentSession.pay_status || 'notpay'
    createdOrder.value = paymentSession.order || null

    if (isWechatPayTerminal(wechatPayStatus.value)) {
      await checkWechatPayStatus(false)
    } else {
      startWechatPayPolling()
    }
  } catch (error: any) {
    submitError.value = parseApiError(error)
    const failedOrder = error?.response?.data?.order
    if (failedOrder?.out_trade_no) {
      createdOrder.value = failedOrder
    }
  } finally {
    submitting.value = false
  }
}

const refreshCreatedOrder = async (): Promise<void> => {
  if (!createdOrder.value?.out_trade_no) return
  try {
    const updated = await getRechargeOrder(createdOrder.value.out_trade_no)
    createdOrder.value = updated
  } catch (error: any) {
    submitError.value = parseApiError(error)
  }
}

const goBack = async (): Promise<void> => {
  await router.push('/recharge-api')
}

watch(
  () => [providerUuid.value, productId.value],
  () => {
    clearWechatPaySession()
    createdOrder.value = null
    submitError.value = ''
    loadDetail().catch(() => {})
  }
)

onMounted(async () => {
  await loadDetail()
})

onBeforeUnmount(() => {
  stopWechatPayPolling()
})
</script>
