# View Implementation Plan: Profile Page

## 1. Overview

The Profile Page allows users to view and manage their account settings, preferences, and equipment. It includes sections for basic profile information (email), unit system preference (metric/imperial), equipment management (mark what equipment they own), and account actions (logout, delete account). This page serves as the central hub for all user personalization and settings.

## 2. View Routing

- **Path**: `/profile`
- **Route Name**: `profile`
- **Access**: Authenticated users only
- **Guard**: Redirect to `/login` if not authenticated
- **Query Params** (optional):
  - `section`: Scroll to specific section ('preferences', 'equipment', 'account')

## 3. Component Structure

```
ProfilePage (view)
├── PageHeader
│   ├── BackButton (optional - if from navigation)
│   └── PageTitle "Profile"
├── ProfileSection
│   ├── SectionHeader "Account"
│   ├── EmailDisplay
│   │   ├── Label
│   │   └── EmailValue
│   └── MemberSinceDisplay
│       ├── Label
│       └── JoinDate
├── PreferencesSection
│   ├── SectionHeader "Preferences"
│   └── UnitSystemToggle
│       ├── Label "Unit System"
│       ├── MetricOption (kg, km)
│       └── ImperialOption (lbs, mi)
├── EquipmentSection
│   ├── SectionHeader "My Equipment"
│   ├── EquipmentDescription
│   ├── EquipmentSearch
│   │   └── SearchInput
│   ├── EquipmentList
│   │   └── EquipmentItem (for each equipment)
│   │       ├── EquipmentName
│   │       ├── EquipmentDescription (tooltip)
│   │       └── OwnershipToggle (checkbox/switch)
│   └── EquipmentCount
│       └── "X of Y equipment owned"
├── AccountActionsSection
│   ├── SectionHeader "Account"
│   ├── LogoutButton
│   └── DeleteAccountButton (danger)
├── DeleteAccountDialog
│   ├── WarningMessage
│   ├── ConfirmationInput (type "DELETE")
│   ├── CancelButton
│   └── ConfirmDeleteButton
└── LoadingState / ErrorState
```

## 4. Component Details

### ProfilePage
- **Description**: Main profile view that organizes user settings into logical sections.
- **Main elements**:
  - Profile information section
  - Preferences section
  - Equipment management section
  - Account actions section
  - Delete confirmation dialog
- **Handled interactions**:
  - Fetches user profile and equipment on mount
  - Manages unit preference updates
  - Handles equipment ownership toggles
  - Manages logout and account deletion
- **Handled validation**: None at page level
- **Types**: `UserProfileVM`
- **Props**: None

### PageHeader
- **Description**: Simple header with page title.
- **Main elements**:
  - "Profile" heading
  - Optional back button for deep navigation
- **Handled interactions**:
  - `@click` on back - Navigate to previous page
- **Handled validation**: None
- **Types**: None
- **Props**: None

### ProfileSection
- **Description**: Read-only display of user account information.
- **Main elements**:
  - Email address (not editable)
  - Member since date
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: `UserProfile`
- **Props**:
  - `email: string`
  - `createdAt: Date`

### EmailDisplay
- **Description**: Shows the user's email address.
- **Main elements**:
  - "Email" label
  - Email value (masked partially for security option)
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `email: string`

### MemberSinceDisplay
- **Description**: Shows when the user joined.
- **Main elements**:
  - "Member since" label
  - Formatted date (e.g., "January 2024")
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `date: Date`

### PreferencesSection
- **Description**: Section for user preferences like unit system.
- **Main elements**:
  - Section header
  - Unit system toggle
- **Handled interactions**: None at container level
- **Handled validation**: None
- **Types**: None
- **Props**: None

### UnitSystemToggle
- **Description**: Toggle/radio to switch between metric and imperial units.
- **Main elements**:
  - Label "Unit System"
  - Two options: Metric (kg, km) and Imperial (lbs, mi)
  - Visual indicator of selected option
  - Auto-saves on change
- **Handled interactions**:
  - `@change` - Update unit preference via API
- **Handled validation**: None
- **Types**: `UnitSystemEnum`
- **Props**:
  - `value: UnitSystemEnum`
  - `isLoading: boolean`
- **Events**:
  - `@change` - Emits new unit system

