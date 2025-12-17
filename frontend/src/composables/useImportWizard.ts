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
  ParsedWorkoutViewModel,
  ParseStats,
  WorkoutCreateItem,
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
  const workouts = ref<ParsedWorkoutViewModel[]>([])
  const parseStats = ref<ParseStats | null>(null)

  // Computed
  const hasData = computed(() => inputText.value.length > 0 || workouts.value.length > 0)

  const inputCharCount = computed(() => inputText.value.length)

  const canParse = computed(() => {
    return inputText.value.trim().length >= 10 && !isParsing.value
  })

  const allExercises = computed(() => {
    return workouts.value.flatMap(w => w.exercises)
  })

  const hasLowConfidenceExercises = computed(() => {
    return allExercises.value.some((ex) => ex.confidenceLevel === 'low' || !ex.matchedExercise)
  })

  const hasUnmatchedExercises = computed(() => {
    return allExercises.value.some((ex) => !ex.matchedExercise)
  })

  const validExercises = computed(() => {
    return allExercises.value.filter((ex) => ex.matchedExercise !== null)
  })

  const canProceedToStep2 = computed(() => {
    return inputText.value.trim().length >= 10
  })

  const canProceedToStep3 = computed(() => {
    return (
      workouts.value.length > 0 &&
      allExercises.value.every((ex) => ex.matchedExercise !== null) &&
      planName.value.trim().length > 0
    )
  })

  const isStep2Valid = computed(() => {
    return (
      workouts.value.length > 0 && planName.value.trim().length > 0 && planName.value.length <= 200
    )
  })

  const isStep3Valid = computed(() => {
    return (
      workouts.value.length > 0 &&
      allExercises.value.every((ex) => ex.matchedExercise !== null) &&
      planName.value.trim().length > 0 &&
      planName.value.length <= 200
    )
  })

  // Methods
  const mapParsedResponseToViewModels = (
    parsedPlan: ParsedWorkoutPlan,
  ): ParsedWorkoutViewModel[] => {
    // Preserve workout structure
    return parsedPlan.workouts.map((workout, workoutIndex) => ({
      id: `workout-${workoutIndex}-${Date.now()}`,
      name: workout.name,
      dayNumber: workout.day_number,
      orderIndex: workout.order_index,
      exercises: workout.exercises.map((item, exIndex) => ({
        id: `parsed-${workoutIndex}-${exIndex}-${Date.now()}`,
        originalText: item.original_text,
        matchedExercise: item.matched_exercise,
        alternativeMatches: item.alternatives || [],
        setConfigurations: item.set_configurations,
        restSeconds: item.rest_seconds,
        notes: item.notes,
        confidenceLevel: item.matched_exercise?.confidence_level || null,
        sequence: item.sequence,
        isManuallyAdded: false,
        isModified: false,
      })),
    }))
  }

  const parseWorkoutText = async (): Promise<void> => {
    if (!canParse.value) return

    isParsing.value = true
    parseError.value = null

    try {
      // Step 1: Start the parse operation
      const startResponse = await workoutPlanService.parseWorkoutText({ text: inputText.value })
      const logId = startResponse.import_log_id

      // Step 2: Poll for status until completed or failed
      let statusResponse = await workoutPlanService.getParseStatus(logId)
      
      while (statusResponse.status === 'pending' || statusResponse.status === 'processing') {
        // Wait 2 seconds before polling again
        await new Promise(resolve => setTimeout(resolve, 2000))
        statusResponse = await workoutPlanService.getParseStatus(logId)
      }

      // Step 3: Handle the result
      if (statusResponse.status === 'completed' && statusResponse.result) {
        const response = statusResponse.result

        // Store import log ID
        importLogId.value = response.parsed_plan.import_log_id

        // Set plan name and description
        planName.value = response.parsed_plan.name
        planDescription.value = response.parsed_plan.description

        // Map workouts to view models
        workouts.value = mapParsedResponseToViewModels(response.parsed_plan)

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
      } else if (statusResponse.status === 'failed') {
        throw new Error(statusResponse.error || 'Parsing failed')
      }
    } catch (err: any) {
      const errorCode = err.response?.data?.error?.code
      const errorMessage = err.response?.data?.error?.message || err.message

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
    for (const workout of workouts.value) {
      const index = workout.exercises.findIndex((ex) => ex.id === exerciseId)
      if (index !== -1) {
        workout.exercises[index] = {
          ...workout.exercises[index],
          ...updates,
          isModified: true,
        }
        break
      }
    }
  }

  const fixExerciseMatch = (exerciseId: string, newMatch: ParsedExerciseMatch): void => {
    for (const workout of workouts.value) {
      const index = workout.exercises.findIndex((ex) => ex.id === exerciseId)
      if (index !== -1) {
        workout.exercises[index] = {
          ...workout.exercises[index],
          matchedExercise: newMatch,
          confidenceLevel: 'high' as ConfidenceLevel, // User confirmed, so high confidence
          isModified: true,
        }
        break
      }
    }
  }

  const selectAlternativeMatch = (exerciseId: string, alternativeIndex: number): void => {
    for (const workout of workouts.value) {
      const exercise = workout.exercises.find((ex) => ex.id === exerciseId)
      if (exercise && exercise.alternativeMatches[alternativeIndex]) {
        const alternative = exercise.alternativeMatches[alternativeIndex]
        fixExerciseMatch(exerciseId, alternative)
        break
      }
    }
  }

  const removeExercise = (exerciseId: string): void => {
    for (const workout of workouts.value) {
      const index = workout.exercises.findIndex((ex) => ex.id === exerciseId)
      if (index !== -1) {
        workout.exercises.splice(index, 1)
        // Update sequences
        workout.exercises.forEach((ex, idx) => {
          ex.sequence = idx
        })
        break
      }
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
      setConfigurations: [
        { set_number: 1, reps_min: 8, reps_max: 12 },
        { set_number: 2, reps_min: 8, reps_max: 12 },
        { set_number: 3, reps_min: 8, reps_max: 12 },
      ],
      restSeconds: 60,
      notes: null,
      confidenceLevel: 'high',
      sequence: 0,
      isManuallyAdded: true,
      isModified: false,
    }

    // Add to first workout or create one if none exist
    if (workouts.value.length === 0) {
      workouts.value.push({
        id: `workout-0-${Date.now()}`,
        name: planName.value || 'Workout 1',
        dayNumber: null,
        orderIndex: 0,
        exercises: [],
      })
    }
    newExercise.sequence = workouts.value[0].exercises.length
    workouts.value[0].exercises.push(newExercise)
  }

  const replaceExercise = (exerciseId: string, newExercise: ExerciseListItem): void => {
    for (const workout of workouts.value) {
      const index = workout.exercises.findIndex((ex) => ex.id === exerciseId)
      if (index !== -1) {
        // Replace the exercise completely with new matched exercise
        workout.exercises[index] = {
          ...workout.exercises[index],
          matchedExercise: {
            exercise_id: newExercise.id,
            exercise_name: newExercise.name,
            original_text: workout.exercises[index].originalText,
            confidence: 1.0,
            confidence_level: 'high',
            primary_muscle_groups: newExercise.primary_muscle_groups,
            secondary_muscle_groups: newExercise.secondary_muscle_groups,
          },
          confidenceLevel: 'high',
          isModified: true,
        }
        break
      }
    }
  }

  const reorderExercises = (workoutId: string, fromIndex: number, toIndex: number): void => {
    const workout = workouts.value.find(w => w.id === workoutId)
    if (!workout) return

    if (
      fromIndex < 0 ||
      fromIndex >= workout.exercises.length ||
      toIndex < 0 ||
      toIndex >= workout.exercises.length
    ) {
      return
    }

    const [movedExercise] = workout.exercises.splice(fromIndex, 1)
    workout.exercises.splice(toIndex, 0, movedExercise)

    // Update sequences
    workout.exercises.forEach((ex, idx) => {
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
      // Map workouts to create request format with nested exercises
      const workoutItems: WorkoutCreateItem[] = workouts.value.map((workout) => ({
        name: workout.name,
        day_number: workout.dayNumber,
        order_index: workout.orderIndex,
        exercises: workout.exercises
          .filter((ex) => ex.matchedExercise !== null)
          .map((ex, index) => ({
            exercise_id: ex.matchedExercise!.exercise_id,
            sequence: index,
            set_configurations: ex.setConfigurations,
            rest_time_seconds: ex.restSeconds,
            confidence_level: ex.confidenceLevel || 'medium',
          })),
      }))

      const response = await workoutPlanService.createFromParsed({
        import_log_id: importLogId.value,
        name: planName.value.trim(),
        description: planDescription.value?.trim() || null,
        workouts: workoutItems,
      })

      uiStore.success('Workout plan created successfully!')
      reset() // Clear wizard state before navigation
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
    workouts.value = []
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
    workouts,
    parseStats,

    // Computed
    hasData,
    inputCharCount,
    canParse,
    allExercises,
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
