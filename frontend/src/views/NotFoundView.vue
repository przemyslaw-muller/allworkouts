<script setup lang="ts">
/**
 * 404 Not Found view.
 */
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
</script>

<template>
  <div class="text-center py-12">
    <h1 class="text-6xl font-bold text-gray-300">404</h1>
    <h2 class="mt-4 text-2xl font-bold text-gray-900">Page Not Found</h2>
    <p class="mt-2 text-gray-600">
      The page you're looking for doesn't exist or has been moved.
    </p>
    <div class="mt-8">
      <RouterLink to="/">
        <BaseButton variant="primary">Go to Dashboard</BaseButton>
      </RouterLink>
    </div>
  </div>
</template>
