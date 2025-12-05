/**
 * Personal records service for managing PRs.
 */
import api from './api'
import type {
  PersonalRecordListResponse,
  PersonalRecordListParams,
  PersonalRecordCreateRequest,
  PersonalRecordCreateResponse,
} from '@/types'

export const personalRecordService = {
  /**
   * Get paginated list of personal records.
   */
  async getAll(params?: PersonalRecordListParams): Promise<PersonalRecordListResponse> {
    const response = await api.get<PersonalRecordListResponse>('/personal-records', { params })
    return response.data
  },

  /**
   * Create a new personal record manually.
   */
  async create(data: PersonalRecordCreateRequest): Promise<PersonalRecordCreateResponse> {
    const response = await api.post<PersonalRecordCreateResponse>('/personal-records', data)
    return response.data
  },

  /**
   * Delete a personal record.
   */
  async delete(recordId: string): Promise<void> {
    await api.delete(`/personal-records/${recordId}`)
  },
}
