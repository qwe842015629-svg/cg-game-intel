<template>
  <section class="py-12">
    <div class="container mx-auto px-4 max-w-3xl">
      <div class="rounded-2xl border border-border bg-card p-6 md:p-8 shadow-sm">
        <h1 class="text-2xl md:text-3xl font-bold">{{ $t('siteName') }}</h1>
        <p class="mt-2 text-muted-foreground">
          {{ $t('i18nDemo.subtitle') }}
        </p>

        <div class="mt-6 grid gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-2">
            <span class="text-sm font-medium text-muted-foreground">{{ $t('i18nDemo.languageLabel') }}</span>
            <select
              :value="languageStore.currentLocale"
              class="rounded-lg border border-border bg-background px-3 py-2"
              @change="onLocaleChange"
            >
              <option
                v-for="locale in languageStore.availableLocales"
                :key="locale.code"
                :value="locale.code"
              >
                {{ locale.name }} ({{ locale.code }})
              </option>
            </select>
          </label>

          <div class="rounded-lg border border-border bg-background p-3 text-sm">
            <p><span class="font-semibold">{{ $t('i18nDemo.currentLocaleLabel') }}</span> {{ languageStore.currentLocale }}</p>
            <p class="mt-1"><span class="font-semibold">{{ $t('i18nDemo.currentUrlLabel') }}</span> {{ route.fullPath }}</p>
          </div>
        </div>

        <div class="mt-6 grid gap-3 md:grid-cols-2">
          <div class="rounded-lg border border-border bg-background p-4">
            <h2 class="font-semibold">{{ $t('home') }} / {{ $t('games') }} / {{ $t('news') }}</h2>
            <p class="mt-1 text-sm text-muted-foreground">{{ $t('support') }} / {{ $t('about') }}</p>
          </div>
          <div class="rounded-lg border border-border bg-background p-4">
            <h2 class="font-semibold">{{ $t('coreFeatures') }}</h2>
            <p class="mt-1 text-sm text-muted-foreground">{{ $t('experienceNextGen') }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useLanguageStore } from '../stores/language'
import type { LocaleCode } from '../i18n/locales'
import { withLocalePrefix } from '../i18n/locale-routing'

const route = useRoute()
const router = useRouter()
const languageStore = useLanguageStore()

const onLocaleChange = async (event: Event) => {
  const nextLocale = (event.target as HTMLSelectElement).value as LocaleCode
  const nextPath = withLocalePrefix(route.fullPath, nextLocale)

  await languageStore.setLocale(nextLocale)

  if (nextPath !== route.fullPath) {
    await router.replace(nextPath)
  }
}
</script>
