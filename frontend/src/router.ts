/**
 * Vue Router configuration with all application routes.
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

// Lazy-loaded views for code splitting
const LoginView = () => import('@/views/LoginView.vue')
const RegisterView = () => import('@/views/RegisterView.vue')
const DashboardView = () => import('@/views/DashboardView.vue')
const OnboardingView = () => import('@/views/OnboardingView.vue')
const PlansListView = () => import('@/views/PlansListView.vue')
const PlanDetailView = () => import('@/views/PlanDetailView.vue')
const PlanEditView = () => import('@/views/PlanEditView.vue')
const PlanImportView = () => import('@/views/PlanImportView.vue')
const ActiveWorkoutView = () => import('@/views/ActiveWorkoutView.vue')
const WorkoutCompleteView = () => import('@/views/WorkoutCompleteView.vue')
const HistoryListView = () => import('@/views/HistoryListView.vue')
const SessionDetailView = () => import('@/views/SessionDetailView.vue')
const StatsView = () => import('@/views/StatsView.vue')
const ProfileView = () => import('@/views/ProfileView.vue')
const NotFoundView = () => import('@/views/NotFoundView.vue')

// Route definitions
const routes: RouteRecordRaw[] = [
  // Auth routes (public)
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false, layout: 'auth' },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false, layout: 'auth' },
  },

  // Onboarding (requires auth, first-time users)
  {
    path: '/onboarding',
    name: 'onboarding',
    component: OnboardingView,
    meta: { requiresAuth: true, layout: 'minimal' },
  },

  // Main app routes (requires auth)
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, layout: 'main' },
  },

  // Workout Plans
  {
    path: '/plans',
    name: 'plans',
    component: PlansListView,
    meta: { requiresAuth: true, layout: 'main' },
  },
  {
    path: '/plans/new',
    name: 'plan-create',
    component: PlanEditView,
    meta: { requiresAuth: true, layout: 'main' },
  },
  {
    path: '/plans/import',
    name: 'plan-import',
    component: PlanImportView,
    meta: { requiresAuth: true, layout: 'main' },
  },
  {
    path: '/plans/:id',
    name: 'plan-detail',
    component: PlanDetailView,
    meta: { requiresAuth: true, layout: 'main' },
    props: true,
  },
  {
    path: '/plans/:id/edit',
    name: 'plan-edit',
    component: PlanEditView,
    meta: { requiresAuth: true, layout: 'main' },
    props: true,
  },

  // Active Workout
  {
    path: '/workout/:sessionId',
    name: 'active-workout',
    component: ActiveWorkoutView,
    meta: { requiresAuth: true, layout: 'workout' },
    props: true,
  },
  {
    path: '/workout/complete',
    name: 'workout-complete',
    component: WorkoutCompleteView,
    meta: { requiresAuth: true, layout: 'minimal' },
  },

  // History
  {
    path: '/history',
    name: 'history',
    component: HistoryListView,
    meta: { requiresAuth: true, layout: 'main' },
  },
  {
    path: '/history/:id',
    name: 'session-detail',
    component: SessionDetailView,
    meta: { requiresAuth: true, layout: 'main' },
    props: true,
  },

  // Stats
  {
    path: '/stats',
    name: 'stats',
    component: StatsView,
    meta: { requiresAuth: true, layout: 'main' },
  },

  // Profile
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true, layout: 'main' },
  },

  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: { requiresAuth: false, layout: 'minimal' },
  },
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

// Navigation guard for authentication
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Initialize auth state if not done
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login with return URL
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && authStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    // Already authenticated, redirect to dashboard
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router

// Type augmentation for route meta
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    layout?: 'auth' | 'main' | 'workout' | 'minimal'
  }
}
