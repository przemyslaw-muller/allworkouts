# View Implementation Plan: History List

## 1. Overview

The History List page provides a chronological view of all past workout sessions. Users can browse, filter, and search their workout history with filtering by status and workout type. The page features a mini-calendar visualization showing workout frequency and uses infinite scroll or load-more pagination for efficient loading of large histories.

## 2. View Routing

- **Path**: `/history`
- **Route Name**: `history`
- **Access**: Authenticated users only
- **Guard**: Redirect to `/login` if not authenticated
- **Query Parameters**:
  - `status` - Filter by session status (optional: `completed`, `abandoned`, `in_progress`)
  - `workout` - Filter by workout plan ID (optional)
  - `from` - Start date filter (optional: ISO date)
  - `to` - End date filter (optional: ISO date)

## 3. Component Structure

```
HistoryListPage (view)
├── PageHeader
│   ├── Title
│   └── MiniCalendar (workout frequency visualization)
├── FilterSection
│   ├── StatusFilterChips
│   │   ├── FilterChip (All)
│   │   ├── FilterChip (Completed)
│   │   ├── FilterChip (Abandoned)
│   │   └── FilterChip (In Progress)
│   ├── WorkoutFilterDropdown
│   └── DateRangePicker (optional)
├── SessionList
│   ├── DateGroupHeader (e.g., "Today", "Yesterday", "January 2025")
│   ├── SessionCard
│   │   ├── SessionInfo (plan name, duration, exercise count)
│   │   ├── StatusBadge
│   │   └── SessionMeta (date, time)
│   ├── SessionCard...
│   └── DateGroupHeader...
├── LoadMoreButton (or InfiniteScrollTrigger)
├── LoadingState (skeleton)
└── EmptyState (conditional - no sessions)
    └── StartWorkoutCTA
```

## 4. Component Details

### HistoryListPage
- **Description**: Main view component that manages the history list, filters, and pagination. Fetches sessions on mount and handles filter changes.
- **Main elements**:
  - PageHeader with title and MiniCalendar
  - FilterSection for filtering sessions
  - SessionList grouped by date
  - LoadMoreButton or infinite scroll
  - Loading and empty states
- **Handled interactions**:
  - Fetches initial data on mount
  - Updates URL query params when filters change
  - Handles pagination (load more)
- **Handled validation**: None
- **Types**: `HistoryListData` (ViewModel)
- **Props**: None

### PageHeader
- **Description**: Header section with page title and mini-calendar showing workout frequency.
- **Main elements**:
  - Page title "Workout History"
  - MiniCalendar component showing last 30 days
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `workoutDates: Date[]` - Dates when workouts occurred

### MiniCalendar
- **Description**: Compact calendar visualization showing which days had workouts. Similar to GitHub contribution graph but for workouts.
- **Main elements**:
  - Grid of 30-35 day cells
  - Cells colored by workout status (completed = green, abandoned = gray)
  - Current day indicator
  - Month labels
- **Handled interactions**:
  - `@click` on day cell - Jump to that date in list (optional)
- **Handled validation**: None
- **Types**: `WorkoutDay[]`
- **Props**:
  - `days: WorkoutDay[]` - Array of day data with workout info

### FilterSection
- **Description**: Filter controls for narrowing down session list.
- **Main elements**:
  - StatusFilterChips row
  - WorkoutFilterDropdown
  - DateRangePicker (optional, expandable)
- **Handled interactions**:
  - Emits filter changes to parent
- **Handled validation**: None
- **Types**: `SessionFilters`
- **Props**:
  - `filters: SessionFilters` - Current filter values
  - `workoutOptions: WorkoutOption[]` - Available workout plans
- **Events**:
  - `@update:filters` - Filter values changed

### StatusFilterChips
- **Description**: Horizontal scrollable chip row for filtering by session status.
- **Main elements**:
  - Chip buttons: All, Completed, Abandoned, In Progress
  - Active chip highlighted
  - Horizontal scroll on mobile
