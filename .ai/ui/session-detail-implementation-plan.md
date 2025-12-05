# View Implementation Plan: Session Detail

## 1. Overview

The Session Detail page displays comprehensive information about a completed or abandoned workout session. It shows the session metadata (date, duration, status), a complete breakdown of all exercises performed with sets, weights, and reps, any personal records achieved during the session, and session notes. Users can optionally repeat the workout to start a new session with the same workout plan.

## 2. View Routing

- **Path**: `/history/:sessionId`
- **Route Name**: `sessionDetail`
- **Access**: Authenticated users only
- **Guard**: 
  - Redirect to `/login` if not authenticated
  - Show 404 if session not found or doesn't belong to user
- **Route Params**:
  - `sessionId` (UUID): The workout session ID

## 3. Component Structure

```
SessionDetailPage (view)
├── PageHeader
│   ├── BackButton
│   ├── WorkoutName
│   └── StatusBadge
├── SessionMetaCard
│   ├── DateDisplay
│   ├── DurationDisplay
│   └── ExerciseCountDisplay
├── PersonalRecordsSection (conditional - if PRs achieved)
│   ├── SectionHeader
│   └── PersonalRecordCard (for each PR)
│       ├── ExerciseName
│       ├── RecordTypeBadge
│       └── RecordValue
├── ExercisesList
│   ├── ExerciseSection (for each exercise)
│   │   ├── ExerciseHeader
│   │   │   ├── ExerciseName
│   │   │   ├── ExerciseInfoButton
│   │   │   └── PRIndicator (if PR on this exercise)
│   │   └── SetsTable
│   │       ├── TableHeader (Set, Weight, Reps)
│   │       └── SetRow (for each set)
│   │           ├── SetNumber
│   │           ├── Weight
│   │           ├── Reps
│   │           └── PRBadge (if this set was a PR)
├── NotesSection (conditional - if notes exist)
│   ├── SectionHeader
│   └── NotesText
├── ActionButtons
│   ├── RepeatWorkoutButton
│   └── DeleteSessionButton (optional)
└── LoadingState / ErrorState
```

## 4. Component Details

### SessionDetailPage
- **Description**: Main view component that fetches and displays a single workout session with all its details.
- **Main elements**:
  - PageHeader with navigation and status
  - SessionMetaCard with overview stats
  - PersonalRecordsSection (if applicable)
  - ExercisesList with all exercises and sets
  - NotesSection (if notes exist)
  - Action buttons
- **Handled interactions**:
  - Fetches session data on mount
  - Handles repeat workout action
  - Handles back navigation
- **Handled validation**: None
- **Types**: `SessionDetailData` (ViewModel)
- **Props**: None

### PageHeader
- **Description**: Top section with back navigation, workout name, and status badge.
- **Main elements**:
  - Back button/arrow (returns to history)
  - Workout plan name as heading
  - Status badge (Completed/Abandoned)
- **Handled interactions**:
  - `@click` on back - Navigate to history (with preserved filters)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `workoutName: string` - Name of the workout plan
  - `status: SessionStatusEnum` - Session status

### SessionMetaCard
- **Description**: Card displaying key session metrics at a glance.
- **Main elements**:
  - Date with day of week
  - Time started
  - Duration (formatted)
  - Total exercises performed
  - Total sets completed
  - Total volume lifted (optional)
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `SessionMeta` (ViewModel)
- **Props**:
  - `meta: SessionMeta` - Session metadata

### PersonalRecordsSection
- **Description**: Highlighted section showing PRs achieved during this session. Only shown if PRs exist.
- **Main elements**:
  - Section header with trophy icon
  - Grid of PersonalRecordCard components
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `SessionPR[]`
- **Props**:
  - `records: SessionPR[]` - Personal records achieved

### PersonalRecordCard
- **Description**: Individual card highlighting a personal record.
- **Main elements**:
  - Trophy or medal icon
  - Exercise name
  - Record type badge (1RM, Set Volume, Total Volume)
  - Record value with unit
- **Handled interactions**:
  - `@click` - Navigate to exercise detail or PR history (optional)
- **Handled validation**: None
- **Types**: `SessionPR`
- **Props**:
  - `record: SessionPR` - Personal record data

