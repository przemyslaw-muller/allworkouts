# View Implementation Plan: Plan Import Wizard

## 1. Overview

The Plan Import Wizard is a 3-step guided flow that allows users to import a workout plan from plain text (e.g., copied from a website, PDF, or notes). The wizard uses AI to parse the text, presents the interpreted results for user review and editing, and then creates the plan. This is the primary way users create new plans in the application.

**Note**: The AI parsing endpoint (`POST /api/v1/workout-plans/parse`) is planned but not yet implemented in the backend. The frontend should be built to work with the expected API contract.

## 2. View Routing

- **Path**: `/plans/import`
- **Route Name**: `planImport`
- **Access**: Authenticated users only
- **Guard**: 
  - Redirect to `/login` if not authenticated
  - Warn before leaving with data entered

## 3. Wizard Steps

1. **Step 1: Input** - User pastes or types their workout plan text
2. **Step 2: Review** - AI-parsed results shown for review and editing
3. **Step 3: Confirm** - Final confirmation and plan naming

## 4. Component Structure

```
PlanImportWizardPage (view)
├── WizardHeader
│   ├── BackButton
│   ├── WizardTitle
│   └── StepIndicator (3 steps)
├── WizardContent
│   ├── Step1InputPane
│   │   ├── InstructionsCard
│   │   ├── TextInputArea
│   │   │   └── BaseTextarea (large, auto-resize)
│   │   ├── ExampleFormats (collapsible)
│   │   └── ParseButton
│   ├── Step2ReviewPane
│   │   ├── ParseResultsSummary
│   │   │   ├── PlanNameInput
│   │   │   ├── ExerciseCountBadge
│   │   │   └── WarningsList (low confidence items)
│   │   ├── ParsedExerciseList
│   │   │   ├── ParsedExerciseCard
│   │   │   │   ├── ExerciseMatch (name, confidence)
│   │   │   │   ├── ExerciseSelector (for corrections)
│   │   │   │   ├── SetsRepsEditor
│   │   │   │   └── RemoveButton
│   │   │   └── ... (more exercises)
│   │   ├── AddExerciseButton
│   │   └── UnmatchedTextSection (if any)
│   └── Step3ConfirmPane
│       ├── FinalPlanSummary
│       │   ├── PlanNameDisplay
│       │   ├── ExerciseCountDisplay
│       │   └── EquipmentSummary
│       ├── ExercisePreviewList
│       └── CreatePlanButton
├── WizardFooter
│   ├── BackStepButton
│   └── NextStepButton / SubmitButton
├── AddExerciseModal
├── ParsingLoadingOverlay
└── UnsavedChangesDialog
```

## 5. Component Details

### PlanImportWizardPage
- **Description**: Main view managing the 3-step wizard flow, state transitions, and data flow between steps.
- **Main elements**:
  - WizardHeader with step indicator
  - Current step content pane
  - WizardFooter with navigation
- **Handled interactions**: 
  - Step navigation
  - Parse API call
  - Plan creation API call
  - Navigation guard
- **Handled validation**: Per-step validation
- **Types**: `ImportWizardState`, `ParsedPlanData`
- **Props**: None

### WizardHeader
- **Description**: Header with back navigation and step progress indicator.
- **Main elements**:
  - Back/cancel button
  - "Import Workout Plan" title
  - Step indicator (1, 2, 3) with labels
- **Handled interactions**:
  - `@back` - Navigate back (with unsaved check)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `currentStep: number` - Current step (1-3)

### StepIndicator
- **Description**: Visual progress indicator showing current step in wizard.
- **Main elements**:
  - Three step circles with labels
  - Connecting lines
  - Active/completed/pending states
- **Handled interactions**: 
  - `@click` on completed step - Go back to that step (optional)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `currentStep: number`
  - `completedSteps: number[]`

### Step1InputPane
- **Description**: First step where user enters their workout plan text.
- **Main elements**:
  - Instructions explaining what to paste
  - Large textarea for input
  - Example formats (collapsible accordion)
  - Parse button
- **Handled interactions**:
  - `@input` on textarea - Update text
  - `@click` on Parse - Trigger parsing
