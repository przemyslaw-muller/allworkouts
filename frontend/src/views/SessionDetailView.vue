<script setup lang="ts">
/**
 * Session detail view.
 * Shows detailed information about a completed workout session.
 * TODO: Implement full detail view with API integration.
 */
import { useRoute, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'

const route = useRoute()
const sessionId = route.params.id
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <RouterLink to="/history" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-1 inline-block">
        &larr; Back to History
      </RouterLink>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Workout Session</h1>
      <p class="text-gray-600 dark:text-gray-400">Session ID: {{ sessionId }}</p>
    </div>

    <!-- Session summary -->
    <BaseCard>
      <div class="grid grid-cols-3 gap-4 text-center mb-6">
        <div>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">--:--</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Duration</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">0</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Exercises</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">0 kg</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Total Volume</p>
        </div>
      </div>
    </BaseCard>

    <!-- Exercises -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Exercises</h2>
      <p class="text-gray-500 dark:text-gray-400 text-center py-8">
        Exercise details will be loaded here.
      </p>
    </BaseCard>
  </div>
</template>
