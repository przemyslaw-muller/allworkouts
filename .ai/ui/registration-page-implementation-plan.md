# View Implementation Plan: Registration Page

## 1. Overview

The Registration Page allows new users to create an account in the AllWorkouts application. It collects email and password information, validates inputs according to security requirements, and upon successful registration, redirects users to the mandatory onboarding flow where they will set their preferences and equipment.

## 2. View Routing

- **Path**: `/register`
- **Route Name**: `register`
- **Access**: Public (unauthenticated users only)
- **Guard**: Redirect to `/dashboard` if already authenticated

## 3. Component Structure

```
RegistrationPage (view)
├── RegistrationForm
│   ├── FormField (email)
│   │   └── BaseInput
│   ├── FormField (password)
│   │   └── BaseInput (type="password")
│   │   └── PasswordStrengthIndicator
│   ├── FormField (confirmPassword)
│   │   └── BaseInput (type="password")
│   ├── PasswordRequirements
│   ├── ErrorBanner (conditional)
│   └── BaseButton (submit)
└── AuthFooter
    └── RouterLink (to login)
```

## 4. Component Details

### RegistrationPage
- **Description**: Main view component serving as the container for the registration form. Provides consistent layout with login page for seamless UX.
- **Main elements**:
  - App logo/branding header
  - Page title ("Create your account")
  - RegistrationForm component
  - AuthFooter with login link
- **Handled interactions**: None (delegates to child components)
- **Handled validation**: None (delegates to RegistrationForm)
- **Types**: None
- **Props**: None

### RegistrationForm
- **Description**: Form component handling user registration with real-time validation feedback and password strength indication.
- **Main elements**:
  - `<form>` wrapper with `@submit.prevent`
  - FormField for email with uniqueness validation
  - FormField for password with strength indicator
  - FormField for password confirmation
  - PasswordRequirements list
  - ErrorBanner for API errors
  - BaseButton for submission
- **Handled interactions**:
  - `@submit` - Form submission
  - `@input` - Real-time input handling
  - `@blur` - Field validation on blur
- **Handled validation**:
  - Email: required, valid format, unique (server-side)
  - Password: required, min 8 characters
  - Confirm password: required, must match password
- **Types**: 
  - `RegistrationFormData` (ViewModel)
  - `RegisterRequest` (DTO)
  - `RegistrationFormErrors` (ViewModel)
- **Props**: None

### PasswordStrengthIndicator
- **Description**: Visual indicator showing password strength based on criteria met.
- **Main elements**:
  - Strength bar (segmented, color-coded)
  - Strength label (Weak, Fair, Good, Strong)
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: 
  - `PasswordStrength` enum
- **Props**:
  - `password: string` - Password to evaluate
  - `strength: PasswordStrength` - Computed strength level

### PasswordRequirements
- **Description**: Displays password requirements with visual feedback on which are met.
- **Main elements**:
  - List of requirements with check/x icons
  - Color coding for met/unmet requirements
- **Handled interactions**: None (display only)
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `password: string` - Password to check against requirements

## 5. Types

### DTOs (matching backend schemas)

```typescript
// Request DTO - matches backend RegisterRequest
interface RegisterRequest {
  email: string;
  password: string;
}

// Response DTO - matches backend AuthResponse
interface AuthResponse {
  user: AuthUserResponse;
  access_token: string;
  refresh_token: string;
}

interface AuthUserResponse {
  id: string; // UUID
  email: string;
  created_at: string; // ISO datetime
}
```

### ViewModels (frontend-specific)

```typescript
// Form data structure
interface RegistrationFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

// Form validation errors
interface RegistrationFormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

// Password strength levels
enum PasswordStrength {
  WEAK = 'weak',
  FAIR = 'fair',
  GOOD = 'good',
  STRONG = 'strong'
}

// Password requirement status
interface PasswordRequirement {
  label: string;
  met: boolean;
  validator: (password: string) => boolean;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const registrationSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
  confirmPassword: z
    .string()
    .min(1, 'Please confirm your password')
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
});

type RegistrationFormData = z.infer<typeof registrationSchema>;
```

## 6. State Management

### Local Component State (RegistrationForm)

```typescript
const formData = ref<RegistrationFormData>({
  email: '',
  password: '',
  confirmPassword: ''
});

const errors = ref<RegistrationFormErrors>({});
const isLoading = ref(false);
const isSubmitted = ref(false);
const touchedFields = ref<Set<string>>(new Set());
```

### Computed Properties

