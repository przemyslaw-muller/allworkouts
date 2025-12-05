/**
 * Workout plan service for managing workout plans.
 */
import api from './api'
import type {
  WorkoutPlanListResponse,
  WorkoutPlanListParams,
  WorkoutPlanDetailResponse,
  WorkoutPlanCreateRequest,
  WorkoutPlanCreateResponse,
  WorkoutPlanUpdateRequest,
  WorkoutPlanUpdateResponse,
} from '@/types'

export const workoutPlanService = {
  /**
   * Get paginated list of workout plans.
   */
  async getAll(params?: WorkoutPlanListParams): Promise<WorkoutPlanListResponse> {
    const response = await api.get<WorkoutPlanListResponse>('/workout-plans', { params })
    return response.data
  },

  /**
   * Get workout plan details by ID.
   */
  async getById(planId: string): Promise<WorkoutPlanDetailResponse> {
    const response = await api.get<WorkoutPlanDetailResponse>(`/workout-plans/${planId}`)
    return response.data
  },

  /**
   * Create a new workout plan.
   */
  async create(data: WorkoutPlanCreateRequest): Promise<WorkoutPlanCreateResponse> {
    const response = await api.post<WorkoutPlanCreateResponse>('/workout-plans', data)
    return response.data
  },

  /**
   * Update an existing workout plan.
   */
  async update(planId: string, data: WorkoutPlanUpdateRequest): Promise<WorkoutPlanUpdateResponse> {
    const response = await api.patch<WorkoutPlanUpdateResponse>(`/workout-plans/${planId}`, data)
    return response.data
  },

  /**
   * Delete a workout plan.
   */
  async delete(planId: string): Promise<void> {
    await api.delete(`/workout-plans/${planId}`)
  },
}
