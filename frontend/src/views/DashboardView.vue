<script setup lang="ts">
/**
 * Dashboard / Home view.
 * Shows recent activity, quick actions, and workout summary.
 * TODO: Implement full dashboard with API integration.
 */
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600">Welcome back! Ready to work out?</p>
    </div>

    <!-- Quick Actions -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
      <div class="flex flex-wrap gap-3">
        <RouterLink to="/plans">
          <BaseButton variant="primary">Start Workout</BaseButton>
        </RouterLink>
        <RouterLink to="/plans/new">
          <BaseButton variant="outline">Create Plan</BaseButton>
        </RouterLink>
        <RouterLink to="/plans/import">
          <BaseButton variant="ghost">Import Plan</BaseButton>
        </RouterLink>
      </div>
    </BaseCard>

    <!-- Stats Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <BaseCard>
        <div class="text-center">
          <p class="text-3xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Workouts This Week</p>
        </div>
      </BaseCard>
      <BaseCard>
        <div class="text-center">
          <p class="text-3xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Total Workouts</p>
        </div>
      </BaseCard>
      <BaseCard>
        <div class="text-center">
          <p class="text-3xl font-bold text-primary-600">0</p>
          <p class="text-sm text-gray-600">Personal Records</p>
        </div>
      </BaseCard>
    </div>

    <!-- Recent Activity -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
      <p class="text-gray-500 text-center py-8">
        No recent workouts. Start your first workout to see activity here!
      </p>
    </BaseCard>
  </div>
</template>
