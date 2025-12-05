<script setup lang="ts">
/**
 * Profile/Settings view.
 * User profile settings, preferences, and equipment configuration.
 * TODO: Implement full settings with API integration.
 */
import { ref } from 'vue'
import { useAuthStore } from '@/stores'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseToggle from '@/components/common/BaseToggle.vue'

const authStore = useAuthStore()

const useMetric = ref(true)
const darkMode = ref(false)

const handleLogout = async () => {
  await authStore.logout()
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Profile & Settings</h1>
      <p class="text-gray-600">Manage your account and preferences</p>
    </div>

    <!-- Account info -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Account</h2>
      <div class="space-y-3">
        <div>
          <label class="text-sm text-gray-600">Email</label>
          <p class="font-medium text-gray-900">{{ authStore.user?.email || 'Not available' }}</p>
        </div>
      </div>
    </BaseCard>

    <!-- Preferences -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Preferences</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900">Metric Units</p>
            <p class="text-sm text-gray-600">Use kg and km instead of lbs and miles</p>
          </div>
          <BaseToggle v-model="useMetric" />
        </div>
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900">Dark Mode</p>
            <p class="text-sm text-gray-600">Use dark theme (coming soon)</p>
          </div>
          <BaseToggle v-model="darkMode" disabled />
        </div>
      </div>
    </BaseCard>

    <!-- Equipment -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">My Equipment</h2>
      <p class="text-gray-500 text-sm mb-4">
        Select the equipment you have available. This helps filter exercises.
      </p>
      <div class="flex flex-wrap gap-2">
        <span class="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">Dumbbells</span>
        <span class="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">Barbell</span>
        <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">Cables</span>
        <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">Machines</span>
      </div>
      <BaseButton variant="outline" class="mt-4">
        Manage Equipment
      </BaseButton>
    </BaseCard>

    <!-- Logout -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Account Actions</h2>
      <BaseButton variant="danger" @click="handleLogout">
        Sign Out
      </BaseButton>
    </BaseCard>
  </div>
</template>
