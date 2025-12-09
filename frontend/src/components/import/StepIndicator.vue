<script setup lang="ts">
/**
 * Step indicator for the import wizard.
 * Shows 3 steps with current/completed/pending states.
 */
import type { WizardStep } from '@/types'

interface Props {
  currentStep: WizardStep
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'stepClick', step: WizardStep): void
}>()

const steps = [
  { number: 1, label: 'Input' },
  { number: 2, label: 'Review' },
  { number: 3, label: 'Confirm' },
] as const

const getStepState = (stepNumber: number): 'completed' | 'current' | 'pending' => {
  if (stepNumber < props.currentStep) return 'completed'
  if (stepNumber === props.currentStep) return 'current'
  return 'pending'
}

const getStepClasses = (stepNumber: number) => {
  const state = getStepState(stepNumber)
  const base = 'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-colors'

  if (state === 'completed') {
    return `${base} bg-green-600 text-white`
  }
  if (state === 'current') {
    return `${base} bg-indigo-600 text-white`
  }
  return `${base} bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400`
}

const getLabelClasses = (stepNumber: number) => {
  const state = getStepState(stepNumber)
  const base = 'mt-1 text-xs font-medium'

  if (state === 'completed') {
    return `${base} text-green-600 dark:text-green-400`
  }
  if (state === 'current') {
    return `${base} text-indigo-600 dark:text-indigo-400`
  }
  return `${base} text-gray-500 dark:text-gray-400`
}

const getConnectorClasses = (stepNumber: number) => {
  const isCompleted = stepNumber < props.currentStep
  const base = 'flex-1 h-0.5 mx-2'

  if (isCompleted) {
    return `${base} bg-green-600`
  }
  return `${base} bg-gray-200 dark:bg-gray-700`
}

const canClickStep = (stepNumber: number): boolean => {
  return stepNumber < props.currentStep
}

const handleStepClick = (stepNumber: number) => {
  if (canClickStep(stepNumber)) {
    emit('stepClick', stepNumber as WizardStep)
  }
}
</script>

<template>
  <div class="flex items-center justify-center">
    <template v-for="(step, index) in steps" :key="step.number">
      <!-- Step circle and label -->
      <div class="flex flex-col items-center">
        <button
          type="button"
          :class="getStepClasses(step.number)"
          :disabled="!canClickStep(step.number)"
          :aria-current="step.number === currentStep ? 'step' : undefined"
          @click="handleStepClick(step.number)"
        >
          <template v-if="getStepState(step.number) === 'completed'">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
          </template>
          <template v-else>
            {{ step.number }}
          </template>
        </button>
        <span :class="getLabelClasses(step.number)">{{ step.label }}</span>
      </div>

      <!-- Connector line -->
      <div
        v-if="index < steps.length - 1"
        :class="getConnectorClasses(step.number)"
        class="mb-5"
      />
    </template>
  </div>
</template>