### EquipmentSection
- **Description**: Section for managing user's owned equipment.
- **Main elements**:
  - Section header with description
  - Search input for filtering
  - Scrollable equipment list
  - Ownership count summary
- **Handled interactions**:
  - `@input` on search - Filter equipment list
  - `@toggle` on equipment - Update ownership
- **Handled validation**: None
- **Types**: `EquipmentItem[]`
- **Props**: None (self-contained)

### EquipmentSearch
- **Description**: Search input for filtering the equipment list.
- **Main elements**:
  - Search icon
  - Text input
  - Clear button (when has value)
- **Handled interactions**:
  - `@input` - Emit search query
  - `@click` on clear - Clear search
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `modelValue: string`
- **Events**:
  - `@update:modelValue` - Search query changed

### EquipmentList
- **Description**: Scrollable list of all equipment with ownership toggles.
- **Main elements**:
  - List container with max-height and scroll
  - EquipmentItem components
  - Empty state when no results
- **Handled interactions**: None at container level
- **Handled validation**: None
- **Types**: `EquipmentVM[]`
- **Props**:
  - `equipment: EquipmentVM[]`
  - `isLoading: boolean`

### EquipmentItem
- **Description**: Single equipment row with name and ownership toggle.
- **Main elements**:
  - Equipment name
  - Description tooltip (hover/tap)
  - Checkbox or toggle switch for ownership
  - Loading indicator when saving
- **Handled interactions**:
  - `@change` on toggle - Update ownership
  - Hover on name - Show description tooltip
- **Handled validation**: None
- **Types**: `EquipmentVM`
- **Props**:
  - `equipment: EquipmentVM`
  - `isUpdating: boolean`
- **Events**:
  - `@toggle` - Ownership toggled

### EquipmentCount
- **Description**: Summary showing how many equipment items are owned.
- **Main elements**:
  - Text: "You own X of Y equipment"
- **Handled interactions**: None
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `ownedCount: number`
  - `totalCount: number`

### AccountActionsSection
- **Description**: Section for account-level actions like logout and deletion.
- **Main elements**:
  - Section header
  - Logout button
  - Delete account button (danger styled)
- **Handled interactions**:
  - `@click` on logout - Log out user
  - `@click` on delete - Show confirmation dialog
- **Handled validation**: None
- **Types**: None
- **Props**: None

### LogoutButton
- **Description**: Button to log out of the application.
- **Main elements**:
  - Button with logout icon
  - "Log Out" text
- **Handled interactions**:
  - `@click` - Clear auth, redirect to login
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `isLoading: boolean`

### DeleteAccountButton
- **Description**: Danger button to initiate account deletion.
- **Main elements**:
  - Red/danger styled button
  - Trash icon
  - "Delete Account" text
- **Handled interactions**:
  - `@click` - Open delete confirmation dialog
- **Handled validation**: None
- **Types**: None
- **Props**: None

### DeleteAccountDialog
- **Description**: Confirmation dialog for permanent account deletion.
- **Main elements**:
  - Warning icon and message
  - Explanation of what will be deleted
  - Input to type "DELETE" to confirm
  - Cancel and Confirm buttons
- **Handled interactions**:
  - `@input` on confirmation - Validate matches "DELETE"
  - `@click` on cancel - Close dialog
  - `@click` on confirm - Delete account if input valid
- **Handled validation**:
  - Confirmation input must match "DELETE" exactly
- **Types**: None
- **Props**:
  - `isOpen: boolean`
  - `isDeleting: boolean`
- **Events**:
  - `@close` - Dialog closed
  - `@confirm` - Deletion confirmed

## 5. Types

### DTOs (matching backend schemas)

```typescript
// From user.py
interface UserResponse {
  id: string; // UUID
  email: string;
  unit_system: UnitSystemEnum;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

// From equipment.py
interface EquipmentListItem {
  id: string; // UUID
  name: string;
  description: string | null;
  is_user_owned: boolean;
}

interface EquipmentOwnershipRequest {
  is_owned: boolean;
}

interface EquipmentOwnershipResponse {
  equipment_id: string; // UUID
  is_owned: boolean;
}

// Unit system enum
type UnitSystemEnum = 'metric' | 'imperial';

// Update profile request (for unit system change)
interface UpdateProfileRequest {
  unit_system?: UnitSystemEnum;
}
```

### ViewModels (frontend-specific)

