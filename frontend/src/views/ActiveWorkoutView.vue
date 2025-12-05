<script setup lang="ts">
/**
 * Active workout view.
 * Main workout tracking interface with exercise logging.
 * TODO: Implement full workout tracking.
 */
import { ref } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'

// Mock exercise data
const currentExercise = ref({
  name: 'Bench Press',
  targetSets: 3,
  targetReps: 10,
})

const completedSets = ref<Array<{ weight: number; reps: number }>>([])

const weight = ref('')
const reps = ref('')

const logSet = () => {
  if (weight.value && reps.value) {
    completedSets.value.push({
      weight: parseFloat(weight.value),
      reps: parseInt(reps.value),
    })
    weight.value = ''
    reps.value = ''
  }
}
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Current Exercise -->
    <BaseCard class="bg-gray-800 border-gray-700">
      <div class="text-center">
        <h2 class="text-xl font-bold text-white">{{ currentExercise.name }}</h2>
        <p class="text-gray-400 mt-1">
          Target: {{ currentExercise.targetSets }} sets x {{ currentExercise.targetReps }} reps
        </p>
      </div>
    </BaseCard>

    <!-- Set logging -->
    <BaseCard class="bg-gray-800 border-gray-700">
      <h3 class="text-lg font-semibold text-white mb-4">Log Set</h3>
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">Weight (kg)</label>
          <input
            v-model="weight"
            type="number"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-center text-lg"
            placeholder="0"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Reps</label>
          <input
            v-model="reps"
            type="number"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-center text-lg"
            placeholder="0"
          />
        </div>
      </div>
      <BaseButton variant="primary" class="w-full" @click="logSet">
        Log Set
      </BaseButton>
    </BaseCard>

    <!-- Completed sets -->
    <BaseCard class="bg-gray-800 border-gray-700">
      <h3 class="text-lg font-semibold text-white mb-4">
        Completed Sets ({{ completedSets.length }}/{{ currentExercise.targetSets }})
      </h3>
      <div v-if="completedSets.length === 0" class="text-center text-gray-500 py-4">
        No sets logged yet
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="(set, index) in completedSets"
          :key="index"
          class="flex items-center justify-between bg-gray-700 px-4 py-2 rounded-lg"
        >
          <span class="text-gray-400">Set {{ index + 1 }}</span>
          <span class="text-white font-medium">{{ set.weight }} kg x {{ set.reps }} reps</span>
        </div>
      </div>
    </BaseCard>

    <!-- Navigation placeholder -->
    <div class="flex gap-3">
      <BaseButton variant="outline" class="flex-1">Previous</BaseButton>
      <BaseButton variant="primary" class="flex-1">Next Exercise</BaseButton>
    </div>
  </div>
</template>
