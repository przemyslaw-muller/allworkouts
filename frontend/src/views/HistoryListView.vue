<script setup lang="ts">
/**
 * Workout history list view.
 * Shows past workout sessions with filtering options.
 * TODO: Implement full list with API integration.
 */
import BaseCard from '@/components/common/BaseCard.vue'
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Workout History</h1>
      <p class="text-gray-600">View your past workout sessions</p>
    </div>

    <!-- Filters placeholder -->
    <BaseCard>
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option>Last 7 days</option>
            <option>Last 30 days</option>
            <option>Last 3 months</option>
            <option>All time</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Workout Type</label>
          <select class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option>All workouts</option>
          </select>
        </div>
      </div>
    </BaseCard>

    <!-- Empty state -->
    <BaseCard class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900">No workout history</h3>
      <p class="mt-2 text-gray-500">Complete your first workout to see it here.</p>
    </BaseCard>
  </div>
</template>