- **Handled validation**: Text required, min 20 characters
- **Types**: None
- **Props**:
  - `inputText: string` - Current text value
  - `error: string | null` - Input error

### Step2ReviewPane
- **Description**: Second step displaying parsed results for review and editing.
- **Main elements**:
  - Suggested plan name (editable)
  - List of parsed exercises with confidence indicators
  - Ability to correct exercise matches
  - Warnings for low-confidence matches
  - Add/remove exercises
- **Handled interactions**:
  - `@edit` on plan name - Update name
  - `@correct` on exercise - Open selector to pick correct match
  - `@edit` on sets/reps - Modify parameters
  - `@remove` on exercise - Remove from list
  - `@add` - Open add exercise modal
- **Handled validation**: At least 1 exercise required
- **Types**: `ParsedExercise[]`
- **Props**:
  - `parsedData: ParsedPlanData` - Parse results

### ParsedExerciseCard
- **Description**: Card displaying a single parsed exercise with confidence and edit capability.
- **Main elements**:
  - Original text (what was parsed)
  - Matched exercise name with confidence badge
  - "Fix Match" button if confidence low
  - Sets/reps editor
  - Rest time (if parsed)
  - Remove button
- **Handled interactions**:
  - `@fixMatch` - Open exercise selector
  - `@edit` on parameters - Update values
  - `@remove` - Remove exercise
- **Handled validation**: Sets/reps validation
- **Types**: `ParsedExercise`
- **Props**:
  - `exercise: ParsedExercise` - Parsed exercise data
  - `index: number` - For sequence

### Step3ConfirmPane
- **Description**: Final confirmation step before creating the plan.
- **Main elements**:
  - Plan name (final display, editable)
  - Total exercises count
  - Equipment needed summary
  - Preview list of exercises
  - Create Plan button
- **Handled interactions**:
  - `@editName` - Modify plan name
  - `@create` - Submit and create plan
- **Handled validation**: Plan name required
- **Types**: None
- **Props**:
  - `planName: string`
  - `exercises: ParsedExercise[]`

### ParsingLoadingOverlay
- **Description**: Full-screen overlay shown while AI is parsing the input text.
- **Main elements**:
  - Loading spinner
  - "Analyzing your workout plan..." message
  - Progress indication (optional)
- **Handled interactions**: None (blocks interaction)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `isVisible: boolean`

## 6. Types

### DTOs (matching backend schemas - planned)

```typescript
// Request to parse workout text
interface ParseWorkoutTextRequest {
  text: string;
  user_equipment_ids?: string[]; // Optional: user's available equipment
}

// Response from parse endpoint
interface ParseWorkoutTextResponse {
  suggested_name: string;
  exercises: ParsedExerciseDTO[];
  warnings: ParseWarning[];
  unmatched_text: string[];
}

interface ParsedExerciseDTO {
  original_text: string; // What was in the input
  matched_exercise: MatchedExerciseInfo | null;
  alternative_matches: MatchedExerciseInfo[];
  sets: number;
  reps_min: number;
  reps_max: number;
  rest_time_seconds: number | null;
  confidence_level: ConfidenceLevelEnum;
}

interface MatchedExerciseInfo {
  id: string; // Exercise UUID
  name: string;
  muscle_group: MuscleGroupEnum;
  equipment: EquipmentBrief[];
  confidence_score: number; // 0-1
}

interface ParseWarning {
  type: 'low_confidence' | 'no_match' | 'ambiguous' | 'equipment_mismatch';
  message: string;
  exercise_index?: number;
}

// Create plan request (existing)
interface WorkoutPlanCreateRequest {
  name: string;
  description?: string | null;
  exercises: WorkoutExerciseCreateItem[];
}
```

### ViewModels (frontend-specific)

