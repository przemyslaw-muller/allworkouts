<script setup lang="ts">
/**
 * Step 2 of the import wizard - Review parsed exercises.
 * User can fix exercise matches, edit parameters, add/remove exercises.
 */
import { ref, computed } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseAlert from '@/components/common/BaseAlert.vue'
import AddExerciseModal from '@/components/common/AddExerciseModal.vue'
import ParsedExerciseCard from './ParsedExerciseCard.vue'
import type { ParsedExerciseViewModel, ParseStats, ExerciseListItem } from '@/types'

interface Props {
  planName: string
  planDescription: string | null
  exercises: ParsedExerciseViewModel[]
  parseStats: ParseStats | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:planName', value: string): void
  (e: 'update:planDescription', value: string | null): void
  (e: 'updateExercise', exerciseId: string, updates: Partial<ParsedExerciseViewModel>): void
  (e: 'selectAlternative', exerciseId: string, alternativeIndex: number): void
  (e: 'replaceExercise', exerciseId: string, newExercise: ExerciseListItem): void
  (e: 'removeExercise', exerciseId: string): void
  (e: 'addExercise', exercise: ExerciseListItem): void
  (e: 'reorderExercises', fromIndex: number, toIndex: number): void
}>()

const showAddModal = ref(false)
const exerciseToReplace = ref<string | null>(null)

const hasWarnings = computed(() => {
  return props.exercises.some(
    (ex) => !ex.matchedExercise || ex.confidenceLevel === 'low',
  )
})

const unmatchedCount = computed(() => {
  return props.exercises.filter((ex) => !ex.matchedExercise).length
})

const lowConfidenceCount = computed(() => {
  return props.exercises.filter(
    (ex) => ex.matchedExercise && ex.confidenceLevel === 'low',
  ).length
})

const existingExerciseIds = computed(() => {
  return props.exercises
    .filter((ex) => ex.matchedExercise)
    .map((ex) => ex.matchedExercise!.exercise_id)
})

const handleUpdateExercise = (exerciseId: string, updates: Partial<ParsedExerciseViewModel>) => {
  emit('updateExercise', exerciseId, updates)
}

const handleSelectAlternative = (exerciseId: string, alternativeIndex: number) => {
  emit('selectAlternative', exerciseId, alternativeIndex)
}

const handleFixMatch = (exerciseId: string) => {
  exerciseToReplace.value = exerciseId
  showAddModal.value = true
}

const handleRemoveExercise = (exerciseId: string) => {
  emit('removeExercise', exerciseId)
}

const handleMoveUp = (index: number) => {
  if (index > 0) {
    emit('reorderExercises', index, index - 1)
  }
}

const handleMoveDown = (index: number) => {
  if (index < props.exercises.length - 1) {
    emit('reorderExercises', index, index + 1)
  }
}

const handleAddExercise = () => {
  exerciseToReplace.value = null
  showAddModal.value = true
}

const handleSelectExercise = (exercise: ExerciseListItem) => {
  if (exerciseToReplace.value) {
    emit('replaceExercise', exerciseToReplace.value, exercise)
  } else {
    emit('addExercise', exercise)
  }
  showAddModal.value = false
  exerciseToReplace.value = null
}
</script>

<template>
  <div class="space-y-6">
    <!-- Parse Summary -->
    <BaseCard v-if="parseStats">
      <div class="flex flex-wrap items-center gap-4 text-sm">
        <span class="font-medium text-gray-900 dark:text-gray-100">
          Parsed {{ parseStats.total }} exercise{{ parseStats.total !== 1 ? 's' : '' }}:
        </span>
        <span v-if="parseStats.highConfidence > 0" class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-green-500" />
          <span class="text-gray-600 dark:text-gray-400">{{ parseStats.highConfidence }} high confidence</span>
        </span>
        <span v-if="parseStats.mediumConfidence > 0" class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-yellow-500" />
          <span class="text-gray-600 dark:text-gray-400">{{ parseStats.mediumConfidence }} medium</span>
        </span>
        <span v-if="parseStats.lowConfidence > 0" class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-red-500" />
          <span class="text-gray-600 dark:text-gray-400">{{ parseStats.lowConfidence }} low</span>
        </span>
        <span v-if="parseStats.unmatched > 0" class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-gray-400" />
          <span class="text-gray-600 dark:text-gray-400">{{ parseStats.unmatched }} unmatched</span>
        </span>
      </div>
    </BaseCard>

    <!-- Warning Alert -->
    <BaseAlert v-if="hasWarnings" variant="warning">
      <template #title>Review Required</template>
      <template #default>
        <span v-if="unmatchedCount > 0">
          {{ unmatchedCount }} exercise{{ unmatchedCount !== 1 ? 's' : '' }} could not be matched.
        </span>
        <span v-if="unmatchedCount > 0 && lowConfidenceCount > 0"> Also, </span>
        <span v-if="lowConfidenceCount > 0">
          {{ lowConfidenceCount }} exercise{{ lowConfidenceCount !== 1 ? 's have' : ' has' }} low confidence matches.
        </span>
        Please review and fix before continuing.
      </template>
    </BaseAlert>

    <!-- Plan Name & Description -->
    <BaseCard>
      <div class="space-y-4">
        <BaseInput
          :model-value="planName"
          label="Plan Name"
          placeholder="Enter a name for this workout plan"
          required
          @update:model-value="emit('update:planName', String($event))"
        />
        <BaseTextarea
          :model-value="planDescription ?? ''"
          label="Description (optional)"
          placeholder="Add a description for this plan..."
          :rows="2"
          @update:model-value="emit('update:planDescription', $event || null)"
        />
      </div>
    </BaseCard>

    <!-- Exercise List -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Exercises ({{ exercises.length }})
        </h3>
        <BaseButton
          type="button"
          variant="outline"
          size="sm"
          @click="handleAddExercise"
        >
          + Add Exercise
        </BaseButton>
      </div>

      <!-- Empty state -->
      <div
        v-if="exercises.length === 0"
        class="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600"
      >
        <p class="text-gray-500 dark:text-gray-400">
          No exercises parsed. Add exercises manually using the button above.
        </p>
      </div>

      <!-- Exercise cards -->
      <TransitionGroup
        v-else
        name="list"
        tag="div"
        class="space-y-4"
      >
        <ParsedExerciseCard
          v-for="(exercise, index) in exercises"
          :key="exercise.id"
          :exercise="exercise"
          :index="index"
          :can-remove="exercises.length > 1"
          @update="handleUpdateExercise(exercise.id, $event)"
          @fix-match="handleFixMatch(exercise.id)"
          @select-alternative="handleSelectAlternative(exercise.id, $event)"
          @remove="handleRemoveExercise(exercise.id)"
          @move-up="handleMoveUp(index)"
          @move-down="handleMoveDown(index)"
        />
      </TransitionGroup>
    </div>

    <!-- Add Exercise Modal -->
    <AddExerciseModal
      v-model="showAddModal"
      :existing-exercise-ids="existingExerciseIds"
      @on-select="handleSelectExercise"
    />
  </div>
</template>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.list-leave-active {
  position: absolute;
}
</style>
