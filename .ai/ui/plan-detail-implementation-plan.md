# View Implementation Plan: Plan Detail

## 1. Overview

The Plan Detail page displays the complete structure of a workout plan including all exercises with their sets, reps, and rest times. Users can view the full plan, see exercise details (muscle groups, equipment), start a workout session directly from this page, navigate to edit mode, or return to the plans list. This is a read-only view focused on presenting the plan information clearly.

## 2. View Routing

- **Path**: `/plans/:planId`
- **Route Name**: `planDetail`
- **Route Params**: `planId: string` (UUID)
- **Access**: Authenticated users only
- **Guard**: Redirect to `/login` if not authenticated

## 3. Component Structure

```
PlanDetailPage (view)
├── PlanDetailHeader
│   ├── BackButton (to plans list)
│   ├── PlanTitle
│   └── HeaderActions
│       ├── EditButton
│       ├── StartWorkoutButton
│       └── MoreMenu (delete option)
├── PlanDescription (conditional)
├── PlanStats
│   ├── StatItem (exercise count)
│   ├── StatItem (estimated duration)
│   └── StatItem (target muscle groups)
├── ExerciseList
│   ├── ExerciseCard
│   │   ├── ExerciseInfo (name, muscle group icon)
│   │   ├── ExerciseDetails (sets x reps, rest time)
│   │   ├── EquipmentBadges
│   │   └── ConfidenceBadge (from import)
│   ├── ExerciseCard
│   └── ... (more exercises)
├── EmptyExercisesState (conditional)
├── LoadingState (conditional)
└── DeleteConfirmDialog
```

## 4. Component Details

### PlanDetailPage
- **Description**: Main view component that fetches and displays a single workout plan with all its exercises. Manages loading, error states, and plan actions.
- **Main elements**:
  - PlanDetailHeader with navigation and actions
  - Plan description section
  - PlanStats summary bar
  - ExerciseList ordered by sequence
- **Handled interactions**: 
  - Fetch plan data on mount
  - Handle delete confirmation
  - Navigate to edit/workout
- **Handled validation**: Validate planId param is UUID
- **Types**: `PlanDetailViewModel` 
- **Props**: None (uses route params)

### PlanDetailHeader
- **Description**: Header with plan name, back navigation, and action buttons.
- **Main elements**:
  - Back arrow button (to /plans)
  - Plan name as h1
  - Edit button (icon or text)
  - Start Workout button (primary CTA)
  - More menu (kebab) with delete option
- **Handled interactions**:
  - `@back` - Navigate to plans list
  - `@edit` - Navigate to plan edit
  - `@startWorkout` - Start session, navigate to active workout
  - `@delete` - Open delete confirmation
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `planName: string` - Plan name
  - `isStarting: boolean` - Loading state for start button

### PlanStats
- **Description**: Summary statistics bar showing quick plan overview.
- **Main elements**:
  - Exercise count (e.g., "8 exercises")
  - Estimated duration (calculated from sets × rest)
  - Primary muscle groups (icons or text)
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `exerciseCount: number`
  - `estimatedMinutes: number`
  - `muscleGroups: MuscleGroupEnum[]`

### ExerciseList
- **Description**: Ordered list of exercises in the workout plan.
- **Main elements**:
  - Section heading "Exercises"
  - List of ExerciseCard components
  - Sequence numbers (1, 2, 3...)
- **Handled interactions**: None (delegates to children)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `exercises: ExerciseDetailViewModel[]`

### ExerciseCard
- **Description**: Card displaying a single exercise with all its parameters.
- **Main elements**:
  - Sequence number badge
  - Exercise name
  - Muscle group icon/badge
  - Sets × reps display (e.g., "4 sets × 8-12 reps")
  - Rest time (e.g., "90s rest")
  - Equipment badges (icons with names)
  - Confidence level indicator (if from import)
- **Handled interactions**:
  - `@click` - Expand/collapse for more details (optional)
