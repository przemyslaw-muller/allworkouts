<script setup lang="ts">
/**
 * Active workout session view.
 * Real-time workout logging with set tracking, rest timer, and progress indication.
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useWorkoutStore } from '@/stores/workout'
import { useUiStore } from '@/stores/ui'
import type { ExerciseSetLogItem, PlannedExerciseWithContext } from '@/types'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import RestTimer from '@/components/common/RestTimer.vue'
import ExerciseDetailSlideOver from '@/components/common/ExerciseDetailSlideOver.vue'

const router = useRouter()
const route = useRoute()
const workoutStore = useWorkoutStore()
const uiStore = useUiStore()

// Local state
const sessionId = ref<string | null>(null)
const elapsedTime = ref(0)
const elapsedInterval = ref<number | null>(null)
const showExitDialog = ref(false)
const showRestTimer = ref(false)
const restTimerSeconds = ref(180)
const showExerciseDetail = ref(false)
const selectedExercise = ref<PlannedExerciseWithContext | null>(null)
const isSubmitting = ref(false)

// Exercise tracking state
interface SetInput {
  weight: string
  reps: string
}

const currentExerciseSetInputs = ref<SetInput[]>([])
const loggedSets = ref<Map<string, ExerciseSetLogItem[]>>(new Map())

// Computed
const session = computed(() => workoutStore.activeSession)
const exercises = computed(() => workoutStore.sessionExercises)
const currentExerciseIndex = computed(() => workoutStore.currentExerciseIndex)
const currentExercise = computed(() => workoutStore.currentExercise)
const progress = computed(() => workoutStore.sessionProgress)
const allCompleted = computed(() => workoutStore.allExercisesCompleted)

// Format elapsed time
const formattedElapsedTime = computed(() => {
  const hours = Math.floor(elapsedTime.value / 3600)
  const minutes = Math.floor((elapsedTime.value % 3600) / 60)
  const seconds = elapsedTime.value % 60

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

// Get exercise status
function getExerciseStatus(exerciseId: string): 'completed' | 'current' | 'pending' {
  if (workoutStore.isExerciseCompleted(exerciseId)) {
    return 'completed'
  }
  if (currentExercise.value?.exercise.id === exerciseId) {
    return 'current'
  }
  return 'pending'
}

// Initialize set inputs for current exercise
function initializeSetInputs() {
  if (!currentExercise.value) return

  const plannedSets = currentExercise.value.planned_sets
  const logged = loggedSets.value.get(currentExercise.value.exercise.id) || []

  // Pre-fill from previous session or defaults
  currentExerciseSetInputs.value = Array.from({ length: plannedSets }, (_, i) => {
    if (i < logged.length) {
      // Already logged
      return {
        weight: logged[i].weight.toString(),
        reps: logged[i].reps.toString(),
      }
    }

    // Pre-fill from context (recent session or defaults)
    const recentSession = currentExercise.value?.context.recent_sessions[0]
    const recentSet = recentSession?.sets[i]

    return {
      weight: recentSet?.weight?.toString() || '',
      reps: recentSet?.reps?.toString() || currentExercise.value?.planned_reps_min.toString() || '',
    }
  })
}

// Log a single set
async function logSet(setIndex: number) {
  if (!currentExercise.value) return

  const input = currentExerciseSetInputs.value[setIndex]
  if (!input.weight || !input.reps) {
    uiStore.showToast('Please enter both weight and reps', 'error')
    return
  }

  isSubmitting.value = true

  try {
    const weight = parseFloat(input.weight)
    const reps = parseInt(input.reps, 10)

    if (isNaN(weight) || isNaN(reps) || weight <= 0 || reps <= 0) {
      uiStore.showToast('Please enter valid weight and reps', 'error')
      return
    }

    // Add to logged sets
    const exerciseId = currentExercise.value.exercise.id
    const current = loggedSets.value.get(exerciseId) || []
    current.push({
      set_number: setIndex + 1,
      reps,
      weight,
      rest_time_seconds: currentExercise.value.rest_seconds,
    })
    loggedSets.value.set(exerciseId, current)

    // Save to localStorage
    saveViewStateToLocalStorage()

    uiStore.showToast(`Set ${setIndex + 1} logged`, 'success')

    // Show rest timer if not last set and rest time is configured
    if (
      setIndex < currentExerciseSetInputs.value.length - 1 &&
      currentExercise.value.rest_seconds
    ) {
      restTimerSeconds.value = currentExercise.value.rest_seconds
      showRestTimer.value = true
    }
  } catch (error) {
    console.error('Error logging set:', error)
    uiStore.showToast('Failed to log set', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Complete current exercise
async function completeCurrentExercise() {
  if (!currentExercise.value) return

  const exerciseId = currentExercise.value.exercise.id
  const sets = loggedSets.value.get(exerciseId)

  if (!sets || sets.length === 0) {
    uiStore.showToast('Please log at least one set', 'error')
    return
  }

  isSubmitting.value = true

  try {
    const result = await workoutStore.logExercise(exerciseId, sets)

    if (result.success) {
      uiStore.showToast(`${currentExercise.value.exercise.name} completed!`, 'success')

      // Move to next exercise if available
      if (currentExerciseIndex.value < exercises.value.length - 1) {
        workoutStore.goToNextExercise()
        initializeSetInputs()
      }
    } else {
      uiStore.showToast(result.error || 'Failed to log exercise', 'error')
    }
  } catch (error) {
    console.error('Error completing exercise:', error)
    uiStore.showToast('Failed to complete exercise', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Complete workout
async function completeWorkout() {
  if (!allCompleted.value) {
    uiStore.showToast('Please complete all exercises first', 'warning')
    return
  }

  isSubmitting.value = true

  try {
    const result = await workoutStore.completeSession()

    if (result.success) {
      // Clear localStorage (view state)
      clearViewStateFromLocalStorage()

      uiStore.showToast('Workout completed!', 'success')
      router.push('/workout/complete')
    } else {
      uiStore.showToast(result.error || 'Failed to complete workout', 'error')
    }
  } catch (error) {
    console.error('Error completing workout:', error)
    uiStore.showToast('Failed to complete workout', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Exit workout
async function exitWorkout() {
  showExitDialog.value = true
}

// Confirm exit
async function confirmExit() {
  isSubmitting.value = true

  try {
    const result = await workoutStore.skipSession('User exited workout')

    if (result.success) {
      clearViewStateFromLocalStorage()
      uiStore.showToast('Workout abandoned', 'info')
      router.push('/dashboard')
    } else {
      uiStore.showToast(result.error || 'Failed to exit workout', 'error')
    }
  } catch (error) {
    console.error('Error exiting workout:', error)
    uiStore.showToast('Failed to exit workout', 'error')
  } finally {
    isSubmitting.value = false
    showExitDialog.value = false
  }
}

// Show exercise detail
function showExerciseInfo(exercise: PlannedExerciseWithContext) {
  selectedExercise.value = exercise
  showExerciseDetail.value = true
}

// Handle rest timer complete
function onRestTimerComplete() {
  showRestTimer.value = false
  uiStore.showToast('Rest complete!', 'info')
}

// Handle rest timer skip
function onRestTimerSkip() {
  showRestTimer.value = false
}

// Go to exercise
function goToExercise(index: number) {
  workoutStore.goToExercise(index)
  initializeSetInputs()
}

// LocalStorage helpers for view-specific state (elapsed time, uncommitted sets)
const VIEW_SESSION_KEY = 'activeWorkoutSession_view'

function saveViewStateToLocalStorage() {
  if (!session.value) return

  const data = {
    sessionId: session.value.session_id,
    loggedSets: Array.from(loggedSets.value.entries()),
    elapsedTime: elapsedTime.value,
  }

  try {
    localStorage.setItem(VIEW_SESSION_KEY, JSON.stringify(data))
  } catch (error) {
    console.error('Error saving view state to localStorage:', error)
  }
}

function loadViewStateFromLocalStorage() {
  try {
    const data = localStorage.getItem(VIEW_SESSION_KEY)
    if (data) {
      const parsed = JSON.parse(data)
      // Only load if it matches the current session
      if (session.value && parsed.sessionId === session.value.session_id) {
        loggedSets.value = new Map(parsed.loggedSets)
        elapsedTime.value = parsed.elapsedTime || 0
      }
    }
  } catch (error) {
    console.error('Error loading view state from localStorage:', error)
  }
}

function clearViewStateFromLocalStorage() {
  try {
    localStorage.removeItem(VIEW_SESSION_KEY)
  } catch (error) {
    console.error('Error clearing view state from localStorage:', error)
  }
}

// Start elapsed timer
function startElapsedTimer() {
  if (elapsedInterval.value) return

  elapsedInterval.value = window.setInterval(() => {
    elapsedTime.value++

    // Save to localStorage every 10 seconds
    if (elapsedTime.value % 10 === 0) {
      saveViewStateToLocalStorage()
    }
  }, 1000)
}

function stopElapsedTimer() {
  if (elapsedInterval.value) {
    clearInterval(elapsedInterval.value)
    elapsedInterval.value = null
  }
}

// Initialize on mount
onMounted(async () => {
  // Check if session ID in route params
  sessionId.value = route.params.sessionId as string

  // Load view state from localStorage (elapsed time, uncommitted sets)
  loadViewStateFromLocalStorage()

  // Check if session is active
  if (!session.value) {
    uiStore.showToast('No active workout session', 'error')
    router.push('/dashboard')
    return
  }

  // Initialize set inputs for current exercise
  initializeSetInputs()

  // Start elapsed timer
  startElapsedTimer()
})

// Watch for exercise changes
watch(currentExerciseIndex, () => {
  initializeSetInputs()
})

// Cleanup on unmount
onUnmounted(() => {
  stopElapsedTimer()
  saveViewStateToLocalStorage()
})
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-32">
    <!-- Fixed Header -->
    <div class="fixed top-0 left-0 right-0 z-40 bg-gray-800 border-b border-gray-700 shadow-lg">
      <div class="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between">
        <div>
          <h1 class="text-lg font-bold text-white">{{ session?.workout.name }}</h1>
          <p class="text-sm text-gray-400">{{ session?.workout_plan.name }} - {{ formattedElapsedTime }}</p>
        </div>
        <BaseButton variant="outline" size="sm" @click="exitWorkout"> Exit </BaseButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="!session" class="pt-20 flex justify-center">
      <BaseSpinner size="lg" />
    </div>

    <!-- Content -->
    <div v-else class="pt-20 max-w-2xl mx-auto px-4 py-4 space-y-4">
      <!-- Exercise List -->
      <div class="space-y-3">
        <div v-for="(exercise, index) in exercises" :key="exercise.exercise.id" class="relative">
          <!-- Exercise Card -->
          <BaseCard
            :class="[
              'transition-all cursor-pointer',
              getExerciseStatus(exercise.exercise.id) === 'completed'
                ? '!bg-gray-800 !border-green-500/30 opacity-75'
                : getExerciseStatus(exercise.exercise.id) === 'current'
                  ? '!bg-gray-800 !border-primary-500'
                  : '!bg-gray-800 !border-gray-700 opacity-60',
            ]"
            @click="goToExercise(index)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <!-- Status Icon -->
                  <span
                    v-if="getExerciseStatus(exercise.exercise.id) === 'completed'"
                    class="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center"
                  >
                    <svg
                      class="w-4 h-4 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </span>
                  <span
                    v-else-if="getExerciseStatus(exercise.exercise.id) === 'current'"
                    class="w-6 h-6 rounded-full bg-primary-500 animate-pulse"
                  />
                  <span v-else class="w-6 h-6 rounded-full bg-gray-600" />

                  <h3 class="text-base font-semibold text-white">{{ exercise.exercise.name }}</h3>

                  <!-- Info Button -->
                  <button
                    type="button"
                    class="text-gray-400 hover:text-white transition-colors"
                    aria-label="Exercise info"
                    @click.stop="showExerciseInfo(exercise)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </button>
                </div>

                <p class="text-sm text-gray-400">
                  {{ exercise.planned_sets }} sets × {{ exercise.planned_reps_min
                  }}{{
                    exercise.planned_reps_max !== exercise.planned_reps_min
                      ? `-${exercise.planned_reps_max}`
                      : ''
                  }}
                  reps
                  <span v-if="exercise.rest_seconds">
                    • {{ Math.floor(exercise.rest_seconds / 60) }}:{{
                      (exercise.rest_seconds % 60).toString().padStart(2, '0')
                    }}
                    rest</span
                  >
                </p>

                <!-- Context info for current exercise -->
                <div
                  v-if="
                    getExerciseStatus(exercise.exercise.id) === 'current' &&
                    exercise.context.recent_sessions.length > 0
                  "
                  class="mt-2 text-xs text-gray-500"
                >
                  Last time: {{ exercise.context.recent_sessions[0].sets.length }} sets ×
                  {{ exercise.context.recent_sessions[0].sets[0]?.weight || '-' }}
                  {{ exercise.context.recent_sessions[0].sets[0] ? 'kg' : '' }}
                </div>
              </div>
            </div>

            <!-- Set Logging (only for current exercise) -->
            <div
              v-if="getExerciseStatus(exercise.exercise.id) === 'current'"
              class="mt-4 space-y-3"
            >
              <div
                v-for="(setInput, setIndex) in currentExerciseSetInputs"
                :key="setIndex"
                class="flex items-center gap-3"
              >
                <span class="text-sm text-gray-400 w-12">Set {{ setIndex + 1 }}</span>

                <!-- Weight Input -->
                <div class="flex-1">
                  <BaseInput
                    v-model="setInput.weight"
                    type="number"
                    step="0.5"
                    placeholder="Weight"
                    class="text-center"
                    :disabled="setIndex < (loggedSets.get(exercise.exercise.id)?.length || 0)"
                  />
                </div>

                <!-- Reps Input -->
                <div class="flex-1">
                  <BaseInput
                    v-model="setInput.reps"
                    type="number"
                    placeholder="Reps"
                    class="text-center"
                    :disabled="setIndex < (loggedSets.get(exercise.exercise.id)?.length || 0)"
                  />
                </div>

                <!-- Log Button -->
                <BaseButton
                  v-if="setIndex >= (loggedSets.get(exercise.exercise.id)?.length || 0)"
                  variant="primary"
                  size="sm"
                  :disabled="isSubmitting"
                  @click.stop="logSet(setIndex)"
                >
                  Log
                </BaseButton>
                <span v-else class="text-green-500 text-sm">✓</span>
              </div>

              <!-- Complete Exercise Button -->
              <BaseButton
                v-if="(loggedSets.get(exercise.exercise.id)?.length || 0) >= exercise.planned_sets"
                variant="primary"
                class="w-full"
                :disabled="isSubmitting"
                @click.stop="completeCurrentExercise"
              >
                Complete Exercise
              </BaseButton>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>

    <!-- Fixed Footer with Progress -->
    <div class="fixed bottom-0 left-0 right-0 z-40 bg-gray-800 border-t border-gray-700 shadow-lg">
      <div class="max-w-2xl mx-auto px-4 py-3">
        <!-- Progress Bar -->
        <div class="mb-3">
          <div class="flex justify-between text-xs text-gray-400 mb-1">
            <span>Progress</span>
            <span>{{ progress.completed }} / {{ progress.total }} exercises</span>
          </div>
          <div class="w-full bg-gray-700 rounded-full h-2">
            <div
              class="bg-primary-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${progress.percentage}%` }"
            />
          </div>
        </div>

        <!-- Complete Workout Button -->
        <BaseButton
          variant="primary"
          class="w-full"
          :disabled="!allCompleted || isSubmitting"
          @click="completeWorkout"
        >
          {{
            allCompleted
              ? 'Complete Workout'
              : `${progress.total - progress.completed} exercises remaining`
          }}
        </BaseButton>
      </div>
    </div>

    <!-- Rest Timer -->
    <RestTimer
      v-if="showRestTimer"
      :initial-seconds="restTimerSeconds"
      @complete="onRestTimerComplete"
      @skip="onRestTimerSkip"
    />

    <!-- Exit Confirmation Dialog -->
    <ConfirmationDialog
      :is-open="showExitDialog"
      title="Exit Workout?"
      message="Your progress will be saved, but the workout will be marked as incomplete. Are you sure you want to exit?"
      confirm-text="Exit Workout"
      cancel-text="Continue Workout"
      variant="danger"
      @confirm="confirmExit"
      @cancel="showExitDialog = false"
    />

    <!-- Exercise Detail Slide Over -->
    <ExerciseDetailSlideOver
      :is-open="showExerciseDetail"
      :exercise="selectedExercise?.exercise || null"
      @close="showExerciseDetail = false"
    />
  </div>
</template>
