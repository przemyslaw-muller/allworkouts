# View Implementation Plan: Plans List

## 1. Overview

The Plans List page displays all of the user's workout plans in a browsable, manageable format. Users can view their plans, see basic info (name, exercise count, last used), create new plans via import, set an active plan, and manage existing plans (edit/delete). This page serves as the central hub for workout plan management.

## 2. View Routing

- **Path**: `/plans`
- **Route Name**: `plans`
- **Access**: Authenticated users only
- **Guard**: Redirect to `/login` if not authenticated

## 3. Component Structure

```
PlansListPage (view)
├── PageHeader
│   ├── PageTitle ("Workout Plans")
│   └── ImportPlanButton
├── PlansListFilters (optional future)
│   └── SearchInput
├── PlansList
│   ├── PlanCard
│   │   ├── PlanInfo (name, description, exercise count)
│   │   ├── PlanMeta (created date, last used)
│   │   ├── ActiveBadge (conditional)
│   │   └── PlanActions (view, edit, delete, set active)
│   ├── PlanCard
│   └── ... (more cards)
├── EmptyState (conditional - no plans)
│   └── ImportPlanCTA
├── LoadingState (conditional)
│   └── PlanCardSkeleton (x3)
└── Pagination (conditional - many plans)
```

## 4. Component Details

### PlansListPage
- **Description**: Main view component that fetches and displays the list of workout plans. Manages loading, error, and empty states.
- **Main elements**:
  - PageHeader with title and import button
  - PlansList or EmptyState based on data
  - Pagination if needed
- **Handled interactions**: 
  - Orchestrates data fetching on mount
  - Handles plan deletion confirmation
  - Manages active plan selection
- **Handled validation**: None
- **Types**: `PlansListState` (ViewModel)
- **Props**: None

### PageHeader
- **Description**: Top section with page title and primary action button.
- **Main elements**:
  - "Workout Plans" heading (h1)
  - "Import Plan" button (primary CTA)
- **Handled interactions**:
  - `@click` on Import Plan - Navigate to import wizard
- **Handled validation**: None
- **Types**: None
- **Props**: None

### PlansList
- **Description**: Container for the grid/list of plan cards.
- **Main elements**:
  - Responsive grid layout (1 col mobile, 2-3 cols desktop)
  - PlanCard components
- **Handled interactions**: None (delegates to children)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `plans: PlanListItemViewModel[]` - Array of plans to display

### PlanCard
- **Description**: Card displaying a single workout plan with actions.
- **Main elements**:
  - Plan name (clickable, links to detail)
  - Description (truncated, 2 lines max)
  - Exercise count badge
  - "Active" badge if this is the active plan
  - Created/last used dates
  - Action buttons/menu (View, Edit, Delete, Set Active)
- **Handled interactions**:
  - `@click` on card - Navigate to plan detail
  - `@click` on View - Navigate to plan detail
  - `@click` on Edit - Navigate to plan edit
  - `@click` on Delete - Emit delete event (parent handles confirm)
  - `@click` on Set Active - Emit setActive event
- **Handled validation**: None
- **Types**: `PlanListItemViewModel`
- **Props**:
  - `plan: PlanListItemViewModel` - Plan data
  - `isActive: boolean` - Whether this is the active plan

### PlanActions
- **Description**: Action buttons or dropdown menu for plan operations.
- **Main elements**:
  - Kebab menu icon (mobile) or button group (desktop)
  - View, Edit, Delete, Set Active options
- **Handled interactions**:
  - `@view` - Emit view event
  - `@edit` - Emit edit event
  - `@delete` - Emit delete event
  - `@setActive` - Emit setActive event
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `planId: string` - Plan ID
  - `isActive: boolean` - Whether this plan is active

### EmptyState
- **Description**: Shown when user has no workout plans. Encourages creating first plan via import.
- **Main elements**:
  - Illustration/icon
  - "No workout plans yet" heading
  - Description encouraging plan creation
  - "Import Your First Plan" button
- **Handled interactions**:
  - `@click` on button - Navigate to import wizard
- **Handled validation**: None
- **Types**: None
- **Props**: None

