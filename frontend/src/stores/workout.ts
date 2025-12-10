/**
 * Workout store - manages active workout session and plans cache.
 * Includes localStorage persistence for active session recovery.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  WorkoutPlanListItem,
  WorkoutPlanDetailResponse,
  WorkoutSessionStartResponse,
  PlannedExerciseWithContext,
  ExerciseSetLogItem,
  CompleteSessionResponse,
  WorkoutPlanListParams,
} from '@/types'
import { workoutPlanService, workoutSessionService } from '@/services'
import { getErrorMessage } from '@/services/api'

// localStorage key for session persistence
const ACTIVE_SESSION_KEY = 'allworkouts_active_session'
const SESSION_MAX_AGE_MS = 24 * 60 * 60 * 1000 // 24 hours

// Persisted session data structure
interface PersistedSessionData {
  activeSession: WorkoutSessionStartResponse
  loggedExercises: [string, LoggedExercise][]
  currentExerciseIndex: number
  savedAt: number // timestamp for stale detection
}

// Local state for tracking logged exercises during a session
export interface LoggedExercise {
  exerciseId: string
  exerciseName: string
  sets: ExerciseSetLogItem[]
  isCompleted: boolean
}

export const useWorkoutStore = defineStore('workout', () => {
  // Plans state
  const plans = ref<WorkoutPlanListItem[]>([])
  const currentPlan = ref<WorkoutPlanDetailResponse | null>(null)
  const isLoadingPlans = ref(false)
  const plansError = ref<string | null>(null)
  const plansPagination = ref({ page: 1, limit: 20, total: 0, total_pages: 0 })

  // Active session state
  const activeSession = ref<WorkoutSessionStartResponse | null>(null)
  const loggedExercises = ref<Map<string, LoggedExercise>>(new Map())
  const currentExerciseIndex = ref(0)
  const isSessionLoading = ref(false)
  const sessionError = ref<string | null>(null)

  // Session completion state
  const completionResult = ref<CompleteSessionResponse | null>(null)

  // --- localStorage Persistence Functions ---

  function saveSessionToLocalStorage() {
    if (!activeSession.value) return

    const data: PersistedSessionData = {
      activeSession: activeSession.value,
      loggedExercises: Array.from(loggedExercises.value.entries()),
      currentExerciseIndex: currentExerciseIndex.value,
      savedAt: Date.now(),
    }

    try {
      localStorage.setItem(ACTIVE_SESSION_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save session to localStorage:', error)
    }
  }

  function loadSessionFromLocalStorage(): PersistedSessionData | null {
    try {
      const data = localStorage.getItem(ACTIVE_SESSION_KEY)
      if (!data) return null

      const parsed: PersistedSessionData = JSON.parse(data)
      return parsed
    } catch (error) {
      console.error('Failed to load session from localStorage:', error)
      clearSessionFromLocalStorage()
      return null
    }
  }

  function clearSessionFromLocalStorage() {
    try {
      localStorage.removeItem(ACTIVE_SESSION_KEY)
    } catch (error) {
      console.error('Failed to clear session from localStorage:', error)
    }
  }

  function isSessionStale(savedAt: number): boolean {
    return Date.now() - savedAt > SESSION_MAX_AGE_MS
  }

  /**
   * Restores an active session from localStorage on app init.
   * Returns true if a session was restored, false otherwise.
   */
  function restoreSessionFromLocalStorage(): boolean {
    const data = loadSessionFromLocalStorage()

    if (!data) return false

    // Check if session is stale (>24 hours)
    if (isSessionStale(data.savedAt)) {
      console.log('Stored session is stale (>24 hours), clearing')
      clearSessionFromLocalStorage()
      return false
    }

    // Restore the session state
    activeSession.value = data.activeSession
    loggedExercises.value = new Map(data.loggedExercises)
    currentExerciseIndex.value = data.currentExerciseIndex

    return true
  }

  // --- End localStorage Persistence Functions ---

  // Plans getters
  const hasPlans = computed(() => plans.value.length > 0)

  // Session getters
  const hasActiveSession = computed(() => !!activeSession.value)

  const sessionExercises = computed((): PlannedExerciseWithContext[] => {
    return activeSession.value?.exercises ?? []
  })

  const currentExercise = computed((): PlannedExerciseWithContext | null => {
    if (!activeSession.value) return null
    return activeSession.value.exercises[currentExerciseIndex.value] ?? null
  })

  const sessionProgress = computed(() => {
    if (!activeSession.value) return { completed: 0, total: 0, percentage: 0 }
    const total = activeSession.value.exercises.length
    const completed = Array.from(loggedExercises.value.values()).filter((e) => e.isCompleted).length
    return {
      completed,
      total,
      percentage: total > 0 ? Math.round((completed / total) * 100) : 0,
    }
  })

  const allExercisesCompleted = computed(() => {
    if (!activeSession.value) return false
    return sessionProgress.value.completed === sessionProgress.value.total
  })

  // Plans actions
  async function fetchPlans(params?: WorkoutPlanListParams) {
    try {
      isLoadingPlans.value = true
      plansError.value = null
      const response = await workoutPlanService.getAll(params)
      plans.value = response.plans
      plansPagination.value = response.pagination
    } catch (err) {
      plansError.value = getErrorMessage(err)
    } finally {
      isLoadingPlans.value = false
    }
  }

  async function fetchPlanDetail(planId: string) {
    try {
      isLoadingPlans.value = true
      plansError.value = null
      const data = await workoutPlanService.getById(planId)
      currentPlan.value = data
      return { success: true, data }
    } catch (err) {
      plansError.value = getErrorMessage(err)
      return { success: false, error: plansError.value }
    } finally {
      isLoadingPlans.value = false
    }
  }

  async function deletePlan(planId: string) {
    try {
      await workoutPlanService.delete(planId)
      plans.value = plans.value.filter((p) => p.id !== planId)
      if (currentPlan.value?.id === planId) {
        currentPlan.value = null
      }
      return { success: true }
    } catch (err) {
      return { success: false, error: getErrorMessage(err) }
    }
  }

  // Session actions
  async function startSession(workoutId: string) {
    try {
      isSessionLoading.value = true
      sessionError.value = null
      const data = await workoutSessionService.start({ workout_id: workoutId })
      activeSession.value = data
      loggedExercises.value = new Map()
      currentExerciseIndex.value = 0
      completionResult.value = null

      // Persist to localStorage
      saveSessionToLocalStorage()

      return { success: true, data }
    } catch (err) {
      sessionError.value = getErrorMessage(err)
      return { success: false, error: sessionError.value }
    } finally {
      isSessionLoading.value = false
    }
  }

  async function logExercise(exerciseId: string, sets: ExerciseSetLogItem[]) {
    if (!activeSession.value) {
      return { success: false, error: 'No active session' }
    }

    try {
      isSessionLoading.value = true
      sessionError.value = null
      await workoutSessionService.logExercise(activeSession.value.session_id, {
        exercise_id: exerciseId,
        sets,
      })

      // Find exercise name
      const exercise = activeSession.value.exercises.find((e) => e.exercise.id === exerciseId)

      // Update local state
      loggedExercises.value.set(exerciseId, {
        exerciseId,
        exerciseName: exercise?.exercise.name ?? 'Unknown',
        sets,
        isCompleted: true,
      })

      // Persist to localStorage
      saveSessionToLocalStorage()

      return { success: true }
    } catch (err) {
      sessionError.value = getErrorMessage(err)
      return { success: false, error: sessionError.value }
    } finally {
      isSessionLoading.value = false
    }
  }

  async function completeSession(notes?: string) {
    if (!activeSession.value) {
      return { success: false, error: 'No active session' }
    }

    try {
      isSessionLoading.value = true
      sessionError.value = null
      const data = await workoutSessionService.complete(activeSession.value.session_id, {
        notes,
      })
      completionResult.value = data
      activeSession.value = null
      loggedExercises.value = new Map()
      currentExerciseIndex.value = 0

      // Clear localStorage
      clearSessionFromLocalStorage()

      return { success: true, data }
    } catch (err) {
      sessionError.value = getErrorMessage(err)
      return { success: false, error: sessionError.value }
    } finally {
      isSessionLoading.value = false
    }
  }

  async function skipSession(notes?: string) {
    if (!activeSession.value) {
      return { success: false, error: 'No active session' }
    }

    try {
      isSessionLoading.value = true
      sessionError.value = null
      await workoutSessionService.skip(activeSession.value.session_id, { notes })
      activeSession.value = null
      loggedExercises.value = new Map()
      currentExerciseIndex.value = 0
      completionResult.value = null

      // Clear localStorage
      clearSessionFromLocalStorage()

      return { success: true }
    } catch (err) {
      sessionError.value = getErrorMessage(err)
      return { success: false, error: sessionError.value }
    } finally {
      isSessionLoading.value = false
    }
  }

  function goToExercise(index: number) {
    if (index >= 0 && activeSession.value && index < activeSession.value.exercises.length) {
      currentExerciseIndex.value = index
      saveSessionToLocalStorage()
    }
  }

  function goToNextExercise() {
    if (
      activeSession.value &&
      currentExerciseIndex.value < activeSession.value.exercises.length - 1
    ) {
      currentExerciseIndex.value++
      saveSessionToLocalStorage()
    }
  }

  function goToPreviousExercise() {
    if (currentExerciseIndex.value > 0) {
      currentExerciseIndex.value--
      saveSessionToLocalStorage()
    }
  }

  function getExerciseLogData(exerciseId: string): LoggedExercise | undefined {
    return loggedExercises.value.get(exerciseId)
  }

  function isExerciseCompleted(exerciseId: string): boolean {
    return loggedExercises.value.get(exerciseId)?.isCompleted ?? false
  }

  function clearCompletionResult() {
    completionResult.value = null
  }

  function clearPlansError() {
    plansError.value = null
  }

  function clearSessionError() {
    sessionError.value = null
  }

  return {
    // Plans state
    plans,
    currentPlan,
    isLoadingPlans,
    plansError,
    plansPagination,
    // Session state
    activeSession,
    loggedExercises,
    currentExerciseIndex,
    isSessionLoading,
    sessionError,
    completionResult,
    // Plans getters
    hasPlans,
    // Session getters
    hasActiveSession,
    sessionExercises,
    currentExercise,
    sessionProgress,
    allExercisesCompleted,
    // Plans actions
    fetchPlans,
    fetchPlanDetail,
    deletePlan,
    // Session actions
    startSession,
    logExercise,
    completeSession,
    skipSession,
    goToExercise,
    goToNextExercise,
    goToPreviousExercise,
    getExerciseLogData,
    isExerciseCompleted,
    clearCompletionResult,
    clearPlansError,
    clearSessionError,
    // Session persistence
    restoreSessionFromLocalStorage,
    clearSessionFromLocalStorage,
  }
})
