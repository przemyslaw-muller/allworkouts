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
import { exerciseService } from '@/services/exerciseService'
import type { ExerciseListItem, MuscleGroup } from '@/types'

interface Props {
  modelValue: boolean
  existingExerciseIds: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'on-select': [exercise: ExerciseListItem]
}>()

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
  return exercises.value.filter(ex => !props.existingExerciseIds.includes(ex.id))
})

const searchExercises = async () => {
  isLoading.value = true
  error.value = null

  try {
    const params: any = {
      limit: 50,
    }

    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    if (muscleGroupFilter.value) {
      params.muscle_group = muscleGroupFilter.value
    }

    const response = await exerciseService.getAll(params)
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

const resetModal = () => {
  searchQuery.value = ''
  muscleGroupFilter.value = ''
  exercises.value = []
  error.value = null
}

// Load exercises when modal opens
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    searchExercises()
  } else {
    resetModal()
  }
})

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
        <div v-else-if="filteredExercises.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
          <p v-if="exercises.length === 0">No exercises found. Try adjusting your search.</p>
          <p v-else>All matching exercises are already in your plan.</p>
        </div>

        <!-- Exercise Items -->
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <button
            v-for="exercise in filteredExercises"
            :key="exercise.id"
            type="button"
            class="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            @click="handleSelect(exercise)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 dark:text-gray-100">{{ exercise.name }}</h4>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {{ exercise.primary_muscle_groups.map(mg => mg.charAt(0).toUpperCase() + mg.slice(1)).join(', ') }}
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
        </div>
      </div>

      <!-- Help Text -->
      <p class="text-sm text-gray-500 dark:text-gray-400">
        Click on an exercise to add it to your workout plan.
      </p>
    </div>

    <template #footer>
      <BaseButton
        type="button"
        variant="outline"
        @click="emit('update:modelValue', false)"
      >
        Cancel
      </BaseButton>
    </template>
  </BaseModal>
</template>
