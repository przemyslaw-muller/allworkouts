<script setup lang="ts">
/**
 * Main application layout with header and navigation.
 * Used for authenticated pages with full navigation.
 */
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore, useWorkoutStore, useUiStore } from '@/stores'

const route = useRoute()
const authStore = useAuthStore()
const workoutStore = useWorkoutStore()
const uiStore = useUiStore()

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
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header
      class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40 dark:bg-gray-800 dark:border-gray-700"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <RouterLink to="/" class="flex items-center space-x-2">
            <img src="/allworkouts_logo.png" alt="AllWorkouts" class="h-8 w-auto" />
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
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100',
              ]"
            >
              {{ item.name }}
            </RouterLink>
          </nav>

          <!-- Right side actions -->
          <div class="flex items-center space-x-4">
            <!-- Dark mode toggle -->
            <button
              class="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-700"
              :title="uiStore.isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
              @click="uiStore.toggleDarkMode()"
            >
              <!-- Sun icon (shown in dark mode) -->
              <svg
                v-if="uiStore.isDarkMode"
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
              <!-- Moon icon (shown in light mode) -->
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                />
              </svg>
            </button>

            <!-- Active workout indicator -->
            <RouterLink
              v-if="hasActiveWorkout"
              to="/workout"
              class="hidden sm:flex items-center px-3 py-1.5 bg-green-100 text-green-700 rounded-full text-sm font-medium hover:bg-green-200 transition-colors dark:bg-green-900 dark:text-green-300 dark:hover:bg-green-800"
            >
              <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Active Workout
            </RouterLink>

            <!-- User menu (desktop) -->
            <button
              class="hidden md:block text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
              @click="handleLogout"
            >
              Logout
            </button>

            <!-- Mobile menu button -->
            <button
              class="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-700"
              aria-label="Toggle menu"
              @click="toggleMobileMenu"
            >
              <svg
                v-if="!isMobileMenuOpen"
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
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
        <div
          v-if="isMobileMenuOpen"
          class="md:hidden border-t border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700"
        >
          <div class="px-2 pt-2 pb-3 space-y-1">
            <!-- Active workout link (mobile) -->
            <RouterLink
              v-if="hasActiveWorkout"
              to="/workout"
              class="flex items-center px-3 py-2 bg-green-100 text-green-700 rounded-md text-base font-medium dark:bg-green-900 dark:text-green-300"
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
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100',
              ]"
              @click="closeMobileMenu"
            >
              {{ item.name }}
            </RouterLink>

            <!-- Dark mode toggle (mobile) -->
            <button
              class="w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100"
              @click="uiStore.toggleDarkMode()"
            >
              {{ uiStore.isDarkMode ? 'Light Mode' : 'Dark Mode' }}
            </button>

            <button
              class="w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100"
              @click="handleLogout"
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
