<script setup lang="ts">
/**
 * Plan create/edit view.
 * Form to create or modify workout plans.
 */
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, RouterLink, onBeforeRouteLeave } from 'vue-router'
import { usePlanEdit } from '@/composables/usePlanEdit'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import BaseAlert from '@/components/common/BaseAlert.vue'
import EditableExerciseCard from '@/components/common/EditableExerciseCard.vue'
import AddExerciseModal from '@/components/common/AddExerciseModal.vue'
import SubstituteExerciseModal from '@/components/common/SubstituteExerciseModal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import type { ExerciseListItem, EditableExercise } from '@/types'

const route = useRoute()
const router = useRouter()

const planId = computed(() => route.params.id as string | undefined)
const isEditing = computed(() => !!planId.value)
const pageTitle = computed(() => isEditing.value ? 'Edit Plan' : 'Create Plan')

const {
  formData,
  isLoading,
  isSaving,
  isDirty,
  canSave,
  error,
  validationErrors,
  fetchPlan,
  savePlan,
  addExercise,
  removeExercise,
  substituteExercise,
  reorderExercises,
  updateExerciseField,
  updateField,
} = usePlanEdit(planId)

// Modal states
const showAddExerciseModal = ref(false)
const showSubstituteModal = ref(false)
const currentExerciseForSubstitute = ref<string | null>(null)
const showUnsavedDialog = ref(false)
const pendingNavigation = ref<string | null>(null)

const existingExerciseIds = computed(() => formData.value.exercises.map(ex => ex.exerciseId))

const currentExercise = computed(() => {
  if (!currentExerciseForSubstitute.value) return null
  return formData.value.exercises.find(ex => ex.id === currentExerciseForSubstitute.value) || null
})

onMounted(async () => {
  if (isEditing.value) {
    await fetchPlan()
  }
})

const handleSave = async () => {
  const success = await savePlan()
  if (success) {
    router.push(`/plans/${planId.value}`)
  }
}

const handleCancel = () => {
  if (isDirty.value) {
    pendingNavigation.value = '/plans'
    showUnsavedDialog.value = true
  } else {
    router.push('/plans')
  }
}

const handleAddExercise = (exercise: ExerciseListItem) => {
  addExercise(exercise)
}

const handleSubstitute = (exerciseId: string) => {
  currentExerciseForSubstitute.value = exerciseId
  showSubstituteModal.value = true
}

const handleSubstituteSelect = (newExercise: ExerciseListItem) => {
  if (currentExerciseForSubstitute.value) {
    substituteExercise(currentExerciseForSubstitute.value, newExercise)
  }
}

const handleRemove = (exerciseId: string) => {
  if (formData.value.exercises.length === 1) {
    // Can't remove last exercise
    return
  }
  removeExercise(exerciseId)
}

const handleMoveUp = (exerciseId: string) => {
  const index = formData.value.exercises.findIndex(ex => ex.id === exerciseId)
  if (index > 0) {
    reorderExercises(index, index - 1)
  }
}

const handleMoveDown = (exerciseId: string) => {
  const index = formData.value.exercises.findIndex(ex => ex.id === exerciseId)
  if (index < formData.value.exercises.length - 1) {
    reorderExercises(index, index + 1)
  }
}

const handleDiscardChanges = () => {
  showUnsavedDialog.value = false
  if (pendingNavigation.value) {
    router.push(pendingNavigation.value)
  }
}

const handleKeepEditing = () => {
  showUnsavedDialog.value = false
  pendingNavigation.value = null
}

// Navigation guard
onBeforeRouteLeave((to, _from, next) => {
  if (isDirty.value) {
    pendingNavigation.value = to.fullPath
    showUnsavedDialog.value = true
    next(false)
  } else {
    next()
  }
})

