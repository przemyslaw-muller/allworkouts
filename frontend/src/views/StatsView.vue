<script setup lang="ts">
/**
 * Stats/Analytics view.
 * Shows workout statistics, progress charts, and trends.
 * TODO: Implement full stats with charts.
 */
import BaseCard from '@/components/common/BaseCard.vue'
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Statistics</h1>
      <p class="text-gray-600">Track your fitness progress</p>
    </div>

    <!-- Overview stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <BaseCard>
        <div class="text-center">
          <p class="text-2xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Total Workouts</p>
        </div>
      </BaseCard>
      <BaseCard>
        <div class="text-center">
          <p class="text-2xl font-bold text-primary-600">0h</p>
          <p class="text-sm text-gray-600">Total Time</p>
        </div>
      </BaseCard>
      <BaseCard>
        <div class="text-center">
          <p class="text-2xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Total Sets</p>
        </div>
      </BaseCard>
      <BaseCard>
        <div class="text-center">
          <p class="text-2xl font-bold text-primary-600">0 kg</p>
          <p class="text-sm text-gray-600">Total Volume</p>
        </div>
      </BaseCard>
    </div>

    <!-- Charts placeholder -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Workout Frequency</h2>
      <div class="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
        <p class="text-gray-500">Chart will be displayed here</p>
      </div>
    </BaseCard>

    <!-- Personal records -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Personal Records</h2>
      <p class="text-gray-500 text-center py-8">
        Complete workouts to see your personal records here.
      </p>
    </BaseCard>
  </div>
</template>
