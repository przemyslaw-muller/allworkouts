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
  ParseWorkoutTextRequest,
  WorkoutPlanParseResponse,
  WorkoutPlanFromParsedRequest,
  WorkoutPlanToggleActiveRequest,
  WorkoutPlanToggleActiveResponse,
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

  /**
   * Set a workout plan as active (deactivates all others).
   */
  async setActive(
    planId: string,
    data: WorkoutPlanToggleActiveRequest,
  ): Promise<WorkoutPlanToggleActiveResponse> {
    const response = await api.patch<WorkoutPlanToggleActiveResponse>(
      `/workout-plans/${planId}/active`,
      data,
    )
    return response.data
  },

  /**
   * Parse workout plan text using AI (starts async processing).
   * Returns import_log_id to poll for status.
   */
  async parseWorkoutText(data: ParseWorkoutTextRequest): Promise<{ import_log_id: string; status: string; message: string }> {
    const response = await api.post<{ import_log_id: string; status: string; message: string }>('/workout-plans/parse', data)
    return response.data
  },

  /**
   * Get the status of a workout plan parsing operation.
   * Poll this endpoint until status is 'completed' or 'failed'.
   */
  async getParseStatus(importLogId: string): Promise<{
    import_log_id: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    result?: WorkoutPlanParseResponse
    error?: string
  }> {
    const response = await api.get<{
      import_log_id: string
      status: 'pending' | 'processing' | 'completed' | 'failed'
      result?: WorkoutPlanParseResponse
      error?: string
    }>(`/workout-plans/parse/status/${importLogId}`)
    return response.data
  },

  /**
   * Create a workout plan from parsed data (Step 2 of import wizard).
   */
  async createFromParsed(data: WorkoutPlanFromParsedRequest): Promise<WorkoutPlanCreateResponse> {
    const response = await api.post<WorkoutPlanCreateResponse>('/workout-plans/from-parsed', data)
    return response.data
  },
}
