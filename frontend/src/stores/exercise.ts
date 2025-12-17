/**
 * Exercise store with caching for improved performance.
 * Caches exercise lists and details to reduce API calls during import workflows.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { exerciseService } from '@/services/exerciseService'
import type {
  ExerciseListItem,
  ExerciseListParams,
  ExerciseDetailResponse,
  ExerciseSubstituteItem,
} from '@/types'

interface CachedExerciseList {
  items: ExerciseListItem[]
  total: number
  timestamp: number
  params: ExerciseListParams
}

const CACHE_TTL = 5 * 60 * 1000 // 5 minutes
const ALL_EXERCISES_CACHE_KEY = 'all_exercises'

export const useExerciseStore = defineStore('exercise', () => {
  // Cache storage
  const listCache = ref<Map<string, CachedExerciseList>>(new Map())
  const detailCache = ref<Map<string, { data: ExerciseDetailResponse; timestamp: number }>>(
    new Map(),
  )
  const substituteCache = ref<Map<string, { data: ExerciseSubstituteItem[]; timestamp: number }>>(
    new Map(),
  )

  // All exercises cache (for dropdown/search scenarios)
  const allExercises = ref<ExerciseListItem[]>([])
  const allExercisesTimestamp = ref<number>(0)
  const isLoadingAll = ref(false)

  // Computed
  const hasAllExercises = computed(() => {
    return allExercises.value.length > 0 && Date.now() - allExercisesTimestamp.value < CACHE_TTL
  })

  // Helper to create cache key from params
  const getCacheKey = (params?: ExerciseListParams): string => {
    if (!params || Object.keys(params).length === 0) {
      return ALL_EXERCISES_CACHE_KEY
    }
    return JSON.stringify(params)
  }

  // Helper to check if cache is valid
  const isCacheValid = (timestamp: number): boolean => {
    return Date.now() - timestamp < CACHE_TTL
  }

  /**
   * Get all exercises (cached). Useful for dropdowns and search.
   * Loads everything once and caches it.
   */
  const getAllExercises = async (
    forceRefresh = false,
  ): Promise<{ items: ExerciseListItem[]; total: number }> => {
    if (!forceRefresh && hasAllExercises.value) {
      return {
        items: allExercises.value,
        total: allExercises.value.length,
      }
    }

    if (isLoadingAll.value) {
      // Wait for existing request to complete
      await new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          if (!isLoadingAll.value) {
            clearInterval(checkInterval)
            resolve(undefined)
          }
        }, 100)
      })
      return {
        items: allExercises.value,
        total: allExercises.value.length,
      }
    }

    isLoadingAll.value = true
    try {
      // Load all exercises (no pagination, sorted by name)
      const response = await exerciseService.getAll({
        page: 1,
        page_size: 10000, // Large enough to get all
        sort_by: 'name',
      })

      allExercises.value = response.items
      allExercisesTimestamp.value = Date.now()

      return {
        items: response.items,
        total: response.total,
      }
    } finally {
      isLoadingAll.value = false
    }
  }

  /**
   * Get exercises with optional filters (cached).
   */
  const getExercises = async (
    params?: ExerciseListParams,
  ): Promise<{ items: ExerciseListItem[]; total: number }> => {
    const cacheKey = getCacheKey(params)

    // Check cache
    const cached = listCache.value.get(cacheKey)
    if (cached && isCacheValid(cached.timestamp)) {
      return {
        items: cached.items,
        total: cached.total,
      }
    }

    // Fetch from API
    const response = await exerciseService.getAll(params)

    // Update cache
    listCache.value.set(cacheKey, {
      items: response.items,
      total: response.total,
      timestamp: Date.now(),
      params: params || {},
    })

    return {
      items: response.items,
      total: response.total,
    }
  }

  /**
   * Get exercise details by ID (cached).
   */
  const getExerciseById = async (exerciseId: string): Promise<ExerciseDetailResponse> => {
    // Check cache
    const cached = detailCache.value.get(exerciseId)
    if (cached && isCacheValid(cached.timestamp)) {
      return cached.data
    }

    // Fetch from API
    const response = await exerciseService.getById(exerciseId)

    // Update cache
    detailCache.value.set(exerciseId, {
      data: response,
      timestamp: Date.now(),
    })

    return response
  }

  /**
   * Get substitute exercises (cached).
   */
  const getSubstitutes = async (exerciseId: string): Promise<ExerciseSubstituteItem[]> => {
    // Check cache
    const cached = substituteCache.value.get(exerciseId)
    if (cached && isCacheValid(cached.timestamp)) {
      return cached.data
    }

    // Fetch from API
    const response = await exerciseService.getSubstitutes(exerciseId)

    // Update cache
    substituteCache.value.set(exerciseId, {
      data: response,
      timestamp: Date.now(),
    })

    return response
  }

  /**
   * Search exercises by name (uses cached all exercises).
   */
  const searchExercises = async (query: string): Promise<ExerciseListItem[]> => {
    const { items } = await getAllExercises()

    if (!query.trim()) {
      return items
    }

    const lowerQuery = query.toLowerCase()
    return items.filter(
      (ex) =>
        ex.name.toLowerCase().includes(lowerQuery) ||
        ex.description?.toLowerCase().includes(lowerQuery),
    )
  }

  /**
   * Invalidate cache for a specific exercise (e.g., after update/delete).
   */
  const invalidateExercise = (exerciseId: string): void => {
    detailCache.value.delete(exerciseId)
    substituteCache.value.delete(exerciseId)
  }

  /**
   * Invalidate list cache (e.g., after creating/deleting exercises).
   */
  const invalidateListCache = (): void => {
    listCache.value.clear()
    allExercises.value = []
    allExercisesTimestamp.value = 0
  }

  /**
   * Clear all caches.
   */
  const clearCache = (): void => {
    listCache.value.clear()
    detailCache.value.clear()
    substituteCache.value.clear()
    allExercises.value = []
    allExercisesTimestamp.value = 0
  }

  return {
    // State
    allExercises,
    isLoadingAll,

    // Computed
    hasAllExercises,

    // Actions
    getAllExercises,
    getExercises,
    getExerciseById,
    getSubstitutes,
    searchExercises,
    invalidateExercise,
    invalidateListCache,
    clearCache,
  }
})
