<script setup lang="ts">
/**
 * Floating rest timer component for workout sessions.
 * Displays countdown with progress ring and controls.
 */
import { ref, computed, watch, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'

interface Props {
  initialSeconds: number
  autoStart?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoStart: true,
})

const emit = defineEmits<{
  complete: []
  skip: []
}>()

const remainingSeconds = ref(props.initialSeconds)
const isRunning = ref(props.autoStart)
const intervalId = ref<number | null>(null)
const audioEnabled = ref(true)

// Format time as MM:SS
const formattedTime = computed(() => {
  const minutes = Math.floor(remainingSeconds.value / 60)
  const seconds = remainingSeconds.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

// Progress percentage for ring
const progressPercentage = computed(() => {
  return ((props.initialSeconds - remainingSeconds.value) / props.initialSeconds) * 100
})

// Start timer
function startTimer() {
  if (intervalId.value) return
  isRunning.value = true
  
  intervalId.value = window.setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
      
      // Play sound on last 3 seconds if audio enabled
      if (audioEnabled.value && remainingSeconds.value <= 3 && remainingSeconds.value > 0) {
        playBeep()
      }
      
      // Complete when time is up
      if (remainingSeconds.value === 0) {
        stopTimer()
        if (audioEnabled.value) {
          playCompletionSound()
        }
        emit('complete')
      }
    }
  }, 1000)
}

// Stop timer
function stopTimer() {
  if (intervalId.value) {
    clearInterval(intervalId.value)
    intervalId.value = null
  }
  isRunning.value = false
}

// Add 30 seconds
function add30Seconds() {
  remainingSeconds.value += 30
}

// Skip rest
function skipRest() {
  stopTimer()
  emit('skip')
}

// Toggle audio
function toggleAudio() {
  audioEnabled.value = !audioEnabled.value
}

// Play beep sound (placeholder - would use Web Audio API in production)
function playBeep() {
  // In production, use AudioContext to play a short beep
  // For now, this is a placeholder
}

// Play completion sound (placeholder)
function playCompletionSound() {
  // In production, use AudioContext to play completion sound
}

// Auto-start on mount if enabled
watch(() => props.autoStart, (autoStart) => {
  if (autoStart && !intervalId.value) {
    startTimer()
  }
}, { immediate: true })

// Cleanup on unmount
onUnmounted(() => {
  stopTimer()
})

defineExpose({
  startTimer,
  stopTimer,
  add30Seconds,
})
</script>

<template>
  <div class="fixed bottom-24 right-4 z-50 bg-gray-800 border-2 border-primary-500 rounded-lg shadow-2xl p-4 min-w-[200px]">
    <!-- Progress Ring -->
    <div class="flex justify-center mb-3">
      <div class="relative w-32 h-32">
        <!-- Background circle -->
        <svg class="w-32 h-32 transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="58"
            stroke="currentColor"
            stroke-width="8"
            fill="none"
            class="text-gray-700"
          />
          <!-- Progress circle -->
          <circle
            cx="64"
            cy="64"
            r="58"
            stroke="currentColor"
            stroke-width="8"
            fill="none"
            class="text-primary-500 transition-all duration-1000 ease-linear"
            :stroke-dasharray="364.42"
            :stroke-dashoffset="364.42 * (1 - progressPercentage / 100)"
            stroke-linecap="round"
          />
        </svg>
        <!-- Time display -->
        <div class="absolute inset-0 flex items-center justify-center">
          <span class="text-3xl font-bold text-white">{{ formattedTime }}</span>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex gap-2 mb-2">
      <BaseButton
        variant="outline"
        size="sm"
        class="flex-1"
        @click="add30Seconds"
        aria-label="Add 30 seconds"
      >
        +30s
      </BaseButton>
      <BaseButton
        variant="outline"
        size="sm"
        class="flex-1"
        @click="skipRest"
      >
        Skip
      </BaseButton>
    </div>

    <!-- Audio toggle -->
    <button
      type="button"
      class="w-full flex items-center justify-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
      @click="toggleAudio"
      :aria-label="audioEnabled ? 'Disable audio' : 'Enable audio'"
    >
      <svg
        v-if="audioEnabled"
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
        />
      </svg>
      <svg
        v-else
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
        />
      </svg>
      <span>{{ audioEnabled ? 'Audio On' : 'Audio Off' }}</span>
    </button>
  </div>
</template>
