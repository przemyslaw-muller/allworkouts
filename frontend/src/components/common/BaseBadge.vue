<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'gray'
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
})

const classes = computed(() => {
  const base = 'badge'
  const variantClass = `badge-${props.variant}`
  const sizeClass = props.size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-2.5 py-0.5'
  return [base, variantClass, sizeClass].join(' ')
})
</script>

<template>
  <span :class="classes">
    <slot />
  </span>
</template>
