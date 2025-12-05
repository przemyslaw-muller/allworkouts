/**
 * Profile store - manages user preferences and equipment ownership.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UnitSystem, EquipmentListItem, UserUpdateRequest } from '@/types'
import { authService, equipmentService } from '@/services'
import { getErrorMessage } from '@/services/api'
import { useAuthStore } from './auth'

export const useProfileStore = defineStore('profile', () => {
  // State
  const equipment = ref<EquipmentListItem[]>([])
  const isLoadingEquipment = ref(false)
  const isUpdating = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const ownedEquipment = computed(() => equipment.value.filter((e) => e.is_user_owned))

  const ownedEquipmentIds = computed(() => new Set(ownedEquipment.value.map((e) => e.id)))

  const unitSystem = computed(() => {
    const authStore = useAuthStore()
    return authStore.user?.unit_system ?? 'metric'
  })

  // Actions
  async function fetchEquipment() {
    try {
      isLoadingEquipment.value = true
      error.value = null
      equipment.value = await equipmentService.getAll()
    } catch (err) {
      error.value = getErrorMessage(err)
    } finally {
      isLoadingEquipment.value = false
    }
  }

  async function updateEquipmentOwnership(equipmentId: string, isOwned: boolean) {
    try {
      isUpdating.value = true
      error.value = null
      await equipmentService.updateOwnership(equipmentId, { is_owned: isOwned })

      // Update local state
      const item = equipment.value.find((e) => e.id === equipmentId)
      if (item) {
        item.is_user_owned = isOwned
      }

      return { success: true }
    } catch (err) {
      error.value = getErrorMessage(err)
      return { success: false, error: error.value }
    } finally {
      isUpdating.value = false
    }
  }

  async function updateUnitSystem(newUnitSystem: UnitSystem) {
    const authStore = useAuthStore()
    try {
      isUpdating.value = true
      error.value = null
      const updateData: UserUpdateRequest = { unit_system: newUnitSystem }
      await authService.updateMe(updateData)
      await authStore.refreshUser()
      return { success: true }
    } catch (err) {
      error.value = getErrorMessage(err)
      return { success: false, error: error.value }
    } finally {
      isUpdating.value = false
    }
  }

  function isEquipmentOwned(equipmentId: string): boolean {
    return ownedEquipmentIds.value.has(equipmentId)
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    equipment,
    isLoadingEquipment,
    isUpdating,
    error,
    // Getters
    ownedEquipment,
    ownedEquipmentIds,
    unitSystem,
    // Actions
    fetchEquipment,
    updateEquipmentOwnership,
    updateUnitSystem,
    isEquipmentOwned,
    clearError,
  }
})