```typescript
// Main profile view model
interface UserProfileVM {
  id: string;
  email: string;
  unitSystem: UnitSystemEnum;
  createdAt: Date;
  memberSinceFormatted: string; // e.g., "January 2024"
}

// Equipment view model
interface EquipmentVM {
  id: string;
  name: string;
  description: string | null;
  isOwned: boolean;
  isUpdating: boolean; // for optimistic UI
}

// Equipment section state
interface EquipmentState {
  items: EquipmentVM[];
  filteredItems: EquipmentVM[];
  searchQuery: string;
  isLoading: boolean;
  ownedCount: number;
  totalCount: number;
}

// Delete confirmation state
interface DeleteAccountState {
  isDialogOpen: boolean;
  confirmationInput: string;
  isValid: boolean;
  isDeleting: boolean;
  error: string | null;
}

// Preferences state
interface PreferencesState {
  unitSystem: UnitSystemEnum;
  isUpdating: boolean;
}
```

### Zod Validation Schemas

```typescript
import { z } from 'zod';

// Unit system validation
const unitSystemSchema = z.enum(['metric', 'imperial']);

// Update profile validation
const updateProfileSchema = z.object({
  unit_system: unitSystemSchema.optional()
});

// Delete confirmation validation
const deleteConfirmationSchema = z.object({
  confirmation: z.string().refine(val => val === 'DELETE', {
    message: 'Type DELETE to confirm'
  })
});

// User response validation
const userResponseSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  unit_system: unitSystemSchema,
  created_at: z.string().datetime(),
  updated_at: z.string().datetime()
});

// Equipment list item validation
const equipmentListItemSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  description: z.string().nullable(),
  is_user_owned: z.boolean()
});
```

## 6. State Management

### Local Component State (ProfilePage)

```typescript
// Loading and error state
const isLoading = ref(true);
const error = ref<string | null>(null);

// User profile
const profile = ref<UserProfileVM | null>(null);

// Preferences
const preferences = reactive<PreferencesState>({
  unitSystem: 'metric',
  isUpdating: false
});

// Equipment
const equipment = reactive<EquipmentState>({
  items: [],
  filteredItems: [],
  searchQuery: '',
  isLoading: true,
  ownedCount: 0,
  totalCount: 0
});

// Delete account
const deleteAccount = reactive<DeleteAccountState>({
  isDialogOpen: false,
  confirmationInput: '',
  isValid: false,
  isDeleting: false,
  error: null
});
```

### Pinia Stores Used

```typescript
// authStore - for logout and user data
interface AuthStore {
  user: {
    id: string;
    email: string;
  } | null;
  isAuthenticated: boolean;
  
  logout(): Promise<void>;
  deleteAccount(): Promise<void>;
  updateProfile(data: UpdateProfileRequest): Promise<void>;
}

// profileStore - for unit preference (synced across app)
interface ProfileStore {
  unitSystem: UnitSystemEnum;
  
  setUnitSystem(system: UnitSystemEnum): void;
  loadProfile(): Promise<void>;
}
```

### Custom Composable: useProfile

```typescript
// composables/useProfile.ts
export function useProfile() {
  const authStore = useAuthStore();
  const profileStore = useProfileStore();
  const router = useRouter();
  
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  const profile = ref<UserProfileVM | null>(null);
  
  const loadProfile = async (): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await getUserProfile();
      profile.value = transformToViewModel(response);
      profileStore.setUnitSystem(response.unit_system);
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  const updateUnitSystem = async (system: UnitSystemEnum): Promise<void> => {
    const previousSystem = profile.value?.unitSystem;
    
    // Optimistic update
    if (profile.value) {
      profile.value.unitSystem = system;
    }
    profileStore.setUnitSystem(system);
    
    try {
      await updateProfile({ unit_system: system });
      showToast({ type: 'success', message: 'Preferences saved' });
    } catch (e) {
      // Revert on error
      if (profile.value && previousSystem) {
        profile.value.unitSystem = previousSystem;
        profileStore.setUnitSystem(previousSystem);
      }
      showToast({ type: 'error', message: 'Failed to save preferences' });
    }
  };
  
  const logout = async (): Promise<void> => {
    try {
      await authStore.logout();
      router.push({ name: 'login' });
    } catch (e) {
      showToast({ type: 'error', message: 'Failed to log out' });
    }
  };
  
  return {
    isLoading,
    error,
    profile,
    loadProfile,
    updateUnitSystem,
    logout
  };
}
```

