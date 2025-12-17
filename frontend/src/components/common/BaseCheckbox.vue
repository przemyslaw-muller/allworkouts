<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  disabled?: boolean
  id?: string
  name?: string
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  id: undefined,
  name: undefined,
  label: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  change: [value: boolean]
}>()

const checkboxId = computed(() => props.id || `checkbox-${Math.random().toString(36).slice(2)}`)

function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.checked)
  emit('change', target.checked)
}
</script>

<template>
  <div class="flex items-center">
    <input
      :id="checkboxId"
      type="checkbox"
      :checked="modelValue"
      :disabled="disabled"
      :name="name"
      class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-primary-600 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
      @change="handleChange"
    />
    <label
      v-if="label"
      :for="checkboxId"
      class="ml-2 text-sm text-gray-700 dark:text-gray-300 select-none"
      :class="{ 'opacity-50 cursor-not-allowed': disabled }"
    >
      {{ label }}
    </label>
  </div>
</template>