- **Handled validation**: None
- **Types**: `ExerciseDetailViewModel`
- **Props**:
  - `exercise: ExerciseDetailViewModel`
  - `sequence: number`

### ConfidenceBadge
- **Description**: Visual indicator of AI import confidence level.
- **Main elements**:
  - Icon (check, warning, question)
  - Tooltip with explanation
- **Handled interactions**:
  - Hover/tap shows tooltip
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `level: ConfidenceLevelEnum` - 'high' | 'medium' | 'low'

### EquipmentBadges
- **Description**: Display of equipment required for the exercise.
- **Main elements**:
  - Equipment icons or pills
  - Equipment names on hover
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `equipment: EquipmentBrief[]`

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From workout_plans.py
interface WorkoutPlanDetailResponse {
  id: string; // UUID
  name: string;
  description: string | null;
  exercises: WorkoutExerciseDetail[];
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

interface WorkoutExerciseDetail {
  id: string; // UUID
  exercise: ExerciseBrief;
  sequence: number;
  sets: number;
  reps_min: number;
  reps_max: number;
  rest_time_seconds: number | null;
  confidence_level: ConfidenceLevelEnum;
}

// From exercises.py
interface ExerciseBrief {
  id: string; // UUID
  name: string;
  muscle_group: MuscleGroupEnum;
  equipment: EquipmentBrief[];
}

interface EquipmentBrief {
  id: string; // UUID
  name: string;
}

// Enums
type ConfidenceLevelEnum = 'high' | 'medium' | 'low';
type MuscleGroupEnum = 
  | 'chest' | 'back' | 'shoulders' | 'biceps' | 'triceps'
  | 'forearms' | 'core' | 'quadriceps' | 'hamstrings'
  | 'glutes' | 'calves' | 'full_body' | 'cardio';
```

### ViewModels (frontend-specific)

```typescript
// Full plan detail for display
interface PlanDetailViewModel {
  id: string;
  name: string;
  description: string | null;
  exercises: ExerciseDetailViewModel[];
  exerciseCount: number;
  estimatedDurationMinutes: number;
  primaryMuscleGroups: MuscleGroupEnum[];
  createdAt: Date;
  updatedAt: Date;
}

// Exercise within plan for display
interface ExerciseDetailViewModel {
  id: string; // workout_exercise ID
  exerciseId: string; // actual exercise ID
  name: string;
  muscleGroup: MuscleGroupEnum;
  muscleGroupDisplay: string; // Human readable
  equipment: EquipmentViewModel[];
  sequence: number;
  sets: number;
  repsMin: number;
  repsMax: number;
  repsDisplay: string; // e.g., "8-12" or "10"
  restTimeSeconds: number | null;
  restTimeDisplay: string | null; // e.g., "90s"
  confidenceLevel: ConfidenceLevelEnum;
}

interface EquipmentViewModel {
  id: string;
  name: string;
  icon?: string; // Optional icon identifier
}

// Page state
interface PlanDetailState {
  plan: PlanDetailViewModel | null;
  isLoading: boolean;
  error: string | null;
  isStartingWorkout: boolean;
  deleteDialog: DeleteDialogState;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const muscleGroupEnum = z.enum([
  'chest', 'back', 'shoulders', 'biceps', 'triceps',
  'forearms', 'core', 'quadriceps', 'hamstrings',
  'glutes', 'calves', 'full_body', 'cardio'
]);

const confidenceLevelEnum = z.enum(['high', 'medium', 'low']);

const equipmentBriefSchema = z.object({
  id: z.string().uuid(),
  name: z.string()
});

const exerciseBriefSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  muscle_group: muscleGroupEnum,
  equipment: z.array(equipmentBriefSchema)
});

