﻿<template>
  <RouterLink :to="`/games/${game.slug || game.id}`" class="group block h-full">
    <div class="bg-card hover:bg-card/80 border border-border rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 h-full flex flex-col items-center text-center">
      
      <!-- Game Icon (App Store Style) -->
      <div class="w-24 h-24 mb-4 relative">
        <div class="w-full h-full rounded-[22px] overflow-hidden shadow-md group-hover:shadow-xl transition-shadow duration-300 bg-muted">
          <img
            v-if="resolvedImage"
            :src="resolvedImage"
            :data-fallbacks="fallbackImages"
            :data-placeholder="placeholderImage"
            :alt="game.name || game.title"
            class="w-full h-full object-cover"
            loading="lazy"
            @error="handleImageError"
          />
          <div v-else class="w-full h-full flex items-center justify-center bg-gray-200 text-gray-400">
             <span class="text-xs">无图标</span>
          </div>
        </div>
      </div>

      <!-- Game Info -->
      <div class="flex-1 w-full">
        <h3 class="text-foreground font-bold text-base mb-1 line-clamp-1 group-hover:text-primary transition-colors">
          {{ game.name || game.title }}
        </h3>
        <p class="text-muted-foreground text-xs mb-3 line-clamp-1">
          {{ game.categoryName || game.category_name }}
          <span v-if="game.platform"> • {{ game.platform }}</span>
        </p>
      </div>
      
      <!-- Action Button (Optional) -->
      <div class="w-full mt-2 flex items-center justify-center gap-3">
         <span class="inline-flex items-center rounded-full bg-amber-50 text-amber-600 px-2.5 py-1 text-xs font-semibold">
           ⭐ {{ gameRating }}
         </span>
         <span class="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-bold group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-300">
           {{ $t('immediateRecharge') }}
         </span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  game: any // Using any to support both legacy and new API structure temporarily
}

const props = defineProps<Props>()

const buildImageCandidates = (game: any): string[] => {
  const unique = new Set<string>()
  const candidates = [
    game?.icon_image_url,
    game?.icon_external_url,
    game?.image,
    game?.banner_image_url,
  ]

  for (const candidate of candidates) {
    const value = String(candidate || '').trim()
    if (value) unique.add(value)
  }

  return Array.from(unique)
}

const buildInlinePlaceholder = (label: string): string => {
  const safeLabel = (label || 'GAME').slice(0, 10)
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">
  <rect width="160" height="160" rx="28" fill="#f5f5f5"/>
  <rect x="1.5" y="1.5" width="157" height="157" rx="26.5" fill="none" stroke="#e5e7eb"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-size="14" font-family="Arial, sans-serif">${safeLabel}</text>
</svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

const placeholderImage = computed(() => {
  const fallbackTitle = String(props.game?.name || props.game?.title || 'GAME')
  return buildInlinePlaceholder(fallbackTitle)
})

const fallbackImages = computed(() => JSON.stringify(buildImageCandidates(props.game).slice(1)))

const resolvedImage = computed(() => {
  const candidates = buildImageCandidates(props.game)
  return candidates[0] || placeholderImage.value
})

const gameRating = computed(() => {
  const explicitRating = Number(props.game?.rating ?? props.game?.score ?? props.game?.stars)
  if (Number.isFinite(explicitRating) && explicitRating > 0) {
    return explicitRating.toFixed(1)
  }

  const viewCount = Number(props.game?.view_count || 0)
  if (Number.isFinite(viewCount) && viewCount > 0) {
    const derivedRating = Math.min(5, 4.2 + Math.log10(viewCount + 1) * 0.2)
    return derivedRating.toFixed(1)
  }

  return props.game?.is_hot || props.game?.hot ? '4.9' : '4.8'
})

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  let queue: string[] = []

  try {
    queue = JSON.parse(img.dataset.fallbacks || '[]')
  } catch {
    queue = []
  }

  const next = queue.shift()
  if (next) {
    img.dataset.fallbacks = JSON.stringify(queue)
    img.src = next
    return
  }

  const placeholder = img.dataset.placeholder || placeholderImage.value
  if (img.src !== placeholder) {
    img.src = placeholder
    return
  }

  img.onerror = null
}
</script>

<style scoped>
/* Smooth rounded corners for icons (Squircle-ish) */
.rounded-\[22px\] {
  border-radius: 22px;
}
</style>