### DeleteConfirmDialog
- **Description**: Modal dialog confirming plan deletion.
- **Main elements**:
  - Warning icon
  - Confirmation message with plan name
  - Cancel button
  - Delete button (destructive)
- **Handled interactions**:
  - `@cancel` - Close dialog
  - `@confirm` - Execute delete, close dialog
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `planName: string` - Name of plan to delete
  - `isOpen: boolean` - Dialog visibility
  - `isDeleting: boolean` - Loading state

## 5. Types

### DTOs (matching backend schemas)

```typescript
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

interface PaginationInfo {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
```

### ViewModels (frontend-specific)

```typescript
// Plan list item for display
interface PlanListItemViewModel {
  id: string;
  name: string;
  description: string | null;
  exerciseCount: number;
  createdAt: Date;
  updatedAt: Date;
  lastUsedAt: Date | null; // From session history, computed
  isActive: boolean;
}

// Page state
interface PlansListState {
  plans: PlanListItemViewModel[];
  activePlanId: string | null;
  isLoading: boolean;
  error: string | null;
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
  };
}

// Delete dialog state
interface DeleteDialogState {
  isOpen: boolean;
  planId: string | null;
  planName: string;
  isDeleting: boolean;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const paginationInfoSchema = z.object({
  total: z.number().int().min(0),
  page: z.number().int().min(1),
  per_page: z.number().int().min(1),
  total_pages: z.number().int().min(0)
});

const workoutPlanListItemSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  description: z.string().nullable(),
  exercise_count: z.number().int().min(0),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime()
});

const workoutPlanListResponseSchema = z.object({
  plans: z.array(workoutPlanListItemSchema),
  pagination: paginationInfoSchema
});
```

## 6. State Management

### Local Component State (PlansListPage)

```typescript
const isLoading = ref(true);
const error = ref<string | null>(null);
const plans = ref<PlanListItemViewModel[]>([]);
const pagination = ref({
  currentPage: 1,
  totalPages: 1,
  totalItems: 0
});

const deleteDialog = ref<DeleteDialogState>({
  isOpen: false,
  planId: null,
  planName: '',
  isDeleting: false
});
```

### Pinia Store (workoutPlanStore)

```typescript
// stores/workoutPlan.ts
interface WorkoutPlanStore {
  // State
  plans: WorkoutPlanListItem[];
  activePlanId: string | null;
  isLoading: boolean;
  error: string | null;
  pagination: PaginationInfo | null;
  
  // Getters
  activePlan: WorkoutPlanListItem | null;
  hasPlans: boolean;
  
  // Actions
  fetchPlans(page?: number): Promise<void>;
  deletePlan(planId: string): Promise<void>;
  setActivePlan(planId: string): void;
  clearActivePlan(): void;
}
```

### Custom Composable: usePlansList

```typescript
// composables/usePlansList.ts
export function usePlansList() {
  const workoutPlanStore = useWorkoutPlanStore();
  const router = useRouter();
  
  const plans = computed(() => workoutPlanStore.plans.map(mapToViewModel));
  const isLoading = computed(() => workoutPlanStore.isLoading);
  const activePlanId = computed(() => workoutPlanStore.activePlanId);
  
  const deleteDialog = ref<DeleteDialogState>({ ... });
  
  const fetchPlans = async (page?: number): Promise<void> => { ... };
  const openDeleteDialog = (plan: PlanListItemViewModel): void => { ... };
  const confirmDelete = async (): Promise<void> => { ... };
  const cancelDelete = (): void => { ... };
  const setActivePlan = (planId: string): void => { ... };
  const navigateToPlan = (planId: string): void => { ... };
  const navigateToEdit = (planId: string): void => { ... };
  const navigateToImport = (): void => { ... };
  
  return {
    plans,
    isLoading,
    activePlanId,
    deleteDialog,
    fetchPlans,
    openDeleteDialog,
    confirmDelete,
    cancelDelete,
    setActivePlan,
    navigateToPlan,
    navigateToEdit,
    navigateToImport
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Workout Plans
```
GET /api/v1/workout-plans?page=1&per_page=20
```

**Request Query Parameters**
```typescript
{
  page?: number; // Default 1
  per_page?: number; // Default 20
}
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
        "description": "Classic 3-day split",
        "exercise_count": 6,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-16T08:00:00Z"
      },
      {
        "id": "uuid-string-2",
        "name": "Full Body",
        "description": null,
        "exercise_count": 8,
        "created_at": "2025-01-10T10:00:00Z",
        "updated_at": "2025-01-10T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 5,
      "page": 1,
      "per_page": 20,
      "total_pages": 1
    }
  },
  "error": null
}
```

#### 2. Delete Workout Plan
```
DELETE /api/v1/workout-plans/{plan_id}
```

**Response (204 No Content)**
```typescript
// Empty response on success
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

