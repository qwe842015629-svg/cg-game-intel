<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="props.modelValue"
        :class="[
          'fixed inset-0 z-50 flex items-center justify-center',
          props.modal ? '' : 'pointer-events-none',
        ]"
        @click="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div v-if="props.modal" class="absolute inset-0 ui-dialog-backdrop" />
        
        <!-- Dialog Content -->
        <div
          :class="['relative z-50 w-full max-w-lg p-6 m-4 ui-dialog-panel pointer-events-auto', props.panelClass]"
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
  panelClass?: string
  modal?: boolean
  closeOnBackdrop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  panelClass: '',
  modal: true,
  closeOnBackdrop: true,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const handleBackdropClick = () => {
  if (!props.modal || !props.closeOnBackdrop) return
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
