<script setup lang="ts">
/**
 * Registration page view.
 */
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  error.value = ''

  // Validate name length
  if (name.value && name.value.length > 100) {
    error.value = 'Name must be 100 characters or less'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  isLoading.value = true

  try {
    const result = await authStore.register({
      email: email.value,
      password: password.value,
      name: name.value || undefined,
    })
    if (result.success) {
      router.push('/onboarding')
    } else {
      error.value = result.error || 'Registration failed'
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Registration failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Create your account</h2>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div
        v-if="error"
        class="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 rounded-md text-sm"
      >
        {{ error }}
      </div>

      <BaseInput
        v-model="name"
        type="text"
        label="Name"
        placeholder="Your name (optional)"
        maxlength="100"
      />

      <BaseInput
        v-model="email"
        type="email"
        label="Email address"
        placeholder="you@example.com"
        required
      />

      <BaseInput
        v-model="password"
        type="password"
        label="Password"
        placeholder="Create a password"
        required
      />

      <BaseInput
        v-model="confirmPassword"
        type="password"
        label="Confirm password"
        placeholder="Confirm your password"
        required
      />

      <BaseButton type="submit" variant="primary" :loading="isLoading" class="w-full">
        Create account
      </BaseButton>
    </form>

    <p class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
      Already have an account?
      <RouterLink
        to="/login"
        class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
      >
        Sign in
      </RouterLink>
    </p>
  </div>
</template>
