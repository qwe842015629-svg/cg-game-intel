<template>
  <div class="min-h-screen py-10">
    <div class="container mx-auto px-4 max-w-7xl">
      <section class="text-center mb-8">
        <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground mb-3">Recharge</p>
        <h1 class="text-3xl md:text-4xl font-bold text-foreground mb-3">游戏充值</h1>
        <p class="text-muted-foreground">选择游戏、填写账号并完成支付，流程清晰、快速到账。</p>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <aside class="lg:col-span-1">
          <div class="surface-card p-5" v-motion-reveal="{ y: 22 }">
            <div class="mb-4">
              <h2 class="text-lg font-semibold text-foreground mb-1">选择游戏</h2>
              <p class="text-sm text-muted-foreground">支持搜索并快速选择</p>
            </div>

            <div class="mb-4 relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="$t('search')"
                class="w-full h-10 pl-10 pr-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
            </div>

            <div class="space-y-2 max-h-[560px] overflow-y-auto pr-1 custom-scrollbar">
              <button
                v-for="game in filteredGames"
                :key="game.id"
                @click="selectedGame = game"
                :class="[
                  'w-full p-3 rounded-lg border text-left transition-colors',
                  selectedGame?.id === game.id
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:bg-muted'
                ]"
              >
                <div class="flex items-center gap-3">
                  <img
                    :src="game.icon"
                    :alt="game.name"
                    class="w-11 h-11 rounded-lg border border-border bg-muted object-cover"
                  />
                  <div class="min-w-0 flex-1">
                    <p class="font-semibold text-foreground truncate">{{ game.name }}</p>
                    <p class="text-xs text-muted-foreground mt-0.5">{{ $t(getCategoryKey(game.category)) }}</p>
                  </div>
                  <ChevronRight class="w-4 h-4 text-muted-foreground" />
                </div>
              </button>
            </div>
          </div>
        </aside>

        <section class="lg:col-span-2 space-y-5">
          <div v-if="!selectedGame" class="surface-card p-8 text-center" v-motion-reveal="{ delay: 70, y: 20 }">
            <Gamepad2 class="w-14 h-14 mx-auto text-muted-foreground mb-4" />
            <h2 class="text-2xl font-semibold text-foreground mb-2">请先选择游戏</h2>
            <p class="text-muted-foreground mb-6">选择后即可填写账号、金额与付款方式。</p>
            <ol class="max-w-md mx-auto text-left text-sm text-muted-foreground space-y-2">
              <li class="flex items-start gap-2"><span class="font-semibold text-foreground">1.</span><span>选择游戏</span></li>
              <li class="flex items-start gap-2"><span class="font-semibold text-foreground">2.</span><span>填写账号信息</span></li>
              <li class="flex items-start gap-2"><span class="font-semibold text-foreground">3.</span><span>选择金额与支付方式</span></li>
              <li class="flex items-start gap-2"><span class="font-semibold text-foreground">4.</span><span>确认订单并完成充值</span></li>
            </ol>
          </div>

          <template v-else>
            <div class="surface-card p-5" v-motion-reveal="{ delay: 40, y: 16 }">
              <div class="flex items-center gap-4">
                <img
                  :src="selectedGame.icon"
                  :alt="selectedGame.name"
                  class="w-14 h-14 rounded-xl border border-border bg-muted object-cover"
                />
                <div class="flex-1">
                  <h3 class="text-xl font-semibold text-foreground">{{ selectedGame.name }}</h3>
                  <p class="text-sm text-muted-foreground">{{ $t(getCategoryKey(selectedGame.category)) }}</p>
                </div>
                <button
                  @click="selectedGame = null"
                  class="px-4 py-2 rounded-lg border border-border text-sm font-medium text-foreground hover:bg-muted transition-colors"
                >
                  重新选择
                </button>
              </div>
            </div>

            <div class="surface-card p-5" v-motion-reveal="{ delay: 70, y: 16 }">
              <h3 class="text-lg font-semibold text-foreground mb-4">账号信息</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label class="block">
                  <span class="block text-sm text-foreground mb-2">{{ $t('gameAccountId') }} *</span>
                  <input
                    v-model="accountId"
                    type="text"
                    :placeholder="$t('enterAccountId')"
                    class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>
                <label class="block">
                  <span class="block text-sm text-foreground mb-2">{{ $t('serverOptional') }}</span>
                  <input
                    v-model="server"
                    type="text"
                    :placeholder="$t('enterServer')"
                    class="w-full h-11 px-3 rounded-lg border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
                  />
                </label>
              </div>
            </div>

            <div class="surface-card p-5" v-motion-reveal="{ delay: 100, y: 16 }">
              <h3 class="text-lg font-semibold text-foreground mb-4">充值金额</h3>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                <button
                  v-for="amount in rechargeAmounts"
                  :key="amount.value"
                  @click="selectedAmount = amount"
                  :class="[
                    'p-4 rounded-lg border text-left transition-colors relative',
                    selectedAmount?.value === amount.value
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:bg-muted'
                  ]"
                >
                  <p class="text-xl font-bold text-foreground">¥{{ amount.value }}</p>
                  <p class="text-xs text-muted-foreground mt-1">{{ amount.bonus }}</p>
                  <p v-if="amount.discount" class="text-xs text-primary mt-1">{{ amount.discount }}</p>
                  <span
                    v-if="amount.hot"
                    class="absolute top-2 right-2 text-[10px] px-1.5 py-0.5 rounded bg-primary text-primary-foreground"
                  >
                    热门
                  </span>
                </button>
              </div>
            </div>

            <div class="surface-card p-5" v-motion-reveal="{ delay: 130, y: 16 }">
              <h3 class="text-lg font-semibold text-foreground mb-4">支付方式</h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  v-for="method in paymentMethods"
                  :key="method.id"
                  @click="selectedPayment = method"
                  :class="[
                    'rounded-lg border p-3 flex flex-col items-center gap-2 transition-colors',
                    selectedPayment?.id === method.id
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:bg-muted'
                  ]"
                >
                  <component :is="method.icon" class="w-5 h-5 text-foreground" />
                  <span class="text-sm text-foreground">{{ $t(method.name) }}</span>
                </button>
              </div>
            </div>

            <div class="surface-card p-5" v-motion-reveal="{ delay: 160, y: 16 }">
              <button
                v-magnetic="{ strength: 0.22, max: 14 }"
                @click="handleSubmit"
                :disabled="!canSubmit"
                :class="[
                  'w-full h-12 rounded-lg font-semibold transition-colors',
                  canSubmit
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'bg-muted text-muted-foreground cursor-not-allowed'
                ]"
              >
                {{ $t('confirmRecharge') }}{{ selectedAmount ? ` ¥${selectedAmount.value}` : '' }}
              </button>

              <ul class="mt-4 space-y-1 text-sm text-muted-foreground">
                <li>{{ $t('rechargeTime') }}</li>
                <li>{{ $t('verifyAccount') }}</li>
                <li>{{ $t('customerService247') }}</li>
              </ul>
            </div>
          </template>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Gamepad2, Search, ChevronRight, CreditCard, Wallet, Smartphone, Laptop } from 'lucide-vue-next'

