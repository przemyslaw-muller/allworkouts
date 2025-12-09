<script setup lang="ts">
/**
 * Plan import wizard view.
 * 3-step guided flow: Input -> Review -> Confirm
 */
import { computed, onBeforeUnmount } from 'vue'
import { useRouter, RouterLink, onBeforeRouteLeave } from 'vue-router'
import { useImportWizard } from '@/composables/useImportWizard'
import { useUiStore } from '@/stores/ui'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import StepIndicator from '@/components/import/StepIndicator.vue'
import Step1InputPane from '@/components/import/Step1InputPane.vue'
import Step2ReviewPane from '@/components/import/Step2ReviewPane.vue'
import Step3ConfirmPane from '@/components/import/Step3ConfirmPane.vue'
import type { WizardStep, ExerciseListItem } from '@/types'

const router = useRouter()
const uiStore = useUiStore()

const {
  // State
  currentStep,
  inputText,
  isParsing,
  parseError,
  isCreating,
  createError,
  planName,
  planDescription,
  exercises,
  parseStats,

  // Computed
  hasData,
  canParse,
  isStep2Valid,

  // Methods
  parseWorkoutText,
  updatePlanName,
  updatePlanDescription,
  updateExercise,
  selectAlternativeMatch,
  replaceExercise,
  removeExercise,
  addExercise,
  reorderExercises,
  prevStep,
  goToStep,
  createPlan,
  reset,
} = useImportWizard()

// Navigation guard - warn before leaving with unsaved data
onBeforeRouteLeave((_to, _from, next) => {
  if (hasData.value && !isCreating.value) {
    uiStore.confirm({
      title: 'Leave Import Wizard?',
      message: 'You have unsaved data. Are you sure you want to leave?',
      confirmText: 'Leave',
      cancelText: 'Stay',
      confirmVariant: 'danger',
    }).then((confirmed) => {
      if (confirmed) {
        reset()
        next()
      } else {
        next(false)
      }
    })
  } else {
    next()
  }
})

// Cleanup on unmount
onBeforeUnmount(() => {
  reset()
})

// Step navigation
const handleStepClick = (step: WizardStep) => {
  goToStep(step)
}

const handleBack = () => {
  if (currentStep.value === 1) {
    router.push('/plans')
  } else {
    prevStep()
  }
}

const handleNext = () => {
  if (currentStep.value === 1) {
    parseWorkoutText()
  } else if (currentStep.value === 2) {
    currentStep.value = 3
  }
}

const handleCreate = () => {
  createPlan()
}

// Step 2 handlers
const handleUpdateExercise = (exerciseId: string, updates: any) => {
  updateExercise(exerciseId, updates)
}

const handleSelectAlternative = (exerciseId: string, alternativeIndex: number) => {
  selectAlternativeMatch(exerciseId, alternativeIndex)
}

const handleReplaceExercise = (exerciseId: string, newExercise: ExerciseListItem) => {
  replaceExercise(exerciseId, newExercise)
}

const handleRemoveExercise = (exerciseId: string) => {
  removeExercise(exerciseId)
}

const handleAddExercise = (exercise: ExerciseListItem) => {
  addExercise(exercise)
}

const handleReorderExercises = (fromIndex: number, toIndex: number) => {
  reorderExercises(fromIndex, toIndex)
}

// Computed for navigation
const canProceedFromStep1 = computed(() => canParse.value)
const canProceedFromStep2 = computed(() => isStep2Valid.value)

const stepTitle = computed(() => {
  switch (currentStep.value) {
    case 1:
      return 'Enter Workout Plan'
    case 2:
      return 'Review & Edit'
    case 3:
      return 'Confirm & Create'
    default:
      return 'Import Workout Plan'
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <RouterLink
          to="/plans"
          class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-1 inline-block"
        >
          &larr; Back to Plans
        </RouterLink>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Import Workout Plan
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
          {{ stepTitle }}
        </p>
      </div>

      <!-- Step Indicator -->
      <div class="hidden sm:block w-64">
        <StepIndicator
          :current-step="currentStep"
          @step-click="handleStepClick"
        />
      </div>
    </div>

    <!-- Mobile Step Indicator -->
    <div class="sm:hidden">
      <StepIndicator
        :current-step="currentStep"
        @step-click="handleStepClick"
      />
    </div>

    <!-- Step Content -->
    <div class="min-h-[400px]">
      <!-- Step 1: Input -->
      <Step1InputPane
        v-if="currentStep === 1"
        v-model="inputText"
        :error="parseError"
        :is-parsing="isParsing"
        :can-parse="canProceedFromStep1"
        @parse="parseWorkoutText"
      />

      <!-- Step 2: Review -->
      <Step2ReviewPane
        v-else-if="currentStep === 2"
        :plan-name="planName"
        :plan-description="planDescription"
        :exercises="exercises"
        :parse-stats="parseStats"
        @update:plan-name="updatePlanName"
        @update:plan-description="updatePlanDescription"
        @update-exercise="handleUpdateExercise"
        @select-alternative="handleSelectAlternative"
        @replace-exercise="handleReplaceExercise"
        @remove-exercise="handleRemoveExercise"
        @add-exercise="handleAddExercise"
        @reorder-exercises="handleReorderExercises"
      />

      <!-- Step 3: Confirm -->
      <Step3ConfirmPane
        v-else-if="currentStep === 3"
        :plan-name="planName"
        :plan-description="planDescription"
        :exercises="exercises"
        :is-creating="isCreating"
        :create-error="createError"
        @create="handleCreate"
        @back="prevStep"
      />
    </div>

    <!-- Footer Navigation (Steps 1 & 2) -->
    <div
      v-if="currentStep < 3"
      class="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700"
    >
      <BaseButton
        type="button"
        variant="outline"
        :disabled="isParsing"
        @click="handleBack"
      >
        {{ currentStep === 1 ? 'Cancel' : 'Back' }}
      </BaseButton>

      <BaseButton
        v-if="currentStep === 2"
        type="button"
        variant="primary"
        :disabled="!canProceedFromStep2"
        @click="handleNext"
      >
        Continue to Confirm
      </BaseButton>
    </div>

    <!-- Loading Overlay for Parsing -->
    <LoadingOverlay
      v-if="isParsing"
      message="Analyzing your workout plan..."
    />
  </div>
</template>
