# View Implementation Plan: Stats Page

## 1. Overview

The Stats Page provides users with a comprehensive overview of their workout history and progress through visualizations and key metrics. It displays workout frequency over time via charts, muscle group training distribution, personal records summary, current streak, and total volume lifted. Users can filter stats by date range and drill down into exercise-specific history.

## 2. View Routing

- **Path**: `/stats`
- **Route Name**: `stats`
- **Access**: Authenticated users only
- **Guard**: Redirect to `/login` if not authenticated
- **Query Params** (optional):
  - `start`: Start date filter (ISO date string)
  - `end`: End date filter (ISO date string)
  - `period`: Preset period ('week', 'month', '3months', '6months', 'year', 'all')

## 3. Component Structure

```
StatsPage (view)
├── PageHeader
│   ├── PageTitle "Stats"
│   └── DateRangeSelector
│       ├── PresetButtons (Week, Month, 3M, 6M, Year, All)
│       └── CustomDatePicker (optional)
├── OverviewSection
│   ├── StatCardRow
│   │   ├── TotalWorkoutsCard
│   │   │   ├── Icon
│   │   │   ├── Value
│   │   │   └── Label
│   │   ├── TotalDurationCard
│   │   │   ├── Icon
│   │   │   ├── Value (formatted)
│   │   │   └── Label
│   │   ├── TotalVolumeCard
│   │   │   ├── Icon
│   │   │   ├── Value (with unit)
│   │   │   └── Label
│   │   └── CurrentStreakCard
│   │       ├── FlameIcon
│   │       ├── StreakDays
│   │       └── Label
├── WorkoutFrequencySection
│   ├── SectionHeader
│   └── WorkoutFrequencyChart (bar chart by month)
│       ├── ChartCanvas
│       ├── MonthLabels
│       └── ValueLabels
├── MuscleGroupSection
│   ├── SectionHeader
│   └── MuscleGroupChart (horizontal bar or pie chart)
│       ├── ChartCanvas
│       ├── MuscleGroupLabels
│       └── SessionCounts
├── PersonalRecordsSection
│   ├── SectionHeader
│   ├── PRCountBadge
│   └── TopPRsList
│       └── PRListItem (for each, limit 5)
│           ├── ExerciseName
│           ├── RecordTypeBadge
│           ├── Value
│           └── AchievedDate
│   └── ViewAllPRsLink
├── ExerciseHistorySection (optional expansion)
│   ├── SectionHeader
│   ├── ExerciseSearchInput
│   └── ExerciseHistoryChart (when exercise selected)
│       ├── ExerciseSelector dropdown
│       └── ProgressChart (line chart of max weight over time)
└── LoadingState / ErrorState / EmptyState
```

## 4. Component Details

### StatsPage
- **Description**: Main stats view that orchestrates all stat sections and handles data fetching with date filtering.
- **Main elements**:
  - Page header with date range selector
  - Overview stats cards
  - Workout frequency chart
  - Muscle group distribution
  - Personal records summary
  - Optional exercise history explorer
- **Handled interactions**:
  - Fetches stats data on mount and when date range changes
  - Manages selected date range state
- **Handled validation**: None
- **Types**: `StatsOverviewData`
- **Props**: None

### PageHeader
- **Description**: Top section with title and date range filter.
- **Main elements**:
  - "Stats" title
  - DateRangeSelector component
- **Handled interactions**: None (container only)
- **Handled validation**: None
- **Types**: None
- **Props**: None

### DateRangeSelector
- **Description**: Filter component for selecting the date range for stats.
- **Main elements**:
  - Preset buttons (Week, Month, 3 Months, 6 Months, Year, All)
  - Optional custom date picker toggle
  - Active state indicator
- **Handled interactions**:
  - `@click` on preset - Set date range
  - `@change` on custom picker - Update custom range
- **Handled validation**: End date must be after start date
- **Types**: `DateRange`
- **Props**:
  - `selectedRange: DateRange`
  - `selectedPreset: string | null`
