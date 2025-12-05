/**
 * Exercise service for managing exercises.
 */
import api from './api'
import type {
  ExerciseListResponse,
  ExerciseListParams,
  ExerciseDetailResponse,
  ExerciseSubstituteItem,
} from '@/types'

export const exerciseService = {
  /**
   * Get paginated list of exercises with optional filters.
   */
  async getAll(params?: ExerciseListParams): Promise<ExerciseListResponse> {
    const response = await api.get<ExerciseListResponse>('/exercises', { params })
    return response.data
  },

  /**
   * Get exercise details by ID.
   */
  async getById(exerciseId: string): Promise<ExerciseDetailResponse> {
    const response = await api.get<ExerciseDetailResponse>(`/exercises/${exerciseId}`)
    return response.data
  },

  /**
   * Get substitute exercises for a given exercise.
   */
  async getSubstitutes(exerciseId: string): Promise<ExerciseSubstituteItem[]> {
    const response = await api.get<ExerciseSubstituteItem[]>(`/exercises/${exerciseId}/substitutes`)
    return response.data
  },
}