const workoutExerciseDetailSchema = z.object({
  id: z.string().uuid(),
  exercise: exerciseBriefSchema,
  sequence: z.number().int().min(0),
  sets: z.number().int().min(1).max(50),
  reps_min: z.number().int().min(1).max(200),
  reps_max: z.number().int().min(1).max(200),
  rest_time_seconds: z.number().int().min(0).max(3600).nullable(),
  confidence_level: confidenceLevelEnum
});

const workoutPlanDetailResponseSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  description: z.string().nullable(),
  exercises: z.array(workoutExerciseDetailSchema),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime()
});
```

## 6. State Management

### Local Component State (PlanDetailPage)

```typescript
const plan = ref<PlanDetailViewModel | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const isStartingWorkout = ref(false);

const deleteDialog = ref<DeleteDialogState>({
  isOpen: false,
  planId: null,
  planName: '',
  isDeleting: false
});
```

### Pinia Store (workoutPlanStore)

```typescript
// stores/workoutPlan.ts (extended)
interface WorkoutPlanStore {
  // State
  currentPlanDetail: WorkoutPlanDetailResponse | null;
  
  // Actions
  fetchPlanDetail(planId: string): Promise<void>;
  clearCurrentPlan(): void;
}
```

### Custom Composable: usePlanDetail

```typescript
// composables/usePlanDetail.ts
export function usePlanDetail(planId: Ref<string>) {
  const workoutPlanStore = useWorkoutPlanStore();
  const sessionStore = useSessionStore();
  const router = useRouter();
  
  const plan = ref<PlanDetailViewModel | null>(null);
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const isStartingWorkout = ref(false);
  
  const estimatedDuration = computed(() => calculateDuration(plan.value));
  const primaryMuscleGroups = computed(() => extractMuscleGroups(plan.value));
  
  const fetchPlan = async (): Promise<void> => { ... };
  const startWorkout = async (): Promise<void> => { ... };
  const navigateToEdit = (): void => { ... };
  const deletePlan = async (): Promise<void> => { ... };
  
  return {
    plan,
    isLoading,
    error,
    isStartingWorkout,
    estimatedDuration,
    primaryMuscleGroups,
    fetchPlan,
    startWorkout,
    navigateToEdit,
    deletePlan
  };
}