```typescript
// Password strength calculation
const passwordStrength = computed((): PasswordStrength => {
  const password = formData.value.password;
  let score = 0;
  
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  
  if (score <= 2) return PasswordStrength.WEAK;
  if (score <= 3) return PasswordStrength.FAIR;
  if (score <= 4) return PasswordStrength.GOOD;
  return PasswordStrength.STRONG;
});

// Password requirements list
const passwordRequirements = computed((): PasswordRequirement[] => [
  {
    label: 'At least 8 characters',
    met: formData.value.password.length >= 8,
    validator: (p) => p.length >= 8
  }
]);
```

### Pinia Store (authStore)

```typescript
// authStore actions used
interface AuthStore {
  register(credentials: RegisterRequest): Promise<void>;
  setTokens(accessToken: string, refreshToken: string): void;
  setUser(user: AuthUserResponse): void;
}
```

### Custom Composable: useRegistrationForm

```typescript
// composables/useRegistrationForm.ts
export function useRegistrationForm() {
  const authStore = useAuthStore();
  const router = useRouter();
  
  const formData = ref<RegistrationFormData>({ ... });
  const errors = ref<RegistrationFormErrors>({});
  const isLoading = ref(false);
  const touchedFields = ref<Set<string>>(new Set());
  
  const passwordStrength = computed(() => { ... });
  const passwordRequirements = computed(() => { ... });
  
  const validate = (): boolean => { ... };
  const validateField = (field: keyof RegistrationFormData): void => { ... };
  const handleSubmit = async (): Promise<void> => { ... };
  const markFieldTouched = (field: string): void => { ... };
  
  return {
    formData,
    errors,
    isLoading,
    touchedFields,
    passwordStrength,
    passwordRequirements,
    validate,
    validateField,
    handleSubmit,
    markFieldTouched
  };
}
```

## 7. API Integration

### Endpoint

```
POST /api/v1/auth/register
```

### Request

