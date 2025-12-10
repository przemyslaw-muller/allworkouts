<script setup lang="ts">
/**
 * Step 1 of the import wizard - Text input pane.
 * User pastes or types their workout plan text here.
 */
import { ref, computed } from 'vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'

interface Props {
  modelValue: string
  error?: string | null
  isParsing?: boolean
  canParse?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  error: null,
  isParsing: false,
  canParse: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'parse'): void
}>()

const showExamples = ref(false)

const charCount = computed(() => props.modelValue.length)

const charCountClass = computed(() => {
  if (charCount.value < 10) return 'text-gray-400 dark:text-gray-500'
  if (charCount.value > 45000) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-green-600 dark:text-green-400'
})

const handleInput = (value: string) => {
  emit('update:modelValue', value)
}

const toggleExamples = () => {
  showExamples.value = !showExamples.value
}
</script>

<template>
  <div class="space-y-6">
    <!-- Instructions -->
    <BaseCard>
      <div class="space-y-4">
        <div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
            Paste Your Workout Plan
          </h3>
          <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Copy and paste your workout plan from any source - a website, PDF, notes app, or even
            just typed text. Our AI will parse it and match exercises from our database.
          </p>
        </div>

        <!-- Text input -->
        <div>
          <BaseTextarea
            :model-value="modelValue"
            placeholder="Example:
Day 1 - Push
Bench Press 4x8-12
Overhead Press 3x10
Dips 3x12-15

Day 2 - Pull
Pull-ups 4x8-10
Barbell Rows 4x10
Face Pulls 3x15..."
            :rows="12"
            :maxlength="50000"
            :error="error || undefined"
            @update:model-value="handleInput"
          />
          <div class="mt-1 flex justify-between text-xs">
            <span :class="charCountClass">
              {{ charCount.toLocaleString() }} / 50,000 characters
            </span>
            <span v-if="charCount < 10" class="text-gray-500 dark:text-gray-400">
              Minimum 10 characters required
            </span>
          </div>
        </div>

        <!-- Parse button -->
        <div class="flex justify-end">
          <BaseButton
            variant="primary"
            :loading="isParsing"
            :disabled="!canParse"
            @click="emit('parse')"
          >
            {{ isParsing ? 'Analyzing...' : 'Parse Workout Plan' }}
          </BaseButton>
        </div>
      </div>
    </BaseCard>

    <!-- Example formats (collapsible) -->
    <BaseCard>
      <button
        type="button"
        class="flex w-full items-center justify-between text-left"
        @click="toggleExamples"
      >
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          Supported Formats
        </span>
        <svg
          :class="['h-5 w-5 text-gray-500 transition-transform', showExamples ? 'rotate-180' : '']"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      <div v-if="showExamples" class="mt-4 space-y-4">
        <div>
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">Simple List</h4>
          <pre
            class="mt-1 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-x-auto"
          >
Bench Press 4x8-12
Overhead Press 3x10
Dips 3x12</pre
          >
        </div>

        <div>
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">With Day Labels</h4>
          <pre
            class="mt-1 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-x-auto"
          >
Day 1 - Push
- Bench Press: 4 sets, 8-12 reps
- Shoulder Press: 3 sets, 10 reps
- Tricep Dips: 3 sets, 12 reps</pre
          >
        </div>

        <div>
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">Detailed Format</h4>
          <pre
            class="mt-1 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-x-auto"
          >
1. Barbell Bench Press
   4 sets x 8-12 reps, 90 seconds rest
2. Dumbbell Shoulder Press
   3 sets x 10 reps, 60 seconds rest</pre
          >
        </div>

        <div>
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">Compact</h4>
          <pre
            class="mt-1 text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-x-auto"
          >
BP 4x8, OHP 3x10, Dips 3x12</pre
          >
        </div>

        <p class="text-xs text-gray-500 dark:text-gray-400">
          Don't worry about the exact format - our AI is flexible and can understand most workout
          plan formats.
        </p>
      </div>
    </BaseCard>
  </div>
</template>
