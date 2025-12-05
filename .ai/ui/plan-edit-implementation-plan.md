# View Implementation Plan: Plan Edit

## 1. Overview

The Plan Edit page allows users to modify an existing workout plan. Users can change the plan name, description, reorder exercises, modify exercise parameters (sets, reps, rest time), substitute exercises, remove exercises, or add new exercises. The page supports drag-and-drop reordering on desktop and touch-based reordering on mobile. Changes can be saved or discarded.

## 2. View Routing

- **Path**: `/plans/:planId/edit`
- **Route Name**: `planEdit`
- **Route Params**: `planId: string` (UUID)
- **Access**: Authenticated users only
- **Guard**: 
  - Redirect to `/login` if not authenticated
  - Warn before leaving with unsaved changes

## 3. Component Structure

```
PlanEditPage (view)
├── PlanEditHeader
│   ├── BackButton (with unsaved changes check)
│   ├── PageTitle ("Edit Plan")
│   └── SaveButton (disabled if no changes/invalid)
├── PlanInfoForm
│   ├── FormField (name)
│   │   └── BaseInput
│   └── FormField (description)
│       └── BaseTextarea
├── ExerciseListEditor
│   ├── DraggableList
│   │   ├── EditableExerciseCard
│   │   │   ├── DragHandle
│   │   │   ├── ExerciseSelector (for substitution)
│   │   │   ├── SetsInput
│   │   │   ├── RepsInputs (min/max)
│   │   │   ├── RestTimeInput
│   │   │   └── RemoveButton
│   │   ├── EditableExerciseCard
│   │   └── ... (more exercises)
│   └── AddExerciseButton
├── AddExerciseModal
│   ├── ExerciseSearch
│   ├── ExerciseResultsList
│   └── ExerciseSelectionForm
├── SubstituteExerciseModal
│   ├── CurrentExerciseInfo
│   ├── SimilarExercisesList
│   └── SearchAllExercises
├── UnsavedChangesDialog
└── LoadingOverlay (while saving)
```

## 4. Component Details

### PlanEditPage
- **Description**: Main view that manages the plan editing form state, validation, and submission. Fetches current plan data, tracks changes, and handles save/cancel operations.
- **Main elements**:
  - PlanEditHeader with save action
  - PlanInfoForm for name/description
  - ExerciseListEditor for exercise management
  - Modals for adding/substituting exercises
- **Handled interactions**: 
  - Fetch plan on mount
  - Track dirty state
  - Handle save submission
  - Guard against accidental navigation
- **Handled validation**: Full form validation before save
- **Types**: `PlanEditFormData`, `PlanEditState`
- **Props**: None (uses route params)

### PlanEditHeader
- **Description**: Header with back navigation and save action.
- **Main elements**:
  - Back button (checks for unsaved changes)
  - "Edit Plan" title
  - Save button (primary, disabled when invalid or unchanged)
- **Handled interactions**:
  - `@back` - Check unsaved, navigate
  - `@save` - Trigger save
- **Handled validation**: None (parent validates)
- **Types**: None
- **Props**:
  - `isSaving: boolean` - Loading state for save button
  - `canSave: boolean` - Whether form is valid and dirty
  - `isDirty: boolean` - Whether form has unsaved changes

### PlanInfoForm
- **Description**: Form section for plan name and description editing.
- **Main elements**:
  - Plan name input (required, max 200 chars)
  - Description textarea (optional, max 1000 chars)
- **Handled interactions**:
  - `@input` on fields - Update form data, mark dirty
- **Handled validation**:
  - Name: required, 1-200 characters
  - Description: optional, max 1000 characters
- **Types**: None
- **Props**:
  - `name: string` - Current name value
  - `description: string | null` - Current description
  - `errors: PlanInfoErrors` - Field errors

### ExerciseListEditor
- **Description**: Container for the editable, reorderable list of exercises.
- **Main elements**:
  - Drag-and-drop sortable list
  - EditableExerciseCard for each exercise
  - Add Exercise button at bottom
- **Handled interactions**:
  - `@reorder` - Update exercise sequence
  - `@add` - Open add exercise modal
