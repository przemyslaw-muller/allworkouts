# View Implementation Plan: Onboarding Page

## 1. Overview

The Onboarding Page is a mandatory multi-step flow that appears after user registration. It collects essential user preferences: unit system (metric/imperial) in Step 1 and available equipment in Step 2. Users cannot skip this flow as these preferences are required for proper application functionality. Upon completion, users are redirected to the dashboard.

## 2. View Routing

- **Path**: `/onboarding`
- **Route Name**: `onboarding`
- **Access**: Protected (authenticated users without completed onboarding)
- **Guard**: 
  - Redirect to `/login` if not authenticated
  - Redirect to `/dashboard` if onboarding already completed
  - Cannot be skipped

## 3. Component Structure

```
OnboardingPage (view)
├── OnboardingContainer
│   ├── StepIndicator
│   ├── UnitSelectionStep (Step 1)
│   │   ├── UnitOptionCard (Metric)
│   │   └── UnitOptionCard (Imperial)
│   ├── EquipmentSelectionStep (Step 2)
│   │   ├── EquipmentCategoryGroup
│   │   │   ├── CategoryHeader
│   │   │   │   └── SelectAllCheckbox
│   │   │   └── EquipmentCheckbox (multiple)
│   │   └── ... (more categories)
│   └── NavigationButtons
│       ├── BackButton (Step 2 only)
│       └── NextButton / CompleteButton
└── LoadingOverlay (conditional)
```

## 4. Component Details

### OnboardingPage
- **Description**: Main view that manages the multi-step onboarding flow, tracking current step and orchestrating data collection.
- **Main elements**:
  - OnboardingContainer with centered layout
  - Step-specific content
  - Navigation buttons
- **Handled interactions**:
  - Step navigation (next, back)
  - Final submission
- **Handled validation**: Delegates to step components
- **Types**: 
  - `OnboardingStep` enum
  - `OnboardingData` ViewModel
- **Props**: None

### StepIndicator
- **Description**: Visual indicator showing current progress through the onboarding steps.
- **Main elements**:
  - Step circles/numbers (1, 2)
  - Connecting line
  - Step labels
  - Active/completed/pending states
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `currentStep: number`
  - `totalSteps: number`
  - `stepLabels: string[]`

### UnitSelectionStep
- **Description**: First step allowing users to select their preferred unit system (metric or imperial) with visual examples.
- **Main elements**:
  - Step title and description
  - Two UnitOptionCard components (Metric, Imperial)
  - Visual examples of each unit system
- **Handled interactions**:
  - `@select` - Unit option selection
- **Handled validation**:
  - At least one option must be selected (default: metric)
- **Types**:
  - `UnitSystem` enum
- **Props**:
  - `modelValue: UnitSystem`
  - `@update:modelValue`

### UnitOptionCard
- **Description**: Selectable card representing a unit system option with examples.
- **Main elements**:
  - Card container with selection state styling
  - Unit system name (Metric/Imperial)
  - Example values (kg/lbs, cm/inches)
  - Radio indicator or checkmark
- **Handled interactions**:
  - `@click` - Select this option
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `unitSystem: UnitSystem`
  - `selected: boolean`
  - `title: string`
  - `examples: string[]`

### EquipmentSelectionStep
- **Description**: Second step allowing users to select their available equipment, organized by category.
- **Main elements**:
  - Step title and description
  - Equipment categories (grouped)
  - Select all/none per category
  - Individual equipment checkboxes
- **Handled interactions**:
  - Equipment checkbox toggle
  - Select all/none per category
- **Handled validation**:
  - No minimum required (can proceed with no equipment)
- **Types**:
  - `Equipment` DTO
  - `EquipmentCategory` type
- **Props**:
  - `equipment: Equipment[]`
  - `selectedIds: Set<string>`
  - `@update:selectedIds`

### EquipmentCategoryGroup
- **Description**: Grouped section of equipment items with category header and select all functionality.
- **Main elements**:
  - Category header with name
  - Select all/none checkbox
  - List of EquipmentCheckbox items
- **Handled interactions**:
  - Toggle all items in category
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `category: string`
  - `items: Equipment[]`
  - `selectedIds: Set<string>`
  - `@toggle`
  - `@toggleAll`

### EquipmentCheckbox
- **Description**: Individual equipment item with checkbox and label.
- **Main elements**:
  - Checkbox input
  - Equipment name label
  - Optional description/icon
- **Handled interactions**:
  - `@change` - Toggle selection
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `equipment: Equipment`
  - `checked: boolean`
  - `@toggle`

