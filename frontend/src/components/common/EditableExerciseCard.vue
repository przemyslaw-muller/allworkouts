<script setup lang="ts">
/**
 * Editable exercise card component for plan editing.
 * Shows exercise info and inline editing for sets, reps, rest time.
 */
import { computed } from 'vue'
import BaseInput from './BaseInput.vue'
import BaseButton from './BaseButton.vue'
import type { EditableExercise, ExerciseFieldErrors } from '@/types'

interface Props {
  exercise: EditableExercise
  canRemove: boolean
  errors?: ExerciseFieldErrors
  canReorder?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canReorder: true,
})

const emit = defineEmits<{
  'on-update-field': [field: keyof EditableExercise, value: any]
  'on-substitute': []
  'on-remove': []
  'on-move-up': []
  'on-move-down': []
}>()

const muscleGroupDisplay = computed(() => {
  return props.exercise.primaryMuscleGroups
    .map((mg) => mg.charAt(0).toUpperCase() + mg.slice(1))
    .join(', ')
})
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-4 space-y-4">
    <!-- Exercise Header -->
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <h3 class="text-lg font-medium text-gray-900">{{ exercise.exerciseName }}</h3>
          <span
            v-if="exercise.isNew"
            class="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800"
          >
            New
          </span>
          <span
            v-else-if="exercise.isModified"
            class="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800"
          >
            Modified
          </span>
        </div>
        <p class="text-sm text-gray-500 mt-1">{{ muscleGroupDisplay }}</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2">
        <BaseButton
          v-if="canReorder"
          type="button"
          variant="ghost"
          size="sm"
          @click="emit('on-move-up')"
          title="Move up"
        >
          ↑
        </BaseButton>
        <BaseButton
          v-if="canReorder"
          type="button"
          variant="ghost"
          size="sm"
          @click="emit('on-move-down')"
          title="Move down"
        >
          ↓
        </BaseButton>
        <BaseButton
          type="button"
          variant="outline"
          size="sm"
          @click="emit('on-substitute')"
        >
          Substitute
        </BaseButton>
        <BaseButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="!canRemove"
          @click="emit('on-remove')"
          class="text-red-600 hover:text-red-700 hover:bg-red-50 disabled:opacity-50"
          title="Remove exercise"
        >
          Remove
        </BaseButton>
      </div>
    </div>

    <!-- Exercise Parameters -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Sets -->
      <div>
        <BaseInput
          :model-value="exercise.sets"
          label="Sets"
          type="number"
          min="1"
          max="50"
          required
          :error="errors?.sets"
          @update:model-value="emit('on-update-field', 'sets', Number($event))"
        />
      </div>

      <!-- Reps Min -->
      <div>
        <BaseInput
          :model-value="exercise.repsMin"
          label="Min Reps"
          type="number"
          min="1"
          max="200"
          required
          :error="errors?.repsMin"
          @update:model-value="emit('on-update-field', 'repsMin', Number($event))"
        />
      </div>

      <!-- Reps Max -->
      <div>
        <BaseInput
          :model-value="exercise.repsMax"
          label="Max Reps"
          type="number"
          min="1"
          max="200"
          required
          :error="errors?.repsMax"
          @update:model-value="emit('on-update-field', 'repsMax', Number($event))"
        />
      </div>

      <!-- Rest Time -->
      <div>
        <BaseInput
          :model-value="exercise.restTimeSeconds ?? ''"
          label="Rest (seconds)"
          type="number"
          min="0"
          max="3600"
          placeholder="60"
          :error="errors?.restTimeSeconds"
          @update:model-value="emit('on-update-field', 'restTimeSeconds', $event ? Number($event) : null)"
        />
      </div>
    </div>

    <!-- Equipment Display -->
    <div v-if="exercise.equipment.length > 0" class="flex items-center gap-2 text-sm text-gray-600">
      <span class="font-medium">Equipment:</span>
      <span>{{ exercise.equipment.map(e => e.name).join(', ') }}</span>
    </div>
  </div>
</template>