```typescript
// Wizard state
interface ImportWizardState {
  currentStep: 1 | 2 | 3;
  inputText: string;
  isParsing: boolean;
  parseError: string | null;
  parsedData: ParsedPlanData | null;
  isCreating: boolean;
  createError: string | null;
}

// Parsed plan for editing
interface ParsedPlanData {
  suggestedName: string;
  exercises: ParsedExerciseViewModel[];
  warnings: ParseWarning[];
  unmatchedText: string[];
}

// Exercise in review/edit state
interface ParsedExerciseViewModel {
  id: string; // Temp ID for UI tracking
  originalText: string;
  matchedExercise: MatchedExerciseInfo | null;
  alternativeMatches: MatchedExerciseInfo[];
  sets: number;
  repsMin: number;
  repsMax: number;
  restTimeSeconds: number | null;
  confidenceLevel: ConfidenceLevelEnum;
  isManuallyAdded: boolean; // True if added by user
  isModified: boolean; // True if user changed something
}

// Step validation state
interface StepValidationState {
  step1: {
    isValid: boolean;
    error: string | null;
  };
  step2: {
    isValid: boolean;
    exerciseErrors: Map<string, ExerciseErrors>;
    generalError: string | null;
  };
  step3: {
    isValid: boolean;
    nameError: string | null;
  };
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

// Step 1: Input validation
const step1Schema = z.object({
  inputText: z.string()
    .min(20, 'Please enter at least 20 characters')
    .max(10000, 'Text is too long (max 10,000 characters)')
});

// Step 2: Parsed exercise validation
const parsedExerciseSchema = z.object({
  matchedExercise: z.object({
    id: z.string().uuid()
  }).nullable().refine(val => val !== null, 'Exercise match required'),
  sets: z.number().int().min(1).max(50),
  repsMin: z.number().int().min(1).max(200),
  repsMax: z.number().int().min(1).max(200),
  restTimeSeconds: z.number().int().min(0).max(3600).nullable()
}).refine(data => data.repsMin <= data.repsMax, {
  message: 'Min reps must be <= max reps',
  path: ['repsMin']
});

const step2Schema = z.object({
  suggestedName: z.string().min(1, 'Plan name required').max(200),
  exercises: z.array(parsedExerciseSchema).min(1, 'At least one exercise required')
});

// Step 3: Final confirmation
const step3Schema = z.object({
  name: z.string().min(1, 'Plan name is required').max(200)
});
```

## 7. State Management

### Local Component State (PlanImportWizardPage)

```typescript
const currentStep = ref<1 | 2 | 3>(1);

// Step 1 state
const inputText = ref('');
const inputError = ref<string | null>(null);

// Parse state
const isParsing = ref(false);
const parseError = ref<string | null>(null);
const parsedData = ref<ParsedPlanData | null>(null);

// Step 3 state
const finalPlanName = ref('');
const isCreating = ref(false);
const createError = ref<string | null>(null);

// Validation state
const validationErrors = ref<StepValidationState>({ ... });

// Dialog state
const unsavedDialog = ref({ isOpen: false, navigateTo: null });
const addExerciseModal = ref({ isOpen: false });
const exerciseSelectorModal = ref({ isOpen: false, exerciseId: null });
```

### Custom Composable: useImportWizard

```typescript
// composables/useImportWizard.ts
export function useImportWizard() {
  const router = useRouter();
  const exerciseStore = useExerciseStore();
  const equipmentStore = useEquipmentStore();
  
  // State
  const currentStep = ref<1 | 2 | 3>(1);
  const inputText = ref('');
  const parsedData = ref<ParsedPlanData | null>(null);
  const isParsing = ref(false);
  const isCreating = ref(false);
  
  // Computed
  const hasData = computed(() => inputText.value.length > 0 || parsedData.value !== null);
  const canProceed = computed(() => validateCurrentStep());
  
  // Step navigation
  const nextStep = (): void => { ... };
  const prevStep = (): void => { ... };
  const goToStep = (step: 1 | 2 | 3): void => { ... };
  
  // Parse operations
  const parseWorkoutText = async (): Promise<void> => { ... };
  
  // Exercise modifications (Step 2)
  const fixExerciseMatch = (exerciseId: string, newMatch: MatchedExerciseInfo): void => { ... };
  const updateExerciseParams = (exerciseId: string, params: Partial<ExerciseParams>): void => { ... };
  const removeExercise = (exerciseId: string): void => { ... };
  const addExercise = (exercise: ExerciseListItem): void => { ... };
  
  // Plan creation
  const createPlan = async (): Promise<void> => { ... };
  
  // Validation
  const validateCurrentStep = (): boolean => { ... };
  
  return {
    currentStep,
    inputText,
    parsedData,
    isParsing,
    isCreating,
    hasData,
    canProceed,
    nextStep,
    prevStep,
    parseWorkoutText,
    fixExerciseMatch,
    updateExerciseParams,
    removeExercise,
    addExercise,
    createPlan
  };
}
```