### Custom Composable: useEquipment

```typescript
// composables/useEquipment.ts
export function useEquipment() {
  const items = ref<EquipmentVM[]>([]);
  const searchQuery = ref('');
  const isLoading = ref(true);
  const error = ref<string | null>(null);
  
  // Filtered items based on search
  const filteredItems = computed(() => {
    if (!searchQuery.value) return items.value;
    
    const query = searchQuery.value.toLowerCase();
    return items.value.filter(eq => 
      eq.name.toLowerCase().includes(query)
    );
  });
  
  // Counts
  const ownedCount = computed(() => 
    items.value.filter(eq => eq.isOwned).length
  );
  
  const totalCount = computed(() => items.value.length);
  
  // Load all equipment
  const loadEquipment = async (): Promise<void> => {
    isLoading.value = true;
    
    try {
      const response = await listEquipment();
      items.value = response.map(eq => ({
        id: eq.id,
        name: eq.name,
        description: eq.description,
        isOwned: eq.is_user_owned,
        isUpdating: false
      }));
    } catch (e) {
      handleError(e);
    } finally {
      isLoading.value = false;
    }
  };
  
  // Toggle equipment ownership
  const toggleOwnership = async (equipmentId: string): Promise<void> => {
    const equipment = items.value.find(eq => eq.id === equipmentId);
    if (!equipment) return;
    
    const newOwned = !equipment.isOwned;
    
    // Optimistic update
    equipment.isOwned = newOwned;
    equipment.isUpdating = true;
    
    try {
      await updateEquipmentOwnership(equipmentId, { is_owned: newOwned });
    } catch (e) {
      // Revert on error
      equipment.isOwned = !newOwned;
      showToast({ type: 'error', message: 'Failed to update equipment' });
    } finally {
      equipment.isUpdating = false;
    }
  };
  
  return {
    items,
    filteredItems,
    searchQuery,
    isLoading,
    error,
    ownedCount,
    totalCount,
    loadEquipment,
    toggleOwnership
  };
}
```

### Custom Composable: useDeleteAccount

```typescript
// composables/useDeleteAccount.ts
export function useDeleteAccount() {
  const authStore = useAuthStore();
  const router = useRouter();
  
  const isDialogOpen = ref(false);
  const confirmationInput = ref('');
  const isDeleting = ref(false);
  const error = ref<string | null>(null);
  
  const isValid = computed(() => 
    confirmationInput.value === 'DELETE'
  );
  
  const openDialog = (): void => {
    isDialogOpen.value = true;
    confirmationInput.value = '';
    error.value = null;
  };
  
  const closeDialog = (): void => {
    isDialogOpen.value = false;
    confirmationInput.value = '';
    error.value = null;
  };
  
  const confirmDelete = async (): Promise<void> => {
    if (!isValid.value) return;
    
    isDeleting.value = true;
    error.value = null;
    
    try {
      await deleteUserAccount();
      await authStore.logout();
      router.push({ name: 'login' });
      showToast({ type: 'success', message: 'Account deleted' });
    } catch (e) {
      error.value = 'Failed to delete account. Please try again.';
    } finally {
      isDeleting.value = false;
    }
  };
  
  return {
    isDialogOpen,
    confirmationInput,
    isValid,
    isDeleting,
    error,
    openDialog,
    closeDialog,
    confirmDelete
  };
}
```

## 7. API Integration

### Endpoints Used

#### 1. Get User Profile
```
GET /api/v1/auth/me
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "unit_system": "metric",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "error": null
}
```

#### 2. Update Profile (Unit System)
```
PATCH /api/v1/auth/me
```

**Request**
```typescript
{
  "unit_system": "imperial"
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "unit_system": "imperial",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:31:00Z"
  },
  "error": null
}
```

#### 3. List Equipment
```
GET /api/v1/equipment
```

