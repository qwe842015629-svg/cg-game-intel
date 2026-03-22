<template>
  <span
    :class="[
      'ui-badge',
      variantClasses,
    ]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const variantClasses = computed(() => {
  const variants = {
    default: 'ui-badge--default',
    secondary: 'ui-badge--secondary',
    destructive: 'ui-badge--destructive',
    outline: 'ui-badge--outline',
  }
  return variants[props.variant]
})
</script>
