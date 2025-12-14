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
import type {
  WorkoutSessionDetailResponse,
  SessionStatus,
  ExerciseSessionFlatDetail,
  ExerciseBrief,
} from '@/types'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const authStore = useAuthStore()

const sessionId = route.params.id as string

// State
const session = ref<WorkoutSessionDetailResponse | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

// Types for grouped exercises
interface GroupedExercise {
  exercise: ExerciseBrief
  sets: ExerciseSessionFlatDetail[]
}

// Computed: Group flat exercise sessions by exercise
const groupedExercises = computed<GroupedExercise[]>(() => {
  if (!session.value) return []

  const groups = new Map<string, GroupedExercise>()

  for (const es of session.value.exercise_sessions) {
    const exerciseId = es.exercise.id
    if (!groups.has(exerciseId)) {
      groups.set(exerciseId, {
        exercise: es.exercise,
        sets: [],
      })
    }
    groups.get(exerciseId)!.sets.push(es)
  }

  // Sort sets within each group by set_number
  for (const group of groups.values()) {
    group.sets.sort((a, b) => a.set_number - b.set_number)
  }

  return Array.from(groups.values())
})

// Computed
const totalVolume = computed(() => {
  if (!session.value) return 0

  return session.value.exercise_sessions.reduce((sum, es) => sum + Number(es.weight) * es.reps, 0)
})

const totalSets = computed(() => {
  return session.value?.exercise_sessions.length || 0
})

const exerciseCount = computed(() => groupedExercises.value.length)

const hasPRs = computed(() => {
  return session.value?.personal_records && session.value.personal_records.length > 0
})

const weightUnit = computed(() => {
  return authStore.user?.unit_system === 'metric' ? 'kg' : 'lbs'
})

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

const getExerciseTotalVolume = (sets: ExerciseSessionFlatDetail[]): number => {
  return sets.reduce((sum, set) => sum + Number(set.weight) * set.reps, 0)
}

const getExerciseTotalReps = (sets: ExerciseSessionFlatDetail[]): number => {
  return sets.reduce((sum, set) => sum + set.reps, 0)
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
      <!-- PRs Summary Card -->
      <BaseCard v-if="hasPRs" class="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-yellow-200 dark:border-yellow-700">
        <div class="flex items-center gap-3 mb-3">
          <div class="flex-shrink-0 w-10 h-10 bg-yellow-100 dark:bg-yellow-800 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-yellow-800 dark:text-yellow-200">
              New Personal Records!
            </h2>
            <p class="text-sm text-yellow-700 dark:text-yellow-300">
              You set {{ session.personal_records.length }} new PR{{ session.personal_records.length > 1 ? 's' : '' }} in this session
            </p>
          </div>
        </div>
        <div class="space-y-2">
          <div
            v-for="(pr, index) in session.personal_records"
            :key="index"
            class="flex items-center justify-between py-2 px-3 bg-white/50 dark:bg-gray-800/50 rounded-lg"
          >
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ pr.exercise_name }}</span>
            <span class="text-yellow-700 dark:text-yellow-300 font-bold">
              {{ Number(pr.value).toFixed(1) }} {{ pr.unit }} (est. 1RM)
            </span>
          </div>
        </div>
      </BaseCard>

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
              <span>{{ formatDate(session.created_at) }}</span>
              <span>·</span>
              <span>{{ formatTime(session.created_at) }}</span>
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
                  session.updated_at && session.status === 'completed'
                    ? (new Date(session.updated_at).getTime() -
                        new Date(session.created_at).getTime()) /
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
              {{ totalVolume.toFixed(0) }} {{ weightUnit }}
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
          v-for="(group, index) in groupedExercises"
          :key="group.exercise.id"
          class="space-y-4"
        >
          <!-- Exercise Header -->
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
                {{ index + 1 }}. {{ group.exercise.name }}
              </h3>
              <div
                class="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-400"
              >
                <span>{{ group.sets.length }} sets</span>
                <span>·</span>
                <span>{{ getExerciseTotalReps(group.sets) }} reps</span>
                <span>·</span>
                <span>
                  {{ getExerciseTotalVolume(group.sets).toFixed(0) }} {{ weightUnit }} volume
                </span>
              </div>
            </div>
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
                    PR
                  </th>
                </tr>
              </thead>
              <tbody
                class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700"
              >
                <tr v-for="set in group.sets" :key="set.id">
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ set.set_number }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ set.weight }} {{ weightUnit }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ set.reps }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                    {{ (Number(set.weight) * set.reps).toFixed(0) }} {{ weightUnit }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap">
                    <span
                      v-if="set.is_pr"
                      class="inline-flex items-center gap-1 px-2 py-1 text-xs font-bold text-yellow-800 bg-yellow-100 dark:text-yellow-200 dark:bg-yellow-800 rounded-full"
                    >
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      PR
                    </span>
                    <span v-else class="text-sm text-gray-400 dark:text-gray-500">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseCard>
      </div>
    </template>
  </div>
</template>
