<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore, useAuthStore } from '@/stores'
import AppLayout from '@/components/common/AppLayout.vue'
import AuthLayout from '@/components/common/AuthLayout.vue'
import MinimalLayout from '@/components/common/MinimalLayout.vue'
import WorkoutLayout from '@/components/common/WorkoutLayout.vue'
import NotificationContainer from '@/components/common/NotificationContainer.vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const route = useRoute()
const uiStore = useUiStore()
const authStore = useAuthStore()

// Determine which layout to use based on route meta
const currentLayout = computed(() => {
  const layout = route.meta.layout || 'main'
  switch (layout) {
    case 'auth':
      return AuthLayout
    case 'workout':
      return WorkoutLayout
    case 'minimal':
      return MinimalLayout
    default:
      return AppLayout
  }
})

// Show loading overlay during auth initialization
const showInitLoading = computed(() => {
  return !authStore.isInitialized && authStore.isLoading
})
</script>

<template>
  <div id="app-root" class="min-h-screen">
    <!-- Loading overlay for initial auth check -->
    <LoadingOverlay v-if="showInitLoading" message="Loading..." />

    <!-- Main content with dynamic layout -->
    <component :is="currentLayout" v-else>
      <RouterView v-slot="{ Component, route: currentRoute }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" :key="currentRoute.path" />
        </Transition>
      </RouterView>
    </component>

    <!-- Global notifications -->
    <NotificationContainer />

    <!-- Global loading overlay (for async operations) -->
    <LoadingOverlay v-if="uiStore.isLoading" :message="uiStore.loadingMessage ?? undefined" />

    <!-- Confirmation dialog -->
    <ConfirmationDialog />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
