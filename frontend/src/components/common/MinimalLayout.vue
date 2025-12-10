<script setup lang="ts">
/**
 * Simple centered layout for onboarding, workout complete, etc.
 * No navigation, just centered content with optional back button.
 */
import { RouterLink } from 'vue-router'

defineProps<{
  showBackButton?: boolean
  backTo?: string
}>()
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col dark:bg-gray-900">
    <!-- Optional header with back button -->
    <header
      v-if="showBackButton"
      class="bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700"
    >
      <div class="max-w-3xl mx-auto px-4 py-4">
        <RouterLink
          :to="backTo || '/'"
          class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
        >
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back
        </RouterLink>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1 flex items-center justify-center px-4 py-8">
      <div class="w-full max-w-2xl">
        <slot />
      </div>
    </main>

    <!-- Branding footer -->
    <footer class="py-4 text-center">
      <p class="text-xs text-gray-500 dark:text-gray-400">AllWorkouts</p>
    </footer>
  </div>
</template>