- **Handled validation**: At least 1 exercise required
- **Types**: None
- **Props**:
  - `exercises: EditableExercise[]` - Exercises to display
  - `error: string | null` - List-level error

### EditableExerciseCard
- **Description**: Card for editing a single exercise within the plan.
- **Main elements**:
  - Drag handle icon
  - Exercise name (with substitute button)
  - Sets number input
  - Reps min/max inputs
  - Rest time input (seconds)
  - Remove button (trash icon)
- **Handled interactions**:
  - Drag handle - Reordering
  - `@substitute` - Open substitute modal
  - `@change` on inputs - Update values
  - `@remove` - Remove exercise (with confirm if only 1)
- **Handled validation**:
  - Sets: 1-50
  - Reps min/max: 1-200, min <= max
  - Rest time: 0-3600 seconds
- **Types**: `EditableExercise`
- **Props**:
  - `exercise: EditableExercise` - Exercise data
  - `canRemove: boolean` - False if last exercise
  - `errors: ExerciseErrors` - Field errors

### AddExerciseModal
- **Description**: Modal for searching and adding new exercises to the plan.
- **Main elements**:
  - Search input
  - Filter by muscle group (optional)
  - Exercise results list
  - Exercise selection with default sets/reps
- **Handled interactions**:
  - `@search` - Filter exercises
  - `@select` - Add exercise to plan
  - `@close` - Close modal
- **Handled validation**: Must select an exercise
- **Types**: None
- **Props**:
  - `isOpen: boolean` - Modal visibility
  - `existingExerciseIds: string[]` - To show already-added exercises

### SubstituteExerciseModal
- **Description**: Modal for substituting an exercise with a similar one.
- **Main elements**:
  - Current exercise info
  - Similar exercises (same muscle group, equipment)
  - Search all exercises option
- **Handled interactions**:
  - `@select` - Substitute exercise
  - `@close` - Close modal
- **Handled validation**: Must select an exercise
- **Types**: None
- **Props**:
  - `isOpen: boolean` - Modal visibility
  - `currentExercise: EditableExercise` - Exercise being substituted

### UnsavedChangesDialog
- **Description**: Confirmation dialog when leaving with unsaved changes.
- **Main elements**:
  - Warning message
  - Discard button (destructive)
  - Keep Editing button (secondary)
- **Handled interactions**:
  - `@discard` - Navigate away
  - `@keepEditing` - Close dialog, stay on page
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `isOpen: boolean` - Dialog visibility

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From workout_plans.py
interface WorkoutPlanDetailResponse {
  id: string;
  name: string;
  description: string | null;
  exercises: WorkoutExerciseDetail[];
  created_at: string;
  updated_at: string;
}

interface WorkoutPlanUpdateRequest {
  name?: string;
  description?: string | null;
  exercises?: WorkoutExerciseCreateItem[];
}

interface WorkoutExerciseCreateItem {
  exercise_id: string;
  sequence: number;
  sets: number;
  reps_min: number;
  reps_max: number;
  rest_time_seconds: number | null;
  confidence_level: ConfidenceLevelEnum;
}

interface WorkoutPlanUpdateResponse {
  id: string;
  updated_at: string;
}

// From exercises.py
interface ExerciseListResponse {
  exercises: ExerciseListItem[];
  pagination: PaginationInfo;
}

interface ExerciseListItem {
  id: string;
  name: string;
  muscle_group: MuscleGroupEnum;
  equipment: EquipmentBrief[];
}
```

### ViewModels (frontend-specific)

```typescript
// Form data structure
interface PlanEditFormData {
  name: string;
  description: string | null;
  exercises: EditableExercise[];
}

// Individual exercise in editor
interface EditableExercise {
  id: string; // workout_exercise ID (or temp ID for new)
  exerciseId: string; // actual exercise ID
  exerciseName: string;
  muscleGroup: MuscleGroupEnum;
  equipment: EquipmentBrief[];
  sequence: number;
  sets: number;
  repsMin: number;
  repsMax: number;
  restTimeSeconds: number | null;
  confidenceLevel: ConfidenceLevelEnum;
  isNew: boolean; // True if added during this edit session
  isModified: boolean; // True if changed during this edit session
}