- **Handled interactions**:
  - `@click` on chip - Update status filter
- **Handled validation**: None
- **Types**: `SessionStatusEnum | null`
- **Props**:
  - `selected: SessionStatusEnum | null` - Currently selected status
- **Events**:
  - `@update:selected` - Status selection changed

### WorkoutFilterDropdown
- **Description**: Dropdown to filter by specific workout plan.
- **Main elements**:
  - Dropdown button showing current selection
  - List of workout plans user has used
  - "All Workouts" option
- **Handled interactions**:
  - `@select` - Select workout plan filter
- **Handled validation**: None
- **Types**: `WorkoutOption`
- **Props**:
  - `options: WorkoutOption[]` - Available workout plans
  - `selected: string | null` - Selected workout plan ID
- **Events**:
  - `@update:selected` - Workout selection changed

### DateRangePicker
- **Description**: Optional date range filter for narrowing down time period.
- **Main elements**:
  - From date input
  - To date input
  - Quick presets (This week, This month, Last 30 days)
  - Clear button
- **Handled interactions**:
  - `@change` - Date range changed
- **Handled validation**:
  - From date must be before or equal to To date
  - Dates cannot be in the future
- **Types**: `DateRange`
- **Props**:
  - `range: DateRange | null` - Current date range
- **Events**:
  - `@update:range` - Date range changed

### SessionList
- **Description**: Scrollable list of session cards grouped by date.
- **Main elements**:
  - DateGroupHeader components for date groupings
  - SessionCard components within each group
  - Virtualized list for performance (if many items)
- **Handled interactions**:
  - Scrolls to maintain position during load more
- **Handled validation**: None
- **Types**: `GroupedSessions`
- **Props**:
  - `groups: GroupedSessions[]` - Sessions grouped by date

### DateGroupHeader
- **Description**: Sticky header showing date group label.
- **Main elements**:
  - Date label ("Today", "Yesterday", or formatted date)
  - Session count for that day (optional)
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `label: string` - Formatted date label
  - `count: number` - Number of sessions on that date

### SessionCard
- **Description**: Card displaying a single workout session with key information.
- **Main elements**:
  - Workout/Plan name
  - Date and time
  - Duration (formatted)
  - Exercise count
  - Status badge
  - Chevron or tap indicator
- **Handled interactions**:
  - `@click` - Navigate to session detail
- **Handled validation**: None
- **Types**: `SessionCardInfo` (ViewModel)
- **Props**:
  - `session: SessionCardInfo` - Session data

### StatusBadge
- **Description**: Visual badge indicating session status.
- **Main elements**:
  - Colored badge with icon and text
  - Completed: Green checkmark
  - Abandoned: Gray/red X
  - In Progress: Blue clock
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: `SessionStatusEnum`
- **Props**:
  - `status: SessionStatusEnum` - Session status

### LoadMoreButton
- **Description**: Button to load additional sessions, or intersection observer for infinite scroll.
- **Main elements**:
  - "Load More" button with loading state
  - Remaining count indicator (optional)
- **Handled interactions**:
  - `@click` - Load next page of sessions
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `isLoading: boolean` - Loading state
  - `hasMore: boolean` - Whether more sessions exist
- **Events**:
  - `@load-more` - Request to load more

### EmptyState
- **Description**: Shown when no workout sessions exist or no results match filters.
- **Main elements**:
  - Illustration/icon
  - Heading (context-dependent)
  - Description text
  - CTA button (context-dependent)
- **Handled interactions**:
  - `@click` on CTA - Navigate based on context
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `hasFilters: boolean` - Whether filters are applied
- **Events**:
  - `@clear-filters` - Clear all filters
  - `@start-workout` - Navigate to start workout

## 5. Types

### DTOs (matching backend schemas)

```typescript
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

interface PaginationInfo {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Enums
type SessionStatusEnum = 'in_progress' | 'completed' | 'abandoned';
```

### ViewModels (frontend-specific)

