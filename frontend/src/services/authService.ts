/**
 * Authentication service for login, register, logout, and token management.
 */
import api, { tokenStorage } from './api'
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  RefreshResponse,
  User,
  UserUpdateRequest,
} from '@/types'

export const authService = {
  /**
   * Login with email and password.
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials)
    const data = response.data
    tokenStorage.setTokens(data.access_token, data.refresh_token)
    return data
  },

  /**
   * Register a new user.
   */
  async register(credentials: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', credentials)
    const data = response.data
    tokenStorage.setTokens(data.access_token, data.refresh_token)
    return data
  },

  /**
   * Refresh the access token.
   */
  async refresh(): Promise<RefreshResponse> {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }
    const response = await api.post<RefreshResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    tokenStorage.setAccessToken(response.data.access_token)
    return response.data
  },

  /**
   * Logout the current user.
   */
  logout(): void {
    tokenStorage.clearTokens()
  },

  /**
   * Get the current user's profile.
   */
  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  /**
   * Update the current user's profile.
   */
  async updateMe(data: UserUpdateRequest): Promise<User> {
    const response = await api.patch<User>('/auth/me', data)
    return response.data
  },

  /**
   * Delete the current user's account.
   */
  async deleteAccount(): Promise<void> {
    await api.delete('/auth/me')
    tokenStorage.clearTokens()
  },

  /**
   * Check if user is authenticated.
   */
  isAuthenticated(): boolean {
    return tokenStorage.hasTokens()
  },
}
