<script setup lang="ts">
/**
 * Stats/Analytics view.
 * Shows workout statistics, progress charts, and trends.
 */
import { ref, computed, onMounted } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import BaseAlert from '@/components/common/BaseAlert.vue'
import { statsService } from '@/services/statsService'
import { getErrorMessage } from '@/services/api'
import type { StatsOverviewResponse, MuscleGroup } from '@/types'

// State
const stats = ref<StatsOverviewResponse | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

// Computed
const formattedDuration = computed(() => {
  if (!stats.value) return '0h'
  const hours = Math.floor(stats.value.total_duration_seconds / 3600)
  const minutes = Math.floor((stats.value.total_duration_seconds % 3600) / 60)
  if (hours === 0) return `${minutes}m`
  if (minutes === 0) return `${hours}h`
  return `${hours}h ${minutes}m`
})

const formattedVolume = computed(() => {
  if (!stats.value) return '0 kg'
  const volume = stats.value.total_volume_kg
  if (volume >= 1000) {
    return `${(volume / 1000).toFixed(1)}t`
  }
  return `${Math.round(volume)} kg`
})

// Get last 6 months for the frequency chart
const frequencyChartData = computed(() => {
  if (!stats.value) return []

  // Generate last 6 months
  const months: { month: string; label: string; count: number }[] = []
  const now = new Date()

  for (let i = 5; i >= 0; i--) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const label = date.toLocaleDateString('en-US', { month: 'short' })

    const workoutData = stats.value.workouts_by_month.find((w) => w.month === monthKey)
    months.push({
      month: monthKey,
      label,
      count: workoutData?.count ?? 0,
    })
  }

  return months
})

const maxFrequencyCount = computed(() => {
  if (frequencyChartData.value.length === 0) return 1
  const max = Math.max(...frequencyChartData.value.map((m) => m.count))
  return max > 0 ? max : 1
})

// Muscle group chart data
const muscleGroupChartData = computed(() => {
  if (!stats.value || stats.value.most_trained_muscle_groups.length === 0) return []

  const maxCount = Math.max(...stats.value.most_trained_muscle_groups.map((m) => m.session_count))

  return stats.value.most_trained_muscle_groups.map((item) => ({
    ...item,
    percentage: maxCount > 0 ? (item.session_count / maxCount) * 100 : 0,
    label: muscleGroupLabels[item.muscle_group] || item.muscle_group,
  }))
})

const muscleGroupLabels: Record<MuscleGroup, string> = {
  chest: 'Chest',
  back: 'Back',
  shoulders: 'Shoulders',
  biceps: 'Biceps',
  triceps: 'Triceps',
  forearms: 'Forearms',
  legs: 'Legs',
  glutes: 'Glutes',
  core: 'Core',
  traps: 'Traps',
  lats: 'Lats',
}

const muscleGroupColors: Record<MuscleGroup, string> = {
  chest: 'bg-red-500',
  back: 'bg-blue-500',
  shoulders: 'bg-yellow-500',
  biceps: 'bg-purple-500',
  triceps: 'bg-pink-500',
  forearms: 'bg-orange-500',
  legs: 'bg-green-500',
  glutes: 'bg-teal-500',
  core: 'bg-indigo-500',
  traps: 'bg-gray-500',
  lats: 'bg-cyan-500',
}

const hasAnyData = computed(() => {
  return stats.value && stats.value.total_workouts > 0
})

