<script setup lang="ts">
/**
 * Workout complete view.
 * Shows workout summary after finishing a session.
 * TODO: Implement full summary with stats.
 */
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
</script>

<template>
  <div class="space-y-6 text-center">
    <!-- Success icon -->
    <div class="flex justify-center">
      <div class="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
        <svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
    </div>

    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Workout Complete!</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Great job! You've finished your workout.</p>
    </div>

    <!-- Summary stats -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Workout Summary</h2>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">00:00</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Duration</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">0</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Exercises</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">0</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Total Sets</p>
        </div>
      </div>
    </BaseCard>

    <!-- Personal records placeholder -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Personal Records</h2>
      <p class="text-gray-500 dark:text-gray-400">No new personal records this session.</p>
    </BaseCard>

    <!-- Actions -->
    <div class="flex flex-col gap-3">
      <RouterLink to="/history" class="btn btn-md btn-outline w-full">
        View Details
      </RouterLink>
      <RouterLink to="/" class="btn btn-md btn-primary w-full">
        Back to Dashboard
      </RouterLink>
    </div>
  </div>
</template>
