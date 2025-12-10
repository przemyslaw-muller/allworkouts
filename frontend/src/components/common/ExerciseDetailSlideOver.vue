<script setup lang="ts">
/**
 * Slide-over panel for exercise details during workout.
 */
import { computed } from 'vue'
import type { ExerciseBrief, MuscleGroup } from '@/types'
import BaseModal from './BaseModal.vue'
import BaseBadge from './BaseBadge.vue'

interface Props {
  isOpen: boolean
  exercise: ExerciseBrief | null
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const muscleGroupLabel = computed(() => {
  const labels: Record<MuscleGroup, string> = {
    chest: 'Chest',
    back: 'Back',
    shoulders: 'Shoulders',
    biceps: 'Biceps',
    triceps: 'Triceps',
    forearms: 'Forearms',
    legs: 'Legs',
    glutes: 'Glutes',
    core: 'Core',
    traps: 'Traps',
    lats: 'Lats',
  }
  return (mg: MuscleGroup) => labels[mg] || mg
})
</script>

<template>
  <BaseModal :model-value="isOpen" size="sm" @close="emit('close')">
    <template #header>
      <h3 class="text-lg font-semibold text-white">
        {{ exercise?.name || 'Exercise Details' }}
      </h3>
    </template>

    <template #default>
      <div v-if="exercise" class="space-y-4">
        <!-- Primary Muscle Groups -->
        <div>
          <h4 class="text-sm font-medium text-gray-400 mb-2">Primary Muscles</h4>
          <div class="flex flex-wrap gap-2">
            <BaseBadge v-for="mg in exercise.primary_muscle_groups" :key="mg" variant="primary">
              {{ muscleGroupLabel(mg) }}
            </BaseBadge>
          </div>
        </div>

        <!-- Secondary Muscle Groups -->
        <div v-if="exercise.secondary_muscle_groups.length > 0">
          <h4 class="text-sm font-medium text-gray-400 mb-2">Secondary Muscles</h4>
          <div class="flex flex-wrap gap-2">
            <BaseBadge v-for="mg in exercise.secondary_muscle_groups" :key="mg" variant="gray">
              {{ muscleGroupLabel(mg) }}
            </BaseBadge>
          </div>
        </div>

        <!-- Placeholder for future features -->
        <div class="text-sm text-gray-500 italic">Exercise instructions and video coming soon</div>
      </div>
    </template>

    <template #footer>
      <button
        type="button"
        class="w-full px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
        @click="emit('close')"
      >
        Close
      </button>
    </template>
  </BaseModal>
</template>