- **Events**:
  - `@change` - Emits new date range

### StatCardRow
- **Description**: Responsive grid of overview stat cards.
- **Main elements**:
  - 4 stat cards in a row (2x2 on mobile)
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: `StatsOverview`
- **Props**:
  - `stats: StatsOverview`

### TotalWorkoutsCard / TotalDurationCard / TotalVolumeCard / CurrentStreakCard
- **Description**: Individual stat card displaying a single key metric.
- **Main elements**:
  - Icon (dumbbell, clock, weight, flame)
  - Large value number
  - Label text
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `value: number | string`
  - `label: string`

### WorkoutFrequencySection
- **Description**: Section showing workout count over time in a bar chart.
- **Main elements**:
  - Section header "Workout Frequency"
  - Bar chart component
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `MonthlyWorkoutCount[]`
- **Props**:
  - `data: MonthlyWorkoutCount[]`

### WorkoutFrequencyChart
- **Description**: Bar chart visualization of workouts per month.
- **Main elements**:
  - Vertical bars for each month
  - X-axis with month labels
  - Y-axis with count values
  - Hover tooltips with exact counts
- **Handled interactions**:
  - Hover on bar - Show tooltip
- **Handled validation**: None
- **Types**: `ChartDataPoint[]`
- **Props**:
  - `data: MonthlyWorkoutCount[]`
  - `height?: number`

### MuscleGroupSection
- **Description**: Section showing muscle group training distribution.
- **Main elements**:
  - Section header "Muscle Groups Trained"
  - Horizontal bar chart or pie chart
- **Handled interactions**: None at container level
- **Handled validation**: None
- **Types**: `MuscleGroupTrainingCount[]`
- **Props**:
  - `data: MuscleGroupTrainingCount[]`

### MuscleGroupChart
- **Description**: Visualization of muscle group training frequency.
- **Main elements**:
  - Horizontal bars with muscle group names
  - Session count values
  - Color coding by muscle group category
- **Handled interactions**:
  - Hover - Show exact session count
- **Handled validation**: None
- **Types**: `MuscleGroupTrainingCount[]`
- **Props**:
  - `data: MuscleGroupTrainingCount[]`
  - `maxBars?: number` - Limit to top N (default 5)

### PersonalRecordsSection
- **Description**: Summary of personal records with count and top PRs list.
- **Main elements**:
  - Section header with PR count badge
  - List of top/recent PRs
  - "View All" link
- **Handled interactions**:
  - `@click` on View All - Navigate to full PR list
  - `@click` on PR item - Navigate to exercise detail
- **Handled validation**: None
- **Types**: `PersonalRecordSummary`
- **Props**:
  - `totalCount: number`
  - `topRecords: PersonalRecordListItem[]`

### PRListItem
- **Description**: Single row in the PR list showing exercise, type, and value.
- **Main elements**:
  - Trophy icon
  - Exercise name
  - Record type badge (1RM, Set Volume, etc.)
  - Value with unit
  - Achievement date
- **Handled interactions**:
  - `@click` - Navigate to exercise history
- **Handled validation**: None
- **Types**: `PersonalRecordListItem`
- **Props**:
  - `record: PersonalRecordListItem`

### ExerciseHistorySection
- **Description**: Optional section for exploring individual exercise progress over time.
- **Main elements**:
  - Section header "Exercise Progress"
  - Exercise search/select dropdown
  - Line chart showing progress when exercise selected
- **Handled interactions**:
  - `@select` on dropdown - Load exercise history
- **Handled validation**: None
- **Types**: `ExerciseHistoryResponse`
- **Props**: None (self-contained)

### ExerciseHistoryChart
- **Description**: Line chart showing exercise performance over time.
- **Main elements**:
  - Line chart with max weight per session
  - X-axis with dates
  - Y-axis with weight values
  - Optional secondary line for volume
- **Handled interactions**:
  - Hover - Show session details tooltip
  - Click point - Navigate to session detail (optional)
