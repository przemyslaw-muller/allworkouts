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
import type { ParsedExerciseViewModel, ParsedWorkoutViewModel } from '@/types'

interface Props {
  planName: string
  planDescription: string | null
  workouts: ParsedWorkoutViewModel[]
  isCreating: boolean
  createError: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'create'): void
  (e: 'back'): void
}>()

const allExercises = computed(() => {
  return props.workouts.flatMap(w => w.exercises)
})

const totalExercises = computed(() => {
  return allExercises.value.length
})

const totalSets = computed(() => {
  return allExercises.value.reduce((sum, ex) => sum + ex.setConfigurations.length, 0)
})

const muscleGroupsSummary = computed(() => {
  const groups = new Set<string>()
  allExercises.value.forEach((ex) => {
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
  return allExercises.value.every((ex) => ex.matchedExercise !== null)
})

const formatSetsReps = (exercise: ParsedExerciseViewModel) => {
  const configs = exercise.setConfigurations
  if (configs.length === 0) return '0 sets'
  
  // Check if all sets have the same rep range
  const firstSet = configs[0]
  const allSame = configs.every(
    (s) => s.reps_min === firstSet.reps_min && s.reps_max === firstSet.reps_max
  )
  
  if (allSame) {
    const reps = firstSet.reps_min === firstSet.reps_max 
      ? `${firstSet.reps_min}`
      : `${firstSet.reps_min}-${firstSet.reps_max}`
    return `${configs.length} × ${reps}`
  }
  
  // Show individual set details
  return configs
    .map((s, i) => {
      const reps = s.reps_min === s.reps_max ? `${s.reps_min}` : `${s.reps_min}-${s.reps_max}`
      return `S${i + 1}: ${reps}`
    })
    .join(', ')
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
        Some exercises are not matched. Please go back and fix all unmatched exercises before
        creating the plan.
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

        <div
          class="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y border-gray-200 dark:border-gray-700"
        >
          <div>
            <p class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
              {{ workouts.length }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Workout{{ workouts.length !== 1 ? 's' : '' }}
            </p>
          </div>
          <div>
            <p class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
              {{ totalExercises }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Exercise{{ totalExercises !== 1 ? 's' : '' }}
            </p>
          </div>
          <div>
            <p class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{{ totalSets }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">Total Sets</p>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">Muscle Groups</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ muscleGroupsSummary || 'None' }}
            </p>
          </div>
        </div>
      </div>
    </BaseCard>

    <!-- Workout Summary List -->
    <div class="space-y-4">
      <BaseCard v-for="workout in workouts" :key="workout.id">
        <div class="mb-4">
          <h4 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ workout.name }}
          </h4>
          <p v-if="workout.dayNumber" class="text-sm text-gray-500 dark:text-gray-400">
            Day {{ workout.dayNumber }}
          </p>
        </div>

        <div class="divide-y divide-gray-200 dark:divide-gray-700">
          <div
            v-for="(exercise, index) in workout.exercises"
            :key="exercise.id"
            class="py-3 first:pt-0 last:pb-0"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex items-start gap-3">
                <span
                  class="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-sm font-medium text-gray-600 dark:text-gray-400"
                >
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
                    {{
                      exercise.matchedExercise?.primary_muscle_groups
                        .map((mg) => mg.charAt(0).toUpperCase() + mg.slice(1))
                        .join(', ')
                    }}
                  </p>
                </div>
              </div>
              <div class="text-right text-sm text-gray-600 dark:text-gray-400 flex-shrink-0">
                <span class="font-medium">{{ formatSetsReps(exercise) }}</span>
                <span v-if="exercise.restSeconds" class="block text-xs text-gray-400">
                  {{ exercise.restSeconds }}s rest
                </span>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-between items-center pt-4">
      <BaseButton type="button" variant="outline" :disabled="isCreating" @click="emit('back')">
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