// Helper: Calculate estimated workout duration
function calculateDuration(plan: PlanDetailViewModel | null): number {
  if (!plan) return 0;
  
  let totalSeconds = 0;
  for (const exercise of plan.exercises) {
    // Assume ~45 seconds per set for actual lifting
    totalSeconds += exercise.sets * 45;
    // Add rest time between sets
    const restTime = exercise.restTimeSeconds || 60;
    totalSeconds += (exercise.sets - 1) * restTime;
  }
  
  return Math.ceil(totalSeconds / 60);
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Plan Detail
```
GET /api/v1/workout-plans/{plan_id}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "name": "Push Pull Legs - Push Day",
    "description": "Focus on chest, shoulders, and triceps",
    "exercises": [
      {
        "id": "workout-exercise-uuid",
        "exercise": {
          "id": "exercise-uuid",
          "name": "Bench Press",
          "muscle_group": "chest",
          "equipment": [
            { "id": "equip-uuid", "name": "Barbell" },
            { "id": "equip-uuid-2", "name": "Bench" }
          ]
        },
        "sequence": 0,
        "sets": 4,
        "reps_min": 8,
        "reps_max": 12,
        "rest_time_seconds": 90,
        "confidence_level": "high"
      },
      {
        "id": "workout-exercise-uuid-2",
        "exercise": {
          "id": "exercise-uuid-2",
          "name": "Overhead Press",
          "muscle_group": "shoulders",
          "equipment": [
            { "id": "equip-uuid", "name": "Barbell" }
          ]
        },
        "sequence": 1,
        "sets": 3,
        "reps_min": 10,
        "reps_max": 12,
        "rest_time_seconds": 60,
        "confidence_level": "medium"
      }
    ],
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-16T08:00:00Z"
  },
  "error": null
}
```

**Error Response (404 Not Found)**
```typescript
{
  "success": false,
  "data": null,
  "error": {
    "code": "PLAN_NOT_FOUND",
    "message": "Workout plan not found"
  }
}
```

#### 2. Start Workout Session
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

#### 3. Delete Workout Plan
```
DELETE /api/v1/workout-plans/{plan_id}
```

**Response (204 No Content)**

### API Service Functions

```typescript
// services/api/workoutPlans.ts
import axios from '@/lib/axios';
import type { WorkoutPlanDetailResponse } from '@/types/workout-plans';
import type { WorkoutSessionStartResponse } from '@/types/workout-sessions';

export async function getWorkoutPlanDetail(planId: string): Promise<WorkoutPlanDetailResponse> {
  const response = await axios.get<APIResponse<WorkoutPlanDetailResponse>>(
    `/api/v1/workout-plans/${planId}`
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

export async function deleteWorkoutPlan(planId: string): Promise<void> {
  await axios.delete(`/api/v1/workout-plans/${planId}`);
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | PlanDetailPage | `onMounted` | Fetch plan detail |
| Click back | BackButton | Router navigation | Navigate to `/plans` |
| Click edit | EditButton | `navigateToEdit()` | Navigate to `/plans/:id/edit` |
| Click Start Workout | StartWorkoutButton | `startWorkout()` | Create session, navigate to `/workout/:sessionId` |
| Click delete (menu) | MoreMenu | `openDeleteDialog()` | Show delete confirmation |
| Confirm delete | DeleteDialog | `deletePlan()` | Delete, navigate to `/plans` |
| Cancel delete | DeleteDialog | `closeDialog()` | Close dialog |
| Click exercise card | ExerciseCard | Expand/collapse | Show more details (optional) |
| Hover confidence badge | ConfidenceBadge | Show tooltip | Display confidence explanation |

### Detailed Interaction Flow

1. **Page Load**:
   - Validate planId from route params
   - Show loading skeleton
   - Fetch plan detail from API
   - Map to ViewModel, calculate derived values
   - Render plan with exercises

2. **Starting a Workout**:
   - User clicks "Start Workout"
   - Button shows loading spinner
   - Call POST /api/v1/workout-sessions/start
   - On success: Navigate to `/workout/:sessionId`
   - On error: Show error toast, re-enable button

3. **Editing the Plan**:
   - User clicks Edit button
   - Navigate to `/plans/:planId/edit`

4. **Deleting the Plan**:
   - User clicks Delete in more menu
   - Show confirmation dialog with plan name
   - If confirmed:
     - Show loading state
     - Call DELETE API
     - On success: Show toast, navigate to `/plans`
     - On error: Show error in dialog

5. **Viewing Exercise Details**:
   - Exercises shown in sequence order
   - Each card shows sets, reps, rest, equipment
   - Confidence badge indicates import quality
   - Optional: tap to expand for more info

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | All content |
| plan loaded | All plan content | LoadingSkeleton |
| error exists | ErrorState | Plan content |
| plan.description exists | PlanDescription | - |
| plan.description is null | - | PlanDescription |
| exercises.length > 0 | ExerciseList | EmptyExercisesState |
| exercises.length = 0 | EmptyExercisesState | ExerciseList |
| confidence != 'high' | ConfidenceBadge | - |
| restTimeSeconds > 0 | RestTimeDisplay | - |

### Exercise Display Logic

| Condition | Display |
|-----------|---------|
| reps_min === reps_max | "10 reps" |
| reps_min !== reps_max | "8-12 reps" |
| rest_time_seconds exists | "90s rest" |
| rest_time_seconds is null | Default rest display or hidden |
| equipment.length > 0 | Equipment badges |
| equipment.length = 0 | "Bodyweight" badge |

### Route Param Validation

```typescript
// In page setup
const route = useRoute();
const planId = computed(() => {
  const id = route.params.planId as string;
  // Validate UUID format
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(id)) {
    router.push({ name: 'plans' });
    return '';
  }
  return id;
});
```

## 10. Error Handling

### API Error Handling

```typescript
async function fetchPlan(): Promise<void> {
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await getWorkoutPlanDetail(planId.value);
    plan.value = mapToViewModel(response);
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const status = e.response?.status;
      const code = e.response?.data?.error?.code;
      
      if (status === 404 || code === 'PLAN_NOT_FOUND') {
        error.value = 'Plan not found';
        // Optionally redirect after delay
        setTimeout(() => router.push({ name: 'plans' }), 2000);
      } else {
        error.value = 'Failed to load plan details';
      }
    } else {
      error.value = 'An unexpected error occurred';
    }
  } finally {
    isLoading.value = false;
  }
}

