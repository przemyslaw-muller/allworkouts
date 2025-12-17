<script setup lang="ts">
/**
 * Modal for searching and adding exercises to a workout plan.
 */
import { ref, computed, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import BaseInput from './BaseInput.vue'
import BaseButton from './BaseButton.vue'
import BaseSelect from './BaseSelect.vue'
import BaseSpinner from './BaseSpinner.vue'
import CustomExerciseModal from './CustomExerciseModal.vue'
import { useExerciseStore } from '@/stores/exercise'
import { useUiStore } from '@/stores/ui'
import type { ExerciseListItem, ExerciseDetailResponse, MuscleGroup } from '@/types'

interface Props {
  modelValue: boolean
  existingExerciseIds: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'on-select': [exercise: ExerciseListItem]
}>()

const showCustomExerciseModal = ref(false)
const editingExercise = ref<ExerciseDetailResponse | null>(null)
const exerciseStore = useExerciseStore()
const uiStore = useUiStore()

const searchQuery = ref('')
const muscleGroupFilter = ref<MuscleGroup | ''>('')
const exercises = ref<ExerciseListItem[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)

const muscleGroupOptions = [
  { value: '', label: 'All Muscle Groups' },
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

const filteredExercises = computed(() => {
  return exercises.value.filter((ex) => !props.existingExerciseIds.includes(ex.id))
})

const searchExercises = async () => {
  isLoading.value = true
  error.value = null

  tr// Use cached store for faster lookups
    let results: ExerciseListItem[]

    if (!searchQuery.value.trim() && !muscleGroupFilter.value) {
      // No filters - get all cached exercises
      const { items } = await exerciseStore.getAllExercises()
      results = items
    } else if (searchQuery.value.trim() && !muscleGroupFilter.value) {
      // Search by name only - use cached search
      results = await exerciseStore.searchExercises(searchQuery.value.trim())
    } else {
      // Has filters - use regular API call with caching
      const params: any = {
        page_size: 50,
      }

      if (searchQuery.value.trim()) {
        params.search = searchQuery.value.trim()
      }

      if (muscleGroupFilter.value) {
        params.muscle_group = muscleGroupFilter.value
      }

      const response = await exerciseStore.getExercises(params)
      results = response.items
    }

    exercises.value = resultice.getAll(params)
    exercises.value = response.exercises
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load exercises'
    exercises.value = []
  } finally {
    isLoading.value = false
  }
}

const handleSelect = (exercise: ExerciseListItem) => {
  emit('on-select', exercise)
  emit('update:modelValue', false)
  resetModal()
}

const handleCustomExerciseCreated = (exercise: ExerciseListItem) => {
  // Automatically select the newly created exercise
  emit('on-select', exercise)
  emit('update:modelValue', false)
  resetModal()
}

const openCustomExerciseModal = () => {
  editingExercise.value = null
  showCustomExerciseModal.value = true
}

const handleEditExercise = async (exercise: ExerciseListItem, event: Event) => {
  event.stopPropagation()
  try {
    // Fetch full exercise details for editing
    const details = await exerciseService.getById(exercise.id)
    editingExercise.value = details
    showCustomExerciseModal.value = true
  } catch (err) {
    uiStore.error('Failed to load exercise details')
  }
}

const handleExerciseUpdated = (updated: ExerciseDetailResponse) => {
  // Update the exercise in our list
  const index = exercises.value.findIndex((e) => e.id === updated.id)
  if (index !== -1) {
    exercises.value[index] = {
      ...exercises.value[index],
      name: updated.name,
      description: updated.description,
      primary_muscle_groups: updated.primary_muscle_groups,
      secondary_muscle_groups: updated.secondary_muscle_groups,
      equipment: updated.equipment,
    }
  }
  uiStore.success('Exercise updated')
}

const confirmDeleteExercise = async (exercise: ExerciseListItem, event: Event) => {
  event.stopPropagation()

  const confirmed = await uiStore.confirm({
    title: 'Delete Exercise',
    message: `Are you sure you want to delete '${exercise.name}'? This cannot be undone.`,
    confirmText: 'Delete',
    confirmVariant: 'danger',
  })

  if (confirmed) {
    try {
      await exerciseService.delete(exercise.id)
      // Remove from list
      exercises.value = exercises.value.filter((e) => e.id !== exercise.id)
      uiStore.success('Exercise deleted')
    } catch (err) {
      uiStore.error('Failed to delete exercise')
    }
  }
}

const resetModal = () => {
  searchQuery.value = ''
  muscleGroupFilter.value = ''
  exercises.value = []
  error.value = null
}

// Load exercises when modal opens
watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      searchExercises()
    } else {
      resetModal()
    }
  },
)

