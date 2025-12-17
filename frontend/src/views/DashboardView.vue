<script setup lang="ts">
/**
 * Dashboard view - main landing page.
 * Shows active session recovery, active plan, quick stats, and action links.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkoutStore } from '@/stores/workout'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { statsService, workoutPlanService } from '@/services'
import { getErrorMessage } from '@/services/api'
import type { StatsOverviewResponse, WorkoutPlanDetailResponse } from '@/types'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import BaseAlert from '@/components/common/BaseAlert.vue'

const router = useRouter()
const workoutStore = useWorkoutStore()
const authStore = useAuthStore()
const uiStore = useUiStore()

// Local state
const stats = ref<StatsOverviewResponse | null>(null)
const isLoadingStats = ref(false)
const statsError = ref<string | null>(null)
const activePlanDetails = ref<WorkoutPlanDetailResponse | null>(null)
const isLoadingPlanDetails = ref(false)

// Computed
const user = computed(() => authStore.user)
const hasActiveSession = computed(() => workoutStore.hasActiveSession)
const activeSession = computed(() => workoutStore.activeSession)
const plans = computed(() => workoutStore.plans)
const hasPlans = computed(() => workoutStore.hasPlans)
const isLoadingPlans = computed(() => workoutStore.isLoadingPlans)

// Active plan (first plan for now, could be enhanced to track which is active)
const activePlan = computed(() => plans.value[0] || null)
const activeWorkouts = computed(() => activePlanDetails.value?.workouts || [])

// Format duration helper
const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

// Calculate elapsed time for active session
const sessionElapsedTime = computed(() => {
  if (!activeSession.value) return ''

  const startTime = new Date(activeSession.value.started_at).getTime()
  const now = Date.now()
  const elapsedMs = now - startTime
  const elapsedMinutes = Math.floor(elapsedMs / (1000 * 60))

  if (elapsedMinutes < 60) return `${elapsedMinutes}m`

  const hours = Math.floor(elapsedMinutes / 60)
  const minutes = elapsedMinutes % 60
  return `${hours}h ${minutes}m`
})

// Get current month workouts count
const currentMonthWorkouts = computed(() => {
  if (!stats.value) return 0

  const currentMonth = new Date().toISOString().slice(0, 7) // YYYY-MM format
  const monthData = stats.value.workouts_by_month.find((m) => m.month === currentMonth)
  return monthData?.count || 0
})

// Actions
async function fetchStats() {
  try {
    isLoadingStats.value = true
    statsError.value = null
    stats.value = await statsService.getOverview()
  } catch (err) {
    console.error('Error fetching stats:', err)
    statsError.value = getErrorMessage(err)
  } finally {
    isLoadingStats.value = false
  }
}

async function fetchPlans() {
  await workoutStore.fetchPlans()
  
  // If there's an active plan, fetch its details to get workouts
  if (activePlan.value) {
    await fetchActivePlanDetails(activePlan.value.id)
  }
}

async function fetchActivePlanDetails(planId: string) {
  try {
    isLoadingPlanDetails.value = true
    activePlanDetails.value = await workoutPlanService.getById(planId)
  } catch (err) {
    console.error('Error fetching plan details:', err)
  } finally {
    isLoadingPlanDetails.value = false
  }
}

async function startWorkout(workoutId?: string) {
  if (!activePlan.value) {
    uiStore.showToast('No workout plan available', 'error')
    return
  }

  try {
    // Use provided workout ID, or fallback to first workout, or use plan ID
    const targetWorkoutId = workoutId || activeWorkouts.value[0]?.id
    
    if (!targetWorkoutId) {
      uiStore.showToast('No workouts found in this plan', 'error')
      return
    }

    const result = await workoutStore.startSession(targetWorkoutId)

    if (result.success && result.data) {
      router.push(`/workout/${result.data.session_id}`)
    } else {
      uiStore.showToast(result.error || 'Failed to start workout', 'error')
    }
  } catch (err) {
    console.error('Error starting workout:', err)
    uiStore.showToast('Failed to start workout', 'error')
  }
}

async function resumeSession() {
  if (activeSession.value) {
    router.push(`/workout/${activeSession.value.session_id}`)
  }
}

async function abandonSession() {
  if (!activeSession.value) return

  try {
    const result = await workoutStore.skipSession('Abandoned from dashboard')

    if (result.success) {
      uiStore.showToast('Session abandoned', 'info')
    } else {
      uiStore.showToast(result.error || 'Failed to abandon session', 'error')
    }
  } catch (err) {
    console.error('Error abandoning session:', err)
    uiStore.showToast('Failed to abandon session', 'error')
  }
}

function goToImport() {
  router.push('/plans/import')
}

// Initialize
onMounted(async () => {
  await Promise.all([fetchStats(), fetchPlans()])
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-6 space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Welcome back{{ user?.email ? `, ${user.email.split('@')[0]}` : '' }}!
      </h1>
      <p class="text-gray-600 dark:text-gray-400">Ready to crush your workout?</p>
    </div>

    <!-- Active Session Recovery Banner -->
    <BaseAlert
      v-if="hasActiveSession && activeSession"
      variant="warning"
      role="region"
      aria-live="polite"
      class="!bg-yellow-900/30 !border-yellow-500"
    >
      <div class="flex items-center justify-between gap-4">
        <div class="flex-1">
          <h3 class="font-semibold text-yellow-200 mb-1">Active Workout in Progress</h3>
          <p class="text-yellow-100 text-sm">
            {{ activeSession.workout_plan.name }} - Started {{ sessionElapsedTime }} ago
          </p>
        </div>
        <div class="flex gap-2">
          <BaseButton variant="outline" size="sm" @click="abandonSession"> Abandon </BaseButton>
          <BaseButton variant="primary" size="sm" @click="resumeSession"> Resume </BaseButton>
        </div>
      </div>
    </BaseAlert>

    <!-- Loading State for Plans -->
    <div v-if="isLoadingPlans" class="flex justify-center py-12">
      <BaseSpinner size="lg" />
    </div>

    <!-- Main Content -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column: Active Plan & Quick Stats -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Active Plan Card -->
        <BaseCard v-if="hasPlans && activePlan">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">{{ activePlan.name }}</h2>
              <p class="text-gray-600 dark:text-gray-400 text-sm">
                {{ activePlan.description || 'Your active workout plan' }}
              </p>
            </div>
            <span
              class="px-3 py-1 bg-primary-500/20 text-primary-400 text-xs font-medium rounded-full"
            >
              Active
            </span>
          </div>

          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400 text-sm mb-4">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <span>{{ activePlan.workout_count }} workouts</span>
            <span class="text-gray-400 dark:text-gray-600">•</span>
            <span>{{ activePlan.exercise_count }} exercises</span>
          </div>

          <!-- Workouts List -->
          <div v-if="isLoadingPlanDetails" class="mb-4 flex justify-center py-4">
            <BaseSpinner size="sm" />
          </div>
          <div v-else-if="activeWorkouts.length > 0" class="mb-4 space-y-2">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Select a workout to start:</p>
            <div
              v-for="workout in activeWorkouts"
              :key="workout.id"
              class="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700/50 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer group"
              @click="() => startWorkout(workout.id)"
            >
              <div class="flex-1">
                <h4 class="text-gray-900 dark:text-white font-medium text-sm">{{ workout.name }}</h4>
                <p class="text-gray-600 dark:text-gray-400 text-xs">
                  {{ workout.exercises.length }} exercise{{ workout.exercises.length !== 1 ? 's' : '' }}
                </p>
              </div>
              <svg
                class="w-5 h-5 text-gray-500 dark:text-gray-400 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          </div>

          <div class="flex gap-3">
            <BaseButton variant="outline" class="flex-1" @click="() => router.push(`/plans/${activePlan.id}`)">
              View Full Plan
            </BaseButton>
          </div>
        </BaseCard>

        <!-- Empty State: No Plans -->
        <BaseCard v-else class="text-center py-12">
          <div class="max-w-sm mx-auto">
            <div class="mb-4 flex justify-center">
              <div class="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                <svg
                  class="w-8 h-8 text-gray-400 dark:text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Workout Plans Yet</h3>
            <p class="text-gray-600 dark:text-gray-400 mb-6">
              Import your first workout plan to get started with your training journey
            </p>
            <BaseButton variant="primary" @click="goToImport"> Import Workout Plan </BaseButton>
          </div>
        </BaseCard>

        <!-- Quick Stats Cards -->
        <div class="grid grid-cols-3 gap-4">
          <!-- Workouts This Month -->
          <BaseCard class="text-center">
            <div v-if="isLoadingStats" class="flex justify-center py-4">
              <BaseSpinner />
            </div>
            <div v-else>
              <p class="text-3xl font-bold text-primary-500 dark:text-primary-400 mb-1">
                {{ currentMonthWorkouts }}
              </p>
              <p class="text-xs text-gray-600 dark:text-gray-400">This Month</p>
            </div>
          </BaseCard>

          <!-- Current Streak -->
          <BaseCard class="text-center">
            <div v-if="isLoadingStats" class="flex justify-center py-4">
              <BaseSpinner />
            </div>
            <div v-else>
              <p class="text-3xl font-bold text-orange-500 dark:text-orange-400 mb-1">
                {{ stats?.current_streak_days || 0 }}
              </p>
              <p class="text-xs text-gray-600 dark:text-gray-400">Day Streak</p>
            </div>
          </BaseCard>

          <!-- Personal Records -->
          <BaseCard class="text-center">
            <div v-if="isLoadingStats" class="flex justify-center py-4">
              <BaseSpinner />
            </div>
            <div v-else>
              <p class="text-3xl font-bold text-green-500 dark:text-green-400 mb-1">
                {{ stats?.personal_records_count || 0 }}
              </p>
              <p class="text-xs text-gray-600 dark:text-gray-400">Total PRs</p>
            </div>
          </BaseCard>
        </div>

        <!-- Stats Error -->
        <BaseAlert v-if="statsError" variant="error">
          <p>Failed to load statistics: {{ statsError }}</p>
        </BaseAlert>
      </div>

      <!-- Right Column: Quick Actions -->
      <div class="space-y-6">
        <!-- Quick Actions Card -->
        <BaseCard>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div class="space-y-3">
            <button
              type="button"
              class="w-full flex items-center gap-3 p-3 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-left"
              @click="() => router.push('/plans')"
            >
              <div
                class="w-10 h-10 bg-primary-100 dark:bg-primary-500/20 rounded-lg flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-primary-600 dark:text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-white">View Plans</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">Manage workout plans</p>
              </div>
              <svg
                class="w-5 h-5 text-gray-500 dark:text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>

            <button
              type="button"
              class="w-full flex items-center gap-3 p-3 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors text-left"
              @click="() => router.push('/history')"
            >
              <div
                class="w-10 h-10 bg-blue-100 dark:bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-blue-600 dark:text-blue-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-white">View History</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">Past workouts</p>
              </div>
              <svg
                class="w-5 h-5 text-gray-500 dark:text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>

            <button
              type="button"
              class="w-full flex items-center gap-3 p-3 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-left"
              @click="() => router.push('/stats')"
            >
              <div
                class="w-10 h-10 bg-green-100 dark:bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-green-600 dark:text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-white">View Stats</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">Progress analytics</p>
              </div>
              <svg
                class="w-5 h-5 text-gray-500 dark:text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
        </BaseCard>

        <!-- Import Plan Button -->
        <BaseButton variant="outline" class="w-full" @click="goToImport">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          Import Workout Plan
        </BaseButton>

        <!-- Total Stats -->
        <BaseCard v-if="stats && !isLoadingStats">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Overall Stats</h2>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-gray-600 dark:text-gray-400 text-sm">Total Workouts</span>
              <span class="text-gray-900 dark:text-white font-semibold">{{ stats.total_workouts }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600 dark:text-gray-400 text-sm">Total Time</span>
              <span class="text-gray-900 dark:text-white font-semibold">{{
                formatDuration(stats.total_duration_seconds)
              }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600 dark:text-gray-400 text-sm">Total Volume</span>
              <span class="text-gray-900 dark:text-white font-semibold">
                {{ Math.round(stats.total_volume_kg).toLocaleString() }} kg
              </span>
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>
