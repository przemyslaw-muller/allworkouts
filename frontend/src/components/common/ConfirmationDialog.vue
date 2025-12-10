<script setup lang="ts">
import { useUiStore } from '@/stores'
import BaseButton from './BaseButton.vue'

const uiStore = useUiStore()

function handleConfirm() {
  if (uiStore.confirmation.onConfirm) {
    uiStore.confirmation.onConfirm()
  }
}

function handleCancel() {
  if (uiStore.confirmation.onCancel) {
    uiStore.confirmation.onCancel()
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="uiStore.confirmation.isOpen"
        class="fixed inset-0 z-[80] flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50" @click="handleCancel" />

        <!-- Dialog -->
        <div
          class="relative w-full max-w-md bg-white rounded-lg shadow-xl animate-slide-up dark:bg-gray-800"
          role="alertdialog"
          aria-modal="true"
        >
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-2 dark:text-gray-100">
              {{ uiStore.confirmation.title }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              {{ uiStore.confirmation.message }}
            </p>
          </div>

          <div
            class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3 dark:border-gray-700"
          >
            <BaseButton variant="secondary" @click="handleCancel">
              {{ uiStore.confirmation.cancelText }}
            </BaseButton>
            <BaseButton :variant="uiStore.confirmation.confirmVariant" @click="handleConfirm">
              {{ uiStore.confirmation.confirmText }}
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
