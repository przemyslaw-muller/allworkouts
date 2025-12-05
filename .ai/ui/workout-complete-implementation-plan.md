# View Implementation Plan: Workout Completion Summary

## 1. Overview

The Workout Completion Summary page is a celebratory view displayed immediately after completing a workout. It shows key achievements from the session including total duration, volume lifted, exercises and sets completed, and most importantly highlights any new personal records achieved. The page provides a positive reinforcement experience to motivate users and includes options to add notes or navigate to the session detail or return home.

## 2. View Routing

- **Path**: `/workout/:sessionId/complete`
- **Route Name**: `workoutComplete`
- **Access**: Authenticated users only
- **Guard**:
  - Redirect to `/login` if not authenticated
  - Redirect to `/dashboard` if session doesn't exist
  - Session must be in `completed` status
- **Route Params**:
  - `sessionId` (UUID): The completed workout session ID
- **Navigation Notes**:
  - Primary entry is from Active Workout page after completing
  - Completion data may be passed via router state to avoid extra API call
  - Can be accessed directly via URL (will fetch data)

## 3. Component Structure

```
WorkoutCompletePage (view)
├── ConfettiAnimation (celebratory effect)
├── CompletionHeader
│   ├── CheckmarkIcon (animated)
│   ├── CongratulationsText
│   └── WorkoutName
├── SummaryStatsGrid
│   ├── DurationStat
│   │   ├── ClockIcon
│   │   ├── Duration value
│   │   └── Label "Duration"
│   ├── ExercisesStat
│   │   ├── DumbbellIcon
│   │   ├── Exercise count value
│   │   └── Label "Exercises"
│   ├── SetsStat
│   │   ├── LayersIcon
│   │   ├── Sets count value
│   │   └── Label "Sets"
│   └── VolumeStat
│       ├── WeightIcon
│       ├── Total volume value
│       └── Label "Volume"
├── PersonalRecordsSection (conditional - if PRs achieved)
│   ├── SectionHeader (with trophy icon)
│   └── PRCardList
│       └── PRCard (for each PR)
│           ├── TrophyBadge
│           ├── ExerciseName
│           ├── RecordType
│           └── RecordValue
├── NotesSection
│   ├── SectionHeader
│   ├── NotesTextarea (if not yet added)
│   └── SaveNotesButton
├── ActionButtons
│   ├── ViewDetailsButton (secondary)
│   └── DoneButton (primary)
└── LoadingState / ErrorState
```

## 4. Component Details

### WorkoutCompletePage
- **Description**: Main view for post-workout celebration and summary. Shows completion stats, PRs, and allows adding notes.
- **Main elements**:
  - Celebratory confetti animation on load
  - Animated checkmark header
  - Grid of summary stats
  - Personal records highlight (if any)
  - Notes input (optional)
  - Navigation buttons
- **Handled interactions**:
  - Initializes from router state or fetches data
  - Saves session notes
  - Navigates to session detail or dashboard
- **Handled validation**: Notes length validation
- **Types**: `WorkoutCompletionData`
- **Props**: None

### ConfettiAnimation
- **Description**: Celebratory confetti effect that plays when the page loads to create positive reinforcement.
- **Main elements**:
  - Canvas-based confetti particles
  - Colorful falling animation
  - Auto-dismisses after a few seconds