```typescript
// History list page data
interface HistoryListData {
  sessions: SessionCardInfo[];
  groupedSessions: GroupedSessions[];
  workoutDays: WorkoutDay[];
  pagination: PaginationState;
  filters: SessionFilters;
  workoutOptions: WorkoutOption[];
  isLoading: boolean;
  isLoadingMore: boolean;
  error: string | null;
}

// Session card display info
interface SessionCardInfo {
  id: string;
  planId: string;
  planName: string;
  date: Date;
  dateFormatted: string; // "Jan 15, 2025"
  timeFormatted: string; // "6:30 PM"
  relativeDate: string; // "Today", "2 days ago", etc.
  durationFormatted: string; // "45 min" or "1h 15m"
  durationSeconds: number;
  exerciseCount: number;
  status: SessionStatusEnum;
}

// Sessions grouped by date for display
interface GroupedSessions {
  dateLabel: string; // "Today", "Yesterday", "January 15, 2025"
  dateKey: string; // "2025-01-15"
  sessions: SessionCardInfo[];
}

// Mini calendar day data
interface WorkoutDay {
  date: Date;
  dateKey: string; // "2025-01-15"
  hasWorkout: boolean;
  status: SessionStatusEnum | null;
  sessionCount: number;
}

// Filter state
interface SessionFilters {
  status: SessionStatusEnum | null;
  workoutPlanId: string | null;
  fromDate: Date | null;
  toDate: Date | null;
}

// Workout option for dropdown
interface WorkoutOption {
  id: string;
  name: string;
}

// Pagination state
interface PaginationState {
  page: number;
  perPage: number;
  total: number;
  totalPages: number;
  hasMore: boolean;
}

// Date range for picker
interface DateRange {
  from: Date;
  to: Date;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const sessionStatusSchema = z.enum(['in_progress', 'completed', 'abandoned']);

const workoutPlanBriefSchema = z.object({
  id: z.string().uuid(),
  name: z.string()
});

const paginationInfoSchema = z.object({
  total: z.number().int().min(0),
  page: z.number().int().min(1),
  per_page: z.number().int().min(1),
  total_pages: z.number().int().min(0)
});

const workoutSessionListItemSchema = z.object({
  id: z.string().uuid(),
  workout_plan: workoutPlanBriefSchema,
  status: sessionStatusSchema,
  exercise_count: z.number().int().min(0),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime()
});

const workoutSessionListResponseSchema = z.object({
  sessions: z.array(workoutSessionListItemSchema),
  pagination: paginationInfoSchema
});

// Filter validation
const sessionFiltersSchema = z.object({
  status: sessionStatusSchema.nullable(),
  workoutPlanId: z.string().uuid().nullable(),
  fromDate: z.date().nullable(),
  toDate: z.date().nullable()
}).refine(
  (data) => {
    if (data.fromDate && data.toDate) {
      return data.fromDate <= data.toDate;
    }
    return true;
  },
  { message: 'From date must be before or equal to To date' }
);
```

## 6. State Management

### Local Component State (HistoryListPage)

```typescript
const isLoading = ref(true);
const isLoadingMore = ref(false);
const error = ref<string | null>(null);

const sessions = ref<SessionCardInfo[]>([]);
const pagination = ref<PaginationState>({
  page: 1,
  perPage: 20,
  total: 0,
  totalPages: 0,
  hasMore: false
});

const filters = ref<SessionFilters>({
  status: null,
  workoutPlanId: null,
  fromDate: null,
  toDate: null
});

const workoutOptions = ref<WorkoutOption[]>([]);
const workoutDays = ref<WorkoutDay[]>([]);
```

### Pinia Stores Used

```typescript
// sessionStore - for managing session history cache
interface SessionStore {
  historySessions: WorkoutSessionListItem[];
  historyPagination: PaginationInfo | null;
  historyFilters: SessionFilters;
  
  fetchHistory(params: HistoryFetchParams): Promise<void>;
  loadMoreHistory(): Promise<void>;
  setFilters(filters: SessionFilters): void;
  clearHistory(): void;
}

// planStore - for workout options in filter
interface PlanStore {
  plans: WorkoutPlanListItem[];
  fetchPlansIfNeeded(): Promise<void>;
}
```

