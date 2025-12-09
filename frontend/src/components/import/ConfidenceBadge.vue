<script setup lang="ts">
/**
 * Confidence badge component for displaying exercise match confidence.
 * Shows high (green), medium (yellow), or low (red) confidence levels.
 */
import { computed } from 'vue'
import type { ConfidenceLevel } from '@/types'

interface Props {
  level: ConfidenceLevel | null
  showLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: true,
})

const badgeConfig = computed(() => {
  switch (props.level) {
    case 'high':
      return {
        label: 'High',
        bgClass: 'bg-green-100 dark:bg-green-900/30',
        textClass: 'text-green-800 dark:text-green-300',
        dotClass: 'bg-green-500',
      }
    case 'medium':
      return {
        label: 'Medium',
        bgClass: 'bg-yellow-100 dark:bg-yellow-900/30',
        textClass: 'text-yellow-800 dark:text-yellow-300',
        dotClass: 'bg-yellow-500',
      }
    case 'low':
      return {
        label: 'Low',
        bgClass: 'bg-red-100 dark:bg-red-900/30',
        textClass: 'text-red-800 dark:text-red-300',
        dotClass: 'bg-red-500',
      }
    default:
      return {
        label: 'Unmatched',
        bgClass: 'bg-gray-100 dark:bg-gray-800',
        textClass: 'text-gray-600 dark:text-gray-400',
        dotClass: 'bg-gray-400',
      }
  }
})
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium',
      badgeConfig.bgClass,
      badgeConfig.textClass,
    ]"
  >
    <span :class="['w-1.5 h-1.5 rounded-full', badgeConfig.dotClass]" />
    <span v-if="showLabel">{{ badgeConfig.label }}</span>
  </span>
</template>
