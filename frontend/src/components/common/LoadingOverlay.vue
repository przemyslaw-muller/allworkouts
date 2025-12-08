<script setup lang="ts">
import BaseSpinner from './BaseSpinner.vue'

interface Props {
  message?: string
}

withDefaults(defineProps<Props>(), {
  message: '',
})
</script>

<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center bg-black/30 dark:bg-black/50">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl flex flex-col items-center gap-4">
      <BaseSpinner size="lg" />
      <p v-if="message" class="text-gray-600 dark:text-gray-400">{{ message }}</p>
    </div>
  </div>
</template>
