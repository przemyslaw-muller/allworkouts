/**
 * Stats service for workout analytics and history.
 */
import api from './api'
import type {
  StatsOverviewResponse,
  StatsOverviewParams,
  ExerciseHistoryResponse,
  ExerciseHistoryParams,
} from '@/types'

export const statsService = {
  /**
   * Get stats overview with optional date range.
   */
  async getOverview(params?: StatsOverviewParams): Promise<StatsOverviewResponse> {
    const response = await api.get<StatsOverviewResponse>('/stats/overview', { params })
    return response.data
  },

  /**
   * Get exercise history for a specific exercise.
   */
  async getExerciseHistory(
    exerciseId: string,
    params?: ExerciseHistoryParams,
  ): Promise<ExerciseHistoryResponse> {
    const response = await api.get<ExerciseHistoryResponse>(`/stats/exercise/${exerciseId}/history`, {
      params,
    })
    return response.data
  },
}