### NavigationButtons
- **Description**: Navigation controls for moving between steps and completing onboarding.
- **Main elements**:
  - Back button (visible on Step 2+)
  - Next/Complete button with loading state
- **Handled interactions**:
  - `@back` - Go to previous step
  - `@next` - Go to next step or complete
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `currentStep: number`
  - `totalSteps: number`
  - `isLoading: boolean`
  - `canProceed: boolean`

## 5. Types

### DTOs (matching backend schemas)

```typescript
// Equipment list item
interface EquipmentListItem {
  id: string; // UUID
  name: string;
  description: string | null;
  is_user_owned: boolean;
}

// Equipment ownership update request
interface EquipmentOwnershipRequest {
  is_owned: boolean;
}

// User preferences (for profile update)
interface UserPreferencesUpdate {
  unit_system: UnitSystemEnum;
}

// Unit system enum
enum UnitSystemEnum {
  METRIC = 'metric',
  IMPERIAL = 'imperial'
}
```

### ViewModels (frontend-specific)

```typescript
// Onboarding step enum
enum OnboardingStep {
  UNITS = 1,
  EQUIPMENT = 2
}

// Complete onboarding data
interface OnboardingData {
  unitSystem: UnitSystemEnum;
  selectedEquipmentIds: Set<string>;
}

// Equipment grouped by category
interface EquipmentByCategory {
  [category: string]: EquipmentListItem[];
}

// Unit option for selection
interface UnitOption {
  value: UnitSystemEnum;
  title: string;
  examples: {
    weight: string;
    height: string;
  };
}
```

### Zod Validation Schemas

```typescript
import { z } from 'zod';

// Unit selection validation
const unitSelectionSchema = z.object({
  unitSystem: z.nativeEnum(UnitSystemEnum)
});

// Equipment selection validation (no minimum required)
const equipmentSelectionSchema = z.object({
  selectedEquipmentIds: z.set(z.string().uuid())
});

// Complete onboarding validation
const onboardingSchema = z.object({
  unitSystem: z.nativeEnum(UnitSystemEnum),
  selectedEquipmentIds: z.set(z.string().uuid())
});
```

## 6. State Management

### Local Component State (OnboardingPage)

```typescript
const currentStep = ref<OnboardingStep>(OnboardingStep.UNITS);
const isLoading = ref(false);
const isSubmitting = ref(false);

const onboardingData = ref<OnboardingData>({
  unitSystem: UnitSystemEnum.METRIC,
  selectedEquipmentIds: new Set()
});

// Equipment loaded from API
const allEquipment = ref<EquipmentListItem[]>([]);
const equipmentLoading = ref(true);
```

### Computed Properties

```typescript
// Group equipment by category (derived from name patterns)
const equipmentByCategory = computed((): EquipmentByCategory => {
  const categories: EquipmentByCategory = {
    'Free Weights': [],
    'Machines': [],
    'Cables': [],
    'Other': []
  };
  
  allEquipment.value.forEach(item => {
    const category = categorizeEquipment(item.name);
    categories[category].push(item);
  });
  
  return categories;
});

// Check if can proceed to next step
const canProceed = computed((): boolean => {
  if (currentStep.value === OnboardingStep.UNITS) {
    return !!onboardingData.value.unitSystem;
  }
  return true; // Equipment selection has no minimum
});

// Step labels for indicator
const stepLabels = computed(() => ['Units', 'Equipment']);
```

### Pinia Stores

```typescript
// profileStore - for saving preferences
interface ProfileStore {
  user: UserResponse | null;
  equipment: EquipmentListItem[];
  
  fetchEquipment(): Promise<void>;
  updateUserPreferences(prefs: UserPreferencesUpdate): Promise<void>;
  updateEquipmentOwnership(equipmentId: string, isOwned: boolean): Promise<void>;
  batchUpdateEquipmentOwnership(updates: Map<string, boolean>): Promise<void>;
  setOnboardingComplete(): void;
}

// authStore - for checking onboarding status
interface AuthStore {
  user: AuthUserResponse | null;
  hasCompletedOnboarding: boolean;
}
```

### Custom Composable: useOnboarding

```typescript
// composables/useOnboarding.ts
export function useOnboarding() {
  const profileStore = useProfileStore();
  const authStore = useAuthStore();
  const router = useRouter();
  
  const currentStep = ref<OnboardingStep>(OnboardingStep.UNITS);
  const onboardingData = ref<OnboardingData>({ ... });
  const isLoading = ref(false);
  
  const equipmentByCategory = computed(() => { ... });
  const canProceed = computed(() => { ... });
  
  const goToNextStep = (): void => { ... };
  const goToPreviousStep = (): void => { ... };
  const completeOnboarding = async (): Promise<void> => { ... };
  const toggleEquipment = (id: string): void => { ... };
  const toggleCategory = (category: string, select: boolean): void => { ... };
  
  return { ... };
}
```

