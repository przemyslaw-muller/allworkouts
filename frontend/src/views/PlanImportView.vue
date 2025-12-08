<script setup lang="ts">
/**
 * Plan import wizard view.
 * Allows importing workout plans from text/JSON.
 * TODO: Implement full import wizard.
 */
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'

const router = useRouter()

const importText = ref('')
const isLoading = ref(false)

const handleImport = async () => {
  if (!importText.value.trim()) return

  isLoading.value = true
  // TODO: Parse and import plan via API
  await new Promise(resolve => setTimeout(resolve, 1000))
  router.push('/plans')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <RouterLink to="/plans" class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-1 inline-block">
        &larr; Back to Plans
      </RouterLink>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Import Workout Plan</h1>
      <p class="text-gray-600 dark:text-gray-400">Paste your workout plan below to import it.</p>
    </div>

    <BaseCard>
      <div class="space-y-4">
        <BaseTextarea
          v-model="importText"
          label="Workout Plan Data"
          placeholder="Paste your workout plan here (text or JSON format)..."
          :rows="10"
        />

        <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Supported Formats</h3>
          <ul class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>- Plain text with exercise names and sets/reps</li>
            <li>- JSON format from AllWorkouts export</li>
            <li>- Common workout app export formats</li>
          </ul>
        </div>

        <div class="flex justify-end gap-3">
          <RouterLink to="/plans" class="btn btn-md btn-ghost">
            Cancel
          </RouterLink>
          <BaseButton
            variant="primary"
            :loading="isLoading"
            :disabled="!importText.trim()"
            @click="handleImport"
          >
            Import Plan
          </BaseButton>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
