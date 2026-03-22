<template>
  <div class="ui-input-shell">
    <input
      v-bind="forwardedAttrs"
      :class="['ui-input', inputClass]"
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'

defineOptions({
  inheritAttrs: false,
})

interface Props {
  modelValue?: string | number
  type?: string
  placeholder?: string
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
})

const attrs = useAttrs()

const inputClass = computed(() => attrs.class)
const forwardedAttrs = computed(() => {
  const result: Record<string, unknown> = {}
  Object.entries(attrs).forEach(([key, value]) => {
    if (key !== 'class') {
      result[key] = value
    }
  })
  return result
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