### Custom Composable: useHistoryList

```typescript
// composables/useHistoryList.ts
export function useHistoryList() {
  const router = useRouter();
  const route = useRoute();
  
  const isLoading = ref(true);
  const isLoadingMore = ref(false);
  const error = ref<string | null>(null);
  const sessions = ref<SessionCardInfo[]>([]);
  const groupedSessions = computed<GroupedSessions[]>(() => groupSessionsByDate(sessions.value));
  const workoutDays = ref<WorkoutDay[]>([]);
  const pagination = ref<PaginationState>({ ... });
  const filters = ref<SessionFilters>({ ... });
  const workoutOptions = ref<WorkoutOption[]>([]);
  
  // Initialize filters from URL query params
  const initFiltersFromUrl = (): void => { ... };
  
  // Update URL when filters change
  const updateUrlFromFilters = (): void => { ... };
  
  // Fetch sessions with current filters
  const fetchSessions = async (reset = true): Promise<void> => { ... };
  
  // Load more sessions
  const loadMore = async (): Promise<void> => { ... };
  
  // Update filters and refetch
  const updateFilters = async (newFilters: Partial<SessionFilters>): Promise<void> => { ... };
  
  // Clear all filters
  const clearFilters = async (): Promise<void> => { ... };
  
  // Navigate to session detail
  const viewSession = (sessionId: string): void => {
    router.push({ name: 'sessionDetail', params: { sessionId } });
  };
  
  // Group sessions by date
  const groupSessionsByDate = (sessions: SessionCardInfo[]): GroupedSessions[] => { ... };
  
  // Generate mini calendar data
  const generateCalendarDays = (sessions: WorkoutSessionListItem[]): WorkoutDay[] => { ... };
  
  return {
    isLoading,
    isLoadingMore,
    error,
    sessions,
    groupedSessions,
    workoutDays,
    pagination,
    filters,
    workoutOptions,
    fetchSessions,
    loadMore,
    updateFilters,
    clearFilters,
    viewSession
  };
}
```

### Utility Composable: useDateFormatting

```typescript
// composables/useDateFormatting.ts
export function useDateFormatting() {
  const formatRelativeDate = (date: Date): string => {
    const now = new Date();
    const diffDays = differenceInDays(now, date);
    
    if (isToday(date)) return 'Today';
    if (isYesterday(date)) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return format(date, 'MMM d, yyyy');
  };
  
  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes} min`;
  };
  
  const formatTime = (date: Date): string => {
    return format(date, 'h:mm a');
  };
  
  const getDateGroupLabel = (date: Date): string => {
    if (isToday(date)) return 'Today';
    if (isYesterday(date)) return 'Yesterday';
    if (isThisWeek(date)) return format(date, 'EEEE'); // Day name
    if (isThisYear(date)) return format(date, 'MMMM d');
    return format(date, 'MMMM d, yyyy');
  };
  
  return {
    formatRelativeDate,
    formatDuration,
    formatTime,
    getDateGroupLabel
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Workout Sessions (History)
```
GET /api/v1/workout-sessions
```

**Query Parameters**
- `page` (int, default 1): Page number
- `per_page` (int, default 20): Items per page
- `status` (string, optional): Filter by status (completed, abandoned, in_progress)
- `workout_plan_id` (UUID, optional): Filter by workout plan
- `from_date` (ISO date, optional): Start date filter
- `to_date` (ISO date, optional): End date filter
- `sort` (string, default "created_at:desc"): Sort order

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
    "pagination": {
      "total": 45,
      "page": 1,
      "per_page": 20,
      "total_pages": 3
    }
  },
  "error": null
}
```

#### 2. Get Workout Plans (for filter dropdown)
```
GET /api/v1/workout-plans
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "plans": [
      { "id": "uuid", "name": "Push Day", ... },
      { "id": "uuid", "name": "Pull Day", ... }
    ],
    "pagination": { ... }
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/sessions.ts
import axios from '@/lib/axios';
import type { 
  WorkoutSessionListResponse,
  WorkoutSessionDetailResponse 
} from '@/types/workout-sessions';

