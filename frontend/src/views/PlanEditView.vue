<script setup lang="ts">
/**
 * Plan create/edit view.
 * Form to create or modify workout plans.
 * TODO: Implement full form with exercise selection.
 */
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'

const route = useRoute()
const router = useRouter()

const planId = route.params.id as string | undefined
const isEditing = computed(() => !!planId)
const pageTitle = computed(() => isEditing.value ? 'Edit Plan' : 'Create Plan')

// Form state
const planName = ref('')
const description = ref('')

const handleSave = () => {
  // TODO: Save plan via API
  router.push('/plans')
}

const handleCancel = () => {
  router.back()
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <RouterLink to="/plans" class="text-sm text-gray-500 hover:text-gray-700 mb-1 inline-block">
        &larr; Back to Plans
      </RouterLink>
      <h1 class="text-2xl font-bold text-gray-900">{{ pageTitle }}</h1>
    </div>

    <!-- Form -->
    <BaseCard>
      <form @submit.prevent="handleSave" class="space-y-4">
        <BaseInput
          v-model="planName"
          label="Plan Name"
          placeholder="e.g., Push Day, Full Body Workout"
          required
        />

        <BaseTextarea
          v-model="description"
          label="Description"
          placeholder="Describe your workout plan..."
          :rows="3"
        />

        <!-- Exercises section placeholder -->
        <div class="border-t pt-4 mt-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Exercises</h3>
          <p class="text-gray-500 text-center py-8">
            Exercise selection will be implemented here.
          </p>
          <BaseButton type="button" variant="outline" class="w-full">
            + Add Exercise
          </BaseButton>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-4 border-t">
          <BaseButton type="button" variant="ghost" @click="handleCancel">
            Cancel
          </BaseButton>
          <BaseButton type="submit" variant="primary">
            {{ isEditing ? 'Save Changes' : 'Create Plan' }}
          </BaseButton>
        </div>
      </form>
    </BaseCard>
  </div>
</template>
