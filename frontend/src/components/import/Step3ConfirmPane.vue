<script setup lang="ts">
/**
 * Step 3 of the import wizard - Confirm and create plan.
 * Final confirmation view before creating the workout plan.
 */
import { computed } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAlert from '@/components/common/BaseAlert.vue'
import ConfidenceBadge from './ConfidenceBadge.vue'
import type { ParsedExerciseViewModel } from '@/types'

interface Props {
  planName: string
  planDescription: string | null
  exercises: ParsedExerciseViewModel[]
  isCreating: boolean
  createError: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'create'): void
  (e: 'back'): void
}>()

const totalSets = computed(() => {
  return props.exercises.reduce((sum, ex) => sum + ex.sets, 0)
})

const muscleGroupsSummary = computed(() => {
  const groups = new Set<string>()
  props.exercises.forEach((ex) => {
    if (ex.matchedExercise) {
      ex.matchedExercise.primary_muscle_groups.forEach((mg) => groups.add(mg))
    }
  })
  return Array.from(groups)
    .map((mg) => mg.charAt(0).toUpperCase() + mg.slice(1))
    .sort()
    .join(', ')
})

const allExercisesMatched = computed(() => {
  return props.exercises.every((ex) => ex.matchedExercise !== null)
})

const formatReps = (min: number, max: number) => {
  if (min === max) return `${min}`
  return `${min}-${max}`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Error Alert -->
    <BaseAlert v-if="createError" variant="error">
      <template #title>Creation Failed</template>
      <template #default>{{ createError }}</template>
    </BaseAlert>

    <!-- Validation Warning -->
    <BaseAlert v-if="!allExercisesMatched" variant="warning">
      <template #title>Cannot Create Plan</template>
      <template #default>
        Some exercises are not matched. Please go back and fix all unmatched exercises before creating the plan.
      </template>
    </BaseAlert>

    <!-- Plan Summary Card -->
    <BaseCard>
      <div class="space-y-4">
        <div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ planName }}
          </h3>
          <p v-if="planDescription" class="mt-1 text-gray-600 dark:text-gray-400">
            {{ planDescription }}
          </p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y border-gray-200 dark:border-gray-700">
          <div>
            <p class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{{ exercises.length }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">Exercise{{ exercises.length !== 1 ? 's' : '' }}</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{{ totalSets }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">Total Sets</p>
          </div>
          <div class="col-span-2">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">Muscle Groups</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ muscleGroupsSummary || 'None' }}</p>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Exercise Preview List -->
    <BaseCard>
      <h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
        Exercise Summary
      </h4>

      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="(exercise, index) in exercises"
          :key="exercise.id"
          class="py-3 first:pt-0 last:pb-0"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ index + 1 }}
              </span>
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-medium text-gray-900 dark:text-gray-100">
                    {{ exercise.matchedExercise?.exercise_name || 'Unknown Exercise' }}
                  </span>
                  <ConfidenceBadge :level="exercise.confidenceLevel" :show-label="false" />
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                  {{ exercise.matchedExercise?.primary_muscle_groups.map(mg => mg.charAt(0).toUpperCase() + mg.slice(1)).join(', ') }}
                </p>
              </div>
            </div>
            <div class="text-right text-sm text-gray-600 dark:text-gray-400 flex-shrink-0">
              <span class="font-medium">{{ exercise.sets }} x {{ formatReps(exercise.repsMin, exercise.repsMax) }}</span>
              <span v-if="exercise.restSeconds" class="block text-xs text-gray-400">
                {{ exercise.restSeconds }}s rest
              </span>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Action Buttons -->
    <div class="flex justify-between items-center pt-4">
      <BaseButton
        type="button"
        variant="outline"
        :disabled="isCreating"
        @click="emit('back')"
      >
        Back to Edit
      </BaseButton>
      <BaseButton
        type="button"
        variant="primary"
        :loading="isCreating"
        :disabled="!allExercisesMatched || isCreating"
        @click="emit('create')"
      >
        {{ isCreating ? 'Creating Plan...' : 'Create Workout Plan' }}
      </BaseButton>
    </div>
  </div>
</template>