## 8. API Integration

### Endpoints Used

#### 1. Parse Workout Text (Planned)
```
POST /api/v1/workout-plans/parse
```

**Request**
```typescript
{
  "text": "Day 1 - Push\nBench Press 4x8-12\nOverhead Press 3x10\nDips 3x12-15",
  "user_equipment_ids": ["uuid-barbell", "uuid-dumbbell"] // Optional
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "suggested_name": "Day 1 - Push",
    "exercises": [
      {
        "original_text": "Bench Press 4x8-12",
        "matched_exercise": {
          "id": "exercise-uuid",
          "name": "Barbell Bench Press",
          "muscle_group": "chest",
          "equipment": [{ "id": "uuid", "name": "Barbell" }],
          "confidence_score": 0.95
        },
        "alternative_matches": [
          {
            "id": "exercise-uuid-2",
            "name": "Dumbbell Bench Press",
            "muscle_group": "chest",
            "equipment": [{ "id": "uuid", "name": "Dumbbell" }],
            "confidence_score": 0.85
          }
        ],
        "sets": 4,
        "reps_min": 8,
        "reps_max": 12,
        "rest_time_seconds": null,
        "confidence_level": "high"
      }
    ],
    "warnings": [
      {
        "type": "low_confidence",
        "message": "Could not confidently match 'Dips' - please verify",
        "exercise_index": 2
      }
    ],
    "unmatched_text": []
  },
  "error": null
}
```

#### 2. Create Workout Plan
```
POST /api/v1/workout-plans
```

**Request**
```typescript
{
  "name": "Push Day",
  "description": null,
  "exercises": [
    {
      "exercise_id": "exercise-uuid",
      "sequence": 0,
      "sets": 4,
      "reps_min": 8,
      "reps_max": 12,
      "rest_time_seconds": 90,
      "confidence_level": "high"
    }
  ]
}
```

**Response (201 Created)**
```typescript
{
  "success": true,
  "data": {
    "id": "new-plan-uuid",
    "name": "Push Day",
    "created_at": "2025-01-15T10:00:00Z"
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/workoutPlans.ts

// Parse workout text (to be implemented)
export async function parseWorkoutText(
  text: string,
  userEquipmentIds?: string[]
): Promise<ParseWorkoutTextResponse> {
  const response = await axios.post<APIResponse<ParseWorkoutTextResponse>>(
    '/api/v1/workout-plans/parse',
    { text, user_equipment_ids: userEquipmentIds }
  );
  return response.data.data;
}

// Create workout plan
export async function createWorkoutPlan(
  data: WorkoutPlanCreateRequest
): Promise<WorkoutPlanCreateResponse> {
  const response = await axios.post<APIResponse<WorkoutPlanCreateResponse>>(
    '/api/v1/workout-plans',
    data
  );
  return response.data.data;
}
```

## 9. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Enter text | Step1 textarea | `updateInputText()` | Update state, clear errors |
| Click Parse | ParseButton | `parseWorkoutText()` | Show loading, call API, go to Step 2 |
| Edit plan name | Step2 name input | `updatePlanName()` | Update parsed data |
| Fix exercise match | ParsedExerciseCard | `openExerciseSelector()` | Open modal to select correct exercise |
| Select correct match | ExerciseSelector | `fixExerciseMatch()` | Update exercise, close modal |
| Edit sets/reps | ParsedExerciseCard | `updateExerciseParams()` | Update exercise |
| Remove exercise | ParsedExerciseCard | `removeExercise()` | Remove from list |
| Add exercise | AddExerciseButton | `openAddModal()` | Open add exercise modal |
| Select new exercise | AddExerciseModal | `addExercise()` | Add to list, close modal |
| Click Next | WizardFooter | `nextStep()` | Validate, go to next step |
| Click Back | WizardFooter | `prevStep()` | Go to previous step |
| Click Create | Step3 | `createPlan()` | Submit plan, navigate to detail |
| Click Cancel | WizardHeader | `confirmNavigation()` | Show unsaved dialog if has data |
| Confirm leave | UnsavedDialog | Navigate away | Leave wizard |
| Keep editing | UnsavedDialog | Close dialog | Stay on wizard |