// Page state
interface PlanEditState {
  originalData: PlanEditFormData | null;
  formData: PlanEditFormData;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  isDirty: boolean;
  validationErrors: FormValidationErrors;
  addExerciseModal: { isOpen: boolean };
  substituteModal: { isOpen: boolean; exerciseId: string | null };
  unsavedChangesDialog: { isOpen: boolean; navigateTo: string | null };
}

// Validation errors structure
interface FormValidationErrors {
  name?: string;
  description?: string;
  exercises?: string; // List-level error (e.g., "At least 1 exercise required")
  exerciseErrors: Map<string, ExerciseFieldErrors>;
}

interface ExerciseFieldErrors {
  sets?: string;
  repsMin?: string;
  repsMax?: string;
  restTimeSeconds?: string;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const editableExerciseSchema = z.object({
  exerciseId: z.string().uuid(),
  sequence: z.number().int().min(0),
  sets: z.number().int().min(1, 'At least 1 set required').max(50, 'Maximum 50 sets'),
  repsMin: z.number().int().min(1, 'At least 1 rep').max(200, 'Maximum 200 reps'),
  repsMax: z.number().int().min(1, 'At least 1 rep').max(200, 'Maximum 200 reps'),
  restTimeSeconds: z.number().int().min(0).max(3600, 'Maximum 60 minutes').nullable()
}).refine(data => data.repsMin <= data.repsMax, {
  message: 'Min reps cannot be greater than max reps',
  path: ['repsMin']
});

const planEditFormSchema = z.object({
  name: z.string()
    .min(1, 'Plan name is required')
    .max(200, 'Name must be 200 characters or less'),
  description: z.string().max(1000, 'Description must be 1000 characters or less').nullable(),
  exercises: z.array(editableExerciseSchema)
    .min(1, 'At least one exercise is required')
});

type PlanEditFormData = z.infer<typeof planEditFormSchema>;
```

## 6. State Management

### Local Component State (PlanEditPage)

```typescript
const originalData = ref<PlanEditFormData | null>(null);
const formData = ref<PlanEditFormData>({
  name: '',
  description: null,
  exercises: []
});
const isLoading = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);
const validationErrors = ref<FormValidationErrors>({
  exerciseErrors: new Map()
});

// Modal states
const addExerciseModal = ref({ isOpen: false });
const substituteModal = ref({ isOpen: false, exerciseId: null as string | null });
const unsavedChangesDialog = ref({ isOpen: false, navigateTo: null as string | null });

// Computed
const isDirty = computed(() => {
  if (!originalData.value) return false;
  return !isEqual(originalData.value, formData.value);
});

const canSave = computed(() => {
  return isDirty.value && isFormValid();
});
```

### Pinia Store Usage

```typescript
// Uses workoutPlanStore for fetching/updating plans
// Uses exerciseStore for searching exercises

