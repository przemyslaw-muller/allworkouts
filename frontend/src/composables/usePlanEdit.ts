/**
 * Composable for managing workout plan editing state and operations.
 */
import { ref, computed, type Ref } from 'vue'
import { workoutPlanService } from '@/services/workoutPlanService'
import { useUiStore } from '@/stores/ui'
import type {
  PlanEditFormData,
  EditableExercise,
  FormValidationErrors,
  ExerciseFieldErrors,
  WorkoutPlanDetailResponse,
  WorkoutPlanUpdateRequest,
  WorkoutExerciseCreateItem,
  ExerciseListItem,
} from '@/types'

export function usePlanEdit(planId: Ref<string | undefined>) {
  const uiStore = useUiStore()

  // State
  const originalData = ref<PlanEditFormData | null>(null)
  const formData = ref<PlanEditFormData>({
    name: '',
    description: null,
    exercises: [],
  })
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const validationErrors = ref<FormValidationErrors>({
    exerciseErrors: new Map(),
  })

  // Computed
  const isDirty = computed(() => {
    if (!originalData.value) return false
    return JSON.stringify(originalData.value) !== JSON.stringify(formData.value)
  })

  const isValid = computed(() => {
    return (
      formData.value.name.trim().length > 0 &&
      formData.value.name.length <= 200 &&
      (!formData.value.description || formData.value.description.length <= 1000) &&
      formData.value.exercises.length > 0 &&
      formData.value.exercises.every(
        (ex) =>
          ex.sets >= 1 &&
          ex.sets <= 50 &&
          ex.repsMin >= 1 &&
          ex.repsMin <= 200 &&
          ex.repsMax >= 1 &&
          ex.repsMax <= 200 &&
          ex.repsMin <= ex.repsMax &&
          (ex.restTimeSeconds === null ||
            (ex.restTimeSeconds >= 0 && ex.restTimeSeconds <= 3600)),
      )
    )
  })

  const canSave = computed(() => isDirty.value && isValid.value)

  // Methods
  const mapResponseToFormData = (response: WorkoutPlanDetailResponse): PlanEditFormData => {
    return {
      name: response.name,
      description: response.description,
      exercises: response.exercises
        .sort((a, b) => a.sequence - b.sequence)
        .map((ex) => ({
          id: ex.id,
          exerciseId: ex.exercise.id,
          exerciseName: ex.exercise.name,
          primaryMuscleGroups: ex.exercise.primary_muscle_groups,
          secondaryMuscleGroups: ex.exercise.secondary_muscle_groups,
          equipment: [],
          sequence: ex.sequence,
          sets: ex.sets,
          repsMin: ex.reps_min,
          repsMax: ex.reps_max,
          restTimeSeconds: ex.rest_time_seconds,
          confidenceLevel: ex.confidence_level,
          isNew: false,
          isModified: false,
        })),
    }
  }

  const fetchPlan = async (): Promise<void> => {
    if (!planId.value) {
      error.value = 'Plan ID is required'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await workoutPlanService.getById(planId.value)
      const data = mapResponseToFormData(response)
      formData.value = data
      originalData.value = JSON.parse(JSON.stringify(data))
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load plan'
      uiStore.error('Failed to load plan. Please try again.')
    } finally {
      isLoading.value = false
    }
  }

  const validateForm = (): boolean => {
    validationErrors.value = { exerciseErrors: new Map() }
    let isFormValid = true

    // Validate name
    if (!formData.value.name.trim()) {
      validationErrors.value.name = 'Plan name is required'
      isFormValid = false
    } else if (formData.value.name.length > 200) {
      validationErrors.value.name = 'Name must be 200 characters or less'
      isFormValid = false
    }

    // Validate description
    if (formData.value.description && formData.value.description.length > 1000) {
      validationErrors.value.description = 'Description must be 1000 characters or less'
      isFormValid = false
    }

    // Validate exercises
    if (formData.value.exercises.length === 0) {
      validationErrors.value.exercises = 'At least one exercise is required'
      isFormValid = false
    }

    // Validate each exercise
    formData.value.exercises.forEach((exercise) => {
      const errors: ExerciseFieldErrors = {}

      if (exercise.sets < 1 || exercise.sets > 50) {
        errors.sets = 'Sets must be between 1 and 50'
        isFormValid = false
      }

      if (exercise.repsMin < 1 || exercise.repsMin > 200) {
        errors.repsMin = 'Reps must be between 1 and 200'
        isFormValid = false
      }

      if (exercise.repsMax < 1 || exercise.repsMax > 200) {
        errors.repsMax = 'Reps must be between 1 and 200'
        isFormValid = false
      }

      if (exercise.repsMin > exercise.repsMax) {
        errors.repsMin = 'Min reps cannot be greater than max reps'
        isFormValid = false
      }

      if (
        exercise.restTimeSeconds !== null &&
        (exercise.restTimeSeconds < 0 || exercise.restTimeSeconds > 3600)
      ) {
        errors.restTimeSeconds = 'Rest time must be between 0 and 3600 seconds'
        isFormValid = false
      }

      if (Object.keys(errors).length > 0) {
        validationErrors.value.exerciseErrors.set(exercise.id, errors)
      }
    })

    return isFormValid
  }

  const mapFormToUpdateRequest = (data: PlanEditFormData): WorkoutPlanUpdateRequest => {
    const exercises: WorkoutExerciseCreateItem[] = data.exercises.map((ex, index) => ({
      exercise_id: ex.exerciseId,
      sequence: index,
      sets: ex.sets,
      reps_min: ex.repsMin,
      reps_max: ex.repsMax,
      rest_time_seconds: ex.restTimeSeconds,
      confidence_level: ex.confidenceLevel,
    }))

    return {
      name: data.name,
      description: data.description,
      exercises,
    }
  }

  const savePlan = async (): Promise<boolean> => {
    if (!planId.value) {
      error.value = 'Plan ID is required'
      return false
    }

    if (!validateForm()) {
      uiStore.error('Please fix validation errors before saving')
      return false
    }

    isSaving.value = true
    error.value = null

    try {
      const updateData = mapFormToUpdateRequest(formData.value)
      await workoutPlanService.update(planId.value, updateData)

      uiStore.success('Plan saved successfully')

      // Update original data to match saved data
      originalData.value = JSON.parse(JSON.stringify(formData.value))

      return true
    } catch (err: any) {
      error.value = err instanceof Error ? err.message : 'Failed to save plan'

      // Handle validation errors from backend
      if (err.response?.data?.error?.details) {
        const details = err.response.data.error.details
        for (const [key, message] of Object.entries(details)) {
          if (key === 'name') {
            validationErrors.value.name = message as string
          } else if (key === 'description') {
            validationErrors.value.description = message as string
          }
        }
      }

      uiStore.error('Failed to save plan. Please try again.')

      return false
    } finally {
      isSaving.value = false
    }
  }

  // Exercise operations
  const addExercise = (exercise: ExerciseListItem): void => {
    const newExercise: EditableExercise = {
      id: `temp-${Date.now()}`,
      exerciseId: exercise.id,
      exerciseName: exercise.name,
      primaryMuscleGroups: exercise.primary_muscle_groups,
      secondaryMuscleGroups: exercise.secondary_muscle_groups,
      equipment: exercise.equipment,
      sequence: formData.value.exercises.length,
      sets: 3,
      repsMin: 8,
      repsMax: 12,
      restTimeSeconds: 60,
      confidenceLevel: 'high',
      isNew: true,
      isModified: false,
    }

    formData.value.exercises.push(newExercise)
  }

  const removeExercise = (exerciseId: string): void => {
    const index = formData.value.exercises.findIndex((ex) => ex.id === exerciseId)
    if (index !== -1) {
      formData.value.exercises.splice(index, 1)
      // Update sequence numbers
      formData.value.exercises.forEach((ex, idx) => {
        ex.sequence = idx
      })
    }
  }

  const substituteExercise = (oldExerciseId: string, newExercise: ExerciseListItem): void => {
    const index = formData.value.exercises.findIndex((ex) => ex.id === oldExerciseId)
    if (index !== -1) {
      const oldExercise = formData.value.exercises[index]
      formData.value.exercises[index] = {
        ...oldExercise,
        exerciseId: newExercise.id,
        exerciseName: newExercise.name,
        primaryMuscleGroups: newExercise.primary_muscle_groups,
        secondaryMuscleGroups: newExercise.secondary_muscle_groups,
        equipment: newExercise.equipment,
        isModified: true,
      }
    }
  }

  const reorderExercises = (fromIndex: number, toIndex: number): void => {
    if (
      fromIndex < 0 ||
      fromIndex >= formData.value.exercises.length ||
      toIndex < 0 ||
      toIndex >= formData.value.exercises.length
    ) {
      return
    }

    const [movedExercise] = formData.value.exercises.splice(fromIndex, 1)
    formData.value.exercises.splice(toIndex, 0, movedExercise)

    // Update sequence numbers
    formData.value.exercises.forEach((ex, idx) => {
      ex.sequence = idx
      ex.isModified = true
    })
  }

  const updateExerciseField = (
    exerciseId: string,
    field: keyof EditableExercise,
    value: any,
  ): void => {
    const exercise = formData.value.exercises.find((ex) => ex.id === exerciseId)
    if (exercise) {
      ;(exercise as any)[field] = value
      exercise.isModified = true

      // Clear validation error for this field if it exists
      const errors = validationErrors.value.exerciseErrors.get(exerciseId)
      if (errors && field in errors) {
        delete (errors as any)[field]
        if (Object.keys(errors).length === 0) {
          validationErrors.value.exerciseErrors.delete(exerciseId)
        }
      }
    }
  }

  const updateField = (field: 'name' | 'description', value: string | null): void => {
    if (field === 'name') {
      formData.value.name = value || ''
    } else {
      formData.value.description = value
    }

    // Clear validation error for this field
    if (validationErrors.value[field]) {
      delete validationErrors.value[field]
    }
  }

  return {
    formData,
    isLoading,
    isSaving,
    isDirty,
    isValid,
    canSave,
    error,
    validationErrors,
    fetchPlan,
    savePlan,
    validateForm,
    addExercise,
    removeExercise,
    substituteExercise,
    reorderExercises,
    updateExerciseField,
    updateField,
  }
}