// Browser refresh warning
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (isDirty.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(() => {
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <RouterLink to="/plans" class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 mb-1 inline-block">
        &larr; Back to Plans
      </RouterLink>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ pageTitle }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <BaseSpinner size="lg" />
    </div>

    <!-- Error State -->
    <BaseAlert v-else-if="error" type="error">
      {{ error }}
    </BaseAlert>

    <!-- Form -->
    <BaseCard v-else>
      <form @submit.prevent="handleSave" class="space-y-6">
        <!-- Plan Info -->
        <div class="space-y-4">
          <BaseInput
            :model-value="formData.name"
            label="Plan Name"
            placeholder="e.g., Push Day, Full Body Workout"
            required
            :error="validationErrors.name"
            @update:model-value="updateField('name', String($event))"
          />

          <BaseTextarea
            :model-value="formData.description || ''"
            label="Description"
            placeholder="Describe your workout plan..."
            :rows="3"
            :error="validationErrors.description"
            @update:model-value="updateField('description', $event || null)"
          />
        </div>

        <!-- Exercises Section -->
        <div class="border-t dark:border-gray-700 pt-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">Exercises</h3>
            <BaseButton
              type="button"
              variant="outline"
              size="sm"
              @click="showAddExerciseModal = true"
            >
              + Add Exercise
            </BaseButton>
          </div>

          <!-- Validation Error -->
          <BaseAlert v-if="validationErrors.exercises" type="error" class="mb-4">
            {{ validationErrors.exercises }}
          </BaseAlert>

          <!-- Exercise List -->
          <div v-if="formData.exercises.length > 0" class="space-y-4">
            <EditableExerciseCard
              v-for="exercise in formData.exercises"
              :key="exercise.id"
              :exercise="exercise"
              :can-remove="formData.exercises.length > 1"
              :can-reorder="formData.exercises.length > 1"
              :errors="validationErrors.exerciseErrors.get(exercise.id)"
              @on-update-field="(field: string, value: any) => updateExerciseField(exercise.id, field as keyof EditableExercise, value)"
              @on-substitute="handleSubstitute(exercise.id)"
              @on-remove="handleRemove(exercise.id)"
              @on-move-up="handleMoveUp(exercise.id)"
              @on-move-down="handleMoveDown(exercise.id)"
            />
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
            <p class="text-gray-500 dark:text-gray-400 mb-4">No exercises added yet</p>
            <BaseButton
              type="button"
              variant="primary"
              @click="showAddExerciseModal = true"
            >
              + Add First Exercise
            </BaseButton>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-between items-center pt-6 border-t dark:border-gray-700">
          <div v-if="isDirty" class="text-sm text-amber-600 dark:text-amber-400">
            You have unsaved changes
          </div>
          <div v-else class="text-sm text-gray-500 dark:text-gray-400">
            No changes
          </div>
          <div class="flex gap-3">
            <BaseButton type="button" variant="ghost" @click="handleCancel">
              Cancel
            </BaseButton>
            <BaseButton
              type="submit"
              variant="primary"
              :disabled="!canSave || isSaving"
              :loading="isSaving"
            >
              {{ isSaving ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Plan') }}
            </BaseButton>
          </div>
        </div>
      </form>
    </BaseCard>

    <!-- Add Exercise Modal -->
    <AddExerciseModal
      v-model="showAddExerciseModal"
      :existing-exercise-ids="existingExerciseIds"
      @on-select="handleAddExercise"
    />

    <!-- Substitute Exercise Modal -->
    <SubstituteExerciseModal
      v-model="showSubstituteModal"
      :current-exercise="currentExercise"
      @on-select="handleSubstituteSelect"
    />

    <!-- Unsaved Changes Dialog -->
    <ConfirmationDialog
      v-model="showUnsavedDialog"
      title="Unsaved Changes"
      message="You have unsaved changes. Are you sure you want to leave? Your changes will be lost."
      confirm-text="Discard Changes"
      cancel-text="Keep Editing"
      confirm-variant="danger"
      @confirm="handleDiscardChanges"
      @cancel="handleKeepEditing"
    />
  </div>
</template>
