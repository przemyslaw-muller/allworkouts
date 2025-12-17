<script setup lang="ts">
/**
 * Modal for creating or editing a custom exercise.
 */
import { ref, computed, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import BaseInput from './BaseInput.vue'
import BaseButton from './BaseButton.vue'
import BaseTextarea from './BaseTextarea.vue'
import BaseSpinner from './BaseSpinner.vue'
import { exerciseService } from '@/services/exerciseService'
import { equipmentService } from '@/services/equipmentService'
import { useExerciseStore } from '@/stores/exercise'
import type {
  ExerciseCreateRequest,
  ExerciseUpdateRequest,
  ExerciseDetailResponse,
  ExerciseListItem,
  EquipmentListItem,
  MuscleGroup,
} from '@/types'

interface Props {
  modelValue: boolean
  exercise?: ExerciseDetailResponse | null // If provided, we're editing
}

const props = withDefaults(defineProps<Props>(), {
  exercise: null,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'on-created': [exercise: ExerciseListItem]
  'on-updated': [exercise: ExerciseDetailResponse]
}>()

// Form state
const name = ref('')
const description = ref('')
const primaryMuscleGroups = ref<Set<MuscleGroup>>(new Set())
const secondaryMuscleGroups = ref<Set<MuscleGroup>>(new Set())
const selectedEquipmentIds = ref<Set<string>>(new Set())

// UI state
const isLoading = ref(false)
const isSaving = ref(false)
const error = ref<string | null>(null)
const equipment = ref<EquipmentListItem[]>([])

const isEditing = computed(() => !!props.exercise)
const modalTitle = computed(() => (isEditing.value ? 'Edit Exercise' : 'Create Custom Exercise'))
const submitLabel = computed(() => (isEditing.value ? 'Save Changes' : 'Create Exercise'))

const muscleGroups: { value: MuscleGroup; label: string }[] = [
  { value: 'chest', label: 'Chest' },
  { value: 'back', label: 'Back' },
  { value: 'shoulders', label: 'Shoulders' },
  { value: 'biceps', label: 'Biceps' },
  { value: 'triceps', label: 'Triceps' },
  { value: 'forearms', label: 'Forearms' },
  { value: 'legs', label: 'Legs' },
  { value: 'glutes', label: 'Glutes' },
  { value: 'core', label: 'Core' },
  { value: 'traps', label: 'Traps' },
  { value: 'lats', label: 'Lats' },
]

// Validation
const canSubmit = computed(() => {
  return name.value.trim().length > 0 && primaryMuscleGroups.value.size > 0
})

const togglePrimaryMuscle = (muscle: MuscleGroup) => {
  if (primaryMuscleGroups.value.has(muscle)) {
    primaryMuscleGroups.value.delete(muscle)
  } else {
    primaryMuscleGroups.value.add(muscle)
    // Remove from secondary if it was there
    secondaryMuscleGroups.value.delete(muscle)
  }
  // Trigger reactivity
  primaryMuscleGroups.value = new Set(primaryMuscleGroups.value)
  secondaryMuscleGroups.value = new Set(secondaryMuscleGroups.value)
}

const toggleSecondaryMuscle = (muscle: MuscleGroup) => {
  if (primaryMuscleGroups.value.has(muscle)) {
    // Can't add primary as secondary
    return
  }
  if (secondaryMuscleGroups.value.has(muscle)) {
    secondaryMuscleGroups.value.delete(muscle)
  } else {
    secondaryMuscleGroups.value.add(muscle)
  }
  secondaryMuscleGroups.value = new Set(secondaryMuscleGroups.value)
}

const toggleEquipment = (equipmentId: string) => {
  if (selectedEquipmentIds.value.has(equipmentId)) {
    selectedEquipmentIds.value.delete(equipmentId)
  } else {
    selectedEquipmentIds.value.add(equipmentId)
  }
  selectedEquipmentIds.value = new Set(selectedEquipmentIds.value)
}

const loadEquipment = async () => {
  isLoading.value = true
  try {
    const response = await equipmentService.getAll()
    equipment.value = response
  } catch (err) {
    console.error('Failed to load equipment:', err)
    // Non-critical - equipment selection is optional
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  name.value = ''
  description.value = ''
  primaryMuscleGroups.value = new Set()
  secondaryMuscleGroups.value = new Set()
  selectedEquipmentIds.value = new Set()
  error.value = null
}

const populateFromExercise = (exercise: ExerciseDetailResponse) => {
  name.value = exercise.name
  description.value = exercise.description || ''
  primaryMuscleGroups.value = new Set(exercise.primary_muscle_groups)
  secondaryMuscleGroups.value = new Set(exercise.secondary_muscle_groups)
  selectedEquipmentIds.value = new Set(exercise.equipment.map((e) => e.id))
}

const handleSubmit = async () => {
  if (!canSubmit.value) return

  const exerciseStore = useExerciseStore()
  isSaving.value = true
  error.value = null

  try {
    if (isEditing.value && props.exercise) {
      // Update existing exercise
      const updateData: ExerciseUpdateRequest = {
        name: name.value.trim(),
        description: description.value.trim() || null,
        primary_muscle_groups: Array.from(primaryMuscleGroups.value),
        secondary_muscle_groups: Array.from(secondaryMuscleGroups.value),
        equipment_ids: Array.from(selectedEquipmentIds.value),
      }

      const updated = await exerciseService.update(props.exercise.id, updateData)
      
      // Invalidate caches after update
      exerciseStore.invalidateExercise(props.exercise.id)
      exerciseStore.invalidateListCache()
      
      emit('on-updated', updated)
    } else {
      // Create new exercise
      const createData: ExerciseCreateRequest = {
        name: name.value.trim(),
        description: description.value.trim() || null,
        primary_muscle_groups: Array.from(primaryMuscleGroups.value),
        secondary_muscle_groups: Array.from(secondaryMuscleGroups.value),
        equipment_ids: Array.from(selectedEquipmentIds.value),
      }

      const response = await exerciseService.create(createData)

      // Invalidate list cache after creating new exercise
      exerciseStore.invalidateListCache()

      // Construct ExerciseListItem from response for parent component
      const newExercise: ExerciseListItem = {
        id: response.id,
        name: response.name,
        description: description.value.trim() || null,
        primary_muscle_groups: Array.from(primaryMuscleGroups.value),
        secondary_muscle_groups: Array.from(secondaryMuscleGroups.value),
        equipment: equipment.value.filter((e) => selectedEquipmentIds.value.has(e.id)),
        is_custom: true,
      }

      emit('on-created', newExercise)
    }

    emit('update:modelValue', false)
    resetForm()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save exercise'
  } finally {
    isSaving.value = false
  }
}

// Load equipment when modal opens
watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      loadEquipment()
      if (props.exercise) {
        populateFromExercise(props.exercise)
      }
    } else {
      resetForm()
    }
  },
)