async function startWorkout(): Promise<void> {
  isStartingWorkout.value = true;
  
  try {
    const response = await startWorkoutSession(planId.value);
    router.push({ 
      name: 'activeWorkout', 
      params: { sessionId: response.session_id } 
    });
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const code = e.response?.data?.error?.code;
      
      if (code === 'SESSION_IN_PROGRESS') {
        showToast({
          type: 'warning',
          message: 'You already have a workout in progress'
        });
        // Could offer to navigate to that session
      } else {
        showToast({
          type: 'error',
          message: 'Failed to start workout. Please try again.'
        });
      }
    }
  } finally {
    isStartingWorkout.value = false;
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Plan not found | 404 | "Plan not found" | Redirect to plans list |
| Network error | - | "Unable to connect" | Show retry button |
| Session in progress | 400 | "You have a workout in progress" | Offer navigation |
| Server error | 500 | "Something went wrong" | Show retry button |
| Invalid plan ID | - | Redirect silently | Navigate to plans list |

## 11. Implementation Steps

1. **Create Types**
   - Add `PlanDetailViewModel`, `ExerciseDetailViewModel` to types
   - Add Zod validation schemas for API responses

2. **Create/Update API Service**
   - Add `getWorkoutPlanDetail()` function
   - Ensure `startWorkoutSession()` exists

3. **Create Composable**
   - Create `src/composables/usePlanDetail.ts`
   - Implement fetch, start workout, delete logic
   - Add duration calculation helper

4. **Create Helper Utilities**
   - Create `src/utils/muscleGroups.ts` for muscle group display mapping
   - Create `src/utils/formatters.ts` for reps/rest formatting

5. **Create Components**
   - Create `src/components/plans/PlanDetailHeader.vue`
   - Create `src/components/plans/PlanStats.vue`
   - Create `src/components/plans/ExerciseList.vue`
   - Create `src/components/plans/ExerciseCard.vue`
   - Create `src/components/common/ConfidenceBadge.vue`
   - Create `src/components/common/EquipmentBadges.vue`

6. **Create Plan Detail Page**
   - Create `src/views/plans/PlanDetailPage.vue`
   - Implement layout with all sections
   - Wire up data and interactions

7. **Configure Router**
   - Add `/plans/:planId` route
   - Ensure auth guard

8. **Add Loading States**
   - Create skeleton for header
   - Create skeleton for exercise cards
   - Handle start workout loading

9. **Style with Tailwind**
   - Style exercise cards with sequence numbers
   - Add muscle group color coding
   - Style equipment badges
   - Add confidence level styling (green/yellow/red)

10. **Add Accessibility**
    - Proper heading hierarchy (h1 for plan name)
    - ARIA labels for action buttons
    - Keyboard navigation
    - Focus management for dialogs

11. **Write Tests**
    - Unit tests for composable and helpers
    - Component tests for ExerciseCard
    - Integration test for page flow
    - Test error states

12. **Manual Testing**
    - Test with various exercise counts
    - Test with/without descriptions
    - Test start workout flow
    - Test delete flow
    - Verify confidence badges
    - Test on mobile and desktop
