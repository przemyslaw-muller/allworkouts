<script setup lang="ts">
/**
 * Plan detail view.
 * Shows workout plan details with exercises and option to start workout.
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import { workoutPlanService } from '@/services/workoutPlanService'
import { workoutSessionService } from '@/services/workoutSessionService'
import { useUiStore } from '@/stores/ui'
import type { WorkoutPlanDetailResponse, WorkoutExerciseDetail, MuscleGroup } from '@/types'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()

// State
const plan = ref<WorkoutPlanDetailResponse | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)
const isStartingWorkout = ref(false)
const startingWorkoutId = ref<string | null>(null)

// Delete dialog state
const deleteDialog = ref({
  isOpen: false,
  isDeleting: false,
})

// Computed
const planId = computed(() => route.params.id as string)

const totalExerciseCount = computed(() => {
  if (!plan.value) return 0
  return plan.value.workouts.reduce((acc, w) => acc + w.exercises.length, 0)
})

const estimatedDurationMinutes = computed(() => {
  if (!plan.value) return 0

  let totalSeconds = 0
  for (const workout of plan.value.workouts) {
    for (const exercise of workout.exercises) {
      // Assume ~45 seconds per set for actual lifting
      totalSeconds += exercise.sets * 45
      // Add rest time between sets
      const restTime = exercise.rest_time_seconds || 60
      totalSeconds += (exercise.sets - 1) * restTime
    }
  }

  return Math.ceil(totalSeconds / 60)
})

const primaryMuscleGroups = computed(() => {
  if (!plan.value) return []

  const muscleGroupCounts = new Map<MuscleGroup, number>()

  for (const workout of plan.value.workouts) {
    for (const exercise of workout.exercises) {
      for (const mg of exercise.exercise.primary_muscle_groups) {
        muscleGroupCounts.set(mg, (muscleGroupCounts.get(mg) || 0) + 1)
      }
    }
  }

  // Sort by count and return top 3
  return Array.from(muscleGroupCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([mg]) => mg)
})

// Methods
const fetchPlan = async (): Promise<void> => {
  isLoading.value = true
  error.value = null

  try {
    plan.value = await workoutPlanService.getById(planId.value)
  } catch (err: any) {
    const status = err.response?.status
    if (status === 404) {
      error.value = 'Plan not found'
      // Redirect after delay
      setTimeout(() => router.push('/plans'), 2000)
    } else {
      error.value = 'Failed to load plan details'
    }
    uiStore.error(error.value)
  } finally {
    isLoading.value = false
  }
}

const startWorkout = async (workoutId: string): Promise<void> => {
  if (!plan.value) return

  isStartingWorkout.value = true
  startingWorkoutId.value = workoutId

  try {
    await workoutSessionService.start({
      workout_id: workoutId,
    })

    uiStore.success('Workout started!')

    // Navigate to active workout
    router.push('/workout')
  } catch (err: any) {
    const code = err.response?.data?.error?.code

    if (code === 'SESSION_IN_PROGRESS') {
      uiStore.warning('You already have a workout in progress')
    } else {
      uiStore.error('Failed to start workout. Please try again.')
    }
  } finally {
    isStartingWorkout.value = false
    startingWorkoutId.value = null
  }
}

const openDeleteDialog = (): void => {
  deleteDialog.value.isOpen = true
}

const closeDeleteDialog = (): void => {
  deleteDialog.value = {
    isOpen: false,
    isDeleting: false,
  }
}

const confirmDelete = async (): Promise<void> => {
  if (!plan.value) return

  deleteDialog.value.isDeleting = true

  try {
    await workoutPlanService.delete(plan.value.id)

    uiStore.success('Plan deleted successfully')

    router.push('/plans')
  } catch (err: any) {
    const errorMessage =
      err.response?.data?.error?.message || 'Failed to delete plan. Please try again.'

    uiStore.error(errorMessage)

    deleteDialog.value.isDeleting = false
  }
}

const formatReps = (exercise: WorkoutExerciseDetail): string => {
  if (exercise.reps_min === exercise.reps_max) {
    return `${exercise.reps_min} reps`
  }
  return `${exercise.reps_min}-${exercise.reps_max} reps`
}

const formatRestTime = (seconds: number | null): string => {
  if (!seconds) return 'No rest specified'
  if (seconds < 60) return `${seconds}s rest`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (remainingSeconds === 0) return `${minutes}m rest`
  return `${minutes}m ${remainingSeconds}s rest`
}

const formatMuscleGroup = (muscleGroup: MuscleGroup): string => {
  return muscleGroup
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const getConfidenceBadgeVariant = (level: string): 'success' | 'warning' | 'gray' => {
  if (level === 'high') return 'success'
  if (level === 'medium') return 'warning'
  return 'gray'
}

// Lifecycle
onMounted(() => {
  fetchPlan()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Loading State -->
    <div v-if="isLoading" class="space-y-6">
      <!-- Header skeleton -->
      <div class="animate-pulse">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-2"></div>
        <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-64 mb-2"></div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48"></div>
      </div>

      <!-- Exercise cards skeleton -->
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
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{{ error }}</h3>
      <div class="flex gap-2 justify-center">
        <BaseButton @click="fetchPlan">Try Again</BaseButton>
        <RouterLink to="/plans" class="btn btn-md btn-outline"> Back to Plans </RouterLink>
      </div>
    </BaseCard>

    <!-- Content -->
    <template v-else-if="plan">
      <!-- Header -->
      <div>
        <RouterLink
          to="/plans"
          class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 mb-2 inline-flex items-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Plans
        </RouterLink>

        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              {{ plan.name }}
            </h1>
            <p v-if="plan.description" class="text-gray-600 dark:text-gray-400 mb-4">
              {{ plan.description }}
            </p>
          </div>

          <div class="flex gap-2 ml-4">
            <RouterLink :to="`/plans/${plan.id}/edit`" class="btn btn-md btn-outline">
              Edit
            </RouterLink>
            <BaseButton variant="ghost" size="md" @click="openDeleteDialog">
              <svg
                class="w-5 h-5 text-red-600 dark:text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Plan Stats -->
      <BaseCard>
        <div class="flex items-center gap-6 flex-wrap">
          <div class="flex items-center gap-2">
            <svg
              class="w-5 h-5 text-gray-400 dark:text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              <span class="font-semibold text-gray-900 dark:text-gray-100">{{
                plan.workouts.length
              }}</span>
              {{ plan.workouts.length === 1 ? 'workout' : 'workouts' }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <svg
              class="w-5 h-5 text-gray-400 dark:text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              <span class="font-semibold text-gray-900 dark:text-gray-100">{{
                totalExerciseCount
              }}</span>
              {{ totalExerciseCount === 1 ? 'exercise' : 'exercises' }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <svg
              class="w-5 h-5 text-gray-400 dark:text-gray-500"
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
            <span class="text-sm text-gray-600 dark:text-gray-400">
              <span class="font-semibold text-gray-900 dark:text-gray-100"
                >~{{ estimatedDurationMinutes }}</span
              >
              minutes
            </span>
          </div>

          <div v-if="primaryMuscleGroups.length > 0" class="flex items-center gap-2">
            <svg
              class="w-5 h-5 text-gray-400 dark:text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <div class="flex gap-1">
              <BaseBadge v-for="mg in primaryMuscleGroups" :key="mg" variant="gray" size="sm">
                {{ formatMuscleGroup(mg) }}
              </BaseBadge>
            </div>
          </div>

          <div v-if="plan.is_active" class="flex items-center gap-2">
            <BaseBadge variant="success" size="sm">Active Plan</BaseBadge>
          </div>
        </div>
      </BaseCard>

      <!-- Workouts -->
      <div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Workouts</h2>

        <!-- Empty state -->
        <BaseCard v-if="plan.workouts.length === 0" class="text-center py-8">
          <p class="text-gray-500 dark:text-gray-400">No workouts in this plan yet.</p>
          <RouterLink :to="`/plans/${plan.id}/edit`" class="btn btn-md btn-primary mt-4">
            Add Workouts
          </RouterLink>
        </BaseCard>

        <!-- Workouts list -->
        <div v-else class="space-y-6">
          <div v-for="(workout, workoutIndex) in plan.workouts" :key="workout.id">
            <!-- Workout header -->
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm shadow-md"
                >
                  {{ workoutIndex + 1 }}
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {{ workout.name }}
                </h3>
                <BaseBadge v-if="workout.day_number" variant="gray" size="sm">
                  Day {{ workout.day_number }}
                </BaseBadge>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ workout.exercises.length }}
                  {{ workout.exercises.length === 1 ? 'exercise' : 'exercises' }}
                </span>
              </div>
              <BaseButton
                variant="primary"
                size="sm"
                :disabled="isStartingWorkout"
                @click="startWorkout(workout.id)"
              >
                <BaseSpinner
                  v-if="isStartingWorkout && startingWorkoutId === workout.id"
                  size="sm"
                  class="mr-2"
                />
                {{
                  isStartingWorkout && startingWorkoutId === workout.id
                    ? 'Starting...'
                    : 'Start Workout'
                }}
              </BaseButton>
            </div>

            <!-- Exercises in workout -->
            <div class="space-y-3 ml-11">
              <BaseCard
                v-for="(exercise, exerciseIndex) in workout.exercises"
                :key="exercise.id"
                class="relative"
              >
                <!-- Sequence number badge -->
                <div
                  class="absolute -left-3 -top-3 w-6 h-6 bg-gray-500 text-white rounded-full flex items-center justify-center font-semibold text-xs shadow-md"
                >
                  {{ exerciseIndex + 1 }}
                </div>

                <div class="space-y-3">
                  <!-- Exercise name and muscle groups -->
                  <div>
                    <h4 class="text-base font-semibold text-gray-900 dark:text-gray-100">
                      {{ exercise.exercise.name }}
                    </h4>
                    <div class="flex items-center gap-2 mt-1">
                      <BaseBadge
                        v-for="mg in exercise.exercise.primary_muscle_groups"
                        :key="mg"
                        variant="primary"
                        size="sm"
                      >
                        {{ formatMuscleGroup(mg) }}
                      </BaseBadge>
                      <BaseBadge
                        v-for="mg in exercise.exercise.secondary_muscle_groups"
                        :key="mg"
                        variant="gray"
                        size="sm"
                      >
                        {{ formatMuscleGroup(mg) }}
                      </BaseBadge>
                    </div>
                  </div>

                  <!-- Sets, reps, rest -->
                  <div class="flex items-center gap-4 text-sm">
                    <div class="flex items-center gap-2">
                      <svg
                        class="w-4 h-4 text-gray-400 dark:text-gray-500"
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
                      <span class="text-gray-600 dark:text-gray-400">
                        <span class="font-semibold text-gray-900 dark:text-gray-100">{{
                          exercise.sets
                        }}</span>
                        {{ exercise.sets === 1 ? 'set' : 'sets' }}
                      </span>
                    </div>

                    <span class="text-gray-300 dark:text-gray-600">x</span>

                    <div class="flex items-center gap-2">
                      <svg
                        class="w-4 h-4 text-gray-400 dark:text-gray-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
                        />
                      </svg>
                      <span class="text-gray-600 dark:text-gray-400">
                        <span class="font-semibold text-gray-900 dark:text-gray-100">{{
                          formatReps(exercise)
                        }}</span>
                      </span>
                    </div>

                    <span class="text-gray-300 dark:text-gray-600">-</span>

                    <div class="flex items-center gap-2">
                      <svg
                        class="w-4 h-4 text-gray-400 dark:text-gray-500"
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
                      <span class="text-gray-600 dark:text-gray-400 text-sm">{{
                        formatRestTime(exercise.rest_time_seconds)
                      }}</span>
                    </div>
                  </div>

                  <!-- Confidence badge -->
                  <div v-if="exercise.confidence_level !== 'high'" class="flex items-center gap-2">
                    <BaseBadge
                      :variant="getConfidenceBadgeVariant(exercise.confidence_level)"
                      size="sm"
                    >
                      {{ exercise.confidence_level }} confidence
                    </BaseBadge>
                    <span class="text-xs text-gray-500 dark:text-gray-400">From import</span>
                  </div>
                </div>
              </BaseCard>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Delete Confirmation Dialog -->
    <ConfirmationDialog
      v-model="deleteDialog.isOpen"
      title="Delete Workout Plan"
      :message="`Are you sure you want to delete '${plan?.name}'? This action cannot be undone.`"
      confirm-text="Delete"
      confirm-variant="danger"
      :is-loading="deleteDialog.isDeleting"
      @confirm="confirmDelete"
      @cancel="closeDeleteDialog"
    />
  </div>
</template>
