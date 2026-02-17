<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @click="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/80" />
        
        <!-- Dialog Content -->
        <div
          class="relative z-50 w-full max-w-lg bg-card border border-border rounded-lg shadow-lg p-6 m-4"
          @click.stop
        >
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const handleBackdropClick = () => {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-active .relative,
.dialog-leave-active .relative {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.dialog-enter-from .relative,
.dialog-leave-to .relative {
  transform: scale(0.95);
  opacity: 0;
}
</style>
