<script setup lang="ts">
/**
 * Workout plans list view.
 * Shows all user's workout plans with options to start, edit, or delete.
 * TODO: Implement full list with API integration.
 */
import { RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Workout Plans</h1>
        <p class="text-gray-600">Manage your workout routines</p>
      </div>
      <div class="flex gap-2">
        <RouterLink to="/plans/import" class="btn btn-md btn-outline">
          Import
        </RouterLink>
        <RouterLink to="/plans/new" class="btn btn-md btn-primary">
          New Plan
        </RouterLink>
      </div>
    </div>

    <!-- Empty state -->
    <BaseCard class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900">No workout plans yet</h3>
      <p class="mt-2 text-gray-500">Get started by creating your first workout plan.</p>
      <div class="mt-6 flex justify-center gap-3">
        <RouterLink to="/plans/new" class="btn btn-md btn-primary">
          Create Plan
        </RouterLink>
        <RouterLink to="/plans/import" class="btn btn-md btn-outline">
          Import Plan
        </RouterLink>
      </div>
    </BaseCard>
  </div>
</template>
