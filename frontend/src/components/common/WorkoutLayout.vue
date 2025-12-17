<script setup lang="ts">
/**
 * Specialized layout for active workout view.
 * Minimal distractions, focus on workout controls.
 * Includes workout timer and quick actions in header.
 */
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useWorkoutStore, useUiStore } from '@/stores'

const router = useRouter()
const workoutStore = useWorkoutStore()
const uiStore = useUiStore()

// Timer display
const elapsedTime = ref('00:00')
let timerInterval: ReturnType<typeof setInterval> | null = null

const hasActiveSession = computed(() => workoutStore.hasActiveSession)

const formatTime = (seconds: number): string => {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const updateTimer = () => {
  if (workoutStore.activeSession?.started_at) {
    const start = new Date(workoutStore.activeSession.started_at).getTime()
    const now = Date.now()
    const seconds = Math.floor((now - start) / 1000)
    elapsedTime.value = formatTime(seconds)
  }
}

const handleEndWorkout = async () => {
  const confirmed = await uiStore.confirm({
    title: 'End Workout',
    message: 'Are you sure you want to end this workout? Your progress will be saved.',
    confirmText: 'End Workout',
    cancelText: 'Continue',
    confirmVariant: 'primary',
  })

  if (confirmed) {
    await workoutStore.completeSession()
    router.push('/workout/complete')
  }
}

const handleCancelWorkout = async () => {
  const confirmed = await uiStore.confirm({
    title: 'Cancel Workout',
    message: 'Are you sure you want to cancel? All progress will be lost.',
    confirmText: 'Cancel Workout',
    cancelText: 'Keep Going',
    confirmVariant: 'danger',
  })

  if (confirmed) {
    await workoutStore.skipSession()
    router.push('/')
  }
}

onMounted(() => {
  updateTimer()
  timerInterval = setInterval(updateTimer, 1000)
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white flex flex-col">
    <!-- Workout header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div class="px-4 py-3">
        <div class="flex items-center justify-between">
          <!-- Back/Cancel -->
          <button
            class="p-2 -ml-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            aria-label="Cancel workout"
            @click="handleCancelWorkout"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          <!-- Timer -->
          <div class="flex flex-col items-center">
            <span class="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">Duration</span>
            <span class="text-2xl font-mono font-bold text-gray-900 dark:text-white">{{ elapsedTime }}</span>
          </div>

          <!-- End workout -->
          <button
            v-if="hasActiveSession"
            class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
            @click="handleEndWorkout"
          >
            Finish
          </button>
          <div v-else class="w-16"></div>
        </div>

        <!-- Workout name -->
        <div v-if="workoutStore.activeSession?.workout_plan?.name" class="mt-2 text-center">
          <h1 class="text-sm text-gray-600 dark:text-gray-300 truncate">
            {{ workoutStore.activeSession.workout_plan.name }}
          </h1>
        </div>
      </div>
    </header>

    <!-- Main workout content -->
    <main class="flex-1 overflow-auto">
      <slot />
    </main>

    <!-- No active session fallback -->
    <div v-if="!hasActiveSession" class="flex-1 flex items-center justify-center px-4">
      <div class="text-center">
        <p class="text-gray-600 dark:text-gray-400 mb-4">No active workout session</p>
        <RouterLink
          to="/plans"
          class="inline-block px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
        >
          Start a Workout
        </RouterLink>
      </div>
    </div>
  </div>
</template>
