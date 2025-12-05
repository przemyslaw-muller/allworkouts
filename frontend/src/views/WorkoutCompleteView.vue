<script setup lang="ts">
/**
 * Workout complete view.
 * Shows workout summary after finishing a session.
 * TODO: Implement full summary with stats.
 */
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
</script>

<template>
  <div class="space-y-6 text-center">
    <!-- Success icon -->
    <div class="flex justify-center">
      <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
        <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
    </div>

    <div>
      <h1 class="text-2xl font-bold text-gray-900">Workout Complete!</h1>
      <p class="text-gray-600 mt-2">Great job! You've finished your workout.</p>
    </div>

    <!-- Summary stats -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Workout Summary</h2>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold text-primary-600">00:00</p>
          <p class="text-sm text-gray-600">Duration</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Exercises</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Total Sets</p>
        </div>
      </div>
    </BaseCard>

    <!-- Personal records placeholder -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Personal Records</h2>
      <p class="text-gray-500">No new personal records this session.</p>
    </BaseCard>

    <!-- Actions -->
    <div class="flex flex-col gap-3">
      <RouterLink to="/history">
        <BaseButton variant="outline" class="w-full">View Details</BaseButton>
      </RouterLink>
      <RouterLink to="/">
        <BaseButton variant="primary" class="w-full">Back to Dashboard</BaseButton>
      </RouterLink>
    </div>
  </div>
</template>