// If exercise prop changes while modal is open (editing different exercise)
watch(
  () => props.exercise,
  (newExercise) => {
    if (props.modelValue && newExercise) {
      populateFromExercise(newExercise)
    }
  },
)
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    :title="modalTitle"
    size="lg"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="space-y-6">
      <!-- Error Alert -->
      <div
        v-if="error"
        class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm"
      >
        {{ error }}
      </div>

      <!-- Name -->
      <BaseInput
        v-model="name"
        label="Exercise Name"
        placeholder="e.g., Dumbbell Curl"
        required
      />

      <!-- Description -->
      <BaseTextarea
        v-model="description"
        label="Description (optional)"
        placeholder="Describe how to perform this exercise..."
        :rows="3"
      />

      <!-- Primary Muscle Groups -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Primary Muscle Groups <span class="text-red-500">*</span>
        </label>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
          <button
            v-for="muscle in muscleGroups"
            :key="muscle.value"
            type="button"
            :class="[
              'px-3 py-2 text-sm rounded-lg border transition-colors',
              primaryMuscleGroups.has(muscle.value)
                ? 'bg-blue-600 border-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-blue-400 dark:hover:border-blue-500',
            ]"
            @click="togglePrimaryMuscle(muscle.value)"
          >
            {{ muscle.label }}
          </button>
        </div>
        <p v-if="primaryMuscleGroups.size === 0" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Select at least one primary muscle group
        </p>
      </div>

      <!-- Secondary Muscle Groups -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Secondary Muscle Groups (optional)
        </label>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
          <button
            v-for="muscle in muscleGroups"
            :key="muscle.value"
            type="button"
            :disabled="primaryMuscleGroups.has(muscle.value)"
            :class="[
              'px-3 py-2 text-sm rounded-lg border transition-colors',
              primaryMuscleGroups.has(muscle.value)
                ? 'bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                : secondaryMuscleGroups.has(muscle.value)
                  ? 'bg-green-600 border-green-600 text-white'
                  : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-green-400 dark:hover:border-green-500',
            ]"
            @click="toggleSecondaryMuscle(muscle.value)"
          >
            {{ muscle.label }}
          </button>
        </div>
      </div>

      <!-- Equipment -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Equipment (optional)
        </label>
        <div v-if="isLoading" class="flex items-center justify-center py-4">
          <BaseSpinner size="sm" />
          <span class="ml-2 text-sm text-gray-500">Loading equipment...</span>
        </div>
        <div v-else-if="equipment.length === 0" class="text-sm text-gray-500 dark:text-gray-400">
          No equipment available
        </div>
        <div v-else class="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto p-1">
          <button
            v-for="eq in equipment"
            :key="eq.id"
            type="button"
            :class="[
              'px-3 py-2 text-sm rounded-lg border transition-colors text-left',
              selectedEquipmentIds.has(eq.id)
                ? 'bg-purple-600 border-purple-600 text-white'
                : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-purple-400 dark:hover:border-purple-500',
            ]"
            @click="toggleEquipment(eq.id)"
          >
            {{ eq.name }}
          </button>
        </div>
      </div>
    </div>

    <template #footer>
      <BaseButton
        type="button"
        variant="outline"
        :disabled="isSaving"
        @click="emit('update:modelValue', false)"
      >
        Cancel
      </BaseButton>
      <BaseButton
        type="button"
        variant="primary"
        :disabled="!canSubmit || isSaving"
        :loading="isSaving"
        @click="handleSubmit"
      >
        {{ submitLabel }}
      </BaseButton>
    </template>
  </BaseModal>
</template>
