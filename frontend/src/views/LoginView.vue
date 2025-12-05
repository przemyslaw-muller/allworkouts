<script setup lang="ts">
/**
 * Login page view.
 * TODO: Implement full login form with validation.
 */
import { ref } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  error.value = ''
  isLoading.value = true

  try {
    const result = await authStore.login({ email: email.value, password: password.value })
    if (result.success) {
      const redirect = route.query.redirect as string || '/'
      router.push(redirect)
    } else {
      error.value = result.error || 'Login failed'
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Login failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-6">Sign in to your account</h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div v-if="error" class="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
        {{ error }}
      </div>

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
        placeholder="Enter your password"
        required
      />

      <BaseButton
        type="submit"
        variant="primary"
        :loading="isLoading"
        class="w-full"
      >
        Sign in
      </BaseButton>
    </form>

    <p class="mt-6 text-center text-sm text-gray-600">
      Don't have an account?
      <RouterLink to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
        Sign up
      </RouterLink>
    </p>
  </div>
</template>
