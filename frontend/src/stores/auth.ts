/**
 * Auth store - manages user authentication state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { authService } from '@/services'
import { tokenStorage, getErrorMessage } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isInitialized = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const userId = computed(() => user.value?.id ?? null)
  const userEmail = computed(() => user.value?.email ?? null)

  // Actions
  async function initialize() {
    if (isInitialized.value) return

    if (!tokenStorage.hasTokens()) {
      isInitialized.value = true
      return
    }

    try {
      isLoading.value = true
      error.value = null
      user.value = await authService.getMe()
    } catch (err) {
      // Token invalid, clear it
      tokenStorage.clearTokens()
      user.value = null
    } finally {
      isLoading.value = false
      isInitialized.value = true
    }
  }

  async function login(credentials: LoginRequest) {
    try {
      isLoading.value = true
      error.value = null
      await authService.login(credentials)
      // Tokens are already set by authService.login
      // Fetch full user profile
      user.value = await authService.getMe()
      return { success: true }
    } catch (err) {
      error.value = getErrorMessage(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  async function register(credentials: RegisterRequest) {
    try {
      isLoading.value = true
      error.value = null
      await authService.register(credentials)
      // Tokens are already set by authService.register
      // Fetch full user profile
      user.value = await authService.getMe()
      return { success: true }
    } catch (err) {
      error.value = getErrorMessage(err)
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    authService.logout()
    user.value = null
  }

  async function refreshUser() {
    try {
      user.value = await authService.getMe()
    } catch (err) {
      error.value = getErrorMessage(err)
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    user,
    isLoading,
    error,
    isInitialized,
    // Getters
    isAuthenticated,
    userId,
    userEmail,
    // Actions
    initialize,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  }
})