- **Handled validation**: None
- **Types**: `ExerciseHistorySession[]`
- **Props**:
  - `data: ExerciseHistorySession[]`
  - `exerciseName: string`
  - `unitSystem: UnitSystemEnum`

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From stats.py
interface MonthlyWorkoutCount {
  month: string; // Format: YYYY-MM
  count: number;
}

interface MuscleGroupTrainingCount {
  muscle_group: MuscleGroupEnum;
  session_count: number;
}

interface StatsOverviewResponse {
  total_workouts: number;
  total_duration_seconds: number;
  total_volume_kg: string; // Decimal as string
  workouts_by_month: MonthlyWorkoutCount[];
  most_trained_muscle_groups: MuscleGroupTrainingCount[];
  current_streak_days: number;
  personal_records_count: number;
}

interface ExerciseHistorySet {
  reps: number;
  weight: string; // Decimal as string
  unit: string;
}

interface ExerciseHistorySession {
  date: string; // ISO datetime
  total_volume: string; // Decimal as string
  total_reps: number;
  max_weight: string; // Decimal as string
  sets: ExerciseHistorySet[];
}

interface ExerciseHistoryResponse {
  exercise: {
    id: string;
    name: string;
  };
  sessions: ExerciseHistorySession[];
}

// Muscle group enum
type MuscleGroupEnum = 
  | 'chest' 
  | 'back' 
  | 'shoulders' 
  | 'biceps' 
  | 'triceps' 
  | 'forearms' 
  | 'legs' 
  | 'glutes' 
  | 'core' 
  | 'traps' 
  | 'lats';

// Personal records from personal_records.py
interface PersonalRecordResponse {
  id: string;
  exercise: {
    id: string;
    name: string;
  };
  record_type: RecordTypeEnum;
  value: string; // Decimal as string
  achieved_at: string; // ISO datetime
}

type RecordTypeEnum = '1rm' | 'set_volume' | 'total_volume';
```

### ViewModels (frontend-specific)

```typescript
// Main stats data
interface StatsOverviewVM {
  totalWorkouts: number;
  totalDuration: {
    seconds: number;
    formatted: string; // e.g., "45h 30m"
  };
  totalVolume: {
    kg: number;
    formatted: string; // e.g., "125,000 lbs"
  };
  currentStreak: number;
  personalRecordsCount: number;
  workoutsByMonth: WorkoutMonthVM[];
  muscleGroups: MuscleGroupVM[];
}

// Chart-ready workout data
interface WorkoutMonthVM {
  month: string; // YYYY-MM
  monthLabel: string; // "Jan 2024"
  count: number;
}

// Chart-ready muscle group data
interface MuscleGroupVM {
  muscleGroup: MuscleGroupEnum;
  label: string; // Formatted name e.g., "Chest"
  sessionCount: number;
  percentage: number; // of total
  color: string; // for chart
}

// Date range for filtering
interface DateRange {
  start: Date | null;
  end: Date | null;
}

type DatePreset = 'week' | 'month' | '3months' | '6months' | 'year' | 'all';

// Personal record list item
interface PersonalRecordVM {
  id: string;
  exerciseId: string;
  exerciseName: string;
  recordType: RecordTypeEnum;
  recordTypeLabel: string;
  value: number;
  valueFormatted: string;
  achievedAt: Date;
  achievedAtFormatted: string;
}

// Exercise history for charts
interface ExerciseHistoryVM {
  exerciseId: string;
  exerciseName: string;
  sessions: ExerciseSessionVM[];
}

interface ExerciseSessionVM {
  date: Date;
  dateFormatted: string;
  maxWeight: number;
  maxWeightFormatted: string;
  totalVolume: number;
  totalVolumeFormatted: string;
  totalReps: number;
  sets: {
    reps: number;
    weight: number;
  }[];
}
```

### Zod Validation Schemas

```typescript
import { z } from 'zod';

// Date range validation
const dateRangeSchema = z.object({
  start: z.date().nullable(),
  end: z.date().nullable()
}).refine(
  data => !data.start || !data.end || data.start <= data.end,
  { message: 'End date must be after start date' }
);