**Error Response (400 Bad Request - has active session)**
```typescript
{
  "success": false,
  "data": null,
  "error": {
    "code": "PLAN_HAS_ACTIVE_SESSION",
    "message": "Cannot delete plan with an active workout session"
  }
}
```

### API Service Functions

```typescript
// services/api/workoutPlans.ts
import axios from '@/lib/axios';
import type { WorkoutPlanListResponse } from '@/types/workout-plans';

export async function getWorkoutPlans(params?: {
  page?: number;
  per_page?: number;
}): Promise<WorkoutPlanListResponse> {
  const response = await axios.get<APIResponse<WorkoutPlanListResponse>>(
    '/api/v1/workout-plans',
    { params }
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
| Page load | PlansListPage | `onMounted` | Fetch plans list |
| Click Import Plan | PageHeader button | `navigateToImport()` | Navigate to `/plans/import` |
| Click plan card | PlanCard | `navigateToPlan()` | Navigate to `/plans/:id` |
| Click View | PlanActions menu | `navigateToPlan()` | Navigate to `/plans/:id` |
| Click Edit | PlanActions menu | `navigateToEdit()` | Navigate to `/plans/:id/edit` |
| Click Delete | PlanActions menu | `openDeleteDialog()` | Show delete confirmation |
| Click Set Active | PlanActions menu | `setActivePlan()` | Update active plan, show toast |
| Confirm delete | DeleteConfirmDialog | `confirmDelete()` | Delete plan, refresh list, show toast |
| Cancel delete | DeleteConfirmDialog | `cancelDelete()` | Close dialog |
| Click page number | Pagination | `fetchPlans(page)` | Fetch plans for page |
| Click Import (empty) | EmptyState | `navigateToImport()` | Navigate to `/plans/import` |

### Detailed Interaction Flow

1. **Page Load**:
   - Show loading skeleton (3 card placeholders)
   - Fetch workout plans from API
   - Render plan cards or empty state
   - Load active plan ID from localStorage/store

2. **Viewing a Plan**:
   - User clicks on plan card or View action
   - Navigate to `/plans/:planId`

3. **Editing a Plan**:
   - User clicks Edit action
   - Navigate to `/plans/:planId/edit`

4. **Deleting a Plan**:
   - User clicks Delete action
   - Show confirmation dialog with plan name
   - If confirmed:
     - Show loading state on delete button
     - Call DELETE API
     - On success: Close dialog, remove from list, show success toast
     - On error: Show error message in dialog

5. **Setting Active Plan**:
   - User clicks Set Active action
   - Update activePlanId in store
   - Persist to localStorage
   - Show "Active" badge on card
   - Show success toast

6. **Pagination**:
   - User clicks page number or next/prev
   - Show loading indicator
   - Fetch new page of plans
   - Scroll to top of list

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingState (skeletons) | PlansList, EmptyState |
| plans.length > 0 | PlansList | EmptyState |
| plans.length = 0 | EmptyState | PlansList |
| totalPages > 1 | Pagination | - |
| plan.isActive | ActiveBadge | - |
| error exists | ErrorState | PlansList |

### Card Display Logic

| Condition | UI Element |
|-----------|-----------|
| description exists | Show description (truncated) |
| description is null | Hide description section |
| isActive = true | Show green "Active" badge |
| exerciseCount > 0 | Show "{n} exercises" badge |
| exerciseCount = 0 | Show "No exercises" with warning style |

### Delete Validation

| Condition | Behavior |
|-----------|----------|
| Plan has active session | Show error, prevent delete |
| Plan is active plan | Allow delete, clear active plan |
| Normal delete | Proceed with confirmation |

## 10. Error Handling

### API Error Handling

```typescript
async function fetchPlans(page = 1): Promise<void> {
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await getWorkoutPlans({ page, per_page: 20 });
    plans.value = response.plans.map(mapToViewModel);
    pagination.value = {
      currentPage: response.pagination.page,
      totalPages: response.pagination.total_pages,
      totalItems: response.pagination.total
    };
  } catch (e) {
    if (axios.isAxiosError(e)) {
      error.value = e.response?.data?.error?.message || 'Failed to load plans';
    } else {
      error.value = 'An unexpected error occurred';
    }
  } finally {
    isLoading.value = false;
  }
}