```typescript
// Headers
{
  'Content-Type': 'application/json'
}

// Body
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

### Response (201 Created)

```typescript
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "created_at": "2025-01-15T10:00:00Z"
    },
    "access_token": "jwt_token_string",
    "refresh_token": "jwt_refresh_token_string"
  },
  "error": null
}
```

### Error Response (400 Bad Request - Email exists)

```typescript
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_EMAIL_EXISTS",
    "message": "Email already registered"
  }
}
```

### API Service Function

```typescript
// services/api/auth.ts
export async function register(credentials: RegisterRequest): Promise<AuthResponse> {
  const response = await axios.post<APIResponse<AuthResponse>>(
    '/api/v1/auth/register',
    credentials
  );
  return response.data.data;
}
```

## 8. User Interactions

| Interaction | Element | Handler | Outcome |
|-------------|---------|---------|---------|
| Focus email field | Email input | Autofocus on mount | Cursor in email field |
| Enter email | Email input | `@input` updates formData | formData.email updated |
| Blur email field | Email input | `@blur` validates + marks touched | Show error if invalid |
| Enter password | Password input | `@input` updates formData | formData.password updated, strength updated |
| Blur password field | Password input | `@blur` validates | Show error if invalid |
| Enter confirm password | Confirm input | `@input` updates formData | formData.confirmPassword updated |
| Blur confirm field | Confirm input | `@blur` validates match | Show error if mismatch |
| Click submit | Submit button | `@click` triggers handleSubmit | Validate → API call → Redirect |
| Press Enter | Form | `@submit.prevent` | Same as click submit |
| Click login link | Link | Vue Router navigation | Navigate to /login |

### Detailed Interaction Flow

1. **Page Load**:
   - Check if user is authenticated
   - If authenticated, redirect to `/dashboard`
   - Autofocus on email input

2. **Email Entry**:
   - User enters email
   - On blur, validate email format
   - Show error if invalid

3. **Password Entry**:
   - User enters password
   - Password strength indicator updates in real-time
   - Requirements list updates in real-time
   - On blur, validate password requirements

4. **Confirm Password**:
   - User enters confirmation
   - On blur, validate passwords match

5. **Form Submission**:
   - User clicks "Create Account"
   - Full validation runs
   - If invalid, show errors and focus first error
   - If valid, make API call with loading state

6. **Success**:
   - Store tokens in authStore
   - Redirect to `/onboarding` (mandatory step)

7. **Error (Email exists)**:
   - Show inline error on email field
   - Focus email field
   - User can correct and retry

## 9. Conditions and Validation

### Client-Side Validation

| Field | Condition | Error Message | Component |
|-------|-----------|---------------|-----------|
| Email | Required | "Email is required" | FormField (email) |
| Email | Valid format | "Please enter a valid email address" | FormField (email) |
| Password | Required | "Password is required" | FormField (password) |
| Password | Min 8 chars | "Password must be at least 8 characters" | FormField (password) |
| Confirm Password | Required | "Please confirm your password" | FormField (confirmPassword) |
| Confirm Password | Must match | "Passwords do not match" | FormField (confirmPassword) |

### Server-Side Validation (reflected in UI)

| Condition | Error Code | Error Message |
|-----------|------------|---------------|
| Email already registered | VALIDATION_EMAIL_EXISTS | "This email is already registered" |
| Invalid email format | VALIDATION_ERROR | "Please enter a valid email address" |
| Password too short | VALIDATION_ERROR | "Password must be at least 8 characters" |

### Validation Timing

- **On blur**: Validate individual field after first interaction
- **On input (after blur)**: Re-validate as user types if field was touched
- **Password match**: Validate on confirmPassword blur and on password change
- **On submit**: Full form validation before API call

### Form State Effects

| Condition | Effect |
|-----------|--------|
| Password entered | Show strength indicator and requirements |
| Field touched + invalid | Show inline error, red border |
| isLoading = true | Disable all inputs, show spinner on button |
| Email exists error | Show inline error on email field |

## 10. Error Handling

### Validation Errors

```typescript
try {
  registrationSchema.parse(formData.value);
} catch (error) {
  if (error instanceof z.ZodError) {
    error.errors.forEach((err) => {
      const field = err.path[0] as keyof RegistrationFormErrors;
      errors.value[field] = err.message;
    });
  }
}
```

### API Errors

| Error Code | Status | User Message | Action |
|------------|--------|--------------|--------|
| VALIDATION_EMAIL_EXISTS | 400 | "This email is already registered" | Show on email field |
| VALIDATION_ERROR | 400 | Map to specific field | Show inline errors |
| INTERNAL_ERROR | 500 | "Something went wrong. Please try again." | Show in ErrorBanner |
| Network Error | - | "Unable to connect. Please check your internet connection." | Show in ErrorBanner |

### Error Handling Implementation

```typescript
async function handleSubmit(): Promise<void> {
  clearErrors();
  
  if (!validate()) {
    focusFirstError();
    return;
  }
  
  isLoading.value = true;
  
  try {
    await authStore.register({
      email: formData.value.email,
      password: formData.value.password
    });
    
    // Redirect to onboarding after successful registration
    router.push({ name: 'onboarding' });
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const apiError = error.response?.data?.error;
      
      if (apiError?.code === 'VALIDATION_EMAIL_EXISTS') {
        errors.value.email = 'This email is already registered';
      } else if (apiError?.code === 'VALIDATION_ERROR') {
        mapServerErrors(apiError.details);
      } else {
        errors.value.general = 'Something went wrong. Please try again.';
      }
    } else {
      errors.value.general = 'Unable to connect. Please check your internet connection.';
    }
  } finally {
    isLoading.value = false;
  }
}
```

## 11. Implementation Steps

1. **Extend Types and Schemas**
   - Add RegisterRequest to `src/types/auth.ts`
   - Create registration validation schema in `src/schemas/auth.ts`
   - Add PasswordStrength enum and related types

2. **Extend Auth API Service**
   - Add `register` function to `src/services/api/auth.ts`

3. **Extend Auth Store**
   - Add `register` action to `src/stores/auth.ts`

4. **Create Password Components**
   - Create `src/components/auth/PasswordStrengthIndicator.vue`
   - Create `src/components/auth/PasswordRequirements.vue`

5. **Create Registration Form Composable**
   - Create `src/composables/useRegistrationForm.ts`
   - Implement form state, validation, password strength calculation

6. **Create Registration Form Component**
   - Create `src/components/auth/RegistrationForm.vue`
   - Use composable for logic
   - Include password strength and requirements components

7. **Create Registration Page View**
   - Create `src/views/auth/RegistrationPage.vue`
   - Add page layout, branding, and RegistrationForm

8. **Configure Router**
   - Add registration route to `src/router/index.ts`
   - Ensure redirect to onboarding after registration

9. **Add Accessibility Features**
   - Proper ARIA labels for password requirements
   - Screen reader announcements for password strength changes
   - Focus management on errors

10. **Style with Tailwind**
    - Style password strength indicator with color progression
    - Style requirements list with icons
    - Ensure consistent styling with login page

11. **Write Tests**
    - Unit tests for password strength calculation
    - Unit tests for validation logic
    - Component tests for RegistrationForm
    - Integration tests for registration flow

12. **Manual Testing**
    - Test valid registration flow
    - Test email already exists error
    - Test password validation feedback
    - Test password match validation
    - Verify redirect to onboarding
