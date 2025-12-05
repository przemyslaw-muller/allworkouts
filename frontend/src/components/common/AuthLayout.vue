<script setup lang="ts">
/**
 * Minimal layout for authentication pages (login, register).
 * Centered card with branding.
 */
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <!-- Branding -->
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h1 class="text-center text-3xl font-bold text-primary-600">
        AllWorkouts
      </h1>
      <p class="mt-2 text-center text-sm text-gray-600">
        Track your fitness journey
      </p>
    </div>

    <!-- Content card -->
    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
        <slot />
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-8 text-center">
      <p class="text-xs text-gray-500">
        &copy; {{ new Date().getFullYear() }} AllWorkouts. All rights reserved.
      </p>
    </div>
  </div>
</template>
