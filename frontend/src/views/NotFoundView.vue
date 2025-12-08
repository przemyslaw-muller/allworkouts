<script setup lang="ts">
/**
 * 404 Not Found view.
 */
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="text-center py-12">
    <h1 class="text-6xl font-bold text-gray-300 dark:text-gray-600">404</h1>
    <h2 class="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">Page Not Found</h2>
    <p class="mt-2 text-gray-600 dark:text-gray-400">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <div class="mt-8">
      <RouterLink to="/" class="btn btn-md btn-primary">
        Go to Dashboard
      </RouterLink>
    </div>
  </div>
</template>