**Query Parameters**
- `search` (optional): Filter by name
- `user_owned` (optional): Filter by ownership

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": [
    {
      "id": "uuid-string",
      "name": "Barbell",
      "description": "Standard Olympic barbell",
      "is_user_owned": true
    },
    {
      "id": "uuid-string",
      "name": "Dumbbells",
      "description": "Adjustable or fixed weight dumbbells",
      "is_user_owned": false
    }
  ],
  "error": null
}
```

#### 4. Update Equipment Ownership
```
PUT /api/v1/equipment/{equipment_id}/ownership
```

**Request**
```typescript
{
  "is_owned": true
}
```

**Response (200 OK)**
```typescript
{
  "success": true,
  "data": {
    "equipment_id": "uuid-string",
    "is_owned": true
  },
  "error": null
}
```

#### 5. Delete Account
```
DELETE /api/v1/auth/me
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
// services/api/profile.ts
import axios from '@/lib/axios';
import type {
  UserResponse,
  UpdateProfileRequest,
  EquipmentListItem,
  EquipmentOwnershipRequest,
  EquipmentOwnershipResponse
} from '@/types/profile';

export async function getUserProfile(): Promise<UserResponse> {
  const response = await axios.get<APIResponse<UserResponse>>(
    '/api/v1/auth/me'
  );
  return response.data.data;
}

export async function updateProfile(
  data: UpdateProfileRequest
): Promise<UserResponse> {
  const response = await axios.patch<APIResponse<UserResponse>>(
    '/api/v1/auth/me',
    data
  );
  return response.data.data;
}

export async function listEquipment(
  params?: { search?: string; user_owned?: boolean }
): Promise<EquipmentListItem[]> {
  const response = await axios.get<APIResponse<EquipmentListItem[]>>(
    '/api/v1/equipment',
    { params }
  );
  return response.data.data;
}

export async function updateEquipmentOwnership(
  equipmentId: string,
  data: EquipmentOwnershipRequest
): Promise<EquipmentOwnershipResponse> {
  const response = await axios.put<APIResponse<EquipmentOwnershipResponse>>(
    `/api/v1/equipment/${equipmentId}/ownership`,
    data
  );
  return response.data.data;
}