- **Handled interactions**: None (visual effect only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `duration?: number` - Duration of animation in ms (default 3000)
  - `particleCount?: number` - Number of particles (default 100)

### CompletionHeader
- **Description**: Hero section with congratulatory message and workout name.
- **Main elements**:
  - Large animated checkmark icon (bounces in)
  - "Workout Complete!" or "Great Job!" heading
  - Workout plan name as subheading
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `workoutName: string` - Name of the completed workout

### SummaryStatsGrid
- **Description**: Grid displaying key workout metrics in an easy-to-scan format.
- **Main elements**:
  - 2x2 grid on mobile, 4-column on desktop
  - Each stat with icon, value, and label
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `WorkoutSummaryStats`
- **Props**:
  - `stats: WorkoutSummaryStats` - Summary statistics

### DurationStat
- **Description**: Single stat card showing workout duration.
- **Main elements**:
  - Clock icon
  - Formatted duration (e.g., "45 min" or "1h 12m")
  - "Duration" label
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `durationSeconds: number` - Total duration in seconds

### ExercisesStat
- **Description**: Single stat card showing exercise count.
- **Main elements**:
  - Dumbbell icon
  - Exercise count value
  - "Exercises" label
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `count: number` - Number of exercises completed

### SetsStat
- **Description**: Single stat card showing total sets completed.
- **Main elements**:
  - Layers/stack icon
  - Sets count value
  - "Sets" label
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `count: number` - Number of sets completed

### VolumeStat
- **Description**: Single stat card showing total volume lifted.
- **Main elements**:
  - Weight/barbell icon
  - Formatted volume with unit (e.g., "5,280 lbs" or "2,400 kg")
  - "Volume" label
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `volumeKg: number` - Total volume in kg
  - `unitSystem: UnitSystemEnum` - User's unit preference

### PersonalRecordsSection
- **Description**: Highlighted section celebrating new PRs. Only shown if records were achieved.
- **Main elements**:
  - Section header with trophy icon and "New Personal Records!" text
  - List/grid of PR cards
- **Handled interactions**: None at container level
- **Handled validation**: None
- **Types**: `NewPersonalRecordInfo[]`
- **Props**:
  - `records: NewPersonalRecordInfo[]` - List of PRs achieved

### PRCard
- **Description**: Individual card highlighting a specific personal record.
- **Main elements**:
  - Trophy/medal icon with glow effect
  - Exercise name
  - Record type badge (1RM, Set Volume, Total Volume)
  - Record value with unit
  - Optional: improvement from previous (e.g., "+5 lbs")
- **Handled interactions**:
  - `@click` - Navigate to exercise history (optional)
- **Handled validation**: None
- **Types**: `NewPersonalRecordInfo`
- **Props**:
  - `record: NewPersonalRecordInfo` - Personal record data

### NotesSection
- **Description**: Optional section for adding workout notes/reflections.
- **Main elements**:
  - "Add Notes" header
  - Textarea for notes input
  - Save button (if modified)
  - Character count indicator
- **Handled interactions**:
  - `@input` on textarea - Track changes
  - `@click` on save - Save notes to session
- **Handled validation**:
  - Max 500 characters
- **Types**: None
- **Props**:
  - `initialNotes?: string` - Pre-existing notes
  - `sessionId: string` - Session ID for saving

### ActionButtons
- **Description**: Bottom action buttons for navigation.
- **Main elements**:
  - "View Details" secondary button
  - "Done" primary button
- **Handled interactions**:
  - `@click` on View Details - Navigate to session detail
  - `@click` on Done - Navigate to dashboard
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `sessionId: string` - For navigation to detail

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From workout_sessions.py - CompleteSessionResponse
interface CompleteSessionResponse {
  session_id: string; // UUID
  status: SessionStatusEnum;
  duration_seconds: number;
  new_personal_records: NewPersonalRecordInfo[];
}

interface NewPersonalRecordInfo {
  exercise_name: string;
  record_type: RecordTypeEnum;
  value: string; // Decimal as string
  unit: string | null;
}

// Enums
type SessionStatusEnum = 'in_progress' | 'completed' | 'abandoned';
type RecordTypeEnum = '1rm' | 'set_volume' | 'total_volume';

// Session detail for additional stats (if fetching)
interface WorkoutSessionDetailResponse {
  id: string;
  workout_plan: {
    id: string;
    name: string;
  } | null;
  status: SessionStatusEnum;
  notes: string | null;
  created_at: string;
  updated_at: string;
  exercises: ExercisePerformanceDTO[];
}

interface ExercisePerformanceDTO {
  exercise: {
    id: string;
    name: string;
  };
  sets: {
    set_number: number;
    reps: number;
    weight: string;
  }[];
}
```

### ViewModels (frontend-specific)

```typescript
// Main completion data
interface WorkoutCompletionData {
  sessionId: string;
  workoutPlanName: string;
  status: SessionStatusEnum;
  completedAt: Date;
  durationSeconds: number;
  durationFormatted: string;
  exerciseCount: number;
  setsCount: number;
  totalVolumeKg: number;
  totalVolumeFormatted: string;
  personalRecords: PRViewModel[];
  notes: string | null;
}

// Summary stats for grid
interface WorkoutSummaryStats {
  duration: {
    seconds: number;
    formatted: string;
  };
  exercises: number;
  sets: number;
  volume: {
    kg: number;
    formatted: string;
  };
}

// Personal record view model
interface PRViewModel {
  exerciseName: string;
  recordType: RecordTypeEnum;
  recordTypeLabel: string; // "1 Rep Max", "Set Volume", "Total Volume"
  value: number;
  valueFormatted: string; // e.g., "185 lbs" or "85 kg"
}

// Notes form state
interface NotesFormState {
  text: string;
  isDirty: boolean;
  isSaving: boolean;
  characterCount: number;
  maxCharacters: number;
}
```

### Zod Validation Schemas

```typescript
import { z } from 'zod';

// Notes validation
const notesSchema = z.object({
  notes: z.string().max(500, 'Notes must be 500 characters or less').optional()
});

// Complete session response validation
const newPRInfoSchema = z.object({
  exercise_name: z.string(),
  record_type: z.enum(['1rm', 'set_volume', 'total_volume']),
  value: z.string().regex(/^\d+(\.\d+)?$/),
  unit: z.string().nullable()
});

const completeSessionResponseSchema = z.object({
  session_id: z.string().uuid(),
  status: z.enum(['in_progress', 'completed', 'abandoned']),
  duration_seconds: z.number().int().min(0),
  new_personal_records: z.array(newPRInfoSchema)
});

// Router state schema (for data passed from active workout)
const routerCompletionStateSchema = z.object({
  completionData: completeSessionResponseSchema.optional()
});
```

## 6. State Management

### Local Component State (WorkoutCompletePage)

```typescript
const route = useRoute();
const router = useRouter();
const sessionId = computed(() => route.params.sessionId as string);

// Loading and error state
const isLoading = ref(true);
const error = ref<string | null>(null);

// Completion data
const completionData = ref<WorkoutCompletionData | null>(null);

// Notes form state
const notes = ref('');
const isNotesDirty = ref(false);
const isSavingNotes = ref(false);

// Animation state
const showConfetti = ref(true);
const showContent = ref(false);
```

### Pinia Stores Used

```typescript
// profileStore - for unit system
interface ProfileStore {
  unitSystem: 'metric' | 'imperial';
  convertWeight(kg: number): number;
  formatWeight(kg: number): string;
}

// sessionStore - for session data (optional)
interface SessionStore {
  // May have completion data cached from active workout
  lastCompletionData: CompleteSessionResponse | null;
  clearLastCompletion(): void;
}
```

### Custom Composable: useWorkoutCompletion

```typescript
// composables/useWorkoutCompletion.ts
export function useWorkoutCompletion(sessionId: string) {
  const route = useRoute();
  const profileStore = useProfileStore();
  
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const completionData = ref<WorkoutCompletionData | null>(null);
  
  // Initialize from router state or fetch
  const initialize = async (): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      // Check if data was passed via router state
      const routerState = history.state?.completionData as CompleteSessionResponse | undefined;
      
      if (routerState) {
        // Use passed data and fetch additional details
        const sessionDetail = await getSessionDetail(sessionId);
        completionData.value = transformToViewModel(routerState, sessionDetail, profileStore);
      } else {
        // Fetch all data
        const sessionDetail = await getSessionDetail(sessionId);
        
        // Validate session is completed
        if (sessionDetail.status !== 'completed') {
          throw new Error('Session is not completed');
        }
        
        // Fetch PRs for this session
        const sessionPRs = await getSessionPersonalRecords(sessionId);
        
        completionData.value = buildCompletionData(sessionDetail, sessionPRs, profileStore);
      }
      
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  // Save notes
  const saveNotes = async (notesText: string): Promise<void> => {
    try {
      await updateSessionNotes(sessionId, { notes: notesText });
      if (completionData.value) {
        completionData.value.notes = notesText;
      }
    } catch (e) {
      throw e;
    }
  };
  
  return {
    isLoading,
    error,
    completionData,
    initialize,
    saveNotes
  };
}

// Transform API response to view model
function transformToViewModel(
  completion: CompleteSessionResponse,
  detail: WorkoutSessionDetailResponse,
  profileStore: ProfileStore
): WorkoutCompletionData {
  // Calculate totals from detail
  let totalSets = 0;
  let totalVolumeKg = 0;
  
  for (const exercise of detail.exercises) {
    for (const set of exercise.sets) {
      totalSets++;
      totalVolumeKg += parseFloat(set.weight) * set.reps;
    }
  }
  
  return {
    sessionId: completion.session_id,
    workoutPlanName: detail.workout_plan?.name || 'Quick Workout',
    status: completion.status,
    completedAt: new Date(detail.updated_at),
    durationSeconds: completion.duration_seconds,
    durationFormatted: formatDuration(completion.duration_seconds),
    exerciseCount: detail.exercises.length,
    setsCount: totalSets,
    totalVolumeKg,
    totalVolumeFormatted: profileStore.formatWeight(totalVolumeKg),
    personalRecords: completion.new_personal_records.map(pr => ({
      exerciseName: pr.exercise_name,
      recordType: pr.record_type,
      recordTypeLabel: getRecordTypeLabel(pr.record_type),
      value: parseFloat(pr.value),
      valueFormatted: formatRecordValue(pr, profileStore)
    })),
    notes: detail.notes
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Session Detail
```
GET /api/v1/workout-sessions/{session_id}
```

Used when completion data is not passed via router state.

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "workout_plan": {
      "id": "uuid-string",
      "name": "Push Day A"
    },
    "status": "completed",
    "notes": "Great workout!",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:15:00Z",
    "exercises": [
      {
        "exercise": { "id": "uuid", "name": "Bench Press" },
        "sets": [
          { "set_number": 1, "reps": 10, "weight": "60.0" }
        ]
      }
    ]
  },
  "error": null
}
```

#### 2. Get Session Personal Records
```
GET /api/v1/personal-records?session_id={session_id}
```

Fetches PRs achieved in a specific session.

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "exercise": { "id": "uuid", "name": "Bench Press" },
      "record_type": "1rm",
      "value": "85.0",
      "achieved_at": "2024-01-15T11:00:00Z"
    }
  ],
  "error": null
}
```

#### 3. Update Session Notes
```
PATCH /api/v1/workout-sessions/{session_id}
```

**Request**
```typescript
{
  "notes": "Felt strong today. Increased bench by 5 lbs."
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "notes": "Felt strong today. Increased bench by 5 lbs."
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/workout.ts

export async function getSessionDetail(sessionId: string): Promise<WorkoutSessionDetailResponse> {
  const response = await axios.get<APIResponse<WorkoutSessionDetailResponse>>(
    `/api/v1/workout-sessions/${sessionId}`
  );
  return response.data.data;
}

export async function getSessionPersonalRecords(sessionId: string): Promise<PersonalRecordResponse[]> {
  const response = await axios.get<APIResponse<PersonalRecordResponse[]>>(
    '/api/v1/personal-records',
    { params: { session_id: sessionId } }
  );
  return response.data.data;
}

export async function updateSessionNotes(
  sessionId: string,
  data: { notes: string }
): Promise<void> {
  await axios.patch(`/api/v1/workout-sessions/${sessionId}`, data);
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | WorkoutCompletePage | `onMounted` | Show confetti, load completion data, animate in content |
| Confetti ends | ConfettiAnimation | `@animationend` | Fade out confetti layer |
| Type notes | NotesTextarea | `v-model` | Update notes text, mark as dirty |
| Click save notes | SaveNotesButton | `saveNotes()` | Save notes to session via API |
| Click View Details | ViewDetailsButton | `router.push()` | Navigate to session detail page |
| Click Done | DoneButton | `router.push()` | Navigate to dashboard |
| Click PR card | PRCard | `navigateToExercise()` | Navigate to exercise history (optional) |

### Detailed Interaction Flow

1. **Page Load Animation Sequence**:
   - Confetti starts immediately
   - Checkmark icon bounces in (0.3s delay)
   - Summary stats fade in with stagger (0.5s delay)
   - PR cards slide in (0.8s delay)
   - Notes and buttons appear (1s delay)

2. **Notes Saving Flow**:
   - User types in textarea
   - Character count updates live
   - "Save" button appears when dirty
   - Click save - show loading state
   - On success - hide save button, show brief success indicator
   - On error - show error toast, keep save button

3. **Navigation Flow**:
   - "View Details" goes to `/history/{sessionId}`
   - "Done" goes to `/dashboard`
   - Both clear any cached completion state

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingState | All content |
| Error exists | ErrorState | All content |
| personalRecords.length > 0 | PersonalRecordsSection | - |
| personalRecords.length = 0 | - | PersonalRecordsSection |
| isNotesDirty = true | SaveNotesButton | - |
| isSavingNotes = true | SaveNotesButton (loading) | - |
| showConfetti = true | ConfettiAnimation | - |

### Input Validation

| Field | Validation | Error Message |
|-------|------------|---------------|
| Notes | Max 500 characters | "Notes must be 500 characters or less" |

## 10. Error Handling

### API Error Handling

```typescript
async function initialize(): Promise<void> {
  try {
    // ... fetch data ...
  } catch (e) {
    if (axios.isAxiosError(e)) {
      if (e.response?.status === 404) {
        error.value = 'Session not found';
      } else if (e.response?.status === 403) {
        error.value = 'You do not have access to this session';
      } else {
        error.value = 'Failed to load workout summary';
      }
    } else {
      error.value = 'An unexpected error occurred';
    }
  }
}

async function saveNotes(text: string): Promise<void> {
  try {
    await updateSessionNotes(sessionId, { notes: text });
    showToast({ type: 'success', message: 'Notes saved' });
  } catch (e) {
    showToast({ type: 'error', message: 'Failed to save notes' });
    throw e; // Keep form dirty
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Session not found | 404 | "Session not found" | Show error with dashboard link |
| Access denied | 403 | "You do not have access to this session" | Show error with dashboard link |
| Session not completed | - | "Session is not completed yet" | Redirect to active workout |
| Network error | - | "Connection error. Please try again." | Show retry button |
| Server error | 500 | "Something went wrong" | Show retry button |
| Notes save failed | 4xx/5xx | "Failed to save notes" | Toast, keep form dirty |

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/workout-completion.ts` with ViewModels
   - Add Zod validation schemas
   - Create DTOs that match backend

2. **Create Utility Functions**
   - Create `src/utils/formatDuration.ts` for duration formatting
   - Create `src/utils/formatRecordType.ts` for PR type labels
   - Add to existing weight formatting utils

3. **Create Composables**
   - Create `src/composables/useWorkoutCompletion.ts`
   - Handle router state and API fetching
   - Include notes saving logic

4. **Create Animation Components**
   - Create `src/components/common/ConfettiAnimation.vue`
   - Create `src/components/common/AnimatedCheckmark.vue`
   - Use CSS animations or canvas for confetti

5. **Create Stats Components**
   - Create `src/components/workout/SummaryStatsGrid.vue`
   - Create `src/components/workout/StatCard.vue`
   - Style with icons and responsive grid

6. **Create PR Components**
   - Create `src/components/workout/PersonalRecordsSection.vue`
   - Create `src/components/workout/PRCard.vue`
   - Add trophy icon and highlighting

7. **Create Notes Components**
   - Create `src/components/workout/NotesSection.vue`
   - Include textarea, character count, save button
   - Handle dirty state and saving

8. **Create Header Component**
   - Create `src/components/workout/CompletionHeader.vue`
   - Animated checkmark
   - Congratulatory text

9. **Create Page View**
   - Create `src/views/WorkoutCompletePage.vue`
   - Orchestrate all components
   - Implement animation sequence

10. **Configure Router**
    - Add route `/workout/:sessionId/complete`
    - Add navigation guard for session status
    - Handle router state for completion data

11. **Add API Integration**
    - Implement getSessionDetail
    - Implement getSessionPersonalRecords
    - Implement updateSessionNotes

12. **Style with Tailwind**
    - Celebratory color palette (greens, golds for PRs)
    - Responsive stat grid (2x2 mobile, 1x4 desktop)
    - Smooth entrance animations
    - Dark mode support

13. **Add Accessibility**
    - ARIA live region for confetti (decorative)
    - Focus management after animations
    - Screen reader announcements for PRs
    - Keyboard navigation for buttons

14. **Write Tests**
    - Unit tests for composables
    - Unit tests for formatters
    - Component tests for stats display
    - Integration test for complete flow

15. **Manual Testing**
    - Test with various PR counts (0, 1, many)
    - Test animation sequence
    - Test notes saving
    - Test direct URL access
    - Test on mobile devices
