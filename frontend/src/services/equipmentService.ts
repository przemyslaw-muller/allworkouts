/**
 * Equipment service for managing equipment and user ownership.
 */
import api from './api'
import type { EquipmentListItem, EquipmentOwnershipRequest, EquipmentOwnershipResponse } from '@/types'

export const equipmentService = {
  /**
   * Get all equipment with user ownership status.
   */
  async getAll(): Promise<EquipmentListItem[]> {
    const response = await api.get<EquipmentListItem[]>('/equipment')
    return response.data
  },

  /**
   * Update equipment ownership status.
   */
  async updateOwnership(
    equipmentId: string,
    data: EquipmentOwnershipRequest,
  ): Promise<EquipmentOwnershipResponse> {
    const response = await api.put<EquipmentOwnershipResponse>(
      `/equipment/${equipmentId}/ownership`,
      data,
    )
    return response.data
  },
}