// API response validation
const monthlyWorkoutCountSchema = z.object({
  month: z.string().regex(/^\d{4}-\d{2}$/),
  count: z.number().int().min(0)
});

const muscleGroupSchema = z.enum([
  'chest', 'back', 'shoulders', 'biceps', 'triceps',
  'forearms', 'legs', 'glutes', 'core', 'traps', 'lats'
]);

const muscleGroupTrainingSchema = z.object({
  muscle_group: muscleGroupSchema,
  session_count: z.number().int().min(0)
});

const statsOverviewResponseSchema = z.object({
  total_workouts: z.number().int().min(0),
  total_duration_seconds: z.number().int().min(0),
  total_volume_kg: z.string().regex(/^\d+(\.\d+)?$/),
  workouts_by_month: z.array(monthlyWorkoutCountSchema),
  most_trained_muscle_groups: z.array(muscleGroupTrainingSchema),
  current_streak_days: z.number().int().min(0),
  personal_records_count: z.number().int().min(0)
});

const exerciseHistorySetSchema = z.object({
  reps: z.number().int().min(1),
  weight: z.string().regex(/^\d+(\.\d+)?$/),
  unit: z.string()
});

const exerciseHistorySessionSchema = z.object({
  date: z.string().datetime(),
  total_volume: z.string().regex(/^\d+(\.\d+)?$/),
  total_reps: z.number().int().min(0),
  max_weight: z.string().regex(/^\d+(\.\d+)?$/),
  sets: z.array(exerciseHistorySetSchema)
});

const exerciseHistoryResponseSchema = z.object({
  exercise: z.object({
    id: z.string().uuid(),
    name: z.string()
  }),
  sessions: z.array(exerciseHistorySessionSchema)
});
```

## 6. State Management

### Local Component State (StatsPage)

```typescript
const route = useRoute();
const router = useRouter();

// Date range state
const selectedPreset = ref<DatePreset>('month');
const dateRange = ref<DateRange>({
  start: null,
  end: null
});

// Loading and error state
const isLoading = ref(true);
const error = ref<string | null>(null);

// Stats data
const statsData = ref<StatsOverviewVM | null>(null);

// Exercise history state (for optional section)
const selectedExerciseId = ref<string | null>(null);
const exerciseHistory = ref<ExerciseHistoryVM | null>(null);
const isLoadingExercise = ref(false);

// Personal records (top N for display)
const topRecords = ref<PersonalRecordVM[]>([]);
```

### Pinia Stores Used

```typescript
// profileStore - for unit system
interface ProfileStore {
  unitSystem: 'metric' | 'imperial';
  convertWeight(kg: number): number;
  formatWeight(kg: number): string;
  formatVolume(kg: number): string;
}
```

### Custom Composable: useStats

```typescript
// composables/useStats.ts
export function useStats() {
  const profileStore = useProfileStore();
  const route = useRoute();
  const router = useRouter();
  
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const statsData = ref<StatsOverviewVM | null>(null);
  
  // Date range from query params or default
  const selectedPreset = ref<DatePreset>(
    (route.query.period as DatePreset) || 'month'
  );
  
  const dateRange = computed<DateRange>(() => {
    return getDateRangeFromPreset(selectedPreset.value);
  });
  
  // Fetch stats
  const fetchStats = async (): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await getStatsOverview({
        start_date: dateRange.value.start?.toISOString(),
        end_date: dateRange.value.end?.toISOString()
      });
      
      statsData.value = transformToViewModel(response, profileStore);
      
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  // Change date range
  const setPreset = (preset: DatePreset): void => {
    selectedPreset.value = preset;
    
    // Update URL query
    router.replace({
      query: preset === 'month' ? {} : { period: preset }
    });
    
    fetchStats();
  };
  
  // Watch for query param changes
  watch(() => route.query.period, (newPeriod) => {
    if (newPeriod && newPeriod !== selectedPreset.value) {
      selectedPreset.value = newPeriod as DatePreset;
      fetchStats();
    }
  });
  
  return {
    isLoading,
    error,
    statsData,
    selectedPreset,
    dateRange,
    fetchStats,
    setPreset
  };
}

