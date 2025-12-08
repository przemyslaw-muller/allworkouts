<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  disabled?: boolean
  id?: string
  name?: string
  label?: string
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  label: '',
  size: 'md',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  change: [value: boolean]
}>()

const toggleId = computed(() => props.id || `toggle-${Math.random().toString(36).slice(2)}`)

const toggleClasses = computed(() => {
  const base = 'relative inline-flex flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900'
  const sizeClasses = props.size === 'sm' ? 'h-5 w-9' : 'h-6 w-11'
  const colorClasses = props.modelValue ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-600'
  const disabledClasses = props.disabled ? 'opacity-50 cursor-not-allowed' : ''
  return [base, sizeClasses, colorClasses, disabledClasses].join(' ')
})

const knobClasses = computed(() => {
  const base = 'pointer-events-none inline-block transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out'
  const sizeClasses = props.size === 'sm' ? 'h-4 w-4' : 'h-5 w-5'
  const translateClasses = props.modelValue
    ? (props.size === 'sm' ? 'translate-x-4' : 'translate-x-5')
    : 'translate-x-0'
  return [base, sizeClasses, translateClasses].join(' ')
})

function toggle() {
  if (!props.disabled) {
    const newValue = !props.modelValue
    emit('update:modelValue', newValue)
    emit('change', newValue)
  }
}
</script>

<template>
  <div class="flex items-center">
    <button
      :id="toggleId"
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :disabled="disabled"
      :class="toggleClasses"
      @click="toggle"
    >
      <span :class="knobClasses" />
    </button>
    <label
      v-if="label"
      :for="toggleId"
      class="ml-3 text-sm text-gray-700 dark:text-gray-300 select-none cursor-pointer"
      :class="{ 'opacity-50 cursor-not-allowed': disabled }"
      @click="toggle"
    >
      {{ label }}
    </label>
  </div>
</template>
