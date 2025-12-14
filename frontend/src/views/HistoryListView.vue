<script setup lang="ts">
/**
 * Workout history list view.
 * Displays chronological list of past workout sessions with filtering.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import { workoutSessionService } from '@/services/workoutSessionService'
import { useUiStore } from '@/stores/ui'
import type { WorkoutSessionListItem, SessionStatus } from '@/types'

const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()

// State
const sessions = ref<WorkoutSessionListItem[]>([])
const isLoading = ref(true)
const error = ref<string | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)
const hasMore = computed(() => currentPage.value < totalPages.value)

// Filters from URL
const statusFilter = ref<SessionStatus | null>((route.query.status as SessionStatus) || null)

// Computed
const hasSessions = computed(() => sessions.value.length > 0)
const hasFilters = computed(() => statusFilter.value !== null)

// Group sessions by date
const groupedSessions = computed(() => {
  const groups: Array<{ label: string; date: string; sessions: WorkoutSessionListItem[] }> = []
  const dateMap = new Map<string, WorkoutSessionListItem[]>()

  for (const session of sessions.value) {
    const dateKey = session.created_at.split('T')[0] // YYYY-MM-DD
    if (!dateMap.has(dateKey)) {
      dateMap.set(dateKey, [])
    }
    dateMap.get(dateKey)!.push(session)
  }

  // Convert to array and sort by date descending
  const sortedEntries = Array.from(dateMap.entries()).sort((a, b) => b[0].localeCompare(a[0]))

  for (const [dateKey, sessionList] of sortedEntries) {
    groups.push({
      label: formatDateLabel(dateKey),
      date: dateKey,
      sessions: sessionList,
    })
  }

  return groups
})

// Methods
const fetchSessions = async (page = 1): Promise<void> => {
  isLoading.value = true
  error.value = null

  try {
    const params: any = { page, limit: 20 }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const response = await workoutSessionService.getAll(params)

    if (page === 1) {
      sessions.value = response.sessions
    } else {
      sessions.value = [...sessions.value, ...response.sessions]
    }

    currentPage.value = response.pagination.page
    totalPages.value = response.pagination.total_pages
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load workout history'
    uiStore.error('Failed to load workout history. Please try again.')
  } finally {
    isLoading.value = false
  }
}

const loadMore = async (): Promise<void> => {
  if (!hasMore.value || isLoading.value) return
  await fetchSessions(currentPage.value + 1)
}

const navigateToSession = (sessionId: string): void => {
  router.push(`/history/${sessionId}`)
}

const filterByStatus = (status: SessionStatus | null): void => {
  statusFilter.value = status

  // Update URL query
  const query: any = { ...route.query }
  if (status) {
    query.status = status
  } else {
    delete query.status
  }
  router.replace({ query })

  // Reset and refetch
  sessions.value = []
  currentPage.value = 1
  fetchSessions(1)
}

const clearFilters = (): void => {
  filterByStatus(null)
}

const formatDateLabel = (dateStr: string): string => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  // Reset time for comparison
  today.setHours(0, 0, 0, 0)
  yesterday.setHours(0, 0, 0, 0)
  date.setHours(0, 0, 0, 0)

  if (date.getTime() === today.getTime()) return 'Today'
  if (date.getTime() === yesterday.getTime()) return 'Yesterday'

  // Format as "January 15, 2025"
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined,
  })
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

// Lifecycle
onMounted(() => {
  fetchSessions(1)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Workout History</h1>
        <p class="text-gray-600 dark:text-gray-400">View your past workout sessions</p>
      </div>
    </div>

    <!-- Filters -->
    <BaseCard>
      <div class="flex items-center gap-2 overflow-x-auto pb-2">
        <button
          type="button"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
            statusFilter === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
          ]"
          @click="filterByStatus(null)"
        >
          All
        </button>
        <button
          type="button"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
            statusFilter === 'completed'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
          ]"
          @click="filterByStatus('completed')"
        >
          Completed
        </button>
        <button
          type="button"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
            statusFilter === 'abandoned'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
          ]"
          @click="filterByStatus('abandoned')"
        >
          Abandoned
        </button>
        <button
          type="button"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
            statusFilter === 'in_progress'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
          ]"
          @click="filterByStatus('in_progress')"
        >
          In Progress
        </button>
      </div>
    </BaseCard>

    <!-- Loading State -->
    <div v-if="isLoading && sessions.length === 0" class="space-y-4">
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
        Failed to load history
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
      <BaseButton @click="fetchSessions(1)">Try Again</BaseButton>
    </BaseCard>

    <!-- Empty State -->
    <BaseCard v-else-if="!hasSessions" class="text-center py-12">
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
        {{ hasFilters ? 'No workouts found' : 'No workout history yet' }}
      </h3>
      <p class="mt-2 text-gray-500 dark:text-gray-400">
        {{
          hasFilters
            ? 'Try adjusting your filters to see more results.'
            : 'Start your first workout to begin tracking your progress.'
        }}
      </p>
      <div class="mt-6 flex gap-3 justify-center">
        <BaseButton v-if="hasFilters" variant="outline" @click="clearFilters"
          >Clear Filters</BaseButton
        >
        <RouterLink v-else to="/plans" class="btn btn-md btn-primary">View Plans</RouterLink>
      </div>
    </BaseCard>

    <!-- Session List -->
    <div v-else class="space-y-6">
      <div v-for="group in groupedSessions" :key="group.date" class="space-y-3">
        <!-- Date Header -->
        <div class="sticky top-0 z-10 bg-gray-50 dark:bg-gray-900 py-2">
          <h2
            class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide"
          >
            {{ group.label }}
          </h2>
        </div>

        <!-- Session Cards -->
        <div class="space-y-3">
          <BaseCard
            v-for="session in group.sessions"
            :key="session.id"
            class="hover:shadow-md transition-shadow cursor-pointer"
            @click="navigateToSession(session.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {{ session.workout.name }}
                  </h3>
                  <BaseBadge :variant="getStatusVariant(session.status)" size="sm">
                    {{ getStatusLabel(session.status) }}
                  </BaseBadge>
                </div>

                <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {{ session.workout_plan.name }}
                </p>

                <div
                  class="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-400"
                >
                  <span>{{ formatTime(session.created_at) }}</span>
                  <span>·</span>
                  <span>{{ session.exercise_count }} exercises</span>
                </div>
              </div>

              <!-- Chevron -->
              <svg
                class="w-5 h-5 text-gray-400 dark:text-gray-500 flex-shrink-0 ml-3"
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
            </div>
          </BaseCard>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore" class="flex justify-center pt-4">
        <BaseButton variant="outline" :loading="isLoading" @click="loadMore">
          Load More
        </BaseButton>
      </div>
    </div>
  </div>
</template>
