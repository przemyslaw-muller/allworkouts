# View Implementation Plan: Active Workout Session

## 1. Overview

The Active Workout Session page is the core real-time workout logging interface. It provides a mobile-first design optimized for gym use with large touch targets, pre-filled values from previous sessions, a rest timer with audio alerts, and progress tracking. This view handles logging individual sets, showing historical context for each exercise, and managing the workout session flow from start to completion.

## 2. View Routing

- **Path**: `/workout/:sessionId`
- **Route Name**: `activeWorkout`
- **Access**: Authenticated users only
- **Guard**:
  - Redirect to `/login` if not authenticated
  - Redirect to `/dashboard` if session doesn't exist or is already completed
  - Session must be in `in_progress` status
- **Route Params**:
  - `sessionId` (UUID): The active workout session ID
- **Navigation Guards**:
  - `beforeRouteLeave`: Show confirmation if workout incomplete

## 3. Component Structure

```
ActiveWorkoutPage (view)
├── WorkoutHeader (fixed)
│   ├── WorkoutTitle
│   ├── ElapsedTimer
│   └── ExitButton
├── ExerciseAccordion (scrollable)
│   ├── ExercisePanel (for each exercise)
│   │   ├── ExercisePanelHeader
│   │   │   ├── StatusIcon (completed/current/pending)
│   │   │   ├── ExerciseName
│   │   │   ├── ExerciseInfoButton
│   │   │   └── ExpandIcon
│   │   └── ExercisePanelContent (when expanded)
│   │       ├── PreviousSessionContext
│   │       │   ├── LastSessionInfo
│   │       │   └── PersonalRecordInfo (if exists)
│   │       ├── SetsList
│   │       │   ├── CompletedSetRow (for logged sets)
│   │       │   │   ├── SetNumber
│   │       │   │   ├── Weight (readonly)
│   │       │   │   ├── Reps (readonly)
│   │       │   │   └── EditButton
│   │       │   └── ActiveSetRow (for current set)
│   │       │       ├── SetNumber
│   │       │       ├── WeightInput
│   │       │       ├── RepsInput
│   │       │       └── LogSetButton
│   │       └── AddSetButton
├── RestTimer (floating, conditional)
│   ├── TimerDisplay (countdown)
│   ├── ProgressRing
│   ├── AddTimeButton (+30s)
│   ├── SkipButton
│   └── AudioToggle
├── WorkoutFooter (fixed)
│   ├── ProgressBar
│   ├── ProgressText
│   └── CompleteWorkoutButton
├── ExitConfirmDialog
├── EditSetDialog
└── ExerciseInfoSlideOver
```

## 4. Component Details

### ActiveWorkoutPage
- **Description**: Main orchestrating component for active workout. Manages session state, localStorage persistence, and coordinates all child components.
- **Main elements**:
  - Fixed header with timer
  - Scrollable exercise accordion
  - Floating rest timer
  - Fixed footer with progress and complete button
  - Various dialogs
- **Handled interactions**:
  - Initializes session from API or localStorage
  - Persists state to localStorage on changes
  - Syncs with backend on set logs
  - Manages rest timer lifecycle
- **Handled validation**: None at page level
- **Types**: `ActiveWorkoutState`
- **Props**: None

### WorkoutHeader
- **Description**: Fixed header showing workout info, elapsed time, and exit action.
- **Main elements**:
  - Workout/Plan name
  - Elapsed timer (counts up from session start)
  - Exit button (X icon)
- **Handled interactions**:
  - `@click` on exit - Show exit confirmation dialog
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `workoutName: string`
  - `startedAt: Date`

### ElapsedTimer
- **Description**: Live timer showing how long the workout has been in progress.
- **Main elements**:
  - Time display (HH:MM:SS or MM:SS)
  - Updates every second
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `startedAt: Date`

### ExerciseAccordion
- **Description**: Accordion list of all exercises in the workout. Only one panel expanded at a time (current exercise).
- **Main elements**:
  - ExercisePanel components for each exercise
  - Scroll behavior to keep current exercise visible
- **Handled interactions**:
  - `@expand` - Expand selected panel, collapse others
- **Handled validation**: None
- **Types**: `ExerciseWithSets[]`
- **Props**:
  - `exercises: ExerciseWithSets[]`
  - `currentExerciseIndex: number`

### ExercisePanel
- **Description**: Single expandable panel for an exercise.
- **Main elements**:
  - ExercisePanelHeader (always visible)
  - ExercisePanelContent (visible when expanded)
- **Handled interactions**:
  - `@click` on header - Toggle expand
- **Handled validation**: None
- **Types**: `ExerciseWithSets`
- **Props**:
  - `exercise: ExerciseWithSets`
  - `isExpanded: boolean`
  - `status: 'completed' | 'current' | 'pending'`

