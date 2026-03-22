<template>
  <div class="min-h-screen py-12">
    <div class="container mx-auto max-w-6xl px-4">
      <section class="surface-card mb-8 p-6 md:p-10" v-motion-reveal="{ y: 20 }">
        <p class="mb-3 text-xs uppercase tracking-[0.16em] text-muted-foreground">
          {{ t("rechargeGuidePage.badge") }}
        </p>
        <h1 class="mb-4 text-3xl font-bold text-foreground md:text-5xl">
          {{ t("rechargeGuidePage.title") }}
        </h1>
        <p class="max-w-3xl text-base leading-relaxed text-muted-foreground md:text-lg">
          {{ t("rechargeGuidePage.subtitle") }}
        </p>
      </section>

      <section class="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <article class="surface-card p-5 md:p-6" v-motion-reveal="{ delay: 40, y: 18 }">
          <h2 class="mb-3 text-xl font-semibold text-foreground">{{ t("rechargeGuidePage.method1.title") }}</h2>
          <p class="mb-4 text-sm text-muted-foreground">{{ t("rechargeGuidePage.method1.desc") }}</p>

          <div class="mb-5 rounded-2xl border border-border bg-card/60 p-3">
            <img
              :src="wechatImageError ? wechatFallbackImage : wechatImage"
              :alt="t('rechargeGuidePage.method1.qrAlt')"
              class="w-full rounded-xl bg-white object-contain"
              @error="wechatImageError = true"
            />
          </div>

          <ol class="space-y-2 text-sm leading-6 text-muted-foreground">
            <li>1. {{ t("rechargeGuidePage.method1.step1") }}</li>
            <li>2. {{ t("rechargeGuidePage.method1.step2") }}</li>
            <li>3. {{ t("rechargeGuidePage.method1.step3") }}</li>
            <li>4. {{ t("rechargeGuidePage.method1.step4") }}</li>
          </ol>
        </article>

        <article class="surface-card p-5 md:p-6" v-motion-reveal="{ delay: 90, y: 18 }">
          <h2 class="mb-3 text-xl font-semibold text-foreground">{{ t("rechargeGuidePage.method2.title") }}</h2>
          <p class="mb-4 text-sm text-muted-foreground">{{ t("rechargeGuidePage.method2.desc") }}</p>

          <div class="mb-5 rounded-2xl border border-border bg-card/60 p-3">
            <img
              :src="xianyuImageError ? xianyuFallbackImage : xianyuImage"
              :alt="t('rechargeGuidePage.method2.qrAlt')"
              class="w-full rounded-xl bg-white object-contain"
              @error="xianyuImageError = true"
            />
          </div>

          <ol class="space-y-2 text-sm leading-6 text-muted-foreground">
            <li>1. {{ t("rechargeGuidePage.method2.step1") }}</li>
            <li>2. {{ t("rechargeGuidePage.method2.step2") }}</li>
            <li>3. {{ t("rechargeGuidePage.method2.step3") }}</li>
            <li>4. {{ t("rechargeGuidePage.method2.step4") }}</li>
          </ol>
        </article>
      </section>

      <section class="surface-card mb-8 p-6 md:p-8" v-motion-reveal="{ delay: 120, y: 18 }">
        <h2 class="mb-4 text-xl font-semibold text-foreground">{{ t("rechargeGuidePage.orderDetails.title") }}</h2>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div class="rounded-xl border border-border bg-card p-4">
            <h3 class="mb-2 text-sm font-semibold text-foreground">{{ t("rechargeGuidePage.orderDetails.templateTitle") }}</h3>
            <p class="text-sm leading-6 text-muted-foreground">
              {{ t("rechargeGuidePage.orderDetails.templateLine1") }}<br />
              {{ t("rechargeGuidePage.orderDetails.templateLine2") }}<br />
              {{ t("rechargeGuidePage.orderDetails.templateLine3") }}<br />
              {{ t("rechargeGuidePage.orderDetails.templateLine4") }}<br />
              {{ t("rechargeGuidePage.orderDetails.templateLine5") }}
            </p>
          </div>
          <div class="rounded-xl border border-border bg-card p-4">
            <h3 class="mb-2 text-sm font-semibold text-foreground">{{ t("rechargeGuidePage.orderDetails.deliveryTitle") }}</h3>
            <p class="text-sm leading-6 text-muted-foreground">
              {{ t("rechargeGuidePage.orderDetails.deliveryLine1") }}<br />
              {{ t("rechargeGuidePage.orderDetails.deliveryLine2") }}<br />
              {{ t("rechargeGuidePage.orderDetails.deliveryLine3") }}
            </p>
          </div>
        </div>
      </section>

      <section class="surface-card p-6 md:p-8" v-motion-reveal="{ delay: 160, y: 18 }">
        <h2 class="mb-3 text-xl font-semibold text-foreground">{{ t("rechargeGuidePage.security.title") }}</h2>
        <ul class="mb-6 space-y-2 text-sm leading-6 text-muted-foreground">
          <li>1. {{ t("rechargeGuidePage.security.item1") }}</li>
          <li>2. {{ t("rechargeGuidePage.security.item2") }}</li>
          <li>3. {{ t("rechargeGuidePage.security.item3") }}</li>
        </ul>

        <div class="flex flex-wrap gap-3">
          <RouterLink
            to="/customer-service"
            class="inline-flex items-center justify-center rounded-lg bg-primary px-5 py-2.5 font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
          >
            {{ t("rechargeGuidePage.actions.contactSupport") }}
          </RouterLink>
          <RouterLink
            to="/"
            class="inline-flex items-center justify-center rounded-lg border border-border px-5 py-2.5 font-semibold text-foreground transition-colors hover:bg-muted"
          >
            {{ t("rechargeGuidePage.actions.backHome") }}
          </RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const wechatImage = "/guide/wechat-qr.png";
const xianyuImage = "/guide/xianyu-card.png";
const wechatFallbackImage = "/guide/wechat-qr-placeholder.svg";
const xianyuFallbackImage = "/guide/xianyu-card-placeholder.svg";

const wechatImageError = ref(false);
const xianyuImageError = ref(false);
</script>
