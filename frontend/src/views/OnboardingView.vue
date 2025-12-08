<script setup lang="ts">
/**
 * Onboarding view for new users.
 * Collects initial preferences like equipment and unit system.
 * TODO: Implement full onboarding flow.
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseToggle from '@/components/common/BaseToggle.vue'

const router = useRouter()

const useMetric = ref(true)
const isLoading = ref(false)

const handleComplete = async () => {
  isLoading.value = true
  // TODO: Save preferences via API
  await new Promise(resolve => setTimeout(resolve, 500))
  router.push('/')
}
</script>

<template>
  <div class="space-y-6">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Welcome to AllWorkouts!</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">Let's set up your preferences to get started.</p>
    </div>

    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Unit System</h2>
      <div class="flex items-center justify-between">
        <div>
          <p class="font-medium text-gray-900 dark:text-gray-100">Use Metric Units</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">Weights in kg, distances in km</p>
        </div>
        <BaseToggle v-model="useMetric" />
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
        {{ useMetric ? 'Using kilograms and kilometers' : 'Using pounds and miles' }}
      </p>
    </BaseCard>

    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Available Equipment</h2>
      <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">
        You can configure your available equipment later in your profile settings.
      </p>
      <div class="flex flex-wrap gap-2">
        <span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">Dumbbells</span>
        <span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">Barbell</span>
        <span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">Pull-up Bar</span>
        <span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">Bench</span>
      </div>
    </BaseCard>

    <BaseButton
      variant="primary"
      :loading="isLoading"
      class="w-full"
      @click="handleComplete"
    >
      Get Started
    </BaseButton>
  </div>
</template>