### ExercisePanelHeader
- **Description**: Header row for exercise panel showing status, name, and expand control.
- **Main elements**:
  - Status icon (green check for completed, blue dot for current, gray for pending)
  - Exercise name
  - Info button (i icon)
  - Expand/collapse chevron
- **Handled interactions**:
  - `@click` on info - Show exercise info slide-over
  - `@click` on header - Toggle expand
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `exerciseName: string`
  - `exerciseId: string`
  - `status: 'completed' | 'current' | 'pending'`
  - `isExpanded: boolean`
  - `completedSets: number`
  - `totalSets: number`

### PreviousSessionContext
- **Description**: Shows historical context for the exercise - what the user did last time and their PR.
- **Main elements**:
  - "Last time" label with date
  - Summary of last session (sets × weight × reps)
  - PR indicator if exists (e.g., "PR: 185 lbs × 5")
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `ExerciseContextInfo`
- **Props**:
  - `context: ExerciseContextInfo`
  - `unitSystem: 'metric' | 'imperial'`

### SetsList
- **Description**: List of all sets for an exercise - completed sets (readonly) and active set (input).
- **Main elements**:
  - CompletedSetRow components for logged sets
  - ActiveSetRow for current set input
- **Handled interactions**: None at container level
- **Handled validation**: None
- **Types**: `SetData[]`
- **Props**:
  - `sets: SetData[]`
  - `plannedSets: number`
  - `currentSetIndex: number`

### CompletedSetRow
- **Description**: Readonly row showing a logged set with edit option.
- **Main elements**:
  - Set number badge
  - Weight display
  - Reps display
  - Edit pencil icon button
- **Handled interactions**:
  - `@click` on edit - Open edit set dialog
- **Handled validation**: None
- **Types**: `CompletedSet`
- **Props**:
  - `set: CompletedSet`
  - `unit: string`

### ActiveSetRow
- **Description**: Input row for logging the current set. Has large touch targets for gym use.
- **Main elements**:
  - Set number indicator
  - Weight input (number, large, pre-filled)
  - Reps input (number, large, pre-filled)
  - "Log Set" button (large, primary)
  - Quick increment/decrement buttons for weight and reps
- **Handled interactions**:
  - `@input` on weight/reps - Update local values
  - `@click` on Log Set - Log the set, start rest timer
  - `@click` on +/- buttons - Increment/decrement values
- **Handled validation**:
  - Weight must be >= 0
  - Reps must be >= 1
- **Types**: `SetInput`
- **Props**:
  - `setNumber: number`
  - `defaultWeight: number`
  - `defaultReps: number`
  - `unit: string`
  - `isLogging: boolean`
- **Events**:
  - `@log` - Set logged with weight and reps

### AddSetButton
- **Description**: Button to add an extra set beyond the planned sets.
- **Main elements**:
  - "+ Add Set" button
- **Handled interactions**:
  - `@click` - Add new set row
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `disabled: boolean` - Disable if max sets reached

### RestTimer
- **Description**: Floating countdown timer that appears after logging a set. Shows remaining rest time with visual progress.
- **Main elements**:
  - Countdown display (MM:SS)
  - Circular progress ring
  - "+30s" button to add time
  - "Skip" button to dismiss
  - Audio toggle button
  - Pulses/vibrates when timer ends
- **Handled interactions**:
  - `@click` on +30s - Add 30 seconds
  - `@click` on Skip - Dismiss timer
  - `@click` on audio - Toggle audio alerts
  - Timer end - Play audio, vibrate if supported
- **Handled validation**: None
- **Types**: `RestTimerState`
- **Props**:
  - `seconds: number` - Remaining seconds
  - `totalSeconds: number` - Total rest time
  - `isAudioEnabled: boolean`
- **Events**:
  - `@complete` - Timer finished
  - `@skip` - Timer skipped
  - `@add-time` - Add time requested

### WorkoutFooter
- **Description**: Fixed footer showing overall progress and complete workout action.
- **Main elements**:
  - Progress bar (filled portion based on completed sets)
  - Progress text (e.g., "12 of 20 sets")
  - "Complete Workout" button
- **Handled interactions**:
  - `@click` on Complete - Finish workout, navigate to summary
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `completedSets: number`
  - `totalSets: number`
  - `canComplete: boolean`

### ExitConfirmDialog
- **Description**: Confirmation dialog when user tries to exit an incomplete workout.
- **Main elements**:
  - Warning message
  - "Keep Going" button (secondary)
  - "Abandon Workout" button (danger)
- **Handled interactions**:
  - `@click` on Keep Going - Close dialog
  - `@click` on Abandon - Mark session as abandoned, exit
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `isOpen: boolean`
- **Events**:
  - `@close` - Dialog closed
  - `@abandon` - User confirmed abandon

### EditSetDialog
- **Description**: Dialog to edit a previously logged set.
- **Main elements**:
  - Weight input
  - Reps input
  - "Save" button
  - "Delete Set" button (danger)
  - "Cancel" button