### Detailed Interaction Flow

1. **Step 1 - Input**:
   - User sees instructions and example formats
   - User pastes or types workout plan text
   - Real-time character count shown
   - Click "Parse Plan" to proceed
   - Validation: min 20 chars, max 10000 chars

2. **Parsing**:
   - Show loading overlay with animation
   - Call parse API endpoint
   - On success: Move to Step 2 with parsed data
   - On error: Show error, stay on Step 1

3. **Step 2 - Review**:
   - Display suggested plan name (editable)
   - Show parsed exercises with confidence badges
   - High confidence (green): Likely correct
   - Medium confidence (yellow): Review recommended
   - Low confidence (red): Needs correction
   - User can fix matches, edit params, add/remove
   - Warnings shown for issues
   - Click "Next" to proceed

4. **Step 3 - Confirm**:
   - Final review of plan name
   - Exercise list preview (read-only)
   - Equipment summary
   - Click "Create Plan" to submit

5. **Creation**:
   - Show loading state
   - Call create API
   - On success: Show success toast, navigate to plan detail
   - On error: Show error, stay on Step 3

## 10. Conditions and Validation

### Step 1 Validation

| Condition | Error | Can Proceed |
|-----------|-------|-------------|
| Text empty | "Please enter your workout plan" | No |
| Text < 20 chars | "Please enter at least 20 characters" | No |
| Text > 10000 chars | "Text is too long" | No |
| Valid text | None | Yes |

### Step 2 Validation

| Condition | Error | Can Proceed |
|-----------|-------|-------------|
| No exercises | "At least one exercise required" | No |
| Exercise has no match | "Please select an exercise for all items" | No |
| Invalid sets/reps | "Invalid sets or reps" | No |
| Valid data | None | Yes |

### Step 3 Validation

| Condition | Error | Can Proceed |
|-----------|-------|-------------|
| Name empty | "Plan name is required" | No |
| Name > 200 chars | "Name must be 200 characters or less" | No |
| Valid name | None | Yes |

### Display Conditions

| Condition | UI Effect |
|-----------|-----------|
| isParsing | Show loading overlay |
| isCreating | Disable all inputs, show loading on button |
| hasWarnings | Show warnings section |
| hasUnmatchedText | Show unmatched text section |
| confidenceLevel = 'low' | Red badge, show "Fix" button prominently |
| confidenceLevel = 'medium' | Yellow badge |
| confidenceLevel = 'high' | Green badge |

## 11. Error Handling

### Parse Error Handling

```typescript
async function parseWorkoutText(): Promise<void> {
  // Validate input
  const result = step1Schema.safeParse({ inputText: inputText.value });
  if (!result.success) {
    inputError.value = result.error.errors[0].message;
    return;
  }
  
  isParsing.value = true;
  parseError.value = null;
  
  try {
    const response = await api.parseWorkoutText(
      inputText.value,
      equipmentStore.userEquipmentIds
    );
    
    parsedData.value = mapToViewModel(response);
    currentStep.value = 2;
    
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const code = e.response?.data?.error?.code;
      
      if (code === 'PARSE_FAILED') {
        parseError.value = 'Could not understand the workout format. Please try a different format.';
      } else if (code === 'TEXT_TOO_COMPLEX') {
        parseError.value = 'The text is too complex. Try simplifying or splitting into multiple plans.';
      } else {
        parseError.value = 'Failed to parse workout. Please try again.';
      }
    } else {
      parseError.value = 'An unexpected error occurred.';
    }
  } finally {
    isParsing.value = false;
  }
}
```

### Create Error Handling