async function confirmDelete(): Promise<void> {
  if (!deleteDialog.value.planId) return;
  
  deleteDialog.value.isDeleting = true;
  
  try {
    await deleteWorkoutPlan(deleteDialog.value.planId);
    
    // Remove from local list
    plans.value = plans.value.filter(p => p.id !== deleteDialog.value.planId);
    
    // Clear active plan if deleted
    if (activePlanId.value === deleteDialog.value.planId) {
      clearActivePlan();
    }
    
    showToast({ type: 'success', message: 'Plan deleted successfully' });
    closeDeleteDialog();
    
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const code = e.response?.data?.error?.code;
      
      if (code === 'PLAN_HAS_ACTIVE_SESSION') {
        deleteDialog.value.error = 'Cannot delete: You have an active workout using this plan.';
      } else {
        deleteDialog.value.error = 'Failed to delete plan. Please try again.';
      }
    } else {
      deleteDialog.value.error = 'An unexpected error occurred.';
    }
  } finally {
    deleteDialog.value.isDeleting = false;
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Network error | - | "Unable to connect. Check your internet." | Retry button |
| Auth expired | 401 | Auto-redirect | Redirect via interceptor |
| Plan not found | 404 | "Plan not found" | Remove from list if exists |
| Active session exists | 400 | "Cannot delete: active session" | Show in dialog, keep dialog open |
| Server error | 500 | "Something went wrong" | Retry button |

## 11. Implementation Steps

1. **Create Types**
   - Add `PlanListItemViewModel` to `src/types/workout-plans.ts`
   - Add `PlansListState`, `DeleteDialogState` ViewModels
   - Add Zod validation schemas

2. **Create/Update API Service**
   - Add `getWorkoutPlans()` to `src/services/api/workoutPlans.ts`
   - Add `deleteWorkoutPlan()` function
   - Ensure proper error type handling

3. **Create Workout Plan Store**
   - Create `src/stores/workoutPlan.ts`
   - Implement state, getters, and actions
   - Handle active plan persistence

4. **Create Composable**
   - Create `src/composables/usePlansList.ts`
   - Implement all plan list logic
   - Handle delete confirmation flow

5. **Create Base Components** (if not existing)
   - Ensure `BaseButton`, `BaseCard` components exist
   - Create `ConfirmDialog` component
   - Create `DropdownMenu` for actions

6. **Create Plan Components**
   - Create `src/components/plans/PlanCard.vue`
   - Create `src/components/plans/PlanActions.vue`
   - Create `src/components/plans/DeleteConfirmDialog.vue`

7. **Create Plans List Page**
   - Create `src/views/plans/PlansListPage.vue`
   - Implement layout with header and list
   - Wire up all interactions

8. **Configure Router**
   - Add `/plans` route to router
   - Ensure auth guard is applied

9. **Add Loading States**
   - Create skeleton cards for loading
   - Add loading indicator to delete button
   - Handle pagination loading

10. **Style with Tailwind**
    - Apply responsive grid (1/2/3 columns)
    - Style plan cards with hover effects
    - Add "Active" badge styling
    - Ensure mobile-friendly action menus

11. **Add Accessibility**
    - Proper heading hierarchy
    - Focus management for dialogs
    - Keyboard navigation for menus
    - ARIA labels for actions

12. **Write Tests**
    - Unit tests for store and composable
    - Component tests for PlanCard
    - Integration test for delete flow
    - Test empty and loading states

13. **Manual Testing**
    - Test with 0, 1, and many plans
    - Test delete confirmation flow
    - Test active plan selection
    - Test pagination (if applicable)
    - Verify responsive layout
