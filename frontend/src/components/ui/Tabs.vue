<template>
  <div>
    <div class="flex space-x-1 border-b border-border">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="[
          'px-4 py-2 text-sm font-medium transition-colors',
          'hover:text-foreground',
          modelValue === tab
            ? 'border-b-2 border-primary text-foreground'
            : 'text-muted-foreground',
        ]"
        @click="$emit('update:modelValue', tab)"
      >
        {{ tab }}
      </button>
    </div>
    
    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  tabs: string[]
  modelValue: string
}

defineProps<Props>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