## 7. API Integration

### Endpoints Used

1. **GET /api/v1/equipment** - Fetch all equipment
2. **PUT /api/v1/equipment/{id}/ownership** - Update equipment ownership (batch)
3. **PUT /api/v1/users/me** - Update user preferences (unit system)

### Fetch Equipment

```typescript
// GET /api/v1/equipment
// Response (200)
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Barbell",
      "description": "Standard Olympic barbell",
      "is_user_owned": false
    },
    // ... more equipment
  ],
  "error": null
}
```

### Update Equipment Ownership

```typescript
// PUT /api/v1/equipment/{equipment_id}/ownership
// Request
{
  "is_owned": true
}

// Response (200)
{
  "success": true,
  "data": {
    "equipment_id": "uuid",
    "is_owned": true
  },
  "error": null
}
```

### Update User Preferences

```typescript
// PUT /api/v1/users/me (assuming this endpoint exists or profile update)
// Request
{
  "unit_system": "metric"
}

// Response (200)
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "unit_system": "metric",
    "updated_at": "2025-01-15T10:00:00Z"
  },
  "error": null
}
```

### API Service Functions

```typescript
// services/api/equipment.ts
export async function fetchEquipment(): Promise<EquipmentListItem[]> {
  const response = await axios.get<APIResponse<EquipmentListItem[]>>('/api/v1/equipment');
  return response.data.data;
}

export async function updateEquipmentOwnership(
  equipmentId: string,
  isOwned: boolean
): Promise<void> {
  await axios.put(`/api/v1/equipment/${equipmentId}/ownership`, { is_owned: isOwned });
}

// services/api/user.ts
export async function updateUserPreferences(
  preferences: UserPreferencesUpdate
): Promise<UserResponse> {
  const response = await axios.put<APIResponse<UserResponse>>(
    '/api/v1/users/me',
    preferences
  );
  return response.data.data;
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | OnboardingPage | `onMounted` | Fetch equipment list |
| Select metric | UnitOptionCard | `@click` | Set unitSystem to METRIC |
| Select imperial | UnitOptionCard | `@click` | Set unitSystem to IMPERIAL |
| Click Next (Step 1) | NextButton | `@click` | Navigate to Step 2 |
| Toggle equipment | EquipmentCheckbox | `@change` | Add/remove from selectedIds |
| Select all in category | CategoryHeader checkbox | `@change` | Add all category items |
| Deselect all in category | CategoryHeader checkbox | `@change` | Remove all category items |
| Click Back (Step 2) | BackButton | `@click` | Navigate to Step 1 |
| Click Complete | CompleteButton | `@click` | Save preferences and equipment |

### Detailed Interaction Flow

1. **Page Load**:
   - Verify user is authenticated
   - Verify onboarding not already completed
   - Fetch equipment list from API
   - Show Step 1 (Unit Selection)

2. **Step 1 - Unit Selection**:
   - Display Metric and Imperial options
   - Default selection: Metric
   - Show examples for each (kg/lbs, cm/in)
   - User clicks to select preferred option
   - Click "Next" to proceed

3. **Step 2 - Equipment Selection**:
   - Display equipment grouped by category
   - No equipment pre-selected
   - User checks individual items or uses "Select All"
   - Can proceed with no equipment selected
   - Click "Back" to return to Step 1
   - Click "Complete" to finish

4. **Completion**:
   - Show loading state
   - Save unit preference to user profile
   - Batch update equipment ownership
   - Mark onboarding as complete
   - Redirect to dashboard

## 9. Conditions and Validation

### Route Guard Conditions

| Condition | Action |
|-----------|--------|
| Not authenticated | Redirect to `/login` |
| Onboarding already completed | Redirect to `/dashboard` |
| Authenticated + onboarding incomplete | Allow access |

### Step-Specific Validation

| Step | Field | Condition | Error |
|------|-------|-----------|-------|
| 1 | unitSystem | Must be selected | N/A (default provided) |
| 2 | equipment | None required | N/A |

### Form State Effects

| Condition | Effect |
|-----------|--------|
| Step 1 | Show unit selection, hide equipment |
| Step 2 | Show equipment selection, show Back button |
| isLoading | Show loading overlay on equipment list |
| isSubmitting | Disable all inputs, show spinner on Complete button |
| Equipment fetch error | Show error message with retry button |

### Navigation Conditions

| Condition | Can Proceed |
|-----------|-------------|
| Step 1 + unit selected | Yes |
| Step 2 | Always (equipment optional) |

## 10. Error Handling

### Equipment Fetch Error

```typescript
async function loadEquipment(): Promise<void> {
  equipmentLoading.value = true;
  equipmentError.value = null;
  
  try {
    allEquipment.value = await fetchEquipment();
  } catch (error) {
    equipmentError.value = 'Failed to load equipment. Please try again.';
    console.error('Equipment fetch error:', error);
  } finally {
    equipmentLoading.value = false;
  }
}
```

### Submission Errors

| Error | User Message | Action |
|-------|--------------|--------|
| Network error | "Unable to save preferences. Please check your connection." | Show toast, allow retry |
| Server error | "Something went wrong. Please try again." | Show toast, allow retry |
| Validation error | Map to specific field | Show inline error |

### Error Handling Implementation

```typescript
async function completeOnboarding(): Promise<void> {
  isSubmitting.value = true;
  
  try {
    // Save unit preference
    await profileStore.updateUserPreferences({
      unit_system: onboardingData.value.unitSystem
    });
    
    // Batch update equipment ownership
    const updates = new Map<string, boolean>();
    allEquipment.value.forEach(item => {
      const isOwned = onboardingData.value.selectedEquipmentIds.has(item.id);
      if (isOwned !== item.is_user_owned) {
        updates.set(item.id, isOwned);
      }
    });
    
    if (updates.size > 0) {
      await profileStore.batchUpdateEquipmentOwnership(updates);
    }
    
    // Mark onboarding complete
    authStore.setOnboardingComplete();
    
    // Redirect to dashboard
    router.push({ name: 'dashboard' });
  } catch (error) {
    uiStore.showToast({
      type: 'error',
      message: 'Failed to save preferences. Please try again.',
      action: { label: 'Retry', handler: completeOnboarding }
    });
  } finally {
    isSubmitting.value = false;
  }
}
```

## 11. Implementation Steps

1. **Create Types**
   - Add `UnitSystemEnum` to types if not existing
   - Create onboarding-specific ViewModels
   - Add equipment types

2. **Create Equipment API Service**
   - Create `src/services/api/equipment.ts`
   - Implement fetchEquipment, updateEquipmentOwnership

3. **Create/Extend Profile Store**
   - Create or extend `src/stores/profile.ts`
   - Add equipment state and actions
   - Add user preferences actions

4. **Extend Auth Store**
   - Add `hasCompletedOnboarding` state
   - Add `setOnboardingComplete` action

5. **Create Onboarding Composable**
   - Create `src/composables/useOnboarding.ts`
   - Implement step navigation, data management, submission

6. **Create Step Indicator Component**
   - Create `src/components/common/StepIndicator.vue`
   - Style with Tailwind for visual progression

7. **Create Unit Selection Components**
   - Create `src/components/onboarding/UnitSelectionStep.vue`
   - Create `src/components/onboarding/UnitOptionCard.vue`

8. **Create Equipment Selection Components**
   - Create `src/components/onboarding/EquipmentSelectionStep.vue`
   - Create `src/components/onboarding/EquipmentCategoryGroup.vue`
   - Create `src/components/onboarding/EquipmentCheckbox.vue`

9. **Create Navigation Buttons Component**
   - Create `src/components/onboarding/NavigationButtons.vue`

10. **Create Onboarding Page View**
    - Create `src/views/onboarding/OnboardingPage.vue`
    - Orchestrate steps and navigation

11. **Configure Router**
    - Add onboarding route
    - Implement navigation guard for onboarding completion check
    - Add redirect from registration to onboarding

12. **Add Accessibility Features**
    - ARIA labels for step progression
    - Keyboard navigation for equipment selection
    - Focus management between steps
    - Announce step changes to screen readers

13. **Style with Tailwind**
    - Responsive layout (centered, constrained width)
    - Card styling for unit options
    - Grouped checkbox styling
    - Step indicator visual states

14. **Write Tests**
    - Unit tests for step navigation logic
    - Component tests for each step
    - Integration tests for complete onboarding flow

15. **Manual Testing**
    - Test complete flow from registration
    - Test step navigation (next/back)
    - Test equipment selection/deselection
    - Test unit system selection
    - Verify redirect to dashboard after completion
    - Test route guards (cannot access when complete)
