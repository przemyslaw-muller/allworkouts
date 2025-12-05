# View Implementation Plan: Dashboard

## 1. Overview

The Dashboard serves as the central hub of the AllWorkouts application after login. It displays the user's active workout plan with quick-start capability, session recovery options for interrupted workouts, key statistics summary, and quick navigation to other areas of the app. The dashboard provides an at-a-glance view of the user's fitness journey and encourages continued engagement.

## 2. View Routing

- **Path**: `/dashboard`
- **Route Name**: `dashboard`
- **Access**: Authenticated users only
- **Guard**: Redirect to `/login` if not authenticated

## 3. Component Structure

```
DashboardPage (view)
├── DashboardHeader
│   ├── UserGreeting
│   └── QuickActions (settings shortcut)
├── SessionRecoveryBanner (conditional - shown if interrupted session exists)
│   ├── RecoveryInfo
│   └── RecoveryActions (resume/discard)
├── ActivePlanCard
│   ├── PlanInfo (name, exercise count)
│   ├── LastWorkoutInfo
│   └── StartWorkoutButton
├── QuickStatsGrid
│   ├── StatCard (total workouts)
│   ├── StatCard (current streak)
│   ├── StatCard (PRs count)
│   └── StatCard (total volume)
├── RecentActivityList
│   ├── ActivityItem (recent workout)
│   ├── ActivityItem (recent workout)
│   └── ViewAllLink
└── EmptyState (conditional - shown if no plan)
    └── CreatePlanCTA
```

## 4. Component Details

### DashboardPage
- **Description**: Main view component that orchestrates the dashboard layout. Fetches initial data on mount and manages loading states.
- **Main elements**:
  - DashboardHeader with user greeting
  - SessionRecoveryBanner (conditionally rendered)
  - ActivePlanCard or EmptyState
  - QuickStatsGrid
  - RecentActivityList
- **Handled interactions**: 
  - Orchestrates data fetching on mount
  - Handles session recovery actions
- **Handled validation**: None
- **Types**: `DashboardData` (ViewModel)
- **Props**: None

### DashboardHeader
- **Description**: Top section with personalized greeting and quick actions.
- **Main elements**:
  - UserGreeting with time-based greeting (Good morning/afternoon/evening)
  - User's display name or email
  - Settings icon button
- **Handled interactions**:
  - `@click` on settings icon - Navigate to profile
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `userEmail: string` - User's email for greeting

### SessionRecoveryBanner
- **Description**: Alert banner shown when user has an interrupted (in-progress) workout session. Prompts user to resume or discard.
- **Main elements**:
  - Warning icon
  - Plan name and session start time
  - Resume button (primary)
  - Discard button (secondary/destructive)
- **Handled interactions**:
  - `@resume` - Navigate to active workout session
  - `@discard` - Show confirmation, then call skip session API
- **Handled validation**: None
- **Types**: `InterruptedSessionInfo` (ViewModel)
- **Props**:
  - `session: InterruptedSessionInfo` - Interrupted session data

### ActivePlanCard
- **Description**: Card displaying the user's active/selected workout plan with quick-start capability.
- **Main elements**:
  - Plan name as heading
  - Plan description (truncated)
  - Exercise count badge
  - Last workout date
  - "Start Workout" button (primary CTA)
  - "View Plan" link
- **Handled interactions**:
  - `@click` on Start Workout - Start new session via API, navigate to active workout
  - `@click` on View Plan - Navigate to plan detail
- **Handled validation**: None
- **Types**: `ActivePlanInfo` (ViewModel)
- **Props**:
  - `plan: ActivePlanInfo` - Active plan data
  - `lastWorkout: Date | null` - Last workout date

### QuickStatsGrid
- **Description**: Grid of key statistics cards showing user's progress at a glance.
- **Main elements**:
  - 2x2 grid on mobile, 4-column on desktop
  - StatCard components
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `QuickStats` (ViewModel)
- **Props**:
  - `stats: QuickStats` - Statistics data

