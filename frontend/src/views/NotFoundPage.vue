<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center px-4 py-16">
    <div class="w-full max-w-2xl rounded-2xl border border-border bg-card p-8 text-center">
      <p class="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-3">
        404
      </p>
      <h1 class="text-3xl md:text-4xl font-bold text-foreground mb-3">
        {{ t('notFoundPage.title') }}
      </h1>
      <p class="text-muted-foreground mb-8">
        {{ t('notFoundPage.description') }}
      </p>

      <div class="flex flex-wrap items-center justify-center gap-3">
        <RouterLink
          :to="localizedPath('/')"
          class="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          {{ t('notFoundPage.backHome') }}
        </RouterLink>
        <RouterLink
          :to="localizedPath('/articles')"
          class="px-4 py-2 rounded-lg border border-border text-foreground hover:bg-muted transition-colors"
        >
          {{ t('notFoundPage.toArticles') }}
        </RouterLink>
        <RouterLink
          :to="localizedPath('/recharge')"
          class="px-4 py-2 rounded-lg border border-border text-foreground hover:bg-muted transition-colors"
        >
          {{ t('notFoundPage.toRecharge') }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { withLocalePrefix } from '../i18n/locale-routing'
import { normalizeLocaleCode } from '../i18n/locale-utils'

const { t, locale } = useI18n()

const localizedPath = (path: string): string => withLocalePrefix(path, normalizeLocaleCode(locale.value))
</script>