interface ExerciseStore {
  exercises: ExerciseListItem[];
  searchExercises(query: string, filters?: ExerciseFilters): Promise<void>;
  getExerciseById(id: string): ExerciseListItem | undefined;
  getSimilarExercises(exerciseId: string): ExerciseListItem[];
}
```

### Custom Composable: usePlanEdit

```typescript
// composables/usePlanEdit.ts
export function usePlanEdit(planId: Ref<string>) {
  const router = useRouter();
  const workoutPlanStore = useWorkoutPlanStore();
  const exerciseStore = useExerciseStore();
  
  // State
  const originalData = ref<PlanEditFormData | null>(null);
  const formData = ref<PlanEditFormData>({ ... });
  const isLoading = ref(true);
  const isSaving = ref(false);
  const validationErrors = ref<FormValidationErrors>({ ... });
  
  // Computed
  const isDirty = computed(() => { ... });
  const canSave = computed(() => { ... });
  
  // Methods
  const fetchPlan = async (): Promise<void> => { ... };
  const savePlan = async (): Promise<void> => { ... };
  const validateForm = (): boolean => { ... };
  const validateField = (field: string): void => { ... };
  
  // Exercise operations
  const addExercise = (exercise: ExerciseListItem): void => { ... };
  const removeExercise = (exerciseId: string): void => { ... };
  const substituteExercise = (oldId: string, newExercise: ExerciseListItem): void => { ... };
  const reorderExercises = (fromIndex: number, toIndex: number): void => { ... };
  const updateExerciseField = (exerciseId: string, field: string, value: any): void => { ... };
  
  // Navigation guard
  const confirmNavigation = (to: string): void => { ... };
  const handleBeforeUnload = (e: BeforeUnloadEvent): void => { ... };
  
  return {
    formData,
    isLoading,
    isSaving,
    isDirty,
    canSave,
    validationErrors,
    fetchPlan,
    savePlan,
    addExercise,
    removeExercise,
    substituteExercise,
    reorderExercises,
    updateExerciseField,
    confirmNavigation
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get Plan Detail (for initial data)
```
GET /api/v1/workout-plans/{plan_id}
```

#### 2. Update Workout Plan
```
PUT /api/v1/workout-plans/{plan_id}
```

**Request**
```typescript
{
  "name": "Updated Push Day",
  "description": "Modified description",
  "exercises": [
    {
      "exercise_id": "uuid-string",
      "sequence": 0,
      "sets": 4,
      "reps_min": 8,
      "reps_max": 12,
      "rest_time_seconds": 90,
      "confidence_level": "high"
    },
    {
      "exercise_id": "uuid-string-2",
      "sequence": 1,
      "sets": 3,
      "reps_min": 10,
      "reps_max": 10,
      "rest_time_seconds": 60,
      "confidence_level": "high"
    }
  ]
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "updated_at": "2025-01-16T12:00:00Z"
  },
  "error": null
}
```

**Error Response (400 Bad Request)**
```typescript
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "name": "Name must be 200 characters or less",
      "exercises[0].sets": "Sets must be between 1 and 50"
    }
  }
}
```

#### 3. Get Exercises (for add/substitute)
```
GET /api/v1/exercises?search=bench&muscle_group=chest&limit=20
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "exercises": [
      {
        "id": "uuid-string",
        "name": "Bench Press",
        "muscle_group": "chest",
        "equipment": [
          { "id": "uuid", "name": "Barbell" }
        ]
      }
    ],
    "pagination": { "total": 15, "page": 1, "per_page": 20, "total_pages": 1 }
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/workoutPlans.ts
export async function updateWorkoutPlan(
  planId: string,
  data: WorkoutPlanUpdateRequest
): Promise<WorkoutPlanUpdateResponse> {
  const response = await axios.put<APIResponse<WorkoutPlanUpdateResponse>>(
    `/api/v1/workout-plans/${planId}`,
    data
  );
  return response.data.data;
}

// services/api/exercises.ts
export async function searchExercises(params: {
  search?: string;
  muscle_group?: MuscleGroupEnum;
  limit?: number;
}): Promise<ExerciseListResponse> {
  const response = await axios.get<APIResponse<ExerciseListResponse>>(
    '/api/v1/exercises',
    { params }
  );
  return response.data.data;
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | PlanEditPage | `onMounted` | Fetch plan, populate form |
| Edit name | Name input | `updateField('name', value)` | Update form, validate |
| Edit description | Description textarea | `updateField('description', value)` | Update form |
| Drag exercise | DragHandle | `reorderExercises(from, to)` | Reorder list, update sequences |
| Edit sets | SetsInput | `updateExerciseField(id, 'sets', value)` | Update exercise, validate |
| Edit reps min | RepsMinInput | `updateExerciseField(id, 'repsMin', value)` | Update exercise, validate |
| Edit reps max | RepsMaxInput | `updateExerciseField(id, 'repsMax', value)` | Update exercise, validate |
| Edit rest time | RestTimeInput | `updateExerciseField(id, 'restTimeSeconds', value)` | Update exercise |
| Click substitute | SubstituteButton | `openSubstituteModal(exerciseId)` | Open modal |
| Select substitute | SubstituteModal | `substituteExercise(oldId, newExercise)` | Replace exercise, close modal |
| Click remove | RemoveButton | `removeExercise(exerciseId)` | Remove (with confirm if last) |
| Click add | AddExerciseButton | `openAddModal()` | Open add modal |
| Search exercise | AddExerciseModal | `searchExercises(query)` | Filter exercise list |
| Select exercise | AddExerciseModal | `addExercise(exercise)` | Add to end of list, close modal |
| Click save | SaveButton | `savePlan()` | Validate, submit, navigate |
| Click back | BackButton | `confirmNavigation()` | Show dialog if dirty, else navigate |
| Confirm discard | UnsavedChangesDialog | Navigate to target | Leave without saving |
| Keep editing | UnsavedChangesDialog | Close dialog | Stay on page |

### Detailed Interaction Flow

1. **Page Load**:
   - Fetch current plan data
   - Map to form data structure
   - Store original for dirty comparison
   - Render editable form

2. **Editing Plan Info**:
   - User edits name/description
   - Real-time validation
   - Track dirty state

3. **Reordering Exercises**:
   - User drags exercise via handle
   - Visual feedback during drag
   - Update sequence numbers on drop
   - Form becomes dirty

4. **Editing Exercise Parameters**:
   - User modifies sets/reps/rest
   - Inline validation
   - Show errors below inputs
   - Form becomes dirty

5. **Substituting an Exercise**:
   - User clicks substitute button
   - Modal shows similar exercises first
   - User can search for any exercise
   - Selection replaces exercise, keeps sets/reps/rest
   - Form becomes dirty

6. **Adding an Exercise**:
   - User clicks "Add Exercise"
   - Modal with search and filters
   - User selects exercise
   - Added to end of list with defaults (3 sets, 8-12 reps, 60s rest)
   - Form becomes dirty

7. **Removing an Exercise**:
   - User clicks remove
   - If last exercise, show warning
   - Otherwise remove immediately
   - Form becomes dirty

8. **Saving Changes**:
   - User clicks Save
   - Full validation runs
   - If invalid, show errors, scroll to first error
   - If valid, submit to API
   - On success: show toast, navigate to plan detail
   - On error: show error, stay on page

9. **Navigating Away**:
   - User clicks back or navigates
   - If dirty, show confirmation dialog
   - "Discard" navigates away
   - "Keep Editing" closes dialog

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | All form content |
| isSaving = true | LoadingOverlay | - |
| isDirty && isValid | SaveButton (enabled) | - |
| !isDirty \|\| !isValid | SaveButton (disabled) | - |
| exercises.length === 1 | RemoveButton (disabled) | - |
| hasValidationErrors | Error messages | - |

### Validation Rules

| Field | Condition | Error Message |
|-------|-----------|---------------|
| name | Required | "Plan name is required" |
| name | Max 200 chars | "Name must be 200 characters or less" |
| description | Max 1000 chars | "Description must be 1000 characters or less" |
| exercises | Min 1 | "At least one exercise is required" |
| sets | 1-50 | "Sets must be between 1 and 50" |
| reps_min | 1-200 | "Reps must be between 1 and 200" |
| reps_max | 1-200 | "Reps must be between 1 and 200" |
| reps_min | <= reps_max | "Min reps cannot be greater than max" |
| rest_time | 0-3600 | "Rest time must be 0-60 minutes" |

### Validation Timing

- **On input**: Validate individual field (debounced for text)
- **On blur**: Validate individual field immediately
- **On save**: Validate entire form
- **On reorder/add/remove**: No immediate validation (on next save)

## 10. Error Handling

### API Error Handling

```typescript
async function savePlan(): Promise<void> {
  // Validate first
  if (!validateForm()) {
    scrollToFirstError();
    return;
  }
  
  isSaving.value = true;
  
  try {
    const updateData = mapFormToUpdateRequest(formData.value);
    await updateWorkoutPlan(planId.value, updateData);
    
    showToast({ type: 'success', message: 'Plan saved successfully' });
    router.push({ name: 'planDetail', params: { planId: planId.value } });
    
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const errorData = e.response?.data?.error;
      
      if (errorData?.code === 'VALIDATION_ERROR' && errorData?.details) {
        // Map server validation errors to form
        mapServerErrors(errorData.details);
        scrollToFirstError();
      } else if (e.response?.status === 404) {
        showToast({ type: 'error', message: 'Plan not found. It may have been deleted.' });
        router.push({ name: 'plans' });
      } else {
        showToast({ type: 'error', message: 'Failed to save changes. Please try again.' });
      }
    } else {
      showToast({ type: 'error', message: 'An unexpected error occurred.' });
    }
  } finally {
    isSaving.value = false;
  }
}

function mapServerErrors(details: Record<string, string>): void {
  for (const [key, message] of Object.entries(details)) {
    if (key === 'name' || key === 'description') {
      validationErrors.value[key] = message;
    } else if (key.startsWith('exercises[')) {
      // Parse exercise index and field: exercises[0].sets
      const match = key.match(/exercises\[(\d+)\]\.(\w+)/);
      if (match) {
        const [, index, field] = match;
        const exerciseId = formData.value.exercises[parseInt(index)]?.id;
        if (exerciseId) {
          const errors = validationErrors.value.exerciseErrors.get(exerciseId) || {};
          errors[field as keyof ExerciseFieldErrors] = message;
          validationErrors.value.exerciseErrors.set(exerciseId, errors);
        }
      }
    }
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Validation error | 400 | Map to field errors | Show inline errors |
| Plan not found | 404 | "Plan not found" | Navigate to plans list |
| Network error | - | "Unable to connect" | Stay on page, retry option |
| Server error | 500 | "Failed to save" | Stay on page, retry option |
| Concurrent edit | 409 | "Plan was modified" | Offer to reload or force save |

## 11. Implementation Steps

1. **Create Types**
   - Add `PlanEditFormData`, `EditableExercise` to types
   - Add `FormValidationErrors`, `ExerciseFieldErrors`
   - Add Zod schemas for form validation

2. **Create/Update API Service**
   - Add `updateWorkoutPlan()` function
   - Add `searchExercises()` function

3. **Create Composable**
   - Create `src/composables/usePlanEdit.ts`
   - Implement all edit operations
   - Handle dirty tracking and validation

4. **Create Drag-and-Drop Utility**
   - Create `src/composables/useDraggable.ts`
   - Support both mouse and touch
   - Handle visual feedback

5. **Create Form Components**
   - Create `src/components/plans/edit/PlanEditHeader.vue`
   - Create `src/components/plans/edit/PlanInfoForm.vue`
   - Create `src/components/plans/edit/ExerciseListEditor.vue`
   - Create `src/components/plans/edit/EditableExerciseCard.vue`
   - Create `src/components/plans/edit/AddExerciseModal.vue`
   - Create `src/components/plans/edit/SubstituteExerciseModal.vue`

6. **Create Base Components** (if not existing)
   - Create `src/components/common/BaseTextarea.vue`
   - Create `src/components/common/NumberInput.vue`
   - Create `src/components/common/UnsavedChangesDialog.vue`
   - Create `src/components/common/SearchInput.vue`

7. **Create Plan Edit Page**
   - Create `src/views/plans/PlanEditPage.vue`
   - Wire up all components and interactions
   - Implement navigation guard

8. **Configure Router**
   - Add `/plans/:planId/edit` route
   - Add beforeRouteLeave guard for unsaved changes

9. **Add Loading and Saving States**
   - Loading skeleton for initial fetch
   - Overlay with spinner while saving
   - Disable form during save

10. **Style with Tailwind**
    - Style editable cards with inputs
    - Add drag handle styling
    - Style modals with search
    - Error state styling for inputs

11. **Add Accessibility**
    - Proper form labels
    - Error announcements (aria-live)
    - Keyboard navigation for drag-and-drop
    - Focus management for modals

12. **Write Tests**
    - Unit tests for validation logic
    - Component tests for EditableExerciseCard
    - Integration test for full edit flow
    - Test dirty state tracking
    - Test navigation guard

13. **Manual Testing**
    - Test all edit operations
    - Test validation and error display
    - Test drag-and-drop on desktop and mobile
    - Test navigation guard behavior
    - Test with slow network