### ExercisesList
- **Description**: Scrollable list of all exercises performed in the session.
- **Main elements**:
  - ExerciseSection components for each exercise
  - Dividers between exercises
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: `ExercisePerformance[]`
- **Props**:
  - `exercises: ExercisePerformance[]` - All exercises with sets

### ExerciseSection
- **Description**: Single exercise display with header and sets table.
- **Main elements**:
  - ExerciseHeader with name and info
  - SetsTable showing all sets performed
- **Handled interactions**:
  - Expandable/collapsible (optional)
- **Handled validation**: None
- **Types**: `ExercisePerformance`
- **Props**:
  - `exercise: ExercisePerformance` - Exercise data with sets

### ExerciseHeader
- **Description**: Header row for an exercise with name, info button, and PR indicator.
- **Main elements**:
  - Exercise name
  - Info icon button (shows exercise details in slide-over)
  - PR indicator if any set was a PR
- **Handled interactions**:
  - `@click` on info icon - Open exercise detail slide-over
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `exerciseName: string` - Name of the exercise
  - `exerciseId: string` - Exercise ID for fetching details
  - `hasPR: boolean` - Whether any set was a PR

### SetsTable
- **Description**: Table displaying all sets performed for an exercise.
- **Main elements**:
  - Header row: Set, Weight, Reps
  - Data rows for each set
  - PR indicators on qualifying sets
  - Totals row (optional)
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `SetPerformance[]`
- **Props**:
  - `sets: SetPerformance[]` - All sets data
  - `unitSystem: 'metric' | 'imperial'` - For weight display

### SetRow
- **Description**: Single row in the sets table.
- **Main elements**:
  - Set number
  - Weight with unit (kg/lbs)
  - Reps count
  - PR badge if applicable
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: `SetPerformance`
- **Props**:
  - `set: SetPerformance` - Set data
  - `unit: string` - Weight unit

### NotesSection
- **Description**: Section displaying session notes if any were added.
- **Main elements**:
  - Section header "Notes"
  - Notes text (preserving line breaks)
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `notes: string` - Session notes

### ActionButtons
- **Description**: Bottom action section with primary and secondary actions.
- **Main elements**:
  - "Repeat Workout" primary button
  - "Delete Session" secondary/danger button (optional)
