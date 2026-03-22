<template>
  <button
    :class="[
      'ui-btn inline-flex items-center justify-center gap-2 whitespace-nowrap',
      variantClasses,
      sizeClasses,
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'default',
  disabled: false,
})

const variantClasses = computed(() => {
  const variants = {
    default: 'ui-btn--default',
    destructive: 'ui-btn--destructive',
    outline: 'ui-btn--outline',
    secondary: 'ui-btn--secondary',
    ghost: 'ui-btn--ghost',
    link: 'ui-btn--link',
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    default: 'ui-btn-size-default',
    sm: 'ui-btn-size-sm',
    lg: 'ui-btn-size-lg',
    icon: 'ui-btn-size-icon',
  }
  return sizes[props.size]
})
</script>
