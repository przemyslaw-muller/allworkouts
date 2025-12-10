<script setup lang="ts">
/**
 * Workout plans list view.
 * Shows all user's workout plans with options to view, edit, or delete.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import { workoutPlanService } from '@/services/workoutPlanService'
import { useUiStore } from '@/stores/ui'
import type { WorkoutPlanListItem } from '@/types'

const router = useRouter()
const uiStore = useUiStore()

// State
const plans = ref<WorkoutPlanListItem[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)

// Delete dialog state
const deleteDialog = ref({
  isOpen: false,
  planId: null as string | null,
  planName: '',
  isDeleting: false,
})

// Set active dialog state
const activeDialog = ref({
  isOpen: false,
  planId: null as string | null,
  planName: '',
  isLoading: false,
})

// Computed
const hasPlans = computed(() => plans.value.length > 0)

// Methods
const fetchPlans = async (): Promise<void> => {
  isLoading.value = true
  error.value = null

  try {
    const response = await workoutPlanService.getAll({ page: 1, limit: 50 })
    plans.value = response.plans
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load plans'
    uiStore.error('Failed to load workout plans. Please try again.')
  } finally {
    isLoading.value = false
  }
}

const openDeleteDialog = (plan: WorkoutPlanListItem): void => {
  deleteDialog.value = {
    isOpen: true,
    planId: plan.id,
    planName: plan.name,
    isDeleting: false,
  }
}

const closeDeleteDialog = (): void => {
  deleteDialog.value = {
    isOpen: false,
    planId: null,
    planName: '',
    isDeleting: false,
  }
}

const confirmDelete = async (): Promise<void> => {
  if (!deleteDialog.value.planId) return

  deleteDialog.value.isDeleting = true

  try {
    await workoutPlanService.delete(deleteDialog.value.planId)

    // Remove from local list
    plans.value = plans.value.filter((p) => p.id !== deleteDialog.value.planId)

    uiStore.success('Plan deleted successfully')

    closeDeleteDialog()
  } catch (err: any) {
    const errorMessage =
      err.response?.data?.error?.message || 'Failed to delete plan. Please try again.'

    uiStore.error(errorMessage)

    deleteDialog.value.isDeleting = false
  }
}

const openActiveDialog = (plan: WorkoutPlanListItem): void => {
  activeDialog.value = {
    isOpen: true,
    planId: plan.id,
    planName: plan.name,
    isLoading: false,
  }
}

const closeActiveDialog = (): void => {
  activeDialog.value = {
    isOpen: false,
    planId: null,
    planName: '',
    isLoading: false,
  }
}

const confirmSetActive = async (): Promise<void> => {
  if (!activeDialog.value.planId) return

  activeDialog.value.isLoading = true

  try {
    await workoutPlanService.setActive(activeDialog.value.planId, { is_active: true })

    // Update local list - set this plan as active, deactivate others
    plans.value = plans.value.map((p) => ({
      ...p,
      is_active: p.id === activeDialog.value.planId,
    }))

    uiStore.success(`${activeDialog.value.planName} is now your active plan`)

    closeActiveDialog()
  } catch (err: any) {
    const errorMessage =
      err.response?.data?.error?.message || 'Failed to set active plan. Please try again.'

    uiStore.error(errorMessage)

    activeDialog.value.isLoading = false
  }
}

const navigateToPlan = (planId: string): void => {
  router.push(`/plans/${planId}`)
}

const navigateToEdit = (planId: string): void => {
  router.push(`/plans/${planId}/edit`)
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Lifecycle
onMounted(() => {
  fetchPlans()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Workout Plans</h1>
        <p class="text-gray-600 dark:text-gray-400">Manage your workout routines</p>
      </div>
      <RouterLink to="/plans/import" class="btn btn-md btn-primary"> Import Plan </RouterLink>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <BaseCard v-for="i in 3" :key="i" class="animate-pulse">
        <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3"></div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
      </BaseCard>
    </div>

    <!-- Error State -->
    <BaseCard v-else-if="error" class="text-center py-8">
      <div class="text-red-600 dark:text-red-400 mb-4">
        <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
        Failed to load plans
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
      <BaseButton @click="fetchPlans">Try Again</BaseButton>
    </BaseCard>

    <!-- Empty State -->
    <BaseCard v-else-if="!hasPlans" class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        />
      </svg>
      <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
        No workout plans yet
      </h3>
      <p class="mt-2 text-gray-500 dark:text-gray-400">
        Get started by importing your first workout plan.
      </p>
      <div class="mt-6">
        <RouterLink to="/plans/import" class="btn btn-md btn-primary">
          Import Your First Plan
        </RouterLink>
      </div>
    </BaseCard>

    <!-- Plans Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <BaseCard
        v-for="plan in plans"
        :key="plan.id"
        class="hover:shadow-md transition-shadow cursor-pointer"
        @click="navigateToPlan(plan.id)"
      >
        <!-- Plan Header -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
                {{ plan.name }}
              </h3>
              <BaseBadge v-if="plan.is_active" variant="success" size="sm">Active</BaseBadge>
            </div>
          </div>
        </div>

        <!-- Description -->
        <p
          v-if="plan.description"
          class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2"
          :title="plan.description"
        >
          {{ plan.description }}
        </p>

        <!-- Metadata -->
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <BaseBadge variant="gray">
            {{ plan.workout_count }} {{ plan.workout_count === 1 ? 'workout' : 'workouts' }}
          </BaseBadge>
          <BaseBadge variant="gray">
            {{ plan.exercise_count }} {{ plan.exercise_count === 1 ? 'exercise' : 'exercises' }}
          </BaseBadge>
          <span>·</span>
          <span>Updated {{ formatDate(plan.updated_at) }}</span>
        </div>

        <!-- Actions -->
        <div
          class="flex items-center gap-2 pt-3 border-t border-gray-100 dark:border-gray-700"
          @click.stop
        >
          <BaseButton type="button" variant="outline" size="sm" @click="navigateToPlan(plan.id)">
            View
          </BaseButton>
          <BaseButton type="button" variant="outline" size="sm" @click="navigateToEdit(plan.id)">
            Edit
          </BaseButton>
          <BaseButton
            v-if="!plan.is_active"
            type="button"
            variant="outline"
            size="sm"
            class="text-green-600 hover:text-green-700 hover:bg-green-50 dark:text-green-400 dark:hover:text-green-300 dark:hover:bg-green-900/30"
            @click="openActiveDialog(plan)"
          >
            Set Active
          </BaseButton>
          <BaseButton
            type="button"
            variant="ghost"
            size="sm"
            class="text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/30"
            @click="openDeleteDialog(plan)"
          >
            Delete
          </BaseButton>
        </div>
      </BaseCard>
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmationDialog
      v-model="deleteDialog.isOpen"
      title="Delete Workout Plan"
      :message="`Are you sure you want to delete '${deleteDialog.planName}'? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-variant="danger"
      :is-loading="deleteDialog.isDeleting"
      @confirm="confirmDelete"
      @cancel="closeDeleteDialog"
    />

    <!-- Set Active Confirmation Dialog -->
    <ConfirmationDialog
      v-model="activeDialog.isOpen"
      title="Set Active Plan"
      :message="`Set '${activeDialog.planName}' as your active workout plan? This will deactivate any currently active plan.`"
      confirm-text="Set Active"
      confirm-variant="primary"
      :is-loading="activeDialog.isLoading"
      @confirm="confirmSetActive"
      @cancel="closeActiveDialog"
    />
  </div>
</template>
