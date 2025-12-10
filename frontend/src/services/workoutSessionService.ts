/**
 * Workout session service for managing active workout sessions.
 */
import api from './api'
import type {
  WorkoutSessionListResponse,
  WorkoutSessionListParams,
  WorkoutSessionDetailResponse,
  WorkoutSessionStartRequest,
  WorkoutSessionStartResponse,
  LogExerciseRequest,
  LogExerciseResponse,
  CompleteSessionRequest,
  CompleteSessionResponse,
  SkipSessionRequest,
  SkipSessionResponse,
} from '@/types'

export const workoutSessionService = {
  /**
   * Get paginated list of workout sessions.
   */
  async getAll(params?: WorkoutSessionListParams): Promise<WorkoutSessionListResponse> {
    const response = await api.get<WorkoutSessionListResponse>('/workout-sessions', { params })
    return response.data
  },

  /**
   * Get workout session details by ID.
   */
  async getById(sessionId: string): Promise<WorkoutSessionDetailResponse> {
    const response = await api.get<WorkoutSessionDetailResponse>(`/workout-sessions/${sessionId}`)
    return response.data
  },

  /**
   * Start a new workout session from a workout plan.
   */
  async start(data: WorkoutSessionStartRequest): Promise<WorkoutSessionStartResponse> {
    const response = await api.post<WorkoutSessionStartResponse>('/workout-sessions/start', data)
    return response.data
  },

  /**
   * Log an exercise during an active session.
   */
  async logExercise(sessionId: string, data: LogExerciseRequest): Promise<LogExerciseResponse> {
    const response = await api.post<LogExerciseResponse>(
      `/workout-sessions/${sessionId}/exercises`,
      data,
    )
    return response.data
  },

  /**
   * Complete a workout session.
   */
  async complete(
    sessionId: string,
    data?: CompleteSessionRequest,
  ): Promise<CompleteSessionResponse> {
    const response = await api.post<CompleteSessionResponse>(
      `/workout-sessions/${sessionId}/complete`,
      data || {},
    )
    return response.data
  },

  /**
   * Skip/abandon a workout session.
   */
  async skip(sessionId: string, data?: SkipSessionRequest): Promise<SkipSessionResponse> {
    const response = await api.post<SkipSessionResponse>(
      `/workout-sessions/${sessionId}/skip`,
      data || {},
    )
    return response.data
  },

  /**
   * Get the current in-progress session if any.
   */
  async getCurrent(): Promise<WorkoutSessionStartResponse | null> {
    try {
      const response = await api.get<WorkoutSessionStartResponse>('/workout-sessions/current')
      return response.data
    } catch {
      // No active session
      return null
    }
  },
}
