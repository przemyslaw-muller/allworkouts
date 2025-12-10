<script setup lang="ts">
/**
 * Session detail view.
 * Shows detailed information about a completed workout session.
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink, useRouter } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { workoutSessionService } from '@/services/workoutSessionService'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import type { WorkoutSessionDetailResponse, SessionStatus, ExerciseSetDetail } from '@/types'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const authStore = useAuthStore()

const sessionId = route.params.id as string

// State
const session = ref<WorkoutSessionDetailResponse | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

// Computed
const totalVolume = computed(() => {
  if (!session.value) return 0

  let volume = 0
  for (const exerciseSession of session.value.exercise_sessions) {
    for (const set of exerciseSession.sets) {
      if (!set.is_warmup) {
        volume += set.weight * set.reps_completed
      }
    }
  }
  return volume
})

const totalSets = computed(() => {
  if (!session.value) return 0

  let count = 0
  for (const exerciseSession of session.value.exercise_sessions) {
    count += exerciseSession.sets.filter((s) => !s.is_warmup).length
  }
  return count
})

const exerciseCount = computed(() => session.value?.exercise_sessions.length || 0)

// Methods
const fetchSession = async (): Promise<void> => {
  isLoading.value = true
  error.value = null

  try {
    const response = await workoutSessionService.getById(sessionId)
    session.value = response
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load session details'
    uiStore.error('Failed to load session details. Please try again.')
  } finally {
    isLoading.value = false
  }
}

const repeatWorkout = (): void => {
  if (!session.value) return
  // Navigate to start a new session with the same workout plan
  router.push(`/plans/${session.value.workout_plan.id}`)
}

const formatDuration = (seconds: number | null): string => {
  if (!seconds) return 'N/A'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const formatDate = (isoString: string): string => {
  const date = new Date(isoString)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const formatTime = (isoString: string): string => {
  const date = new Date(isoString)
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}

const formatWeight = (weight: number, unit: string): string => {
  return `${weight} ${unit}`
}

const getStatusVariant = (status: SessionStatus): 'success' | 'danger' | 'warning' => {
  if (status === 'completed') return 'success'
  if (status === 'abandoned') return 'danger'
  return 'warning'
}

const getStatusLabel = (status: SessionStatus): string => {
  if (status === 'completed') return 'Completed'
  if (status === 'abandoned') return 'Abandoned'
  return 'In Progress'
}

const getSetVolume = (set: ExerciseSetDetail): number => {
  return set.weight * set.reps_completed
}

const getExerciseTotalVolume = (sets: ExerciseSetDetail[]): number => {
  return sets.filter((s) => !s.is_warmup).reduce((sum, set) => sum + getSetVolume(set), 0)
}

const getExerciseTotalReps = (sets: ExerciseSetDetail[]): number => {
  return sets.filter((s) => !s.is_warmup).reduce((sum, set) => sum + set.reps_completed, 0)
}

// Lifecycle
onMounted(() => {
  fetchSession()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <RouterLink
        to="/history"
        class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 mb-2 inline-flex items-center gap-1"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to History
      </RouterLink>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <BaseSpinner size="lg" />
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
        Failed to load session
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
      <BaseButton @click="fetchSession">Try Again</BaseButton>
    </BaseCard>

    <!-- Session Content -->
    <template v-else-if="session">
      <!-- Session Header -->
      <BaseCard>
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {{ session.workout.name }}
              </h1>
              <BaseBadge :variant="getStatusVariant(session.status)">
                {{ getStatusLabel(session.status) }}
              </BaseBadge>
            </div>
            <p class="text-gray-600 dark:text-gray-400 mb-1">
              {{ session.workout_plan.name }}
            </p>
            <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span>{{ formatDate(session.started_at) }}</span>
              <span>·</span>
              <span>{{ formatTime(session.started_at) }}</span>
            </div>
          </div>
          <BaseButton
            v-if="session.status === 'completed'"
            variant="outline"
            @click="repeatWorkout"
          >
            Repeat Workout
          </BaseButton>
        </div>

        <!-- Session Stats -->
        <div
          class="grid grid-cols-1 sm:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700"
        >
          <div class="text-center">
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {{
                formatDuration(
                  session.completed_at
                    ? (new Date(session.completed_at).getTime() -
                        new Date(session.started_at).getTime()) /
                        1000
                    : null,
                )
              }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Duration</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ exerciseCount }}</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Exercises</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ totalSets }}</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Sets</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {{ totalVolume.toFixed(0) }}
              {{ authStore.user?.unit_system === 'metric' ? 'kg' : 'lbs' }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Total Volume</p>
          </div>
        </div>

        <!-- Session Notes -->
        <div v-if="session.notes" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</p>
          <p class="text-gray-600 dark:text-gray-400">{{ session.notes }}</p>
        </div>
      </BaseCard>

      <!-- Exercise Sessions -->
      <div class="space-y-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Exercises</h2>

        <BaseCard
          v-for="(exerciseSession, index) in session.exercise_sessions"
          :key="exerciseSession.id"
          class="space-y-4"
        >
          <!-- Exercise Header -->
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
                {{ index + 1 }}. {{ exerciseSession.exercise.name }}
              </h3>
              <div
                class="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-400"
              >
                <span>{{ exerciseSession.sets.filter((s) => !s.is_warmup).length }} sets</span>
                <span>·</span>
                <span>{{ getExerciseTotalReps(exerciseSession.sets) }} reps</span>
                <span>·</span>
                <span>
                  {{ getExerciseTotalVolume(exerciseSession.sets).toFixed(0) }}
                  {{ authStore.user?.unit_system === 'metric' ? 'kg' : 'lbs' }} volume
                </span>
              </div>
            </div>
          </div>

          <!-- Exercise Notes -->
          <div v-if="exerciseSession.notes" class="text-sm text-gray-600 dark:text-gray-400 italic">
            {{ exerciseSession.notes }}
          </div>

          <!-- Sets Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th
                    scope="col"
                    class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    Set
                  </th>
                  <th
                    scope="col"
                    class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    Weight
                  </th>
                  <th
                    scope="col"
                    class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    Reps
                  </th>
                  <th
                    scope="col"
                    class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    Volume
                  </th>
                  <th
                    scope="col"
                    class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    RPE
                  </th>
                </tr>
              </thead>
              <tbody
                class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700"
              >
                <tr
                  v-for="set in exerciseSession.sets"
                  :key="set.id"
                  :class="{ 'opacity-60': set.is_warmup }"
                >
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ set.set_number }}{{ set.is_warmup ? ' (W)' : '' }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ formatWeight(set.weight, set.weight_unit) }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ set.reps_completed }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ getSetVolume(set).toFixed(0) }} {{ set.weight_unit }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ set.rpe || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Set Notes -->
          <div v-if="exerciseSession.sets.some((s) => s.notes)" class="space-y-1">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Set Notes:</p>
            <div
              v-for="set in exerciseSession.sets.filter((s) => s.notes)"
              :key="set.id"
              class="text-sm text-gray-600 dark:text-gray-400"
            >
              <span class="font-medium">Set {{ set.set_number }}:</span> {{ set.notes }}
            </div>
          </div>
        </BaseCard>
      </div>
    </template>
  </div>
</template>
