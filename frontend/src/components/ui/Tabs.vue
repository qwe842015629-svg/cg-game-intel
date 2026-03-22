<template>
  <div>
    <div class="ui-tabs-list">
      <button
        v-for="tab in normalizedTabs"
        :key="tab.value"
        :class="['ui-tab', modelValue === tab.value ? 'ui-tab--active' : '']"
        @click="$emit('update:modelValue', tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="mt-5">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

type TabOption = string | { label: string; value: string };

interface Props {
  tabs: TabOption[];
  modelValue: string;
}

const props = defineProps<Props>();

const normalizedTabs = computed(() => {
  return props.tabs.map((tab) => {
    if (typeof tab === "string") {
      return {
        label: tab,
        value: tab,
      };
    }

    return tab;
  });
});

defineEmits<{
  "update:modelValue": [value: string];
}>();
</script>
