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
      <RouterLink to="/history" class="text-sm text-gray-500 hover:text-gray-700 mb-1 inline-block">
        &larr; Back to History
      </RouterLink>
      <h1 class="text-2xl font-bold text-gray-900">Workout Session</h1>
      <p class="text-gray-600">Session ID: {{ sessionId }}</p>
    </div>

    <!-- Session summary -->
    <BaseCard>
      <div class="grid grid-cols-3 gap-4 text-center mb-6">
        <div>
          <p class="text-2xl font-bold text-primary-600">--:--</p>
          <p class="text-sm text-gray-600">Duration</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Exercises</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-primary-600">0 kg</p>
          <p class="text-sm text-gray-600">Total Volume</p>
        </div>
      </div>
    </BaseCard>

    <!-- Exercises -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Exercises</h2>
      <p class="text-gray-500 text-center py-8">
        Exercise details will be loaded here.
      </p>
    </BaseCard>
  </div>
</template>
