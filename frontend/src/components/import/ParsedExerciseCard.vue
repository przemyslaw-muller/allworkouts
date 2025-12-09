<script setup lang="ts">
/**
 * Parsed exercise card for the import wizard Step 2.
 * Shows parsed exercise with confidence indicator and ability to fix match.
 */
import { computed } from 'vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import ConfidenceBadge from './ConfidenceBadge.vue'
import type { ParsedExerciseViewModel } from '@/types'

interface Props {
  exercise: ParsedExerciseViewModel
  index: number
  canRemove: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update', updates: Partial<ParsedExerciseViewModel>): void
  (e: 'fixMatch'): void
  (e: 'selectAlternative', alternativeIndex: number): void
  (e: 'remove'): void
  (e: 'moveUp'): void
  (e: 'moveDown'): void
}>()

const muscleGroupDisplay = computed(() => {
  if (!props.exercise.matchedExercise) return ''
  return props.exercise.matchedExercise.primary_muscle_groups
    .map((mg) => mg.charAt(0).toUpperCase() + mg.slice(1))
    .join(', ')
})

const needsAttention = computed(() => {
  return !props.exercise.matchedExercise || props.exercise.confidenceLevel === 'low'
})

const showAlternatives = computed(() => {
  return props.exercise.alternativeMatches.length > 0 && needsAttention.value
})

const handleUpdateSets = (value: number) => {
  emit('update', { sets: value })
}

const handleUpdateRepsMin = (value: number) => {
  emit('update', { repsMin: value })
}

const handleUpdateRepsMax = (value: number) => {
  emit('update', { repsMax: value })
}

const handleUpdateRest = (value: number | null) => {
  emit('update', { restSeconds: value })
}
</script>

<template>
  <div
    :class="[
      'rounded-lg border p-4 space-y-4 transition-colors',
      needsAttention
        ? 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-700'
        : 'border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700',
    ]"
  >
    <!-- Header with original text and confidence -->
    <div class="flex items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <!-- Original parsed text -->
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-1 truncate">
          Parsed from: "{{ exercise.originalText }}"
        </p>

        <!-- Matched exercise name -->
        <div class="flex items-center gap-2 flex-wrap">
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
            {{ exercise.matchedExercise?.exercise_name || 'No Match Found' }}
          </h3>
          <ConfidenceBadge :level="exercise.confidenceLevel" />
          <span
            v-if="exercise.isManuallyAdded"
            class="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
          >
            Manually Added
          </span>
          <span
            v-else-if="exercise.isModified"
            class="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200"
          >
            Modified
          </span>
        </div>

        <!-- Muscle groups -->
        <p v-if="muscleGroupDisplay" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ muscleGroupDisplay }}
        </p>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <BaseButton
          type="button"
          variant="ghost"
          size="sm"
          title="Move up"
          @click="emit('moveUp')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
          </svg>
        </BaseButton>
        <BaseButton
          type="button"
          variant="ghost"
          size="sm"
          title="Move down"
          @click="emit('moveDown')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </BaseButton>
        <BaseButton
          type="button"
          variant="outline"
          size="sm"
          @click="emit('fixMatch')"
        >
          {{ exercise.matchedExercise ? 'Change' : 'Select' }} Exercise
        </BaseButton>
        <BaseButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="!canRemove"
          class="text-red-600 hover:text-red-700 hover:bg-red-50 disabled:opacity-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/50"
          title="Remove exercise"
          @click="emit('remove')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </BaseButton>
      </div>
    </div>

    <!-- Alternative matches (shown if low confidence or unmatched) -->
    <div v-if="showAlternatives" class="bg-white dark:bg-gray-800 rounded-md p-3 border border-gray-200 dark:border-gray-600">
      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Did you mean one of these?
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="(alt, altIndex) in exercise.alternativeMatches.slice(0, 3)"
          :key="alt.exercise_id"
          type="button"
          class="inline-flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-md text-gray-800 dark:text-gray-200 transition-colors"
          @click="emit('selectAlternative', altIndex)"
        >
          {{ alt.exercise_name }}
          <span class="text-xs text-gray-500 dark:text-gray-400">
            ({{ Math.round(alt.confidence * 100) }}%)
          </span>
        </button>
      </div>
    </div>

    <!-- Exercise parameters (only shown if exercise is matched) -->
    <div v-if="exercise.matchedExercise" class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div>
        <BaseInput
          :model-value="exercise.sets"
          label="Sets"
          type="number"
          min="1"
          max="50"
          required
          @update:model-value="handleUpdateSets(Number($event))"
        />
      </div>
      <div>
        <BaseInput
          :model-value="exercise.repsMin"
          label="Min Reps"
          type="number"
          min="1"
          max="200"
          required
          @update:model-value="handleUpdateRepsMin(Number($event))"
        />
      </div>
      <div>
        <BaseInput
          :model-value="exercise.repsMax"
          label="Max Reps"
          type="number"
          min="1"
          max="200"
          required
          @update:model-value="handleUpdateRepsMax(Number($event))"
        />
      </div>
      <div>
        <BaseInput
          :model-value="exercise.restSeconds ?? ''"
          label="Rest (sec)"
          type="number"
          min="0"
          max="3600"
          placeholder="60"
          @update:model-value="handleUpdateRest($event ? Number($event) : null)"
        />
      </div>
    </div>

    <!-- Notes if present -->
    <p v-if="exercise.notes" class="text-sm text-gray-600 dark:text-gray-400 italic">
      Note: {{ exercise.notes }}
    </p>
  </div>
</template>