// Helper: Get date range from preset
function getDateRangeFromPreset(preset: DatePreset): DateRange {
  const now = new Date();
  const end = new Date(now);
  let start: Date | null = null;
  
  switch (preset) {
    case 'week':
      start = new Date(now);
      start.setDate(start.getDate() - 7);
      break;
    case 'month':
      start = new Date(now);
      start.setMonth(start.getMonth() - 1);
      break;
    case '3months':
      start = new Date(now);
      start.setMonth(start.getMonth() - 3);
      break;
    case '6months':
      start = new Date(now);
      start.setMonth(start.getMonth() - 6);
      break;
    case 'year':
      start = new Date(now);
      start.setFullYear(start.getFullYear() - 1);
      break;
    case 'all':
      start = null;
      break;
  }
  
  return { start, end: preset === 'all' ? null : end };
}

// Transform API response to view model
function transformToViewModel(
  response: StatsOverviewResponse,
  profileStore: ProfileStore
): StatsOverviewVM {
  const totalVolumeKg = parseFloat(response.total_volume_kg);
  
  // Calculate total muscle group sessions for percentages
  const totalMuscleGroupSessions = response.most_trained_muscle_groups
    .reduce((sum, mg) => sum + mg.session_count, 0);
  
  return {
    totalWorkouts: response.total_workouts,
    totalDuration: {
      seconds: response.total_duration_seconds,
      formatted: formatTotalDuration(response.total_duration_seconds)
    },
    totalVolume: {
      kg: totalVolumeKg,
      formatted: profileStore.formatVolume(totalVolumeKg)
    },
    currentStreak: response.current_streak_days,
    personalRecordsCount: response.personal_records_count,
    workoutsByMonth: response.workouts_by_month.map(wm => ({
      month: wm.month,
      monthLabel: formatMonthLabel(wm.month),
      count: wm.count
    })),
    muscleGroups: response.most_trained_muscle_groups.map(mg => ({
      muscleGroup: mg.muscle_group,
      label: formatMuscleGroupLabel(mg.muscle_group),
      sessionCount: mg.session_count,
      percentage: totalMuscleGroupSessions > 0 
        ? (mg.session_count / totalMuscleGroupSessions) * 100 
        : 0,
      color: getMuscleGroupColor(mg.muscle_group)
    }))
  };
}
```

### Custom Composable: useExerciseHistory

```typescript
// composables/useExerciseHistory.ts
export function useExerciseHistory() {
  const profileStore = useProfileStore();
  
  const selectedExerciseId = ref<string | null>(null);
  const historyData = ref<ExerciseHistoryVM | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  
  const fetchHistory = async (exerciseId: string): Promise<void> => {
    selectedExerciseId.value = exerciseId;
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await getExerciseHistory(exerciseId, { limit: 50 });
      historyData.value = transformExerciseHistory(response, profileStore);
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  const clearHistory = (): void => {
    selectedExerciseId.value = null;
    historyData.value = null;
  };
  
  return {
    selectedExerciseId,
    historyData,
    isLoading,
    error,
    fetchHistory,
    clearHistory
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Stats Overview
```
GET /api/v1/stats/overview
```

**Query Parameters**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "total_workouts": 45,
    "total_duration_seconds": 162000,
    "total_volume_kg": "125000.00",
    "workouts_by_month": [
      { "month": "2024-01", "count": 12 },
      { "month": "2023-12", "count": 10 }
    ],
    "most_trained_muscle_groups": [
      { "muscle_group": "chest", "session_count": 25 },
      { "muscle_group": "back", "session_count": 22 }
    ],
    "current_streak_days": 5,
    "personal_records_count": 15
  },
  "error": null
}
```

#### 2. Get Exercise History
```
GET /api/v1/stats/exercise/{exercise_id}/history
```

**Query Parameters**
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string
- `limit` (optional): Max sessions to return (default 50, max 100)

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "exercise": {
      "id": "uuid-string",
      "name": "Bench Press"
    },
    "sessions": [
      {
        "date": "2024-01-15T10:30:00Z",
        "total_volume": "1800.00",
        "total_reps": 30,
        "max_weight": "80.0",
        "sets": [
          { "reps": 10, "weight": "70.0", "unit": "kg" },
          { "reps": 8, "weight": "80.0", "unit": "kg" }
        ]
      }
    ]
  },
  "error": null
}
```

#### 3. List Personal Records
```
GET /api/v1/personal-records
```

**Query Parameters**
- `limit` (optional): Max records to return
- `offset` (optional): Pagination offset

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "exercise": {
        "id": "uuid-string",
        "name": "Bench Press"
      },
      "record_type": "1rm",
      "value": "85.0",
      "achieved_at": "2024-01-15T11:00:00Z"
    }
  ],
  "error": null
}
```

### API Service Functions

```typescript
// services/api/stats.ts
import axios from '@/lib/axios';
import type {
  StatsOverviewResponse,
  ExerciseHistoryResponse,
  PersonalRecordResponse
} from '@/types/stats';