### StatCard
- **Description**: Individual stat display card with icon, value, and label.
- **Main elements**:
  - Icon (contextual based on stat type)
  - Large value display
  - Label text
  - Optional trend indicator
- **Handled interactions**: 
  - `@click` - Navigate to stats page (optional)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `icon: string` - Icon name
  - `value: string | number` - Display value
  - `label: string` - Stat label
  - `trend?: 'up' | 'down' | 'neutral'` - Optional trend indicator

### RecentActivityList
- **Description**: List of recent workout sessions with quick info.
- **Main elements**:
  - Section heading "Recent Workouts"
  - List of ActivityItem components (max 3-5)
  - "View All" link to history
- **Handled interactions**:
  - `@click` on View All - Navigate to history page
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `sessions: RecentSessionInfo[]` - Recent sessions array

### ActivityItem
- **Description**: Single row displaying a recent workout session.
- **Main elements**:
  - Plan name
  - Relative date (e.g., "2 days ago")
  - Duration
  - Status indicator (completed/skipped)
- **Handled interactions**:
  - `@click` - Navigate to session detail
- **Handled validation**: None
- **Types**: `RecentSessionInfo` (ViewModel)
- **Props**:
  - `session: RecentSessionInfo` - Session data

### EmptyState
- **Description**: Shown when user has no workout plans. Encourages creating first plan.
- **Main elements**:
  - Illustration/icon
  - Heading "No workout plan yet"
  - Description text
  - "Create Plan" button
  - "Import Plan" button
- **Handled interactions**:
  - `@click` on Create Plan - Navigate to plan creation (or import wizard)
  - `@click` on Import Plan - Navigate to import wizard
- **Handled validation**: None
- **Types**: None
- **Props**: None

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From stats.py
interface StatsOverviewResponse {
  total_workouts: number;
  total_duration_seconds: number;
  total_volume_kg: string; // Decimal as string
  workouts_by_month: MonthlyWorkoutCount[];
  most_trained_muscle_groups: MuscleGroupTrainingCount[];
  current_streak_days: number;
  personal_records_count: number;
}

interface MonthlyWorkoutCount {
  month: string; // Format: YYYY-MM
  count: number;
}

interface MuscleGroupTrainingCount {
  muscle_group: MuscleGroupEnum;
  session_count: number;
}