- **Handled interactions**:
  - `@click` on Repeat - Start new session with same workout
  - `@click` on Delete - Show confirmation, delete session
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `workoutPlanId: string` - For starting new session
  - `sessionId: string` - For deletion

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From workout_sessions.py
interface WorkoutSessionDetailResponse {
  id: string; // UUID
  workout_plan: WorkoutPlanBrief;
  status: SessionStatusEnum;
  exercise_sessions: ExerciseSessionDetail[];
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

interface WorkoutPlanBrief {
  id: string; // UUID
  name: string;
}

interface ExerciseSessionDetail {
  id: string; // UUID
  exercise: ExerciseBrief;
  set_number: int;
  weight: string; // Decimal as string
  reps: int;
  rest_time_seconds: int | null;
  created_at: string; // ISO datetime
}

interface ExerciseBrief {
  id: string; // UUID
  name: string;
}

// From personal_records.py
interface PersonalRecordListItem {
  id: string; // UUID
  exercise: PersonalRecordExerciseInfo;
  record_type: RecordTypeEnum;
  value: string; // Decimal as string
  unit: string | null;
  achieved_at: string; // ISO datetime
  exercise_session_id: string | null; // UUID
}

// Enums
type SessionStatusEnum = 'in_progress' | 'completed' | 'abandoned';
type RecordTypeEnum = '1rm' | 'set_volume' | 'total_volume';
```

### ViewModels (frontend-specific)

```typescript
// Session detail page data
interface SessionDetailData {
  session: SessionDetailInfo;
  isLoading: boolean;
  error: string | null;
}

// Main session info
interface SessionDetailInfo {
  id: string;
  workoutPlan: {
    id: string;
    name: string;
  };
  status: SessionStatusEnum;
  meta: SessionMeta;
  exercises: ExercisePerformance[];
  personalRecords: SessionPR[];
  notes: string | null;
}

// Session metadata for display
interface SessionMeta {
  date: Date;
  dateFormatted: string; // "Monday, January 15, 2025"
  timeFormatted: string; // "6:30 PM"
  durationSeconds: number;
  durationFormatted: string; // "1h 15m"
  exerciseCount: number;
  totalSets: number;
  totalVolume: number; // In user's preferred unit
  totalVolumeFormatted: string; // "2,500 kg" or "5,512 lbs"
}

// Exercise performance in session
interface ExercisePerformance {
  exerciseId: string;
  exerciseName: string;
  sets: SetPerformance[];
  hasPR: boolean;
  totalVolume: number;
  totalVolumeFormatted: string;
}

// Individual set performance
interface SetPerformance {
  id: string;
  setNumber: number;
  weight: number; // In user's preferred unit
  weightFormatted: string; // "135 lbs"
  reps: number;
  isPR: boolean;
  prType: RecordTypeEnum | null;
  restTimeSeconds: number | null;
}

// Personal record achieved in session
interface SessionPR {
  id: string;
  exerciseId: string;
  exerciseName: string;
  recordType: RecordTypeEnum;
  recordTypeLabel: string; // "1 Rep Max", "Set Volume", "Total Volume"
  value: number;
  valueFormatted: string; // "185 lbs" or "2,500 kg"
  unit: string;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const sessionStatusSchema = z.enum(['in_progress', 'completed', 'abandoned']);
const recordTypeSchema = z.enum(['1rm', 'set_volume', 'total_volume']);

const exerciseBriefSchema = z.object({
  id: z.string().uuid(),
  name: z.string()
});

const exerciseSessionDetailSchema = z.object({
  id: z.string().uuid(),
  exercise: exerciseBriefSchema,
  set_number: z.number().int().min(1),
  weight: z.string(), // Decimal as string
  reps: z.number().int().min(1),
  rest_time_seconds: z.number().int().nullable(),
  created_at: z.string().datetime()
});

const workoutSessionDetailResponseSchema = z.object({
  id: z.string().uuid(),
  workout_plan: z.object({
    id: z.string().uuid(),
    name: z.string()
  }),
  status: sessionStatusSchema,
  exercise_sessions: z.array(exerciseSessionDetailSchema),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime()
});

const personalRecordListItemSchema = z.object({
  id: z.string().uuid(),
  exercise: z.object({
    id: z.string().uuid(),
    name: z.string()
  }),
  record_type: recordTypeSchema,
  value: z.string(),
  unit: z.string().nullable(),
  achieved_at: z.string().datetime(),
  exercise_session_id: z.string().uuid().nullable()
});
```

## 6. State Management

### Local Component State (SessionDetailPage)

```typescript
const isLoading = ref(true);
const error = ref<string | null>(null);
const session = ref<SessionDetailInfo | null>(null);
const isStartingWorkout = ref(false);
const showDeleteConfirm = ref(false);
```

### Pinia Stores Used

```typescript
// profileStore - for unit system preference
interface ProfileStore {
  unitSystem: 'metric' | 'imperial';
  convertWeight(kg: number): number;
  formatWeight(kg: number): string;
}

// sessionStore - for starting new sessions
interface SessionStore {
  startSession(workoutPlanId: string): Promise<string>;
}
```

### Custom Composable: useSessionDetail

```typescript
// composables/useSessionDetail.ts
export function useSessionDetail(sessionId: string) {
  const router = useRouter();
  const profileStore = useProfileStore();
  
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const session = ref<SessionDetailInfo | null>(null);
  const isStartingWorkout = ref(false);
  
  // Fetch session data
  const fetchSession = async (): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const [sessionData, prsData] = await Promise.all([
        getWorkoutSessionDetail(sessionId),
        getPersonalRecordsForSession(sessionId)
      ]);
      
      session.value = transformToViewModel(sessionData, prsData, profileStore);
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  // Transform API response to view model
  const transformToViewModel = (
    data: WorkoutSessionDetailResponse,
    prs: PersonalRecordListItem[],
    profile: ProfileStore
  ): SessionDetailInfo => {
    // Group exercise sessions by exercise
    const exerciseMap = groupExercisesByExercise(data.exercise_sessions);
    
    // Calculate totals and format
    const exercises = Object.entries(exerciseMap).map(([exerciseId, sessions]) => {
      const sets = sessions.map(s => ({
        id: s.id,
        setNumber: s.set_number,
        weight: profile.convertWeight(parseFloat(s.weight)),
        weightFormatted: profile.formatWeight(parseFloat(s.weight)),
        reps: s.reps,
        isPR: prs.some(pr => pr.exercise_session_id === s.id),
        prType: prs.find(pr => pr.exercise_session_id === s.id)?.record_type ?? null,
        restTimeSeconds: s.rest_time_seconds
      }));
      
      return {
        exerciseId,
        exerciseName: sessions[0].exercise.name,
        sets,
        hasPR: sets.some(s => s.isPR),
        totalVolume: calculateTotalVolume(sets),
        totalVolumeFormatted: formatVolume(calculateTotalVolume(sets), profile)
      };
    });
    
    return {
      id: data.id,
      workoutPlan: data.workout_plan,
      status: data.status,
      meta: calculateMeta(data, exercises, profile),
      exercises,
      personalRecords: transformPRs(prs, profile),
      notes: null // Notes may come from a separate field
    };
  };
  
  // Start new workout with same plan
  const repeatWorkout = async (): Promise<void> => {
    if (!session.value) return;
    
    isStartingWorkout.value = true;
    
    try {
      const newSessionId = await startWorkoutSession(session.value.workoutPlan.id);
      router.push({ name: 'activeWorkout', params: { sessionId: newSessionId } });
    } catch (e) {
      showToast({ type: 'error', message: 'Failed to start workout' });
    } finally {
      isStartingWorkout.value = false;
    }
  };
  
  // Navigate back to history
  const goBack = (): void => {
    router.back();
  };
  
  return {
    isLoading,
    error,
    session,
    isStartingWorkout,
    fetchSession,
    repeatWorkout,
    goBack
  };
}
```

### Utility: Weight Conversion

```typescript
// composables/useUnitConversion.ts
export function useUnitConversion() {
  const profileStore = useProfileStore();
  
  const convertWeight = (kg: number): number => {
    if (profileStore.unitSystem === 'imperial') {
      return kg * 2.20462;
    }
    return kg;
  };
  
  const formatWeight = (kg: number): string => {
    const converted = convertWeight(kg);
    const unit = profileStore.unitSystem === 'imperial' ? 'lbs' : 'kg';
    return `${converted.toFixed(1)} ${unit}`;
  };
  
  const getRecordTypeLabel = (type: RecordTypeEnum): string => {
    const labels: Record<RecordTypeEnum, string> = {
      '1rm': '1 Rep Max',
      'set_volume': 'Set Volume',
      'total_volume': 'Total Volume'
    };
    return labels[type];
  };
  
  return {
    convertWeight,
    formatWeight,
    getRecordTypeLabel
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Workout Session Detail
```
GET /api/v1/workout-sessions/{session_id}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "workout_plan": {
      "id": "uuid-string",
      "name": "Push Day"
    },
    "status": "completed",
    "exercise_sessions": [
      {
        "id": "uuid-string",
        "exercise": { "id": "uuid", "name": "Bench Press" },
        "set_number": 1,
        "weight": "60.0",
        "reps": 10,
        "rest_time_seconds": 90,
        "created_at": "2025-01-15T18:05:00Z"
      },
      {
        "id": "uuid-string",
        "exercise": { "id": "uuid", "name": "Bench Press" },
        "set_number": 2,
        "weight": "70.0",
        "reps": 8,
        "rest_time_seconds": 90,
        "created_at": "2025-01-15T18:08:00Z"
      }
    ],
    "created_at": "2025-01-15T18:00:00Z",
    "updated_at": "2025-01-15T19:00:00Z"
  },
  "error": null
}
```

**Response (404 Not Found)**
```typescript
{
  "success": false,
  "data": null,
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "Workout session not found"
  }
}
```

#### 2. Get Personal Records for Session
```
GET /api/v1/personal-records?exercise_session_ids={sessionId}
```

**Note**: This may require a backend endpoint enhancement to filter PRs by the exercise session IDs from a workout session. Alternative: fetch all PRs and filter client-side, or include PRs in the session detail response.

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "records": [
      {
        "id": "uuid-string",
        "exercise": { "id": "uuid", "name": "Bench Press" },
        "record_type": "1rm",
        "value": "85.0",
        "unit": "kg",
        "achieved_at": "2025-01-15T18:08:00Z",
        "exercise_session_id": "uuid-string"
      }
    ],
    "pagination": { ... }
  },
  "error": null
}
```

#### 3. Start Workout Session (for Repeat)
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
    "started_at": "2025-01-16T10:00:00Z",
    "exercises": [...]
  },
  "error": null
}
```

#### 4. Delete Session (Optional)
```
DELETE /api/v1/workout-sessions/{session_id}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "deleted": true
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/sessions.ts
import axios from '@/lib/axios';
import type { 
  WorkoutSessionDetailResponse,
  WorkoutSessionStartResponse 
} from '@/types/workout-sessions';

export async function getWorkoutSessionDetail(
  sessionId: string
): Promise<WorkoutSessionDetailResponse> {
  const response = await axios.get<APIResponse<WorkoutSessionDetailResponse>>(
    `/api/v1/workout-sessions/${sessionId}`
  );
  return response.data.data;
}

export async function startWorkoutSession(
  workoutPlanId: string
): Promise<string> {
  const response = await axios.post<APIResponse<WorkoutSessionStartResponse>>(
    '/api/v1/workout-sessions/start',
    { workout_plan_id: workoutPlanId }
  );
  return response.data.data.session_id;
}

export async function deleteWorkoutSession(
  sessionId: string
): Promise<void> {
  await axios.delete(`/api/v1/workout-sessions/${sessionId}`);
}

// services/api/personal-records.ts
export async function getPersonalRecordsForSession(
  sessionId: string
): Promise<PersonalRecordListItem[]> {
  // This may need a different approach based on backend support
  // Option 1: Filter by workout_session_id if supported
  // Option 2: Get all PRs and filter client-side by date range
  const response = await axios.get<APIResponse<PersonalRecordListResponse>>(
    '/api/v1/personal-records',
    { params: { workout_session_id: sessionId } }
  );
  return response.data.data.records;
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | SessionDetailPage | `onMounted` | Fetch session and PRs data |
| Click back | PageHeader | `goBack()` | Navigate to history (router.back) |
| Click exercise info | ExerciseHeader | `showExerciseDetail()` | Open exercise info slide-over |
| Click Repeat Workout | ActionButtons | `repeatWorkout()` | Start new session, navigate to active workout |
| Click Delete | ActionButtons | `showDeleteConfirm` | Show confirmation dialog |
| Confirm Delete | DeleteConfirmDialog | `deleteSession()` | Delete session, navigate to history |
| Cancel Delete | DeleteConfirmDialog | Close dialog | Hide dialog, no action |

### Detailed Interaction Flow

1. **Initial Load**:
   - Extract sessionId from route params
   - Show loading skeleton
   - Fetch session detail and PRs in parallel
   - Transform data to view model with unit conversion
   - Group exercises and calculate totals
   - Display session content

2. **Repeat Workout**:
   - User clicks "Repeat Workout"
   - Button shows loading state
   - Call POST to start new session
   - On success, navigate to active workout view
   - On error, show toast error

3. **Back Navigation**:
   - User clicks back button
   - Use router.back() to return to history
   - Filter state should be preserved in URL

4. **Exercise Info**:
   - User clicks info icon on exercise
   - Open slide-over panel with exercise details
   - Show exercise description, target muscles, equipment

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | SessionContent |
| error exists | ErrorState | SessionContent |
| Session loaded | SessionContent | LoadingSkeleton, ErrorState |
| PRs exist (length > 0) | PersonalRecordsSection | - |
| No PRs | - | PersonalRecordsSection |
| Notes exist | NotesSection | - |
| No notes | - | NotesSection |
| Status = completed | Green status badge | - |
| Status = abandoned | Gray/red status badge | - |

### Status-based Styling

| Status | Badge Color | Badge Text | Icon |
|--------|-------------|------------|------|
| completed | Green | "Completed" | Checkmark |
| abandoned | Gray/Red | "Abandoned" | X or minus |
| in_progress | Blue | "In Progress" | Clock |

## 10. Error Handling

### API Error Handling

```typescript
async function fetchSession(): Promise<void> {
  isLoading.value = true;
  error.value = null;
  
  try {
    const [sessionData, prsData] = await Promise.allSettled([
      getWorkoutSessionDetail(sessionId),
      getPersonalRecordsForSession(sessionId)
    ]);
    
    if (sessionData.status === 'rejected') {
      throw sessionData.reason;
    }
    
    // PRs failing is non-critical
    const prs = prsData.status === 'fulfilled' ? prsData.value : [];
    
    session.value = transformToViewModel(sessionData.value, prs, profileStore);
    
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const status = e.response?.status;
      const code = e.response?.data?.error?.code;
      
      if (status === 404) {
        error.value = 'Workout session not found.';
        // Could redirect to history after delay
      } else if (status === 403) {
        error.value = 'You do not have access to this session.';
        router.push({ name: 'history' });
      } else if (status === 401) {
        // Handled by interceptor
        return;
      } else {
        error.value = 'Failed to load session details. Please try again.';
      }
    } else {
      error.value = 'An unexpected error occurred.';
    }
  } finally {
    isLoading.value = false;
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Not found | 404 | "Workout session not found." | Show error, back to history link |
| Forbidden | 403 | "You don't have access to this session." | Redirect to history |
| Auth expired | 401 | Auto-redirect to login | Redirect via interceptor |
| Server error | 500 | "Failed to load session. Please try again." | Retry button |
| Network error | - | "Unable to connect. Check your connection." | Retry button |

### Repeat Workout Error Handling

```typescript
async function repeatWorkout(): Promise<void> {
  if (!session.value) return;
  
  isStartingWorkout.value = true;
  
  try {
    const newSessionId = await startWorkoutSession(session.value.workoutPlan.id);
    router.push({ name: 'activeWorkout', params: { sessionId: newSessionId } });
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const code = e.response?.data?.error?.code;
      
      if (code === 'SESSION_IN_PROGRESS') {
        showToast({
          type: 'warning',
          message: 'You have a workout in progress. Finish or discard it first.',
          action: {
            label: 'Go to Workout',
            handler: () => router.push({ name: 'dashboard' })
          }
        });
      } else if (code === 'PLAN_NOT_FOUND') {
        showToast({
          type: 'error',
          message: 'This workout plan no longer exists.'
        });
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

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/session-detail.ts` with ViewModels
   - Add Zod schemas for API response validation
   - Create utility types for transformed data

2. **Create API Service Functions**
   - Add `getWorkoutSessionDetail` to `src/services/api/sessions.ts`
   - Add `getPersonalRecordsForSession` to `src/services/api/personal-records.ts`
   - Handle error responses appropriately

3. **Create Composables**
   - Create `src/composables/useSessionDetail.ts`
   - Implement data transformation logic
   - Implement repeat workout functionality

4. **Create Utility Components**
   - Create/update `src/components/common/StatusBadge.vue`
   - Create `src/components/common/PRBadge.vue` (small PR indicator)

5. **Create Session Detail Components**
   - Create `src/components/session/SessionMetaCard.vue`
   - Create `src/components/session/PersonalRecordsSection.vue`
   - Create `src/components/session/PersonalRecordCard.vue`
   - Create `src/components/session/ExercisesList.vue`
   - Create `src/components/session/ExerciseSection.vue`
   - Create `src/components/session/SetsTable.vue`
   - Create `src/components/session/NotesSection.vue`

6. **Create Page View**
   - Create `src/views/SessionDetailPage.vue`
   - Wire up all components with composable
   - Implement action buttons

7. **Configure Router**
   - Add session detail route to `src/router/index.ts`
   - Set up param handling for sessionId

8. **Add Loading and Error States**
   - Create skeleton loader matching layout
   - Create error state with retry
   - Create 404 state for not found

9. **Style with Tailwind**
   - Apply card styling for meta and PRs
   - Style sets table with proper spacing
   - Add PR highlighting (gold/yellow accents)
   - Support dark mode

10. **Add Unit Conversion**
    - Integrate with profile store for unit preference
    - Convert weights from kg to lbs if imperial
    - Format weights with appropriate precision

11. **Add Accessibility**
    - Ensure proper table semantics
    - Add ARIA labels for badges and icons
    - Implement focus management
    - Support keyboard navigation

12. **Write Tests**
    - Unit tests for data transformation
    - Unit tests for unit conversion
    - Component tests for key components
    - Integration test for page flow

13. **Manual Testing**
    - Test with various session types
    - Test PR display
    - Test repeat workout flow
    - Test error states
    - Test on mobile and desktop