// Load stats
async function loadStats() {
  try {
    isLoading.value = true
    error.value = null
    stats.value = await statsService.getOverview()
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Statistics</h1>
      <p class="text-gray-600 dark:text-gray-400">Track your fitness progress</p>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center py-12">
      <BaseSpinner size="lg" />
    </div>

    <!-- Error state -->
    <BaseAlert v-else-if="error" variant="error" class="my-4">
      {{ error }}
      <button
        type="button"
        class="ml-2 text-sm underline hover:no-underline"
        @click="loadStats"
      >
        Try again
      </button>
    </BaseAlert>

    <!-- Stats content -->
    <template v-else-if="stats">
      <!-- Overview stats cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <BaseCard>
          <div class="text-center">
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ stats.total_workouts }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Total Workouts</p>
          </div>
        </BaseCard>
        <BaseCard>
          <div class="text-center">
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ formattedDuration }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Total Time</p>
          </div>
        </BaseCard>
        <BaseCard>
          <div class="text-center">
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ stats.current_streak_days }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Day Streak</p>
          </div>
        </BaseCard>
        <BaseCard>
          <div class="text-center">
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ stats.personal_records_count }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Personal Records</p>
          </div>
        </BaseCard>
      </div>

      <!-- Additional stat: Total Volume -->
      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Total Volume Lifted</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">
              {{ formattedVolume }}
            </p>
          </div>
          <div class="text-5xl">
            <svg class="w-12 h-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
            </svg>
          </div>
        </div>
      </BaseCard>

      <!-- Workout Frequency Chart -->
      <BaseCard>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Workout Frequency
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">Last 6 months</p>

        <div v-if="hasAnyData" class="space-y-3">
          <!-- Bar chart -->
          <div class="flex items-end justify-between gap-2 h-40">
            <div
              v-for="month in frequencyChartData"
              :key="month.month"
              class="flex-1 flex flex-col items-center"
            >
              <!-- Bar -->
              <div class="w-full flex flex-col items-center justify-end h-32">
                <span
                  v-if="month.count > 0"
                  class="text-xs text-gray-600 dark:text-gray-400 mb-1"
                >
                  {{ month.count }}
                </span>
                <div
                  class="w-full max-w-[40px] bg-primary-500 rounded-t transition-all duration-300"
                  :style="{
                    height: `${(month.count / maxFrequencyCount) * 100}%`,
                    minHeight: month.count > 0 ? '8px' : '0px',
                  }"
                />
              </div>
              <!-- Label -->
              <span class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {{ month.label }}
              </span>
            </div>
          </div>
        </div>

        <div v-else class="h-40 flex items-center justify-center">
          <p class="text-gray-500 dark:text-gray-400">
            Complete workouts to see your frequency chart
          </p>
        </div>
      </BaseCard>

      <!-- Muscle Group Distribution -->
      <BaseCard>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Muscle Groups Trained
        </h2>

        <div v-if="muscleGroupChartData.length > 0" class="space-y-3">
          <div
            v-for="item in muscleGroupChartData"
            :key="item.muscle_group"
            class="space-y-1"
          >
            <div class="flex justify-between text-sm">
              <span class="text-gray-700 dark:text-gray-300">{{ item.label }}</span>
              <span class="text-gray-500 dark:text-gray-400">
                {{ item.session_count }} {{ item.session_count === 1 ? 'session' : 'sessions' }}
              </span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div
                class="h-3 rounded-full transition-all duration-300"
                :class="muscleGroupColors[item.muscle_group] || 'bg-primary-500'"
                :style="{ width: `${item.percentage}%` }"
              />
            </div>
          </div>
        </div>

        <div v-else class="py-8 text-center">
          <p class="text-gray-500 dark:text-gray-400">
            Complete workouts to see your muscle group distribution
          </p>
        </div>
      </BaseCard>

      <!-- Quick Stats Summary -->
      <BaseCard v-if="hasAnyData">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Summary
        </h2>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Avg. workouts/month</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">
              {{ frequencyChartData.length > 0
                ? (frequencyChartData.reduce((sum, m) => sum + m.count, 0) / frequencyChartData.length).toFixed(1)
                : '0'
              }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Avg. workout duration</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">
              {{ stats.total_workouts > 0
                ? Math.round(stats.total_duration_seconds / stats.total_workouts / 60) + 'm'
                : '0m'
              }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Avg. volume/workout</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">
              {{ stats.total_workouts > 0
                ? Math.round(stats.total_volume_kg / stats.total_workouts) + ' kg'
                : '0 kg'
              }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Most trained</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">
              {{ muscleGroupChartData.length > 0 ? muscleGroupChartData[0].label : '-' }}
            </span>
          </div>
        </div>
      </BaseCard>
    </template>
  </div>
</template>
