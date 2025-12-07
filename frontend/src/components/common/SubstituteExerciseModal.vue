<script setup lang="ts">
/**
 * Modal for substituting an exercise with a similar one.
 */
import { ref, computed, watch } from 'vue'
import BaseModal from './BaseModal.vue'
import BaseInput from './BaseInput.vue'
import BaseButton from './BaseButton.vue'
import BaseSpinner from './BaseSpinner.vue'
import { exerciseService } from '@/services/exerciseService'
import type { EditableExercise, ExerciseListItem, ExerciseSubstituteItem } from '@/types'

interface Props {
  modelValue: boolean
  currentExercise: EditableExercise | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'on-select': [exercise: ExerciseListItem]
}>()

const searchQuery = ref('')
const substitutes = ref<ExerciseSubstituteItem[]>([])
const searchResults = ref<ExerciseListItem[]>([])
const isLoadingSubstitutes = ref(false)
const isSearching = ref(false)
const error = ref<string | null>(null)
const showAllExercises = ref(false)

const displayedExercises = computed(() => {
  if (showAllExercises.value) {
    return searchResults.value
  }
  return substitutes.value
})

const loadSubstitutes = async () => {
  if (!props.currentExercise) return

  isLoadingSubstitutes.value = true
  error.value = null

  try {
    substitutes.value = await exerciseService.getSubstitutes(props.currentExercise.exerciseId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load substitutes'
    substitutes.value = []
  } finally {
    isLoadingSubstitutes.value = false
  }
}

const searchAllExercises = async () => {
  isSearching.value = true
  error.value = null

  try {
    const params: any = {
      limit: 50,
    }

    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }

    const response = await exerciseService.getAll(params)
    searchResults.value = response.exercises
    showAllExercises.value = true
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to search exercises'
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

const handleSelect = (exercise: ExerciseListItem | ExerciseSubstituteItem) => {
  emit('on-select', exercise as ExerciseListItem)
  emit('update:modelValue', false)
  resetModal()
}

const handleShowAll = () => {
  searchQuery.value = ''
  searchAllExercises()
}

const resetModal = () => {
  searchQuery.value = ''
  substitutes.value = []
  searchResults.value = []
  showAllExercises.value = false
  error.value = null
}

// Load substitutes when modal opens
watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.currentExercise) {
    loadSubstitutes()
  } else {
    resetModal()
  }
})

// Debounced search
let searchTimeout: number | null = null
watch(searchQuery, () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  if (showAllExercises.value && searchQuery.value.trim()) {
    searchTimeout = window.setTimeout(() => {
      if (props.modelValue) {
        searchAllExercises()
      }
    }, 300)
  }
})
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    title="Substitute Exercise"
    size="lg"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="space-y-4">
      <!-- Current Exercise Info -->
      <div v-if="currentExercise" class="bg-gray-50 rounded-lg p-4">
        <p class="text-sm text-gray-600 mb-1">Current exercise:</p>
        <h4 class="font-medium text-gray-900">{{ currentExercise.exerciseName }}</h4>
        <p class="text-sm text-gray-500 mt-1">
          {{ currentExercise.primaryMuscleGroups.map(mg => mg.charAt(0).toUpperCase() + mg.slice(1)).join(', ') }}
        </p>
      </div>

      <!-- Search (only when showing all) -->
      <div v-if="showAllExercises">
        <BaseInput
          v-model="searchQuery"
          label="Search all exercises"
          placeholder="e.g., bench press, squat..."
          type="text"
        />
      </div>

      <!-- Section Header -->
      <div class="flex items-center justify-between">
        <h4 class="font-medium text-gray-900">
          {{ showAllExercises ? 'All Exercises' : 'Similar Exercises' }}
        </h4>
        <BaseButton
          v-if="!showAllExercises"
          type="button"
          variant="ghost"
          size="sm"
          @click="handleShowAll"
        >
          Search All
        </BaseButton>
        <BaseButton
          v-else
          type="button"
          variant="ghost"
          size="sm"
          @click="showAllExercises = false"
        >
          ← Back to Similar
        </BaseButton>
      </div>

      <!-- Exercise List -->
      <div class="border border-gray-200 rounded-lg max-h-96 overflow-y-auto">
        <!-- Loading State -->
        <div v-if="isLoadingSubstitutes || isSearching" class="flex items-center justify-center py-12">
          <BaseSpinner size="lg" />
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="p-4 text-center text-red-600">
          {{ error }}
        </div>

        <!-- Empty State -->
        <div v-else-if="displayedExercises.length === 0" class="p-8 text-center text-gray-500">
          <p v-if="showAllExercises">No exercises found. Try adjusting your search.</p>
          <p v-else>No similar exercises found for this exercise.</p>
          <BaseButton
            v-if="!showAllExercises"
            type="button"
            variant="outline"
            size="sm"
            class="mt-4"
            @click="handleShowAll"
          >
            Search All Exercises
          </BaseButton>
        </div>

        <!-- Exercise Items -->
        <div v-else class="divide-y divide-gray-200">
          <button
            v-for="exercise in displayedExercises"
            :key="exercise.id"
            type="button"
            class="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
            @click="handleSelect(exercise)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h4 class="font-medium text-gray-900">{{ exercise.name }}</h4>
                  <span
                    v-if="'match_score' in exercise && typeof exercise.match_score === 'number' && exercise.match_score >= 0.8"
                    class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800"
                  >
                    High Match
                  </span>
                </div>
                <p class="text-sm text-gray-500 mt-1">
                  {{ exercise.primary_muscle_groups.map(mg => mg.charAt(0).toUpperCase() + mg.slice(1)).join(', ') }}
                </p>
                <div v-if="exercise.equipment.length > 0" class="flex items-center gap-1 mt-1">
                  <span
                    v-for="eq in exercise.equipment"
                    :key="eq.id"
                    class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700"
                  >
                    {{ eq.name }}
                  </span>
                </div>
              </div>
              <div class="ml-4">
                <span class="text-blue-600 text-sm font-medium">Select →</span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- Help Text -->
      <p class="text-sm text-gray-500">
        {{ showAllExercises 
          ? 'Click on an exercise to replace the current one.' 
          : 'These exercises work similar muscle groups and use compatible equipment.' 
        }}
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
