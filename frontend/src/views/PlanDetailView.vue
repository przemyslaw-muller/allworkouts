<script setup lang="ts">
/**
 * Plan detail view.
 * Shows workout plan details with exercises and option to start workout.
 * TODO: Implement full detail view with API integration.
 */
import { useRoute, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const route = useRoute()
const planId = route.params.id
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <RouterLink to="/plans" class="text-sm text-gray-500 hover:text-gray-700 mb-1 inline-block">
          &larr; Back to Plans
        </RouterLink>
        <h1 class="text-2xl font-bold text-gray-900">Plan Details</h1>
        <p class="text-gray-600">Plan ID: {{ planId }}</p>
      </div>
      <div class="flex gap-2">
        <RouterLink :to="`/plans/${planId}/edit`">
          <BaseButton variant="outline">Edit</BaseButton>
        </RouterLink>
        <BaseButton variant="primary">Start Workout</BaseButton>
      </div>
    </div>

    <!-- Plan info placeholder -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Exercises</h2>
      <p class="text-gray-500 text-center py-8">
        Plan details will be loaded here.
      </p>
    </BaseCard>
  </div>
</template>