- **Handled interactions**:
  - `@submit` - Update set
  - `@delete` - Delete set
  - `@cancel` - Close without changes
- **Handled validation**:
  - Weight must be >= 0
  - Reps must be >= 1
- **Types**: `SetInput`
- **Props**:
  - `set: CompletedSet`
  - `isOpen: boolean`
- **Events**:
  - `@save` - Save changes
  - `@delete` - Delete set
  - `@close` - Close dialog

### ExerciseInfoSlideOver
- **Description**: Slide-over panel showing exercise details and instructions.
- **Main elements**:
  - Exercise name
  - Target muscles
  - Equipment required
  - Instructions/description
  - Close button
- **Handled interactions**:
  - `@click` on close - Close panel
  - Swipe right to dismiss (mobile)
- **Handled validation**: None
- **Types**: `ExerciseDetail`
- **Props**:
  - `exerciseId: string`
  - `isOpen: boolean`

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From workout_sessions.py
interface WorkoutSessionStartResponse {
  session_id: string; // UUID
  workout_plan: WorkoutPlanBrief;
  started_at: string; // ISO datetime
  exercises: PlannedExerciseWithContext[];
}

interface PlannedExerciseWithContext {
  planned_exercise_id: string; // UUID
  exercise: ExerciseBrief;
  planned_sets: number;
  planned_reps_min: number;
  planned_reps_max: number;
  rest_seconds: number | null;
  context: ExerciseContextInfo;
}

interface ExerciseContextInfo {
  personal_record: PersonalRecordBrief | null;
  recent_sessions: RecentSessionInfo[];
}

interface PersonalRecordBrief {
  record_type: RecordTypeEnum;
  value: string; // Decimal as string
  achieved_at: string; // ISO datetime
}

interface RecentSessionInfo {
  date: string; // ISO datetime
  sets: RecentSetInfo[];
}

interface RecentSetInfo {
  reps: number;
  weight: string; // Decimal as string
}

interface ExerciseBrief {
  id: string; // UUID
  name: string;
}

interface LogExerciseRequest {
  exercise_id: string; // UUID
  sets: ExerciseSetLogItem[];
}

interface ExerciseSetLogItem {
  set_number: number;
  reps: number;
  weight: string; // Decimal as string
  rest_time_seconds: number | null;
}

interface LogExerciseResponse {
  exercise_session_ids: string[]; // UUIDs
}

interface CompleteSessionResponse {
  session_id: string;
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
```

### ViewModels (frontend-specific)

```typescript
// Main active workout state
interface ActiveWorkoutState {
  sessionId: string;
  workoutPlan: {
    id: string;
    name: string;
  };
  startedAt: Date;
  exercises: ExerciseWithSets[];
  currentExerciseIndex: number;
  restTimer: RestTimerState;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

// Exercise with all set data
interface ExerciseWithSets {
  plannedExerciseId: string;
  exerciseId: string;
  exerciseName: string;
  plannedSets: number;
  plannedRepsMin: number;
  plannedRepsMax: number;
  restSeconds: number;
  context: ExerciseContextVM;
  loggedSets: LoggedSet[];
  status: 'completed' | 'current' | 'pending';
}

// Context view model
interface ExerciseContextVM {
  personalRecord: {
    type: RecordTypeEnum;
    value: number;
    valueFormatted: string;
    date: Date;
  } | null;
  lastSession: {
    date: Date;
    dateFormatted: string;
    summary: string; // e.g., "5 sets × 135 lbs"
    sets: { reps: number; weight: number }[];
  } | null;
}

// Logged set
interface LoggedSet {
  id: string; // Temporary client ID or server ID
  setNumber: number;
  weight: number; // In user's unit
  reps: number;
  restTimeSeconds: number | null;
  isServerSynced: boolean;
  exerciseSessionId: string | null; // Server ID once synced
}

// Set input for forms
interface SetInput {
  setNumber: number;
  weight: number;
  reps: number;
}

// Rest timer state
interface RestTimerState {
  isActive: boolean;
  remainingSeconds: number;
  totalSeconds: number;
  isAudioEnabled: boolean;
}

// Progress tracking
interface WorkoutProgress {
  completedSets: number;
  totalSets: number;
  completedExercises: number;
  totalExercises: number;
  percentComplete: number;
}

// LocalStorage persisted state
interface PersistedWorkoutState {
  sessionId: string;
  workoutPlanId: string;
  workoutPlanName: string;
  startedAt: string; // ISO string
  exercises: ExerciseWithSets[];
  currentExerciseIndex: number;
  restTimerAudioEnabled: boolean;
  lastSavedAt: string; // ISO string
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

// Set input validation
const setInputSchema = z.object({
  setNumber: z.number().int().min(1),
  weight: z.number().min(0),
  reps: z.number().int().min(1)
});

// Log exercise request validation
const logExerciseRequestSchema = z.object({
  exercise_id: z.string().uuid(),
  sets: z.array(z.object({
    set_number: z.number().int().min(1),
    reps: z.number().int().min(1),
    weight: z.string().regex(/^\d+(\.\d+)?$/),
    rest_time_seconds: z.number().int().nullable()
  })).min(1)
});

// Session start response validation
const plannedExerciseSchema = z.object({
  planned_exercise_id: z.string().uuid(),
  exercise: z.object({
    id: z.string().uuid(),
    name: z.string()
  }),
  planned_sets: z.number().int().min(1),
  planned_reps_min: z.number().int().min(1),
  planned_reps_max: z.number().int().min(1),
  rest_seconds: z.number().int().nullable(),
  context: z.object({
    personal_record: z.object({
      record_type: z.enum(['1rm', 'set_volume', 'total_volume']),
      value: z.string(),
      achieved_at: z.string().datetime()
    }).nullable(),
    recent_sessions: z.array(z.object({
      date: z.string().datetime(),
      sets: z.array(z.object({
        reps: z.number().int(),
        weight: z.string()
      }))
    }))
  })
});

const workoutSessionStartResponseSchema = z.object({
  session_id: z.string().uuid(),
  workout_plan: z.object({
    id: z.string().uuid(),
    name: z.string()
  }),
  started_at: z.string().datetime(),
  exercises: z.array(plannedExerciseSchema)
});
```

## 6. State Management

### Local Component State (ActiveWorkoutPage)

```typescript
const isLoading = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);

const workoutState = ref<ActiveWorkoutState | null>(null);
const currentExerciseIndex = ref(0);

const restTimer = reactive<RestTimerState>({
  isActive: false,
  remainingSeconds: 0,
  totalSeconds: 0,
  isAudioEnabled: true
});

const showExitConfirm = ref(false);
const showEditSet = ref(false);
const editingSet = ref<LoggedSet | null>(null);
const showExerciseInfo = ref(false);
const exerciseInfoId = ref<string | null>(null);
```

### Pinia Stores Used

```typescript
// sessionStore - for workout session management
interface SessionStore {
  activeSession: ActiveWorkoutState | null;
  
