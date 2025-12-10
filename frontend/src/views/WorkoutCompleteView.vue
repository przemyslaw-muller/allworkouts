<script setup lang="ts">
/**
 * Workout completion summary view.
 * Displays workout statistics and achievements after completing a workout.
 */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkoutStore } from '@/stores/workout'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'

const router = useRouter()
const workoutStore = useWorkoutStore()

const completionResult = computed(() => workoutStore.completionResult)
const hasNewPRs = computed(() => 
  completionResult.value && completionResult.value.new_personal_records.length > 0
)

// Format duration
const formattedDuration = computed(() => {
  if (!completionResult.value) return ''
  
  const seconds = completionResult.value.duration_seconds
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
})

// Record type labels
const recordTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    '1rm': 'One Rep Max',
    'set_volume': 'Set Volume',
    'total_volume': 'Total Volume',
  }
  return labels[type] || type
}

// Navigate to dashboard
function goToDashboard() {
  workoutStore.clearCompletionResult()
  router.push('/dashboard')
}

// Navigate to session detail (if we have session ID)
function viewDetails() {
  if (completionResult.value) {
    router.push(`/history/${completionResult.value.session_id}`)
  }
}

onMounted(() => {
  // Redirect if no completion result
  if (!completionResult.value) {
    router.push('/dashboard')
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center p-4">
    <div v-if="completionResult" class="max-w-md w-full space-y-6">
      <!-- Success Header -->
      <div class="text-center">
        <div class="mb-4 flex justify-center">
          <div class="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center">
            <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">Workout Complete!</h1>
        <p class="text-gray-400">Great job on finishing your workout</p>
      </div>

      <!-- Stats Summary -->
      <BaseCard class="!bg-gray-800 !border-gray-700">
        <div class="grid grid-cols-2 gap-4">
          <!-- Duration -->
          <div class="text-center">
            <div class="text-3xl font-bold text-white mb-1">{{ formattedDuration }}</div>
            <div class="text-sm text-gray-400">Duration</div>
          </div>

          <!-- Exercises -->
          <div class="text-center">
            <div class="text-3xl font-bold text-white mb-1">{{ completionResult.new_personal_records.length }}</div>
            <div class="text-sm text-gray-400">New PRs</div>
          </div>
        </div>
      </BaseCard>

      <!-- Personal Records -->
      <BaseCard v-if="hasNewPRs" class="!bg-gray-800 !border-primary-500">
        <div class="flex items-center gap-2 mb-4">
          <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
            />
          </svg>
          <h2 class="text-xl font-bold text-white">New Personal Records!</h2>
        </div>

        <div class="space-y-3">
          <div
            v-for="(pr, index) in completionResult.new_personal_records"
            :key="index"
            class="bg-gray-700/50 rounded-lg p-3"
          >
            <div class="flex items-start justify-between mb-1">
              <h3 class="font-semibold text-white">{{ pr.exercise_name }}</h3>
              <BaseBadge variant="success">{{ recordTypeLabel(pr.record_type) }}</BaseBadge>
            </div>
            <p class="text-2xl font-bold text-primary-500">
              {{ pr.value }}{{ pr.unit ? ` ${pr.unit}` : '' }}
            </p>
          </div>
        </div>
      </BaseCard>

      <!-- No PRs message -->
      <BaseCard v-else class="!bg-gray-800 !border-gray-700">
        <div class="text-center py-4">
          <p class="text-gray-400">No new personal records this time</p>
          <p class="text-sm text-gray-500 mt-1">Keep pushing to beat your best!</p>
        </div>
      </BaseCard>

      <!-- Actions -->
      <div class="space-y-3">
        <BaseButton variant="primary" class="w-full" @click="goToDashboard">
          Back to Dashboard
        </BaseButton>
        <BaseButton variant="outline" class="w-full" @click="viewDetails">
          View Details
        </BaseButton>
      </div>
    </div>
  </div>
</template>
