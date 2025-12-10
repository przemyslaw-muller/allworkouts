/**
 * Composable for managing the workout plan import wizard state and operations.
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { workoutPlanService } from '@/services/workoutPlanService'
import { useUiStore } from '@/stores/ui'
import type {
  WizardStep,
  ParsedWorkoutPlan,
  ParsedExerciseViewModel,
  ParseStats,
  WorkoutExerciseCreateItem,
  ExerciseListItem,
  ParsedExerciseMatch,
  ConfidenceLevel,
} from '@/types'

export function useImportWizard() {
  const router = useRouter()
  const uiStore = useUiStore()

  // State
  const currentStep = ref<WizardStep>(1)
  const inputText = ref('')
  const isParsing = ref(false)
  const parseError = ref<string | null>(null)
  const isCreating = ref(false)
  const createError = ref<string | null>(null)

  // Parsed data
  const importLogId = ref<string | null>(null)
  const planName = ref('')
  const planDescription = ref<string | null>(null)
  const exercises = ref<ParsedExerciseViewModel[]>([])
  const parseStats = ref<ParseStats | null>(null)

  // Computed
  const hasData = computed(() => inputText.value.length > 0 || exercises.value.length > 0)

  const inputCharCount = computed(() => inputText.value.length)

  const canParse = computed(() => {
    return inputText.value.trim().length >= 10 && !isParsing.value
  })

  const hasLowConfidenceExercises = computed(() => {
    return exercises.value.some((ex) => ex.confidenceLevel === 'low' || !ex.matchedExercise)
  })

  const hasUnmatchedExercises = computed(() => {
    return exercises.value.some((ex) => !ex.matchedExercise)
  })

  const validExercises = computed(() => {
    return exercises.value.filter((ex) => ex.matchedExercise !== null)
  })

  const canProceedToStep2 = computed(() => {
    return inputText.value.trim().length >= 10
  })

  const canProceedToStep3 = computed(() => {
    return (
      exercises.value.length > 0 &&
      exercises.value.every((ex) => ex.matchedExercise !== null) &&
      planName.value.trim().length > 0
    )
  })

  const isStep2Valid = computed(() => {
    return (
      exercises.value.length > 0 && planName.value.trim().length > 0 && planName.value.length <= 200
    )
  })

  const isStep3Valid = computed(() => {
    return (
      exercises.value.length > 0 &&
      exercises.value.every((ex) => ex.matchedExercise !== null) &&
      planName.value.trim().length > 0 &&
      planName.value.length <= 200
    )
  })

  // Methods
  const mapParsedResponseToViewModels = (
    parsedPlan: ParsedWorkoutPlan,
  ): ParsedExerciseViewModel[] => {
    return parsedPlan.exercises.map((item, index) => ({
      id: `parsed-${index}-${Date.now()}`,
      originalText: item.original_text,
      matchedExercise: item.matched_exercise,
      alternativeMatches: item.alternatives || [],
      sets: item.sets,
      repsMin: item.reps_min,
      repsMax: item.reps_max,
      restSeconds: item.rest_seconds,
      notes: item.notes,
      confidenceLevel: item.matched_exercise?.confidence_level || null,
      sequence: item.sequence,
      isManuallyAdded: false,
      isModified: false,
    }))
  }

  const parseWorkoutText = async (): Promise<void> => {
    if (!canParse.value) return

    isParsing.value = true
    parseError.value = null

    try {
      const response = await workoutPlanService.parseWorkoutText({ text: inputText.value })

      // Store import log ID
      importLogId.value = response.parsed_plan.import_log_id

      // Set plan name and description
      planName.value = response.parsed_plan.name
      planDescription.value = response.parsed_plan.description

      // Map exercises to view models
      exercises.value = mapParsedResponseToViewModels(response.parsed_plan)

      // Store stats
      parseStats.value = {
        total: response.total_exercises,
        highConfidence: response.high_confidence_count,
        mediumConfidence: response.medium_confidence_count,
        lowConfidence: response.low_confidence_count,
        unmatched: response.unmatched_count,
      }

      // Move to step 2
      currentStep.value = 2
    } catch (err: any) {
      const errorCode = err.response?.data?.error?.code
      const errorMessage = err.response?.data?.error?.message

      if (errorCode === 'VALIDATION_ERROR' || errorCode === 'TEXT_TOO_SHORT') {
        parseError.value = errorMessage || 'Please enter at least 10 characters'
      } else if (errorCode === 'TEXT_TOO_LONG') {
        parseError.value = 'Text is too long. Please limit to 50,000 characters.'
      } else if (errorCode === 'LLM_SERVICE_ERROR') {
        parseError.value = 'AI service is temporarily unavailable. Please try again later.'
      } else {
        parseError.value = errorMessage || 'Failed to parse workout text. Please try again.'
      }

      uiStore.error(parseError.value!)
    } finally {
      isParsing.value = false
    }
  }

  const updatePlanName = (name: string): void => {
    planName.value = name
  }

  const updatePlanDescription = (description: string | null): void => {
    planDescription.value = description
  }

  const updateExercise = (exerciseId: string, updates: Partial<ParsedExerciseViewModel>): void => {
    const index = exercises.value.findIndex((ex) => ex.id === exerciseId)
    if (index !== -1) {
      exercises.value[index] = {
        ...exercises.value[index],
        ...updates,
        isModified: true,
      }
    }
  }

  const fixExerciseMatch = (exerciseId: string, newMatch: ParsedExerciseMatch): void => {
    const index = exercises.value.findIndex((ex) => ex.id === exerciseId)
    if (index !== -1) {
      exercises.value[index] = {
        ...exercises.value[index],
        matchedExercise: newMatch,
        confidenceLevel: 'high' as ConfidenceLevel, // User confirmed, so high confidence
        isModified: true,
      }
    }
  }

  const selectAlternativeMatch = (exerciseId: string, alternativeIndex: number): void => {
    const exercise = exercises.value.find((ex) => ex.id === exerciseId)
    if (exercise && exercise.alternativeMatches[alternativeIndex]) {
      const alternative = exercise.alternativeMatches[alternativeIndex]
      fixExerciseMatch(exerciseId, alternative)
    }
  }

  const removeExercise = (exerciseId: string): void => {
    const index = exercises.value.findIndex((ex) => ex.id === exerciseId)
    if (index !== -1) {
      exercises.value.splice(index, 1)
      // Update sequences
      exercises.value.forEach((ex, idx) => {
        ex.sequence = idx
      })
    }
  }

  const addExercise = (exercise: ExerciseListItem): void => {
    const newExercise: ParsedExerciseViewModel = {
      id: `manual-${Date.now()}`,
      originalText: exercise.name,
      matchedExercise: {
        exercise_id: exercise.id,
        exercise_name: exercise.name,
        original_text: exercise.name,
        confidence: 1.0,
        confidence_level: 'high',
        primary_muscle_groups: exercise.primary_muscle_groups,
        secondary_muscle_groups: exercise.secondary_muscle_groups,
      },
      alternativeMatches: [],
      sets: 3,
      repsMin: 8,
      repsMax: 12,
      restSeconds: 60,
      notes: null,
      confidenceLevel: 'high',
      sequence: exercises.value.length,
      isManuallyAdded: true,
      isModified: false,
    }

    exercises.value.push(newExercise)
  }

  const replaceExercise = (exerciseId: string, newExercise: ExerciseListItem): void => {
    const index = exercises.value.findIndex((ex) => ex.id === exerciseId)
    if (index !== -1) {
      exercises.value[index] = {
        ...exercises.value[index],
        matchedExercise: {
          exercise_id: newExercise.id,
          exercise_name: newExercise.name,
          original_text: exercises.value[index].originalText,
          confidence: 1.0,
          confidence_level: 'high',
          primary_muscle_groups: newExercise.primary_muscle_groups,
          secondary_muscle_groups: newExercise.secondary_muscle_groups,
        },
        confidenceLevel: 'high',
        isModified: true,
      }
    }
  }

  const reorderExercises = (fromIndex: number, toIndex: number): void => {
    if (
      fromIndex < 0 ||
      fromIndex >= exercises.value.length ||
      toIndex < 0 ||
      toIndex >= exercises.value.length
    ) {
      return
    }

    const [movedExercise] = exercises.value.splice(fromIndex, 1)
    exercises.value.splice(toIndex, 0, movedExercise)

    // Update sequences
    exercises.value.forEach((ex, idx) => {
      ex.sequence = idx
    })
  }

  const nextStep = (): void => {
    if (currentStep.value === 1 && canProceedToStep2.value) {
      parseWorkoutText()
    } else if (currentStep.value === 2 && isStep2Valid.value) {
      currentStep.value = 3
    }
  }

  const prevStep = (): void => {
    if (currentStep.value === 2) {
      currentStep.value = 1
    } else if (currentStep.value === 3) {
      currentStep.value = 2
    }
  }

  const goToStep = (step: WizardStep): void => {
    // Only allow going back, not skipping ahead
    if (step < currentStep.value) {
      currentStep.value = step
    }
  }

  const createPlan = async (): Promise<void> => {
    if (!isStep3Valid.value || !importLogId.value) {
      uiStore.error('Please review and fix all exercises before creating the plan')
      return
    }

    isCreating.value = true
    createError.value = null

    try {
      // Map exercises to create request format
      const exerciseItems: WorkoutExerciseCreateItem[] = exercises.value
        .filter((ex) => ex.matchedExercise !== null)
        .map((ex, index) => ({
          exercise_id: ex.matchedExercise!.exercise_id,
          sequence: index,
          sets: ex.sets,
          reps_min: ex.repsMin,
          reps_max: ex.repsMax,
          rest_time_seconds: ex.restSeconds,
          confidence_level: ex.confidenceLevel || 'medium',
        }))

      const response = await workoutPlanService.createFromParsed({
        import_log_id: importLogId.value,
        name: planName.value.trim(),
        description: planDescription.value?.trim() || null,
        exercises: exerciseItems,
      })

      uiStore.success('Workout plan created successfully!')
      router.push({ name: 'plan-detail', params: { id: response.id } })
    } catch (err: any) {
      const errorCode = err.response?.data?.error?.code
      const errorMessage = err.response?.data?.error?.message

      if (errorCode === 'IMPORT_LOG_NOT_FOUND') {
        createError.value = 'Import session expired. Please start over.'
      } else if (errorCode === 'IMPORT_LOG_ALREADY_USED') {
        createError.value = 'This import has already been used.'
      } else if (errorCode === 'VALIDATION_ERROR') {
        createError.value = errorMessage || 'Invalid plan data. Please review and try again.'
      } else {
        createError.value = errorMessage || 'Failed to create plan. Please try again.'
      }

      uiStore.error(createError.value!)
    } finally {
      isCreating.value = false
    }
  }

  const reset = (): void => {
    currentStep.value = 1
    inputText.value = ''
    isParsing.value = false
    parseError.value = null
    isCreating.value = false
    createError.value = null
    importLogId.value = null
    planName.value = ''
    planDescription.value = null
    exercises.value = []
    parseStats.value = null
  }

  return {
    // State
    currentStep,
    inputText,
    isParsing,
    parseError,
    isCreating,
    createError,
    importLogId,
    planName,
    planDescription,
    exercises,
    parseStats,

    // Computed
    hasData,
    inputCharCount,
    canParse,
    hasLowConfidenceExercises,
    hasUnmatchedExercises,
    validExercises,
    canProceedToStep2,
    canProceedToStep3,
    isStep2Valid,
    isStep3Valid,

    // Methods
    parseWorkoutText,
    updatePlanName,
    updatePlanDescription,
    updateExercise,
    fixExerciseMatch,
    selectAlternativeMatch,
    removeExercise,
    addExercise,
    replaceExercise,
    reorderExercises,
    nextStep,
    prevStep,
    goToStep,
    createPlan,
    reset,
  }
}