// Debounced search
let searchTimeout: number | null = null
watch([searchQuery, muscleGroupFilter], () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = window.setTimeout(() => {
    if (props.modelValue) {
      searchExercises()
    }
  }, 300)
})
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Add Exercise"
    size="lg"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="space-y-4">
      <!-- Search and Filters -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BaseInput
          v-model="searchQuery"
          label="Search exercises"
          placeholder="e.g., bench press, squat..."
          type="text"
        />
        <BaseSelect
          v-model="muscleGroupFilter"
          label="Muscle group"
          :options="muscleGroupOptions"
        />
      </div>

      <!-- Exercise List -->
      <div class="border border-gray-200 dark:border-gray-700 rounded-lg max-h-96 overflow-y-auto">
        <!-- Loading State -->
        <div v-if="isLoading" class="flex items-center justify-center py-12">
          <BaseSpinner size="lg" />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="p-4 text-center text-red-600 dark:text-red-400">
          {{ error }}
        </div>

        <!-- Empty State -->
        <div
          v-else-if="filteredExercises.length === 0"
          class="p-8 text-center text-gray-500 dark:text-gray-400"
        >
          <p v-if="exercises.length === 0">No exercises found. Try adjusting your search.</p>
          <p v-else>All matching exercises are already in your plan.</p>
        </div>

        <!-- Exercise Items -->
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div
            v-for="exercise in filteredExercises"
            :key="exercise.id"
            class="flex items-center px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <button
              type="button"
              class="flex-1 text-left"
              @click="handleSelect(exercise)"
            >
              <div class="flex items-start">
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ exercise.name }}</h4>
                    <span
                      v-if="exercise.is_custom"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300"
                    >
                      Custom
                    </span>
                  </div>
                  <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {{
                      exercise.primary_muscle_groups
                        .map((mg) => mg.charAt(0).toUpperCase() + mg.slice(1))
                        .join(', ')
                    }}
                  </p>
                  <div v-if="exercise.equipment.length > 0" class="flex items-center gap-1 mt-1">
                    <span
                      v-for="eq in exercise.equipment"
                      :key="eq.id"
                      class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs text-gray-700 dark:text-gray-300"
                    >
                      {{ eq.name }}
                    </span>
                  </div>
                </div>
                <div class="ml-4">
                  <span class="text-blue-600 dark:text-blue-400 text-sm font-medium">Add →</span>
                </div>
              </div>
            </button>
            <!-- Edit/Delete buttons for custom exercises -->
            <div v-if="exercise.is_custom" class="flex items-center gap-1 ml-2">
              <button
                type="button"
                class="p-1.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded transition-colors"
                title="Edit exercise"
                @click="handleEditExercise(exercise, $event)"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                type="button"
                class="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded transition-colors"
                title="Delete exercise"
                @click="confirmDeleteExercise(exercise, $event)"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Help Text -->
      <p class="text-sm text-gray-500 dark:text-gray-400">
        Click on an exercise to add it to your workout plan.
      </p>

      <!-- Create Custom Exercise Link -->
      <div class="pt-2 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
          @click="openCustomExerciseModal"
        >
          + Create a custom exercise
        </button>
      </div>
    </div>

    <template #footer>
      <BaseButton type="button" variant="outline" @click="emit('update:modelValue', false)">
        Cancel
      </BaseButton>
    </template>
  </BaseModal>

  <!-- Custom Exercise Modal -->
  <CustomExerciseModal
    v-model="showCustomExerciseModal"
    :exercise="editingExercise"
    @on-created="handleCustomExerciseCreated"
    @on-updated="handleExerciseUpdated"
  />
</template>
