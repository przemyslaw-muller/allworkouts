/**
 * Barrel export for all Pinia stores.
 */
export { useAuthStore } from './auth'
export { useProfileStore } from './profile'
export { useWorkoutStore, type LoggedExercise } from './workout'
export {
  useUiStore,
  type Notification,
  type NotificationType,
  type ModalState,
  type ConfirmationState,
} from './ui'