// From workout_plans.py
interface WorkoutPlanListItem {
  id: string; // UUID
  name: string;
  description: string | null;
  exercise_count: number;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

interface WorkoutPlanListResponse {
  plans: WorkoutPlanListItem[];
  pagination: PaginationInfo;
}

// From workout_sessions.py
interface WorkoutSessionListItem {
  id: string; // UUID
  workout_plan: WorkoutPlanBrief;
  status: SessionStatusEnum;
  exercise_count: number;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

interface WorkoutPlanBrief {
  id: string; // UUID
  name: string;
}

interface WorkoutSessionListResponse {
  sessions: WorkoutSessionListItem[];
  pagination: PaginationInfo;
}

// Enums
type SessionStatusEnum = 'in_progress' | 'completed' | 'skipped';
```

### ViewModels (frontend-specific)

```typescript
// Dashboard data aggregate
interface DashboardData {
  activePlan: ActivePlanInfo | null;
  interruptedSession: InterruptedSessionInfo | null;
  quickStats: QuickStats;
  recentSessions: RecentSessionInfo[];
  isLoading: boolean;
  error: string | null;
}

// Active plan info
interface ActivePlanInfo {
  id: string;
  name: string;
  description: string | null;
  exerciseCount: number;
  lastWorkoutDate: Date | null;
}

// Interrupted session info
interface InterruptedSessionInfo {
  sessionId: string;
  planId: string;
  planName: string;
  startedAt: Date;
  exerciseCount: number;
}

// Quick stats for display
interface QuickStats {
  totalWorkouts: number;
  currentStreak: number;
  personalRecordsCount: number;
  totalVolumeFormatted: string; // Formatted with unit (e.g., "1,234 kg")
}

// Recent session for activity list
interface RecentSessionInfo {
  id: string;
  planName: string;
  date: Date;
  durationFormatted: string; // e.g., "45 min"
  status: SessionStatusEnum;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

// No form input on dashboard, but can validate API responses
const statsOverviewSchema = z.object({
  total_workouts: z.number().int().min(0),
  total_duration_seconds: z.number().int().min(0),
  total_volume_kg: z.string(), // Decimal as string
  workouts_by_month: z.array(z.object({
    month: z.string().regex(/^\d{4}-\d{2}$/),
    count: z.number().int().min(0)
  })),
  most_trained_muscle_groups: z.array(z.object({
    muscle_group: z.enum([
      'chest', 'back', 'shoulders', 'biceps', 'triceps', 
      'forearms', 'core', 'quadriceps', 'hamstrings', 
      'glutes', 'calves', 'full_body', 'cardio'
    ]),
    session_count: z.number().int().min(0)
  })),
  current_streak_days: z.number().int().min(0),
  personal_records_count: z.number().int().min(0)
});

const workoutSessionListItemSchema = z.object({
  id: z.string().uuid(),
  workout_plan: z.object({
    id: z.string().uuid(),
    name: z.string()
  }),
  status: z.enum(['in_progress', 'completed', 'skipped']),
  exercise_count: z.number().int().min(0),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime()
});
```

## 6. State Management

### Local Component State (DashboardPage)

```typescript
const isLoading = ref(true);
const error = ref<string | null>(null);
const dashboardData = ref<DashboardData>({
  activePlan: null,
  interruptedSession: null,
  quickStats: {
    totalWorkouts: 0,
    currentStreak: 0,
    personalRecordsCount: 0,
    totalVolumeFormatted: '0 kg'
  },
  recentSessions: [],
  isLoading: true,
  error: null
});
```

### Pinia Stores Used

```typescript
// authStore - for user info
interface AuthStore {
  user: AuthUserResponse | null;
  isAuthenticated: boolean;
}

// workoutPlanStore - for active plan (optional, could be local)
interface WorkoutPlanStore {
  activePlan: WorkoutPlanListItem | null;
  setActivePlan(plan: WorkoutPlanListItem): void;
  clearActivePlan(): void;
}

// sessionStore - for tracking in-progress session
interface SessionStore {
  currentSession: WorkoutSessionListItem | null;
  hasInterruptedSession: boolean;
  checkForInterruptedSession(): Promise<void>;
  discardSession(sessionId: string): Promise<void>;
}

// statsStore - for caching stats (optional)
interface StatsStore {
  overview: StatsOverviewResponse | null;
  fetchOverview(): Promise<void>;
  lastFetched: Date | null;
}
```

### Custom Composable: useDashboard

```typescript
// composables/useDashboard.ts
export function useDashboard() {
  const authStore = useAuthStore();
  const sessionStore = useSessionStore();
  const router = useRouter();
  
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const activePlan = ref<ActivePlanInfo | null>(null);
  const interruptedSession = ref<InterruptedSessionInfo | null>(null);
  const quickStats = ref<QuickStats | null>(null);
  const recentSessions = ref<RecentSessionInfo[]>([]);
  
  const fetchDashboardData = async (): Promise<void> => { ... };
  const startWorkout = async (planId: string): Promise<void> => { ... };
  const resumeSession = async (sessionId: string): Promise<void> => { ... };
  const discardSession = async (sessionId: string): Promise<void> => { ... };
  
  return {
    isLoading,
    error,
    activePlan,
    interruptedSession,
    quickStats,
    recentSessions,
    fetchDashboardData,
    startWorkout,
    resumeSession,
    discardSession
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Stats Overview
```
GET /api/v1/stats/overview
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "total_workouts": 45,
    "total_duration_seconds": 72000,
    "total_volume_kg": "12500.50",
    "workouts_by_month": [
      { "month": "2025-01", "count": 12 }
    ],
    "most_trained_muscle_groups": [
      { "muscle_group": "chest", "session_count": 15 }
    ],
    "current_streak_days": 5,
    "personal_records_count": 23
  },
  "error": null
}
```

#### 2. Get Workout Plans (for active plan)
```
GET /api/v1/workout-plans?limit=1
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "plans": [
      {
        "id": "uuid-string",
        "name": "Push Pull Legs",
        "description": "3-day split program",
        "exercise_count": 6,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      }
    ],
    "pagination": { "total": 3, "page": 1, "per_page": 1 }
  },
  "error": null
}
```

#### 3. Get Recent Sessions
```
GET /api/v1/workout-sessions?limit=5&status=completed,skipped
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "uuid-string",
        "workout_plan": { "id": "uuid", "name": "Push Day" },
        "status": "completed",
        "exercise_count": 5,
        "created_at": "2025-01-14T18:00:00Z",
        "updated_at": "2025-01-14T19:00:00Z"
      }
    ],
    "pagination": { "total": 45, "page": 1, "per_page": 5 }
  },
  "error": null
}
```

#### 4. Check for In-Progress Session
```
GET /api/v1/workout-sessions?status=in_progress&limit=1
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "uuid-string",
        "workout_plan": { "id": "uuid", "name": "Leg Day" },
        "status": "in_progress",
        "exercise_count": 3,
        "created_at": "2025-01-15T08:00:00Z",
        "updated_at": "2025-01-15T08:30:00Z"
      }
    ],
    "pagination": { "total": 1, "page": 1, "per_page": 1 }
  },
  "error": null
}
```

#### 5. Start Workout Session
```
POST /api/v1/workout-sessions/start
```

**Request**
```typescript
{
  "workout_plan_id": "uuid-string"
}
```

**Response (201 Created)**
```typescript
{
  "success": true,
  "data": {
    "session_id": "uuid-string",
    "workout_plan": { "id": "uuid", "name": "Push Day" },
    "started_at": "2025-01-15T10:00:00Z",
    "exercises": [...]
  },
  "error": null
}
```

#### 6. Skip/Discard Session
```
POST /api/v1/workout-sessions/{session_id}/skip
```

**Request**
```typescript
{
  "notes": "Discarded from dashboard"
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "session_id": "uuid-string",
    "status": "skipped"
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/dashboard.ts
import axios from '@/lib/axios';
import type { StatsOverviewResponse } from '@/types/stats';
import type { WorkoutPlanListResponse } from '@/types/workout-plans';
import type { WorkoutSessionListResponse, WorkoutSessionStartResponse } from '@/types/workout-sessions';

export async function getStatsOverview(): Promise<StatsOverviewResponse> {
  const response = await axios.get<APIResponse<StatsOverviewResponse>>(
    '/api/v1/stats/overview'
  );
  return response.data.data;
}

export async function getWorkoutPlans(limit = 10): Promise<WorkoutPlanListResponse> {
  const response = await axios.get<APIResponse<WorkoutPlanListResponse>>(
    '/api/v1/workout-plans',
    { params: { limit } }
  );
  return response.data.data;
}

export async function getWorkoutSessions(params: {
  limit?: number;
  status?: string;
}): Promise<WorkoutSessionListResponse> {
  const response = await axios.get<APIResponse<WorkoutSessionListResponse>>(
    '/api/v1/workout-sessions',
    { params }
  );
  return response.data.data;
}

export async function startWorkoutSession(planId: string): Promise<WorkoutSessionStartResponse> {
  const response = await axios.post<APIResponse<WorkoutSessionStartResponse>>(
    '/api/v1/workout-sessions/start',
    { workout_plan_id: planId }
  );
  return response.data.data;
}

export async function skipSession(sessionId: string, notes?: string): Promise<void> {
  await axios.post(`/api/v1/workout-sessions/${sessionId}/skip`, { notes });
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | DashboardPage | `onMounted` | Fetch all dashboard data in parallel |
| Click Start Workout | ActivePlanCard button | `startWorkout()` | Create session, navigate to `/workout/:id` |
| Click View Plan | ActivePlanCard link | Router navigation | Navigate to `/plans/:id` |
| Click Resume | SessionRecoveryBanner | `resumeSession()` | Navigate to `/workout/:sessionId` |
| Click Discard | SessionRecoveryBanner | `discardSession()` | Show confirm dialog, skip session, hide banner |
| Click StatCard | QuickStatsGrid | Router navigation | Navigate to `/stats` |
| Click View All | RecentActivityList | Router navigation | Navigate to `/history` |
| Click ActivityItem | RecentActivityList | Router navigation | Navigate to `/history/:sessionId` |
| Click Create Plan | EmptyState | Router navigation | Navigate to `/plans/import` |
| Click Import Plan | EmptyState | Router navigation | Navigate to `/plans/import` |
| Click Settings | DashboardHeader | Router navigation | Navigate to `/profile` |
| Pull to refresh | DashboardPage (mobile) | `fetchDashboardData()` | Re-fetch all dashboard data |

### Detailed Interaction Flow

1. **Page Load**:
   - Show loading skeleton
   - Fetch in parallel: stats overview, workout plans, recent sessions, in-progress check
   - Once all data loaded, render dashboard components
   - If in-progress session found, show SessionRecoveryBanner

2. **Starting a Workout**:
   - User clicks "Start Workout" on ActivePlanCard
   - Button shows loading state
   - Call POST /api/v1/workout-sessions/start
   - On success, navigate to `/workout/:sessionId`
   - On error, show error toast

3. **Session Recovery**:
   - If in-progress session exists, banner appears at top
   - "Resume" navigates directly to active workout
   - "Discard" shows confirmation dialog
   - On confirm, calls skip endpoint, then hides banner

4. **Navigation**:
   - All navigation uses Vue Router
   - Stats card navigates to /stats
   - Activity items navigate to session detail
   - View All navigates to history

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| Has active plan | ActivePlanCard | EmptyState |
| No plans exist | EmptyState | ActivePlanCard |
| Has interrupted session | SessionRecoveryBanner | - |
| No interrupted session | - | SessionRecoveryBanner |
| isLoading = true | LoadingSkeleton | All content |
| error exists | ErrorState | Dashboard content |
| No recent sessions | EmptyActivityMessage | RecentActivityList |

### Data Loading States

| State | UI Behavior |
|-------|-------------|
| Initial load | Show skeleton placeholders |
| Refresh | Show refresh indicator, keep existing data |
| Error | Show error banner with retry button |
| Partial error | Show available data, error indicator for failed section |

## 10. Error Handling

### API Error Handling

```typescript
async function fetchDashboardData(): Promise<void> {
  isLoading.value = true;
  error.value = null;
  
  try {
    const [statsData, plansData, sessionsData, inProgressData] = await Promise.allSettled([
      getStatsOverview(),
      getWorkoutPlans(1),
      getWorkoutSessions({ limit: 5, status: 'completed,skipped' }),
      getWorkoutSessions({ limit: 1, status: 'in_progress' })
    ]);
    
    // Handle stats
    if (statsData.status === 'fulfilled') {
      quickStats.value = mapStatsToViewModel(statsData.value);
    }
    
    // Handle active plan
    if (plansData.status === 'fulfilled' && plansData.value.plans.length > 0) {
      activePlan.value = mapPlanToViewModel(plansData.value.plans[0]);
    }
    
    // Handle recent sessions
    if (sessionsData.status === 'fulfilled') {
      recentSessions.value = sessionsData.value.sessions.map(mapSessionToViewModel);
    }
    
    // Handle interrupted session
    if (inProgressData.status === 'fulfilled' && inProgressData.value.sessions.length > 0) {
      interruptedSession.value = mapToInterruptedSession(inProgressData.value.sessions[0]);
    }
    
    // Check if all failed
    const allFailed = [statsData, plansData, sessionsData].every(r => r.status === 'rejected');
    if (allFailed) {
      error.value = 'Failed to load dashboard data. Please try again.';
    }
    
  } catch (e) {
    error.value = 'An unexpected error occurred.';
  } finally {
    isLoading.value = false;
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Network error | - | "Unable to connect. Check your internet connection." | Show retry button |
| Auth expired | 401 | Auto-redirect to login | Redirect via interceptor |
| Server error | 500 | "Something went wrong. Please try again." | Show retry button |
| Partial failure | Mixed | Show available data + section error | Allow refresh |

### Start Workout Error Handling

```typescript
async function startWorkout(planId: string): Promise<void> {
  isStarting.value = true;
  
  try {
    const response = await startWorkoutSession(planId);
    router.push({ name: 'activeWorkout', params: { sessionId: response.session_id } });
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const code = error.response?.data?.error?.code;
      
      if (code === 'SESSION_IN_PROGRESS') {
        // User has another session in progress
        showToast({
          type: 'warning',
          message: 'You have a workout in progress. Please finish or discard it first.'
        });
        // Refresh to show recovery banner
        await checkForInterruptedSession();
      } else {
        showToast({
          type: 'error',
          message: 'Failed to start workout. Please try again.'
        });
      }
    }
  } finally {
    isStarting.value = false;
  }
}
```

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/stats.ts` with stats DTOs
   - Create `src/types/dashboard.ts` with ViewModels
   - Add Zod schemas for API response validation

2. **Create API Service Functions**
   - Create `src/services/api/stats.ts` with stats endpoints
   - Add dashboard-specific functions to existing services
   - Ensure axios interceptors handle auth/errors

3. **Create/Update Pinia Stores**
   - Create `src/stores/stats.ts` for caching stats
   - Update `src/stores/session.ts` for interrupted session tracking
   - Ensure stores integrate with API services

4. **Create Dashboard Composable**
   - Create `src/composables/useDashboard.ts`
   - Implement parallel data fetching
   - Handle session recovery logic

5. **Create Base Components** (if not existing)
   - Create `src/components/common/LoadingSkeleton.vue`
   - Create `src/components/common/ErrorState.vue`
   - Create `src/components/common/EmptyState.vue`

6. **Create Dashboard-Specific Components**
   - Create `src/components/dashboard/DashboardHeader.vue`
   - Create `src/components/dashboard/SessionRecoveryBanner.vue`
   - Create `src/components/dashboard/ActivePlanCard.vue`
   - Create `src/components/dashboard/QuickStatsGrid.vue`
   - Create `src/components/dashboard/StatCard.vue`
   - Create `src/components/dashboard/RecentActivityList.vue`
   - Create `src/components/dashboard/ActivityItem.vue`

7. **Create Dashboard Page View**
   - Create `src/views/DashboardPage.vue`
   - Implement layout with all child components
   - Wire up data flow and event handlers

8. **Configure Router**
   - Add dashboard route to `src/router/index.ts`
   - Set up as post-login redirect target
   - Implement auth guard

9. **Add Loading and Error States**
   - Implement skeleton loading for each section
   - Add error boundaries for partial failures
   - Implement pull-to-refresh (mobile)

10. **Style with Tailwind**
    - Apply responsive grid layouts
    - Add card shadows and hover states
    - Ensure consistent spacing and typography
    - Support dark mode

11. **Add Accessibility**
    - Add proper heading hierarchy
    - Implement focus management
    - Add ARIA labels for interactive elements
    - Ensure keyboard navigation

12. **Write Tests**
    - Unit tests for composable logic
    - Component tests for each dashboard component
    - Integration test for full dashboard flow
    - Test error states and loading states

13. **Manual Testing**
    - Test with various data states (no plans, has plans, in-progress session)
    - Test network error handling
    - Test on mobile and desktop viewports
    - Verify navigation flows
