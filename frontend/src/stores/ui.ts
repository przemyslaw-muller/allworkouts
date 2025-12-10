/**
 * UI store - manages global UI state like loading, notifications, and modals.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Notification types
export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: string
  type: NotificationType
  message: string
  duration?: number
  persistent?: boolean
}

// Modal types
export interface ModalState {
  isOpen: boolean
  component: string | null
  props: Record<string, unknown>
  onClose?: () => void
}

// Confirmation dialog
export interface ConfirmationState {
  isOpen: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  confirmVariant: 'primary' | 'danger'
  onConfirm: (() => void) | null
  onCancel: (() => void) | null
}

export const useUiStore = defineStore('ui', () => {
  // Global loading state
  const isLoading = ref(false)
  const loadingMessage = ref<string | null>(null)
  const loadingCount = ref(0)

  // Notifications
  const notifications = ref<Notification[]>([])
  let notificationIdCounter = 0

  // Modal state
  const modal = ref<ModalState>({
    isOpen: false,
    component: null,
    props: {},
  })

  // Confirmation dialog
  const confirmation = ref<ConfirmationState>({
    isOpen: false,
    title: '',
    message: '',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    confirmVariant: 'primary',
    onConfirm: null,
    onCancel: null,
  })

  // Sidebar state (for mobile)
  const isSidebarOpen = ref(false)

  // Theme
  const isDarkMode = ref(false)

  // Initialize dark mode from localStorage or system preference
  function initDarkMode() {
    const stored = localStorage.getItem('darkMode')
    if (stored !== null) {
      isDarkMode.value = stored === 'true'
    } else {
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyDarkMode()
  }

  // Apply dark mode class to document
  function applyDarkMode() {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // Getters
  const hasNotifications = computed(() => notifications.value.length > 0)
  const latestNotification = computed(
    () => notifications.value[notifications.value.length - 1] ?? null,
  )

  // Loading actions
  function startLoading(message?: string) {
    loadingCount.value++
    isLoading.value = true
    if (message) {
      loadingMessage.value = message
    }
  }

  function stopLoading() {
    loadingCount.value = Math.max(0, loadingCount.value - 1)
    if (loadingCount.value === 0) {
      isLoading.value = false
      loadingMessage.value = null
    }
  }

  function forceStopLoading() {
    loadingCount.value = 0
    isLoading.value = false
    loadingMessage.value = null
  }

  // Notification actions
  function notify(
    type: NotificationType,
    message: string,
    options?: { duration?: number; persistent?: boolean },
  ) {
    const id = `notification-${++notificationIdCounter}`
    const notification: Notification = {
      id,
      type,
      message,
      duration: options?.duration ?? 5000,
      persistent: options?.persistent ?? false,
    }

    notifications.value.push(notification)

    // Auto-remove non-persistent notifications
    if (!notification.persistent && notification.duration) {
      setTimeout(() => {
        removeNotification(id)
      }, notification.duration)
    }

    return id
  }

  function success(message: string, options?: { duration?: number; persistent?: boolean }) {
    return notify('success', message, options)
  }

  function error(message: string, options?: { duration?: number; persistent?: boolean }) {
    return notify('error', message, { duration: 7000, ...options })
  }

  function warning(message: string, options?: { duration?: number; persistent?: boolean }) {
    return notify('warning', message, options)
  }

  function info(message: string, options?: { duration?: number; persistent?: boolean }) {
    return notify('info', message, options)
  }

  function removeNotification(id: string) {
    notifications.value = notifications.value.filter((n) => n.id !== id)
  }

  function clearAllNotifications() {
    notifications.value = []
  }

  // Modal actions
  function openModal(component: string, props: Record<string, unknown> = {}, onClose?: () => void) {
    modal.value = {
      isOpen: true,
      component,
      props,
      onClose,
    }
  }

  function closeModal() {
    if (modal.value.onClose) {
      modal.value.onClose()
    }
    modal.value = {
      isOpen: false,
      component: null,
      props: {},
    }
  }

  // Confirmation dialog actions
  function confirm(options: {
    title: string
    message: string
    confirmText?: string
    cancelText?: string
    confirmVariant?: 'primary' | 'danger'
  }): Promise<boolean> {
    return new Promise((resolve) => {
      confirmation.value = {
        isOpen: true,
        title: options.title,
        message: options.message,
        confirmText: options.confirmText ?? 'Confirm',
        cancelText: options.cancelText ?? 'Cancel',
        confirmVariant: options.confirmVariant ?? 'primary',
        onConfirm: () => {
          closeConfirmation()
          resolve(true)
        },
        onCancel: () => {
          closeConfirmation()
          resolve(false)
        },
      }
    })
  }

  function closeConfirmation() {
    confirmation.value = {
      isOpen: false,
      title: '',
      message: '',
      confirmText: 'Confirm',
      cancelText: 'Cancel',
      confirmVariant: 'primary',
      onConfirm: null,
      onCancel: null,
    }
  }

  // Sidebar actions
  function toggleSidebar() {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  function openSidebar() {
    isSidebarOpen.value = true
  }

  function closeSidebar() {
    isSidebarOpen.value = false
  }

  // Theme actions
  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('darkMode', String(isDarkMode.value))
    applyDarkMode()
  }

  function setDarkMode(value: boolean) {
    isDarkMode.value = value
    localStorage.setItem('darkMode', String(value))
    applyDarkMode()
  }

  // Initialize on store creation
  initDarkMode()

  return {
    // Loading state
    isLoading,
    loadingMessage,
    // Notifications
    notifications,
    hasNotifications,
    latestNotification,
    // Modal
    modal,
    // Confirmation
    confirmation,
    // Sidebar
    isSidebarOpen,
    // Theme
    isDarkMode,
    // Loading actions
    startLoading,
    stopLoading,
    forceStopLoading,
    // Notification actions
    notify,
    success,
    error,
    warning,
    info,
    removeNotification,
    clearAllNotifications,
    // Modal actions
    openModal,
    closeModal,
    // Confirmation actions
    confirm,
    closeConfirmation,
    // Sidebar actions
    toggleSidebar,
    openSidebar,
    closeSidebar,
    // Theme actions
    initDarkMode,
    toggleDarkMode,
    setDarkMode,
  }
})
