<script setup lang="ts">
/**
 * Onboarding view for new users.
 * 2-step wizard: (1) Unit selection, (2) Equipment selection.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCheckbox from '@/components/common/BaseCheckbox.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import OnboardingStepIndicator from '@/components/common/OnboardingStepIndicator.vue'
import { useProfileStore } from '@/stores/profile'
import { useUiStore } from '@/stores/ui'
import { equipmentService } from '@/services/equipmentService'
import { getErrorMessage } from '@/services/api'
import type { EquipmentListItem, UnitSystem } from '@/types'

const router = useRouter()
const profileStore = useProfileStore()
const uiStore = useUiStore()

// Wizard state
const currentStep = ref<1 | 2>(1)

// Step 1: Unit selection
const selectedUnit = ref<UnitSystem>('metric')

// Step 2: Equipment selection
const equipment = ref<EquipmentListItem[]>([])
const selectedEquipmentIds = ref<Set<string>>(new Set())
const isLoadingEquipment = ref(false)
const equipmentError = ref<string | null>(null)

// Completing
const isCompleting = ref(false)

// Computed
const canProceedStep1 = computed(() => true) // Units always have a selection

const canComplete = computed(() => true) // Equipment selection is optional

const selectedCount = computed(() => selectedEquipmentIds.value.size)

// Load equipment on mount
onMounted(async () => {
  await loadEquipment()
})

async function loadEquipment() {
  try {
    isLoadingEquipment.value = true
    equipmentError.value = null
    equipment.value = await equipmentService.getAll()
  } catch (err) {
    equipmentError.value = getErrorMessage(err)
  } finally {
    isLoadingEquipment.value = false
  }
}

// Equipment selection
function toggleEquipment(equipmentId: string) {
  if (selectedEquipmentIds.value.has(equipmentId)) {
    selectedEquipmentIds.value.delete(equipmentId)
  } else {
    selectedEquipmentIds.value.add(equipmentId)
  }
  // Force reactivity
  selectedEquipmentIds.value = new Set(selectedEquipmentIds.value)
}

function isSelected(equipmentId: string): boolean {
  return selectedEquipmentIds.value.has(equipmentId)
}

function selectAll() {
  selectedEquipmentIds.value = new Set(equipment.value.map((e) => e.id))
}

function selectNone() {
  selectedEquipmentIds.value = new Set()
}

// Navigation
function nextStep() {
  if (currentStep.value === 1 && canProceedStep1.value) {
    currentStep.value = 2
  }
}

function prevStep() {
  if (currentStep.value === 2) {
    currentStep.value = 1
  }
}

// Complete onboarding
async function handleComplete() {
  isCompleting.value = true

  try {
    // Save unit preference
    const unitResult = await profileStore.updateUnitSystem(selectedUnit.value)
    if (!unitResult.success) {
      uiStore.error(unitResult.error || 'Failed to save unit preference')
      return
    }

    // Save equipment ownership for each selected item
    const selectedIds = Array.from(selectedEquipmentIds.value)

    for (const equipmentId of selectedIds) {
      await equipmentService.updateOwnership(equipmentId, { is_owned: true })
    }

    uiStore.success('Onboarding complete! Welcome to AllWorkouts.')
    router.push('/')
  } catch (err) {
    uiStore.error(getErrorMessage(err))
  } finally {
    isCompleting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Welcome to AllWorkouts!</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">
        Let's set up your preferences to get started.
      </p>
    </div>

    <!-- Step Indicator -->
    <OnboardingStepIndicator :current-step="currentStep" />

    <!-- Step 1: Unit Selection -->
    <template v-if="currentStep === 1">
      <BaseCard>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Choose Your Unit System
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
          Select how you'd like to measure weights and distances.
        </p>

        <div class="space-y-3">
          <!-- Metric option -->
          <label
            class="flex items-center p-4 border rounded-lg cursor-pointer transition-colors"
            :class="
              selectedUnit === 'metric'
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            "
          >
            <input
              v-model="selectedUnit"
              type="radio"
              name="unit"
              value="metric"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900 dark:text-gray-100">Metric</span>
              <p class="text-sm text-gray-500 dark:text-gray-400">Kilograms (kg) and kilometers</p>
            </div>
          </label>

          <!-- Imperial option -->
          <label
            class="flex items-center p-4 border rounded-lg cursor-pointer transition-colors"
            :class="
              selectedUnit === 'imperial'
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            "
          >
            <input
              v-model="selectedUnit"
              type="radio"
              name="unit"
              value="imperial"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900 dark:text-gray-100">Imperial</span>
              <p class="text-sm text-gray-500 dark:text-gray-400">Pounds (lbs) and miles</p>
            </div>
          </label>
        </div>
      </BaseCard>

      <BaseButton variant="primary" class="w-full" :disabled="!canProceedStep1" @click="nextStep">
        Next: Select Equipment
      </BaseButton>
    </template>

    <!-- Step 2: Equipment Selection -->
    <template v-if="currentStep === 2">
      <BaseCard>
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Select Your Equipment
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Choose the equipment you have access to. This helps us suggest relevant exercises.
            </p>
          </div>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ selectedCount }} selected
          </span>
        </div>

        <!-- Quick actions -->
        <div class="flex gap-2 mb-4">
          <button
            type="button"
            class="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
            @click="selectAll"
          >
            Select all
          </button>
          <span class="text-gray-300 dark:text-gray-600">|</span>
          <button
            type="button"
            class="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
            @click="selectNone"
          >
            Clear all
          </button>
        </div>

        <!-- Loading state -->
        <div v-if="isLoadingEquipment" class="flex justify-center py-8">
          <BaseSpinner size="lg" />
        </div>

        <!-- Error state -->
        <div
          v-else-if="equipmentError"
          class="text-center py-8 text-red-600 dark:text-red-400"
        >
          <p>{{ equipmentError }}</p>
          <button
            type="button"
            class="mt-2 text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
            @click="loadEquipment"
          >
            Try again
          </button>
        </div>

        <!-- Equipment grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label
            v-for="item in equipment"
            :key="item.id"
            class="flex items-start p-3 border rounded-lg cursor-pointer transition-colors"
            :class="
              isSelected(item.id)
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            "
          >
            <BaseCheckbox
              :model-value="isSelected(item.id)"
              class="mt-0.5"
              @update:model-value="toggleEquipment(item.id)"
            />
            <div class="ml-3">
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ item.name }}</span>
              <p v-if="item.description" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                {{ item.description }}
              </p>
            </div>
          </label>
        </div>

        <p class="text-xs text-gray-500 dark:text-gray-400 mt-4">
          You can update your equipment anytime in your profile settings.
        </p>
      </BaseCard>

      <div class="flex gap-3">
        <BaseButton variant="secondary" class="flex-1" @click="prevStep">
          Back
        </BaseButton>
        <BaseButton
          variant="primary"
          class="flex-1"
          :loading="isCompleting"
          :disabled="!canComplete"
          @click="handleComplete"
        >
          Get Started
        </BaseButton>
      </div>
    </template>
  </div>
</template>
