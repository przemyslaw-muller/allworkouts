<script setup lang="ts">
/**
 * Main application layout with header and navigation.
 * Used for authenticated pages with full navigation.
 */
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore, useWorkoutStore } from '@/stores'

const route = useRoute()
const authStore = useAuthStore()
const workoutStore = useWorkoutStore()

const isMobileMenuOpen = ref(false)

// Navigation items
const navItems = [
  { name: 'Dashboard', to: '/', icon: 'home' },
  { name: 'Plans', to: '/plans', icon: 'clipboard' },
  { name: 'History', to: '/history', icon: 'clock' },
  { name: 'Stats', to: '/stats', icon: 'chart' },
  { name: 'Profile', to: '/profile', icon: 'user' },
]

// Check if there's an active workout
const hasActiveWorkout = computed(() => workoutStore.hasActiveSession)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const handleLogout = async () => {
  await authStore.logout()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center space-x-2">
            <span class="text-xl font-bold text-primary-600">AllWorkouts</span>
          </RouterLink>

          <!-- Desktop Navigation -->
          <nav class="hidden md:flex items-center space-x-1">
            <RouterLink
              v-for="item in navItems"
              :key="item.name"
              :to="item.to"
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="[
                route.path === item.to || (item.to !== '/' && route.path.startsWith(item.to))
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              ]"
            >
              {{ item.name }}
            </RouterLink>
          </nav>

          <!-- Right side actions -->
          <div class="flex items-center space-x-4">
            <!-- Active workout indicator -->
            <RouterLink
              v-if="hasActiveWorkout"
              to="/workout"
              class="hidden sm:flex items-center px-3 py-1.5 bg-green-100 text-green-700 rounded-full text-sm font-medium hover:bg-green-200 transition-colors"
            >
              <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Active Workout
            </RouterLink>

            <!-- User menu (desktop) -->
            <button
              @click="handleLogout"
              class="hidden md:block text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>

            <!-- Mobile menu button -->
            <button
              @click="toggleMobileMenu"
              class="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              aria-label="Toggle menu"
            >
              <svg
                v-if="!isMobileMenuOpen"
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg
                v-else
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div v-if="isMobileMenuOpen" class="md:hidden border-t border-gray-200 bg-white">
          <div class="px-2 pt-2 pb-3 space-y-1">
            <!-- Active workout link (mobile) -->
            <RouterLink
              v-if="hasActiveWorkout"
              to="/workout"
              class="flex items-center px-3 py-2 bg-green-100 text-green-700 rounded-md text-base font-medium"
              @click="closeMobileMenu"
            >
              <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Active Workout
            </RouterLink>

            <RouterLink
              v-for="item in navItems"
              :key="item.name"
              :to="item.to"
              class="block px-3 py-2 rounded-md text-base font-medium"
              :class="[
                route.path === item.to || (item.to !== '/' && route.path.startsWith(item.to))
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              ]"
              @click="closeMobileMenu"
            >
              {{ item.name }}
            </RouterLink>

            <button
              @click="handleLogout"
              class="w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </Transition>
    </header>

    <!-- Main content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <slot />
    </main>
  </div>
</template>
