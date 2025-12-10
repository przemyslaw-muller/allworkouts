/**
 * Exercise service for managing exercises.
 */
import api from './api'
import type {
  ExerciseListResponse,
  ExerciseListParams,
  ExerciseDetailResponse,
  ExerciseSubstituteItem,
  ExerciseCreateRequest,
  ExerciseCreateResponse,
  ExerciseUpdateRequest,
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

  /**
   * Create a custom exercise.
   */
  async create(data: ExerciseCreateRequest): Promise<ExerciseCreateResponse> {
    const response = await api.post<ExerciseCreateResponse>('/exercises', data)
    return response.data
  },

  /**
   * Update a custom exercise. Only the owner can update their custom exercises.
   */
  async update(exerciseId: string, data: ExerciseUpdateRequest): Promise<ExerciseDetailResponse> {
    const response = await api.patch<ExerciseDetailResponse>(`/exercises/${exerciseId}`, data)
    return response.data
  },

  /**
   * Delete a custom exercise. Only the owner can delete their custom exercises.
   */
  async delete(exerciseId: string): Promise<void> {
    await api.delete(`/exercises/${exerciseId}`)
  },
}