interface GetSessionsParams {
  page?: number;
  per_page?: number;
  status?: SessionStatusEnum;
  workout_plan_id?: string;
  from_date?: string;
  to_date?: string;
  sort?: string;
}

export async function getWorkoutSessions(
  params: GetSessionsParams = {}
): Promise<WorkoutSessionListResponse> {
  const response = await axios.get<APIResponse<WorkoutSessionListResponse>>(
    '/api/v1/workout-sessions',
    { params }
  );
  return response.data.data;
}

export async function getWorkoutSessionsForCalendar(
  fromDate: string,
  toDate: string
): Promise<WorkoutSessionListItem[]> {
  // Fetch all sessions in date range for calendar
  const response = await axios.get<APIResponse<WorkoutSessionListResponse>>(
    '/api/v1/workout-sessions',
    { 
      params: { 
        from_date: fromDate, 
        to_date: toDate,
        per_page: 100 // Get all sessions in range
      } 
    }
  );
  return response.data.data.sessions;
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | HistoryListPage | `onMounted` | Initialize filters from URL, fetch sessions |
| Click status chip | StatusFilterChips | `updateFilters()` | Filter by status, refetch, update URL |
| Select workout | WorkoutFilterDropdown | `updateFilters()` | Filter by workout, refetch, update URL |
| Change date range | DateRangePicker | `updateFilters()` | Filter by dates, refetch, update URL |
| Click session card | SessionCard | `viewSession()` | Navigate to `/history/:sessionId` |
| Click Load More | LoadMoreButton | `loadMore()` | Fetch next page, append to list |
| Scroll to bottom | InfiniteScrollTrigger | `loadMore()` | Auto-fetch next page |
| Click Clear Filters | FilterSection | `clearFilters()` | Reset filters, refetch all |
| Click calendar day | MiniCalendar | Scroll to date | Scroll list to that date group |
| Click Start Workout | EmptyState | Router navigation | Navigate to dashboard |
| Pull to refresh | HistoryListPage (mobile) | `fetchSessions(true)` | Refetch from beginning |

### Detailed Interaction Flow

1. **Initial Load**:
   - Parse URL query params for filters
   - Show loading skeletons
   - Fetch sessions with current filters in parallel with calendar data
   - Transform to view models, group by date
   - Hide loading, show content

2. **Filtering**:
   - User selects filter option
   - Update URL query params
   - Show inline loading indicator
   - Fetch sessions with new filters
   - Replace list content
   - Scroll to top

3. **Load More**:
   - User clicks Load More or scrolls to trigger
   - Show loading indicator on button
   - Fetch next page
   - Append new sessions to existing list
   - Update pagination state

4. **Navigation to Detail**:
   - User taps/clicks session card
   - Navigate to session detail page
   - Preserve filter state in URL for back navigation

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | SessionList, EmptyState |
| Sessions exist | SessionList | EmptyState |
| No sessions, no filters | EmptyState (no history) | SessionList |
| No sessions, has filters | EmptyState (no results) | SessionList |
| hasMore = true | LoadMoreButton | - |
| hasMore = false | - | LoadMoreButton |
| isLoadingMore = true | LoadMoreButton (loading) | - |
| Error exists | ErrorBanner | - |

### Filter Validation

| Validation | Condition | Error Message |
|------------|-----------|---------------|
| Date range | fromDate <= toDate | "Start date must be before end date" |
| Future dates | date <= today | "Cannot filter by future dates" |

## 10. Error Handling

### API Error Handling

```typescript
async function fetchSessions(reset = true): Promise<void> {
  if (reset) {
    isLoading.value = true;
    pagination.value.page = 1;
  } else {
    isLoadingMore.value = true;
  }
  error.value = null;
  
  try {
    const params = buildApiParams(filters.value, pagination.value);
    const response = await getWorkoutSessions(params);
    
    const mapped = response.sessions.map(mapSessionToViewModel);
    
    if (reset) {
      sessions.value = mapped;
    } else {
      sessions.value = [...sessions.value, ...mapped];
    }
    
    pagination.value = {
      page: response.pagination.page,
      perPage: response.pagination.per_page,
      total: response.pagination.total,
      totalPages: response.pagination.total_pages,
      hasMore: response.pagination.page < response.pagination.total_pages
    };
    
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const status = e.response?.status;
      
      if (status === 401) {
        // Handled by interceptor - redirect to login
        return;
      }
      
      if (status === 400) {
        error.value = 'Invalid filter parameters. Please adjust your filters.';
      } else if (status >= 500) {
        error.value = 'Server error. Please try again later.';
      } else {
        error.value = 'Failed to load workout history.';
      }
    } else {
      error.value = 'An unexpected error occurred.';
    }
    
    showToast({
      type: 'error',
      message: error.value
    });
  } finally {
    isLoading.value = false;
    isLoadingMore.value = false;
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Network error | - | "Unable to connect. Check your connection." | Retry button |
| Auth expired | 401 | Auto-redirect to login | Redirect via interceptor |
| Bad request | 400 | "Invalid filter parameters." | Clear filters option |
| Server error | 500 | "Something went wrong. Please try again." | Retry button |
| Empty results | - | "No workouts found" / "No workouts match your filters" | Context-specific CTA |

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/history.ts` with ViewModels
   - Add Zod schemas for filter validation
   - Extend existing session types if needed

2. **Create API Service Functions**
   - Add `getWorkoutSessions` to `src/services/api/sessions.ts`
   - Add helper for calendar data fetching
   - Ensure proper error handling

3. **Create Composables**
   - Create `src/composables/useHistoryList.ts`
   - Create `src/composables/useDateFormatting.ts` (if not existing)
   - Implement date grouping logic

4. **Create Filter Components**
   - Create `src/components/history/StatusFilterChips.vue`
   - Create `src/components/history/WorkoutFilterDropdown.vue`
   - Create `src/components/history/DateRangePicker.vue` (optional)
   - Create `src/components/history/FilterSection.vue`

5. **Create MiniCalendar Component**
   - Create `src/components/history/MiniCalendar.vue`
   - Implement day cell rendering with status colors
   - Add click-to-scroll interaction

6. **Create Session Card Components**
   - Create `src/components/history/SessionCard.vue`
   - Create `src/components/common/StatusBadge.vue`
   - Create `src/components/history/DateGroupHeader.vue`

7. **Create List Components**
   - Create `src/components/history/SessionList.vue`
   - Create `src/components/common/LoadMoreButton.vue`

8. **Create Page View**
   - Create `src/views/HistoryListPage.vue`
   - Wire up all components and composable
   - Implement URL query param sync

9. **Configure Router**
   - Add history route to `src/router/index.ts`
   - Set up query param handling

10. **Add Loading and Empty States**
    - Create loading skeletons for session cards
    - Create empty states for no history and no results
    - Add error state with retry

11. **Style with Tailwind**
    - Apply responsive layouts (cards stack on mobile)
    - Style filter chips with active states
    - Add sticky date group headers
    - Support dark mode

12. **Add Accessibility**
    - Add proper heading hierarchy
    - Ensure filter chips are keyboard navigable
    - Add ARIA labels for status badges
    - Implement focus management after filter changes

13. **Write Tests**
    - Unit tests for date formatting utilities
    - Unit tests for grouping logic
    - Component tests for filter interactions
    - Integration test for full page flow

14. **Manual Testing**
    - Test with various filter combinations
    - Test empty states
    - Test pagination/load more
    - Test on mobile and desktop
    - Verify URL query param persistence
