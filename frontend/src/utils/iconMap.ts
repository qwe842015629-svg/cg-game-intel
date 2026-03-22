import type { Component } from 'vue'
import { Gamepad2, Globe2, Landmark, Palmtree } from 'lucide-vue-next'

interface CategoryLike {
  id?: string
  code?: string
  nameKey?: string
  name?: string
  icon?: string
}

const GAME_CATEGORY_ICON_MAP: Record<string, Component> = {
  all: Gamepad2,
  game: Gamepad2,
  games: Gamepad2,
  international: Globe2,
  global: Globe2,
  world: Globe2,
  'hongkong-taiwan': Landmark,
  hongkong: Landmark,
  taiwan: Landmark,
  hk: Landmark,
  tw: Landmark,
  'southeast-asia': Palmtree,
  southeast: Palmtree,
  sea: Palmtree,
}

const normalize = (value: unknown): string =>
  String(value || '')
    .trim()
    .toLowerCase()

export const resolveGameCategoryIcon = (category: CategoryLike | string): Component => {
  const token = typeof category === 'string'
    ? category
    : [category.code, category.id, category.nameKey, category.name, category.icon]
        .filter(Boolean)
        .join('|')

  const normalized = normalize(token)
  for (const [key, icon] of Object.entries(GAME_CATEGORY_ICON_MAP)) {
    if (normalized.includes(key)) return icon
  }

  if (normalized.includes('🌍')) return Globe2
  if (normalized.includes('🏮')) return Landmark
  if (normalized.includes('🌴')) return Palmtree
  return Gamepad2
}
