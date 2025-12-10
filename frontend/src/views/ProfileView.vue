<script setup lang="ts">
/**
 * Profile/Settings view.
 * User profile settings, preferences, and equipment configuration.
 */
import { computed } from 'vue'
import { useAuthStore, useProfileStore } from '@/stores'
import { useUiStore } from '@/stores/ui'
import { useEquipment } from '@/composables/useEquipment'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseToggle from '@/components/common/BaseToggle.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseCheckbox from '@/components/common/BaseCheckbox.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'

const authStore = useAuthStore()
const profileStore = useProfileStore()
const uiStore = useUiStore()

// Equipment management
const {
  searchQuery,
  filteredEquipment,
  isLoading: isLoadingEquipment,
  ownedCount,
  totalCount,
  toggleOwnership,
  clearSearch,
  isEquipmentUpdating,
} = useEquipment()

// Unit system preference
const unitSystem = computed(() => profileStore.unitSystem)
const isMetric = computed({
  get: () => unitSystem.value === 'metric',
  set: (value: boolean) => {
    const newSystem = value ? 'metric' : 'imperial'
    profileStore.updateUnitSystem(newSystem).then((result) => {
      if (result.success) {
        uiStore.success('Preferences saved')
      } else {
        uiStore.error('Failed to save preferences')
      }
    })
  },
})

const darkMode = computed({
  get: () => uiStore.isDarkMode,
  set: (value: boolean) => {
    uiStore.setDarkMode(value)
  },
})

const handleLogout = async () => {
  await authStore.logout()
}

// Format member since date
const memberSince = computed(() => {
  if (!authStore.user?.created_at) return ''
  const date = new Date(authStore.user.created_at)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Profile & Settings</h1>
      <p class="text-gray-600 dark:text-gray-400">Manage your account and preferences</p>
    </div>

    <!-- Account info -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Account</h2>
      <div class="space-y-3">
        <div>
          <label class="text-sm text-gray-600 dark:text-gray-400">Email</label>
          <p class="font-medium text-gray-900 dark:text-gray-100">
            {{ authStore.user?.email || 'Not available' }}
          </p>
        </div>
        <div v-if="memberSince">
          <label class="text-sm text-gray-600 dark:text-gray-400">Member since</label>
          <p class="font-medium text-gray-900 dark:text-gray-100">{{ memberSince }}</p>
        </div>
      </div>
    </BaseCard>

    <!-- Preferences -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Preferences</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900 dark:text-gray-100">Metric Units</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Use kg and km instead of lbs and miles
            </p>
          </div>
          <BaseToggle v-model="isMetric" :disabled="profileStore.isUpdating" />
        </div>
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-gray-900 dark:text-gray-100">Dark Mode</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Use dark theme</p>
          </div>
          <BaseToggle v-model="darkMode" />
        </div>
      </div>
    </BaseCard>

    <!-- Equipment -->
    <BaseCard>
      <div class="space-y-4">
        <div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">My Equipment</h2>
          <p class="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Select the equipment you have available. This helps filter exercises and provide better
            recommendations.
          </p>
        </div>

        <!-- Search -->
        <div class="relative">
          <BaseInput
            v-model="searchQuery"
            type="search"
            placeholder="Search equipment..."
            class="w-full"
          />
          <button
            v-if="searchQuery"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Clear search"
            @click="clearSearch"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Equipment count -->
        <div class="text-sm text-gray-600 dark:text-gray-400">
          <span class="font-medium text-gray-900 dark:text-gray-100">{{ ownedCount }}</span> of
          <span class="font-medium text-gray-900 dark:text-gray-100">{{ totalCount }}</span>
          equipment owned
        </div>

        <!-- Equipment list -->
        <div v-if="isLoadingEquipment" class="flex justify-center py-8">
          <BaseSpinner size="lg" />
        </div>

        <div
          v-else-if="filteredEquipment.length > 0"
          class="border border-gray-200 dark:border-gray-700 rounded-lg divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto"
        >
          <div
            v-for="equipment in filteredEquipment"
            :key="equipment.id"
            class="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <p class="font-medium text-gray-900 dark:text-gray-100">{{ equipment.name }}</p>
                <BaseSpinner v-if="isEquipmentUpdating(equipment.id)" size="sm" />
              </div>
              <p
                v-if="equipment.description"
                class="text-sm text-gray-600 dark:text-gray-400 mt-0.5"
              >
                {{ equipment.description }}
              </p>
            </div>
            <BaseCheckbox
              :model-value="equipment.is_user_owned"
              :disabled="isEquipmentUpdating(equipment.id)"
              @update:model-value="toggleOwnership(equipment)"
            />
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>No equipment found matching "{{ searchQuery }}"</p>
          <button
            class="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 mt-2"
            @click="clearSearch"
          >
            Clear search
          </button>
        </div>
      </div>
    </BaseCard>

    <!-- Logout -->
    <BaseCard>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Account Actions</h2>
      <BaseButton variant="danger" @click="handleLogout"> Sign Out </BaseButton>
    </BaseCard>
  </div>
</template>