interface Game {
  id: number
  name: string
  category: string
  icon: string
}

interface RechargeAmount {
  value: number
  bonus: string
  hot?: boolean
  discount?: string
}

interface PaymentMethod {
  id: string
  name: string
  icon: any
}

const searchQuery = ref('')

const games = ref<Game[]>([
  { id: 1, name: '王者荣耀', category: 'MOBA', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=王者' },
  { id: 2, name: '和平精英', category: '射击', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=和平' },
  { id: 3, name: '原神', category: 'RPG', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=原神' },
  { id: 4, name: '英雄联盟手游', category: 'MOBA', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=LOL' },
  { id: 5, name: '穿越火线', category: '射击', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=CF' },
  { id: 6, name: '地下城与勇士', category: 'RPG', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=DNF' },
  { id: 7, name: '崩坏：星穹铁道', category: 'RPG', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=星铁' },
  { id: 8, name: '光遇', category: '冒险', icon: 'https://placehold.co/88x88/e2e8f0/475569?text=光遇' },
])

const filteredGames = computed(() => {
  if (!searchQuery.value) return games.value
  return games.value.filter((game) => game.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const selectedGame = ref<Game | null>(null)
const accountId = ref('')
const server = ref('')

const rechargeAmounts: RechargeAmount[] = [
  { value: 6, bonus: '60 钻石' },
  { value: 30, bonus: '300 钻石' },
  { value: 68, bonus: '680 钻石', hot: true },
  { value: 128, bonus: '1280 钻石', discount: '送 28 钻石' },
  { value: 328, bonus: '3280 钻石', discount: '送 128 钻石' },
  { value: 648, bonus: '6480 钻石', hot: true, discount: '送 248 钻石' },
]

const selectedAmount = ref<RechargeAmount | null>(null)

const paymentMethods: PaymentMethod[] = [
  { id: 'wechat', name: 'wechatPay', icon: Smartphone },
  { id: 'alipay', name: 'alipay', icon: Wallet },
  { id: 'card', name: 'bankCard', icon: CreditCard },
  { id: 'online', name: 'onlineBanking', icon: Laptop },
]

const selectedPayment = ref<PaymentMethod | null>(null)

const canSubmit = computed(() => {
  return selectedGame.value && accountId.value && selectedAmount.value && selectedPayment.value
})

const getCategoryKey = (category: string): string => {
  const categoryMap: Record<string, string> = {
    MOBA: 'mobaCategory',
    RPG: 'rpgCategory',
    射击: 'shootingCategory',
    策略: 'strategyCategory',
    冒险: 'adventureCategory',
  }
  return categoryMap[category] || 'gameCategory'
}

const handleSubmit = () => {
  if (!canSubmit.value) return

  alert('充值功能开发中，后续将接入真实支付流程。')
  console.log({
    game: selectedGame.value,
    accountId: accountId.value,
    server: server.value,
    amount: selectedAmount.value,
    payment: selectedPayment.value,
  })
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--primary-color) 48%, #94a3b8 52%);
  border-radius: 999px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
</style>