  // Load session from API or localStorage
  loadSession(sessionId: string): Promise<void>;
  
  // Save session to localStorage
  persistToLocalStorage(): void;
  
  // Log a set
  logSet(exerciseIndex: number, set: SetInput): Promise<void>;
  
  // Update a logged set
  updateSet(exerciseIndex: number, setIndex: number, set: SetInput): Promise<void>;
  
  // Delete a logged set
  deleteSet(exerciseIndex: number, setIndex: number): Promise<void>;
  
  // Complete workout
  completeWorkout(notes?: string): Promise<CompleteSessionResponse>;
  
  // Abandon workout
  abandonWorkout(notes?: string): Promise<void>;
  
  // Clear session
  clearSession(): void;
}

// profileStore - for unit preference
interface ProfileStore {
  unitSystem: 'metric' | 'imperial';
  convertWeight(kg: number): number;
  formatWeight(kg: number): string;
  convertToKg(value: number): number;
}
```

### Custom Composable: useActiveWorkout

```typescript
// composables/useActiveWorkout.ts
export function useActiveWorkout(sessionId: string) {
  const router = useRouter();
  const sessionStore = useSessionStore();
  const profileStore = useProfileStore();
  
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const workoutState = ref<ActiveWorkoutState | null>(null);
  
  // Initialize workout from API or localStorage
  const initializeWorkout = async (): Promise<void> => {
    isLoading.value = true;
    
    try {
      // Check localStorage first for recovery
      const persisted = loadFromLocalStorage(sessionId);
      
      if (persisted) {
        workoutState.value = hydrateFromPersisted(persisted);
      } else {
        // Fetch from API
        const response = await getSessionForWorkout(sessionId);
        workoutState.value = transformToState(response, profileStore);
      }
      
      // Start persistence
      startAutoPersist();
      
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  // Log a set
  const logSet = async (weight: number, reps: number): Promise<void> => {
    if (!workoutState.value) return;
    
    const exercise = currentExercise.value;
    const setNumber = exercise.loggedSets.length + 1;
    
    // Optimistic update
    const tempId = `temp-${Date.now()}`;
    exercise.loggedSets.push({
      id: tempId,
      setNumber,
      weight,
      reps,
      restTimeSeconds: exercise.restSeconds,
      isServerSynced: false,
      exerciseSessionId: null
    });
    
    // Update status
    updateExerciseStatus(exercise);
    
    // Persist to localStorage
    persistToLocalStorage();
    
    // Start rest timer
    startRestTimer(exercise.restSeconds);
    
    // Sync to server
    try {
      const weightKg = profileStore.convertToKg(weight);
      const response = await logExerciseSet(sessionId, {
        exercise_id: exercise.exerciseId,
        sets: [{
          set_number: setNumber,
          reps,
          weight: weightKg.toString(),
          rest_time_seconds: exercise.restSeconds
        }]
      });
      
      // Update with server ID
      const loggedSet = exercise.loggedSets.find(s => s.id === tempId);
      if (loggedSet && response.exercise_session_ids.length > 0) {
        loggedSet.exerciseSessionId = response.exercise_session_ids[0];
        loggedSet.isServerSynced = true;
      }
      
    } catch (e) {
      // Keep optimistic update, mark as not synced
      showToast({ type: 'warning', message: 'Set saved locally. Will sync when online.' });
    }
  };
  
  // Complete workout
  const completeWorkout = async (notes?: string): Promise<void> => {
    if (!workoutState.value) return;
    
    try {
      const response = await completeSession(sessionId, { notes });
      
      // Clear localStorage
      clearLocalStorage(sessionId);
      
      // Navigate to completion summary
      router.push({
        name: 'workoutComplete',
        params: { sessionId },
        state: { completionData: response }
      });
      
    } catch (e) {
      handleError(e);
    }
  };
  
  // Abandon workout
  const abandonWorkout = async (notes?: string): Promise<void> => {
    try {
      await skipSession(sessionId, { notes: notes || 'Abandoned from active workout' });
      clearLocalStorage(sessionId);
      router.push({ name: 'dashboard' });
    } catch (e) {
      handleError(e);
    }
  };
  
  // Computed
  const currentExercise = computed(() => 
    workoutState.value?.exercises[workoutState.value.currentExerciseIndex]
  );
  
  const progress = computed<WorkoutProgress>(() => {
    if (!workoutState.value) {
      return { completedSets: 0, totalSets: 0, completedExercises: 0, totalExercises: 0, percentComplete: 0 };
    }
    
    const exercises = workoutState.value.exercises;
    const completedSets = exercises.reduce((sum, ex) => sum + ex.loggedSets.length, 0);
    const totalSets = exercises.reduce((sum, ex) => sum + ex.plannedSets, 0);
    const completedExercises = exercises.filter(ex => ex.status === 'completed').length;
    
    return {
      completedSets,
      totalSets,
      completedExercises,
      totalExercises: exercises.length,
      percentComplete: totalSets > 0 ? (completedSets / totalSets) * 100 : 0
    };
  });
  
  const canComplete = computed(() => {
    return progress.value.completedSets > 0;
  });
  
  return {
    isLoading,
    error,
    workoutState,
    currentExercise,
    progress,
    canComplete,
    initializeWorkout,
    logSet,
    updateSet,
    deleteSet,
    completeWorkout,
    abandonWorkout,
    moveToNextExercise,
    moveToPreviousExercise
  };
}
```

### Custom Composable: useRestTimer

```typescript
// composables/useRestTimer.ts
export function useRestTimer() {
  const remainingSeconds = ref(0);
  const totalSeconds = ref(0);
  const isActive = ref(false);
  const isAudioEnabled = ref(true);
  
  let intervalId: number | null = null;
  
  const start = (seconds: number): void => {
    stop();
    remainingSeconds.value = seconds;
    totalSeconds.value = seconds;
    isActive.value = true;
    
    intervalId = window.setInterval(() => {
      remainingSeconds.value--;
      
      if (remainingSeconds.value <= 0) {
        complete();
      }
    }, 1000);
  };
  
  const stop = (): void => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
    isActive.value = false;
    remainingSeconds.value = 0;
  };
  
  const addTime = (seconds: number = 30): void => {
    remainingSeconds.value += seconds;
    totalSeconds.value += seconds;
  };
  
  const skip = (): void => {
    stop();
  };
  
  const complete = (): void => {
    stop();
    
    if (isAudioEnabled.value) {
      playTimerSound();
    }
    
    // Vibrate if supported
    if ('vibrate' in navigator) {
      navigator.vibrate([200, 100, 200]);
    }
  };
  
  const toggleAudio = (): void => {
    isAudioEnabled.value = !isAudioEnabled.value;
  };
  
  const progressPercent = computed(() => {
    if (totalSeconds.value === 0) return 0;
    return ((totalSeconds.value - remainingSeconds.value) / totalSeconds.value) * 100;
  });
  
  onUnmounted(() => {
    stop();
  });
  
  return {
    remainingSeconds,
    totalSeconds,
    isActive,
    isAudioEnabled,
    progressPercent,
    start,
    stop,
    addTime,
    skip,
    toggleAudio
  };
}
```

### Custom Composable: useElapsedTimer

```typescript
// composables/useElapsedTimer.ts
export function useElapsedTimer(startedAt: Ref<Date | null>) {
  const elapsedSeconds = ref(0);
  let intervalId: number | null = null;
  
  const start = (): void => {
    if (!startedAt.value) return;
    
    intervalId = window.setInterval(() => {
      elapsedSeconds.value = Math.floor(
        (Date.now() - startedAt.value!.getTime()) / 1000
      );
    }, 1000);
  };
  
  const stop = (): void => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };
  
  const formatted = computed(() => {
    const hours = Math.floor(elapsedSeconds.value / 3600);
    const minutes = Math.floor((elapsedSeconds.value % 3600) / 60);
    const seconds = elapsedSeconds.value % 60;
    
    if (hours > 0) {
      return `${hours}:${pad(minutes)}:${pad(seconds)}`;
    }
    return `${minutes}:${pad(seconds)}`;
  });
  
  const pad = (n: number): string => n.toString().padStart(2, '0');
  
  watch(startedAt, (val) => {
    if (val) start();
    else stop();
  }, { immediate: true });
  
  onUnmounted(() => stop());
  
  return {
    elapsedSeconds,
    formatted
  };
}
```

### localStorage Persistence

```typescript
// utils/workoutPersistence.ts
const STORAGE_KEY = 'activeWorkout';

export function persistWorkoutState(state: ActiveWorkoutState): void {
  const persisted: PersistedWorkoutState = {
    sessionId: state.sessionId,
    workoutPlanId: state.workoutPlan.id,
    workoutPlanName: state.workoutPlan.name,
    startedAt: state.startedAt.toISOString(),
    exercises: state.exercises,
    currentExerciseIndex: state.currentExerciseIndex,
    restTimerAudioEnabled: state.restTimer.isAudioEnabled,
    lastSavedAt: new Date().toISOString()
  };
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(persisted));
}

export function loadPersistedState(sessionId: string): PersistedWorkoutState | null {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return null;
  
  try {
    const parsed = JSON.parse(stored) as PersistedWorkoutState;
    if (parsed.sessionId !== sessionId) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function clearPersistedState(sessionId?: string): void {
  if (sessionId) {
    const stored = loadPersistedState(sessionId);
    if (stored && stored.sessionId === sessionId) {
      localStorage.removeItem(STORAGE_KEY);
    }
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function hasPersistedSession(): { exists: boolean; sessionId: string | null } {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return { exists: false, sessionId: null };
  
  try {
    const parsed = JSON.parse(stored) as PersistedWorkoutState;
    return { exists: true, sessionId: parsed.sessionId };
  } catch {
    return { exists: false, sessionId: null };
  }
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Session for Workout (if needed)
```
GET /api/v1/workout-sessions/{session_id}/workout
```

This endpoint returns session data with exercise context (same as start response).

**Response (200 OK)**: Same as WorkoutSessionStartResponse

#### 2. Log Exercise Sets
```
POST /api/v1/workout-sessions/{session_id}/log
```

**Request**
```typescript
{
  "exercise_id": "uuid-string",
  "sets": [
    {
      "set_number": 1,
      "reps": 10,
      "weight": "60.0",
      "rest_time_seconds": 90
    }
  ]
}
```

**Response (201 Created)**
```typescript
{
  "success": true,
  "data": {
    "exercise_session_ids": ["uuid-string"]
  },
  "error": null
}
```

#### 3. Update Exercise Session (Edit Set)
```
PATCH /api/v1/workout-sessions/{session_id}/exercise-sessions/{exercise_session_id}
```

**Request**
```typescript
{
  "weight": "65.0",
  "reps": 8
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "weight": "65.0",
    "reps": 8
  },
  "error": null
}
```

#### 4. Delete Exercise Session (Delete Set)
```
DELETE /api/v1/workout-sessions/{session_id}/exercise-sessions/{exercise_session_id}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": { "deleted": true },
  "error": null
}
```

#### 5. Complete Session
```
POST /api/v1/workout-sessions/{session_id}/complete
```

**Request**
```typescript
{
  "notes": "Great workout!"
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "session_id": "uuid-string",
    "status": "completed",
    "duration_seconds": 3600,
    "new_personal_records": [
      {
        "exercise_name": "Bench Press",
        "record_type": "1rm",
        "value": "85.0",
        "unit": "kg"
      }
    ]
  },
  "error": null
}
```

#### 6. Skip/Abandon Session
```
POST /api/v1/workout-sessions/{session_id}/skip
```

**Request**
```typescript
{
  "notes": "Abandoned from active workout"
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "session_id": "uuid-string",
    "status": "abandoned"
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/workout.ts
import axios from '@/lib/axios';
import type { 
  LogExerciseRequest,
  LogExerciseResponse,
  CompleteSessionRequest,
  CompleteSessionResponse,
  SkipSessionRequest
} from '@/types/workout-sessions';

export async function logExerciseSet(
  sessionId: string,
  data: LogExerciseRequest
): Promise<LogExerciseResponse> {
  const response = await axios.post<APIResponse<LogExerciseResponse>>(
    `/api/v1/workout-sessions/${sessionId}/log`,
    data
  );
  return response.data.data;
}

export async function updateExerciseSession(
  sessionId: string,
  exerciseSessionId: string,
  data: { weight: string; reps: number }
): Promise<void> {
  await axios.patch(
    `/api/v1/workout-sessions/${sessionId}/exercise-sessions/${exerciseSessionId}`,
    data
  );
}

export async function deleteExerciseSession(
  sessionId: string,
  exerciseSessionId: string
): Promise<void> {
  await axios.delete(
    `/api/v1/workout-sessions/${sessionId}/exercise-sessions/${exerciseSessionId}`
  );
}

export async function completeSession(
  sessionId: string,
  data: CompleteSessionRequest = {}
): Promise<CompleteSessionResponse> {
  const response = await axios.post<APIResponse<CompleteSessionResponse>>(
    `/api/v1/workout-sessions/${sessionId}/complete`,
    data
  );
  return response.data.data;
}

export async function skipSession(
  sessionId: string,
  data: SkipSessionRequest = {}
): Promise<void> {
  await axios.post(`/api/v1/workout-sessions/${sessionId}/skip`, data);
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | ActiveWorkoutPage | `onMounted` | Load from localStorage or API, start elapsed timer |
| Click exercise panel | ExercisePanelHeader | `expandExercise()` | Expand panel, collapse others, scroll into view |
| Input weight | ActiveSetRow | `v-model` | Update weight value |
| Input reps | ActiveSetRow | `v-model` | Update reps value |
| Click +/- buttons | ActiveSetRow | `increment/decrement()` | Adjust weight/reps by step |
| Click Log Set | ActiveSetRow | `logSet()` | Log set, start rest timer, update progress |
| Click +30s | RestTimer | `addTime()` | Add 30 seconds to timer |
| Click Skip | RestTimer | `skip()` | Dismiss rest timer |
| Click audio toggle | RestTimer | `toggleAudio()` | Toggle audio on/off |
| Timer ends | RestTimer | Auto | Play sound, vibrate, dismiss timer |
| Click Edit | CompletedSetRow | `openEditDialog()` | Open edit set dialog |
| Save edit | EditSetDialog | `updateSet()` | Update set, sync to server |
| Delete set | EditSetDialog | `deleteSet()` | Remove set, update progress |
| Click Add Set | AddSetButton | `addSet()` | Add new active set row |
| Click exercise info | ExercisePanelHeader | `showExerciseInfo()` | Open exercise info slide-over |
| Click Exit | WorkoutHeader | `showExitConfirm` | Show exit confirmation |
| Confirm abandon | ExitConfirmDialog | `abandonWorkout()` | Abandon session, navigate to dashboard |
| Click Complete | WorkoutFooter | `completeWorkout()` | Complete session, navigate to summary |
| Browser close/refresh | Window | `beforeunload` | Persist to localStorage, warn if unsaved |

### Detailed Interaction Flow

1. **Initialization**:
   - Check localStorage for persisted state
   - If found, restore state and resume
   - If not, fetch session data from API
   - Transform to view model with unit conversion
   - Start elapsed timer
   - Auto-expand first incomplete exercise

2. **Logging a Set**:
   - User inputs weight and reps
   - Click "Log Set"
   - Optimistic update - add set to list immediately
   - Start rest timer (from exercise rest_seconds)
   - Persist to localStorage
   - Sync to server in background
   - Update exercise status and progress
   - Auto-advance to next set or exercise

3. **Rest Timer Flow**:
   - Timer appears as floating overlay
   - Countdown from rest_seconds
   - User can add time, skip, or let it complete
   - On complete: audio beep, vibration
   - Timer dismisses

4. **Completing Workout**:
   - User clicks "Complete Workout"
   - Show brief loading state
   - Call complete endpoint
   - Clear localStorage
   - Navigate to completion summary with PR data

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | WorkoutContent |
| Error exists | ErrorState | WorkoutContent |
| restTimer.isActive | RestTimer (floating) | - |
| Exercise completed | CompletedSetRows | ActiveSetRow |
| More sets available | ActiveSetRow | - |
| canComplete = true | Complete button enabled | Button disabled |
| showExitConfirm = true | ExitConfirmDialog | - |
| showEditSet = true | EditSetDialog | - |
| showExerciseInfo = true | ExerciseInfoSlideOver | - |

### Input Validation

| Field | Validation | Error Message |
|-------|------------|---------------|
| Weight | >= 0 | "Weight must be 0 or greater" |
| Reps | >= 1 | "Must do at least 1 rep" |
| Reps | Integer | "Reps must be a whole number" |

### Exercise Status Logic

```typescript
function getExerciseStatus(exercise: ExerciseWithSets): 'completed' | 'current' | 'pending' {
  const { loggedSets, plannedSets } = exercise;
  
  if (loggedSets.length >= plannedSets) {
    return 'completed';
  }
  
  if (loggedSets.length > 0) {
    return 'current';
  }
  
  return 'pending';
}
```

## 10. Error Handling

### API Error Handling

```typescript
async function logSet(weight: number, reps: number): Promise<void> {
  // ... optimistic update ...
  
  try {
    const response = await logExerciseSet(sessionId, request);
    // Update with server ID
  } catch (e) {
    if (axios.isAxiosError(e)) {
      if (!e.response) {
        // Network error - keep local, retry later
        showToast({
          type: 'warning',
          message: 'Saved locally. Will sync when online.'
        });
      } else if (e.response.status === 400) {
        // Validation error - revert
        revertOptimisticUpdate();
        showToast({
          type: 'error',
          message: 'Invalid set data. Please check your input.'
        });
      } else {
        // Server error - keep local, retry later
        showToast({
          type: 'warning',
          message: 'Server error. Set saved locally.'
        });
      }
    }
  }
}
```

### Offline Resilience

```typescript
// On app startup or connectivity change
async function syncPendingSets(): Promise<void> {
  const persisted = loadPersistedState();
  if (!persisted) return;
  
  const unsyncedSets = getAllUnsyncedSets(persisted.exercises);
  
  for (const set of unsyncedSets) {
    try {
      await syncSetToServer(set);
      markAsSynced(set);
    } catch (e) {
      // Will retry on next sync
    }
  }
  
  persistToLocalStorage();
}

// Listen for online event
window.addEventListener('online', syncPendingSets);
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Network error | - | "Saved locally. Will sync when online." | Continue, retry later |
| Validation error | 400 | "Invalid set data." | Revert, show error |
| Session not found | 404 | "Session not found." | Redirect to dashboard |
| Session completed | 409 | "Session already completed." | Redirect to history |
| Auth expired | 401 | Auto-redirect | Via interceptor |
| Server error | 500 | "Server error. Try again." | Retry option |

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/active-workout.ts` with all ViewModels
   - Add Zod schemas for validation
   - Create localStorage persistence types

2. **Create Utility Functions**
   - Create `src/utils/workoutPersistence.ts` for localStorage
   - Create audio/vibration utilities
   - Create weight increment step calculator

3. **Create Composables**
   - Create `src/composables/useActiveWorkout.ts`
   - Create `src/composables/useRestTimer.ts`
   - Create `src/composables/useElapsedTimer.ts`
   - Create `src/composables/useSetInput.ts`

4. **Create Timer Components**
   - Create `src/components/workout/RestTimer.vue`
   - Create `src/components/workout/ElapsedTimer.vue`
   - Add audio assets for timer

5. **Create Exercise Components**
   - Create `src/components/workout/ExerciseAccordion.vue`
   - Create `src/components/workout/ExercisePanel.vue`
   - Create `src/components/workout/ExercisePanelHeader.vue`
   - Create `src/components/workout/PreviousSessionContext.vue`

6. **Create Set Input Components**
   - Create `src/components/workout/SetsList.vue`
   - Create `src/components/workout/ActiveSetRow.vue`
   - Create `src/components/workout/CompletedSetRow.vue`
   - Create `src/components/workout/AddSetButton.vue`

7. **Create Header and Footer**
   - Create `src/components/workout/WorkoutHeader.vue`
   - Create `src/components/workout/WorkoutFooter.vue`
   - Create `src/components/workout/ProgressBar.vue`

8. **Create Dialogs**
   - Create `src/components/workout/ExitConfirmDialog.vue`
   - Create `src/components/workout/EditSetDialog.vue`
   - Create/reuse `src/components/common/ExerciseInfoSlideOver.vue`

9. **Create Page View**
   - Create `src/views/ActiveWorkoutPage.vue`
   - Wire up all components
   - Implement navigation guards

10. **Configure Router**
    - Add active workout route
    - Add beforeRouteLeave guard
    - Add beforeunload listener

11. **Add API Integration**
    - Implement logExerciseSet
    - Implement updateExerciseSession
    - Implement deleteExerciseSession
    - Implement completeSession
    - Implement skipSession

12. **Add localStorage Persistence**
    - Implement auto-save on state changes
    - Implement recovery on page load
    - Implement sync when online

13. **Style with Tailwind**
    - Mobile-first large touch targets (44x44px min)
    - Fixed header and footer
    - Floating rest timer with backdrop
    - Smooth accordion transitions
    - Dark mode support

14. **Add Accessibility**
    - ARIA live regions for timer
    - Focus management for accordion
    - Keyboard navigation for inputs
    - Screen reader announcements

15. **Write Tests**
    - Unit tests for composables
    - Unit tests for persistence
    - Component tests for input row
    - Integration test for log flow

16. **Manual Testing**
    - Test full workout flow
    - Test offline/online transitions
    - Test timer audio/vibration
    - Test browser refresh recovery
    - Test on mobile devices