```typescript
async function createPlan(): Promise<void> {
  if (!validateStep3()) return;
  
  isCreating.value = true;
  createError.value = null;
  
  try {
    const request = mapToCreateRequest(parsedData.value, finalPlanName.value);
    const response = await api.createWorkoutPlan(request);
    
    showToast({ type: 'success', message: 'Plan created successfully!' });
    router.push({ name: 'planDetail', params: { planId: response.id } });
    
  } catch (e) {
    if (axios.isAxiosError(e)) {
      const code = e.response?.data?.error?.code;
      
      if (code === 'VALIDATION_ERROR') {
        createError.value = 'Invalid plan data. Please review and try again.';
      } else if (code === 'DUPLICATE_NAME') {
        createError.value = 'A plan with this name already exists.';
      } else {
        createError.value = 'Failed to create plan. Please try again.';
      }
    } else {
      createError.value = 'An unexpected error occurred.';
    }
  } finally {
    isCreating.value = false;
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Parse failed | 422 | "Could not understand format" | Stay on Step 1, suggest format tips |
| Text too complex | 400 | "Text too complex" | Suggest simplification |
| No matches found | 200 | Show in warnings | Allow manual additions |
| Validation error | 400 | Map to fields | Show inline errors |
| Duplicate name | 409 | "Name already exists" | Allow name change |
| Network error | - | "Unable to connect" | Retry button |
| Server error | 500 | "Something went wrong" | Retry button |

## 12. Implementation Steps

1. **Create Types**
   - Add parse request/response DTOs
   - Add ParsedPlanData, ParsedExerciseViewModel
   - Add ImportWizardState
   - Add Zod schemas for each step

2. **Create API Service**
   - Add `parseWorkoutText()` function (will error until backend implements)
   - Ensure `createWorkoutPlan()` exists

3. **Create Composable**
   - Create `src/composables/useImportWizard.ts`
   - Implement step navigation
   - Implement parse and create logic
   - Handle exercise modifications

4. **Create Wizard Components**
   - Create `src/components/import/WizardHeader.vue`
   - Create `src/components/import/StepIndicator.vue`
   - Create `src/components/import/Step1InputPane.vue`
   - Create `src/components/import/Step2ReviewPane.vue`
   - Create `src/components/import/Step3ConfirmPane.vue`
   - Create `src/components/import/ParsedExerciseCard.vue`
   - Create `src/components/import/ConfidenceBadge.vue`
   - Create `src/components/import/ParsingLoadingOverlay.vue`

5. **Create Shared Components** (if not existing)
   - Create `src/components/common/ExerciseSearchModal.vue`
   - Create `src/components/common/LargeTextarea.vue`
   - Create `src/components/common/CollapsibleSection.vue`

6. **Create Wizard Page**
   - Create `src/views/plans/PlanImportWizardPage.vue`
   - Implement step rendering
   - Wire up all interactions

7. **Configure Router**
   - Add `/plans/import` route
   - Add navigation guard

8. **Add Loading States**
   - Parsing overlay with animation
   - Step transition animations
   - Create button loading state

9. **Style with Tailwind**
   - Style step indicator
   - Style confidence badges
   - Large textarea styling
   - Card styling for parsed exercises
   - Mobile-responsive layout

10. **Add Accessibility**
    - ARIA labels for wizard steps
    - Focus management between steps
    - Loading state announcements
    - Error announcements

11. **Write Tests**
    - Unit tests for composable
    - Component tests for each step
    - Integration test for full flow
    - Test validation at each step

12. **Manual Testing**
    - Test various input formats
    - Test parse error handling
    - Test exercise corrections
    - Test add/remove operations
    - Test navigation guard
    - Test on mobile

## 13. Example Input Formats

Document these in the UI for user reference:

```
Format 1: Simple list
Bench Press 4x8-12
Overhead Press 3x10
Dips 3x12

Format 2: With days
Day 1 - Push
- Bench Press: 4 sets, 8-12 reps
- Shoulder Press: 3 sets, 10 reps
- Tricep Dips: 3 sets, 12 reps

Format 3: Detailed
1. Barbell Bench Press
   4 sets x 8-12 reps, 90 seconds rest
2. Dumbbell Shoulder Press
   3 sets x 10 reps, 60 seconds rest

Format 4: Compact
BP 4x8, OHP 3x10, Dips 3x12
```