export async function deleteUserAccount(): Promise<void> {
  await axios.delete('/api/v1/auth/me');
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Page load | ProfilePage | `onMounted` | Load profile and equipment data |
| Toggle unit system | UnitSystemToggle | `updateUnitSystem()` | Save preference, update across app |
| Type in search | EquipmentSearch | `v-model` | Filter equipment list in real-time |
| Clear search | EquipmentSearch | `clearSearch()` | Reset to full list |
| Toggle equipment | EquipmentItem | `toggleOwnership()` | Update ownership, show loading |
| Click Logout | LogoutButton | `logout()` | Clear auth, redirect to login |
| Click Delete Account | DeleteAccountButton | `openDialog()` | Show confirmation dialog |
| Type confirmation | DeleteAccountDialog | `v-model` | Validate matches "DELETE" |
| Click Cancel | DeleteAccountDialog | `closeDialog()` | Close dialog, reset |
| Click Confirm Delete | DeleteAccountDialog | `confirmDelete()` | Delete account if valid |

### Detailed Interaction Flow

1. **Unit System Change**:
   - User clicks on Metric or Imperial option
   - Option shows selected state immediately
   - API call made in background
   - On success: Brief success toast
   - On error: Revert selection, show error toast
   - All weights across app update based on new preference

2. **Equipment Management**:
   - User can scroll through all equipment
   - User can search to filter list
   - User toggles checkbox/switch for each item
   - Toggle shows loading state while saving
   - Count at bottom updates automatically

3. **Account Deletion**:
   - User clicks "Delete Account" button
   - Warning dialog appears
   - User must type "DELETE" exactly
   - Confirm button only enabled when input valid
   - On confirm: Delete account, logout, redirect

## 9. Conditions and Validation

### Display Conditions

| Condition | Component Shown | Component Hidden |
|-----------|-----------------|------------------|
| isLoading = true | LoadingSkeleton | All content |
| Error exists | ErrorState | All content |
| equipment.isLoading = true | EquipmentSkeleton | EquipmentList |
| searchQuery.length > 0 | ClearSearchButton | - |
| filteredItems.length = 0 | EmptySearchResult | EquipmentList items |
| isDialogOpen = true | DeleteAccountDialog | - |
| deleteConfirmation = "DELETE" | Confirm button enabled | - |

### Input Validation

| Field | Validation | Error Message |
|-------|------------|---------------|
| Delete confirmation | Must equal "DELETE" exactly | "Type DELETE to confirm" |

### Empty States

| Scenario | Message |
|----------|---------|
| No equipment matches search | "No equipment found matching 'query'" |

## 10. Error Handling

### API Error Handling

```typescript
async function loadProfile(): Promise<void> {
  try {
    const response = await getUserProfile();
    profile.value = transformToViewModel(response);
  } catch (e) {
    if (axios.isAxiosError(e)) {
      if (e.response?.status === 401) {
        // Auth interceptor handles redirect
      } else {
        error.value = 'Failed to load profile';
      }
    } else {
      error.value = 'An unexpected error occurred';
    }
  }
}

async function toggleOwnership(equipmentId: string): Promise<void> {
  const equipment = items.value.find(eq => eq.id === equipmentId);
  if (!equipment) return;
  
  const previousState = equipment.isOwned;
  equipment.isOwned = !previousState;
  
  try {
    await updateEquipmentOwnership(equipmentId, { is_owned: !previousState });
  } catch (e) {
    equipment.isOwned = previousState; // Revert
    showToast({ 
      type: 'error', 
      message: 'Failed to update equipment. Please try again.' 
    });
  }
}
```

### Error Types and Messages

| Error Type | Status | User Message | Action |
|------------|--------|--------------|--------|
| Auth expired | 401 | Auto-redirect | Via interceptor |
| Load profile failed | 4xx/5xx | "Failed to load profile" | Show retry button |
| Update preference failed | 4xx/5xx | "Failed to save preferences" | Toast, revert |
| Update equipment failed | 4xx/5xx | "Failed to update equipment" | Toast, revert |
| Delete account failed | 4xx/5xx | "Failed to delete account" | Show in dialog |
| Network error | - | "Connection error" | Toast with retry |

## 11. Implementation Steps

1. **Create Types and Schemas**
   - Create `src/types/profile.ts` with all DTOs and ViewModels
   - Add Zod validation schemas
   - Create unit system utilities

2. **Create Composables**
   - Create `src/composables/useProfile.ts`
   - Create `src/composables/useEquipment.ts`
   - Create `src/composables/useDeleteAccount.ts`

3. **Update Pinia Stores**
   - Add/update `src/stores/auth.ts` with logout, deleteAccount
   - Add/update `src/stores/profile.ts` with unitSystem state

4. **Create Profile Section Components**
   - Create `src/components/profile/ProfileSection.vue`
   - Create `src/components/profile/EmailDisplay.vue`
   - Create `src/components/profile/MemberSinceDisplay.vue`

5. **Create Preferences Components**
   - Create `src/components/profile/PreferencesSection.vue`
   - Create `src/components/profile/UnitSystemToggle.vue`
   - Style as segmented control or radio buttons

6. **Create Equipment Components**
   - Create `src/components/profile/EquipmentSection.vue`
   - Create `src/components/profile/EquipmentSearch.vue`
   - Create `src/components/profile/EquipmentList.vue`
   - Create `src/components/profile/EquipmentItem.vue`
   - Create `src/components/profile/EquipmentCount.vue`

7. **Create Account Action Components**
   - Create `src/components/profile/AccountActionsSection.vue`
   - Create `src/components/profile/LogoutButton.vue`
   - Create `src/components/profile/DeleteAccountButton.vue`
   - Create `src/components/profile/DeleteAccountDialog.vue`

8. **Create Page View**
   - Create `src/views/ProfilePage.vue`
   - Wire up all sections
   - Handle loading and error states

9. **Configure Router**
   - Add route `/profile`
   - Add to navigation/menu

10. **Add API Integration**
    - Implement getUserProfile
    - Implement updateProfile
    - Implement listEquipment
    - Implement updateEquipmentOwnership
    - Implement deleteUserAccount

11. **Style with Tailwind**
    - Section cards with headers
    - Toggle/radio styling for unit system
    - Checkbox styling for equipment
    - Danger styling for delete
    - Dark mode support

12. **Add Accessibility**
    - Form labels and associations
    - ARIA for toggle states
    - Focus management in dialog
    - Keyboard navigation
    - Screen reader announcements

13. **Write Tests**
    - Unit tests for composables
    - Component tests for toggles
    - Integration test for equipment flow
    - Integration test for delete flow

14. **Manual Testing**
    - Test unit system changes app-wide
    - Test equipment search and toggle
    - Test logout flow
    - Test delete account flow
    - Test error scenarios
    - Test on mobile devices