export interface StatsQueryParams {
  start_date?: string;
  end_date?: string;
}

export async function getStatsOverview(
  params?: StatsQueryParams
): Promise<StatsOverviewResponse> {
  const response = await axios.get<APIResponse<StatsOverviewResponse>>(
    '/api/v1/stats/overview',
    { params }
  );
  return response.data.data;
}

export async function getExerciseHistory(
  exerciseId: string,
  params?: StatsQueryParams & { limit?: number }
): Promise<ExerciseHistoryResponse> {
  const response = await axios.get<APIResponse<ExerciseHistoryResponse>>(
    `/api/v1/stats/exercise/${exerciseId}/history`,
    { params }
  );
  return response.data.data;
}

export async function getPersonalRecords(
  params?: { limit?: number; offset?: number }
): Promise<PersonalRecordResponse[]> {
  const response = await axios.get<APIResponse<PersonalRecordResponse[]>>(
    '/api/v1/personal-records',
    { params }
  );
  return response.data.data;
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | StatsPage | `onMounted` | Fetch stats for default period (month) |
| Click preset button | DateRangeSelector | `setPreset()` | Update date range, refetch stats |
| Hover chart bar | WorkoutFrequencyChart | Native tooltip | Show exact count for month |
| Hover muscle group | MuscleGroupChart | Native tooltip | Show session count and percentage |
| Click View All PRs | PersonalRecordsSection | `router.push()` | Navigate to full PR list page |
| Click PR item | PRListItem | `router.push()` | Navigate to exercise history |
| Select exercise | ExerciseSearchDropdown | `fetchHistory()` | Load and display exercise chart |
| Hover chart point | ExerciseHistoryChart | Native tooltip | Show session details |

### Detailed Interaction Flow

1. **Initial Load**:
   - Check URL for period query param
   - Default to 'month' if not specified
   - Fetch stats overview
   - Fetch top 5 personal records
   - Render charts when data loads

2. **Date Range Change**:
   - User clicks preset button
   - Button shows active state
   - URL updates with period param
   - Stats refetch with new range
   - Charts animate to new data

3. **Exercise History Exploration**:
   - User types in search dropdown
   - Exercises matching query appear
   - User selects exercise
   - History data loads
   - Line chart renders with animation

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | All content |
| Error exists | ErrorState | All content |
| totalWorkouts = 0 | EmptyState | Charts and PRs |
| workoutsByMonth.length > 0 | WorkoutFrequencyChart | EmptyChartMessage |
| muscleGroups.length > 0 | MuscleGroupChart | EmptyChartMessage |
| personalRecordsCount > 0 | PersonalRecordsSection | - |
| selectedExerciseId != null | ExerciseHistoryChart | PlaceholderText |

### Empty States

| Scenario | Message |
|----------|---------|
| No workouts at all | "No workouts yet. Start your first workout to see stats!" |
| No workouts in range | "No workouts in this time period. Try a different range." |
| No PRs | "Keep working out to set personal records!" |
| No exercise history | "Select an exercise to see your progress over time" |

## 10. Error Handling

### API Error Handling

```typescript
async function fetchStats(): Promise<void> {
  try {
    const response = await getStatsOverview(params);
    statsData.value = transformToViewModel(response, profileStore);
  } catch (e) {
    if (axios.isAxiosError(e)) {
      if (e.response?.status === 401) {
        // Auth interceptor handles redirect
      } else if (!e.response) {
        error.value = 'Unable to connect. Please check your connection.';
      } else {
        error.value = 'Failed to load stats. Please try again.';
      }
    } else {
      error.value = 'An unexpected error occurred.';
    }
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Network error | - | "Unable to connect. Please check your connection." | Show retry button |
| Auth expired | 401 | Auto-redirect | Via interceptor |
| Server error | 500 | "Failed to load stats. Please try again." | Show retry button |
| Exercise not found | 404 | "Exercise not found." | Clear selection |

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/stats.ts` with all DTOs and ViewModels
   - Add Zod validation schemas
   - Create muscle group color mapping

2. **Create Utility Functions**
   - Create `src/utils/formatDuration.ts` - format total hours/minutes
   - Create `src/utils/formatMuscleGroup.ts` - format enum to label
   - Create `src/utils/datePresets.ts` - date range calculations
   - Create `src/utils/chartColors.ts` - consistent chart theming

3. **Create Composables**
   - Create `src/composables/useStats.ts`
   - Create `src/composables/useExerciseHistory.ts`
   - Handle date range and API integration

4. **Create Date Range Components**
   - Create `src/components/stats/DateRangeSelector.vue`
   - Create `src/components/stats/PresetButton.vue`
   - Style with active states

5. **Create Stat Card Components**
   - Create `src/components/stats/StatCard.vue`
   - Create `src/components/stats/StatCardRow.vue`
   - Icons and responsive grid

6. **Create Chart Components**
   - Create `src/components/charts/BarChart.vue` (or use chart library)
   - Create `src/components/charts/HorizontalBarChart.vue`
   - Create `src/components/charts/LineChart.vue`
   - Consider using Chart.js or lightweight alternative

7. **Create Section Components**
   - Create `src/components/stats/WorkoutFrequencySection.vue`
   - Create `src/components/stats/MuscleGroupSection.vue`
   - Create `src/components/stats/PersonalRecordsSection.vue`
   - Create `src/components/stats/ExerciseHistorySection.vue`

8. **Create PR Components**
   - Create `src/components/stats/PRListItem.vue`
   - Create `src/components/stats/PRCard.vue`
   - Style with record type badges

9. **Create Page View**
   - Create `src/views/StatsPage.vue`
   - Wire up all sections
   - Handle loading and empty states

10. **Configure Router**
    - Add route `/stats`
    - Handle query params for period

11. **Add API Integration**
    - Implement getStatsOverview
    - Implement getExerciseHistory
    - Implement getPersonalRecords (limit 5)

12. **Add Chart Library**
    - Install Chart.js or vue-chartjs
    - Create chart wrapper components
    - Configure responsive options

13. **Style with Tailwind**
    - Card layouts for stat overview
    - Responsive grid (mobile-first)
    - Chart containers with proper sizing
    - Dark mode chart colors

14. **Add Accessibility**
    - Chart alt text and descriptions
    - Keyboard navigation for date presets
    - Screen reader announcements for stat values
    - Focus management

15. **Write Tests**
    - Unit tests for composables
    - Unit tests for date utilities
    - Component tests for stat cards
    - Integration test for filter flow

16. **Manual Testing**
    - Test with various data amounts
    - Test empty states
    - Test date range filtering
    - Test chart responsiveness
    - Test on mobile devices
