/**
 * Composable for managing equipment selection and ownership.
 */
import { ref, computed, onMounted } from 'vue'
import { useProfileStore } from '@/stores'
import { useUiStore } from '@/stores/ui'
import type { EquipmentListItem } from '@/types'

export function useEquipment() {
  const profileStore = useProfileStore()
  const uiStore = useUiStore()

  const searchQuery = ref('')
  const updatingEquipmentIds = ref<Set<string>>(new Set())

  // Computed properties
  const equipment = computed(() => profileStore.equipment)
  const isLoading = computed(() => profileStore.isLoadingEquipment)
  const error = computed(() => profileStore.error)

  const filteredEquipment = computed(() => {
    if (!searchQuery.value) {
      return equipment.value
    }

    const query = searchQuery.value.toLowerCase()
    return equipment.value.filter((eq) =>
      eq.name.toLowerCase().includes(query)
    )
  })

  const ownedCount = computed(() =>
    equipment.value.filter((eq) => eq.is_user_owned).length
  )

  const totalCount = computed(() => equipment.value.length)

  // Check if specific equipment is being updated
  const isEquipmentUpdating = (equipmentId: string): boolean => {
    return updatingEquipmentIds.value.has(equipmentId)
  }

  // Load equipment data
  const loadEquipment = async () => {
    await profileStore.fetchEquipment()
    if (profileStore.error) {
      uiStore.error('Failed to load equipment')
    }
  }

  // Toggle equipment ownership
  const toggleOwnership = async (equipmentItem: EquipmentListItem) => {
    const newOwned = !equipmentItem.is_user_owned

    // Add to updating set
    updatingEquipmentIds.value.add(equipmentItem.id)

    // Optimistically update UI
    const previousOwned = equipmentItem.is_user_owned
    equipmentItem.is_user_owned = newOwned

    try {
      const result = await profileStore.updateEquipmentOwnership(
        equipmentItem.id,
        newOwned
      )

      if (!result.success) {
        // Revert on error
        equipmentItem.is_user_owned = previousOwned
        uiStore.error(result.error || 'Failed to update equipment')
      }
    } catch (err) {
      // Revert on error
      equipmentItem.is_user_owned = previousOwned
      uiStore.error('Failed to update equipment')
    } finally {
      // Remove from updating set
      updatingEquipmentIds.value.delete(equipmentItem.id)
    }
  }

  // Clear search
  const clearSearch = () => {
    searchQuery.value = ''
  }

  // Load equipment on mount
  onMounted(() => {
    if (equipment.value.length === 0) {
      loadEquipment()
    }
  })

  return {
    // State
    searchQuery,
    equipment,
    filteredEquipment,
    isLoading,
    error,
    ownedCount,
    totalCount,
    // Methods
    loadEquipment,
    toggleOwnership,
    clearSearch,
    isEquipmentUpdating,
  }
}
