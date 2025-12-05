# View Implementation Plan: Login Page

## 1. Overview

The Login Page provides authentication for existing users to access the AllWorkouts application. It presents a simple form with email and password fields, a "Remember me" option for extended sessions, and navigation to the registration page for new users. Upon successful authentication, users are redirected to the dashboard.

## 2. View Routing

- **Path**: `/login`
- **Route Name**: `login`
- **Access**: Public (unauthenticated users only)
- **Guard**: Redirect to `/dashboard` if already authenticated

## 3. Component Structure

```
LoginPage (view)
├── LoginForm
│   ├── FormField (email)
│   │   └── BaseInput
│   ├── FormField (password)
│   │   └── BaseInput (type="password")
│   ├── BaseCheckbox (remember me)
│   ├── ErrorBanner (conditional)
│   └── BaseButton (submit)
└── AuthFooter
    └── RouterLink (to registration)
```

## 4. Component Details

### LoginPage
- **Description**: Main view component that serves as the container for the login form. Centers the form on screen with responsive width constraints.
- **Main elements**: 
  - App logo/branding header
  - LoginForm component
  - AuthFooter with registration link
- **Handled interactions**: None (delegates to child components)
- **Handled validation**: None (delegates to LoginForm)
- **Types**: None
- **Props**: None

### LoginForm
- **Description**: Form component that handles user input, validation, and submission for authentication. Manages local form state and communicates with authStore.
- **Main elements**:
  - `<form>` wrapper with `@submit.prevent`
  - FormField for email input with label
  - FormField for password input with label
  - BaseCheckbox for "Remember me" option
  - ErrorBanner for displaying authentication errors
  - BaseButton for form submission with loading state
- **Handled interactions**:
  - `@submit` - Form submission triggers validation and API call
  - `@input` - Real-time input handling for form fields
  - `@blur` - Validation trigger on field blur
- **Handled validation**:
  - Email: required, valid email format (using zod `z.string().email()`)
  - Password: required, minimum 8 characters
  - Form-level: All fields must be valid before submission
- **Types**: 
  - `LoginFormData` (ViewModel)
  - `LoginRequest` (DTO)
  - `LoginFormErrors` (ViewModel)
- **Props**: None

### ErrorBanner
- **Description**: Displays authentication error messages returned from the API.
- **Main elements**:
  - Error icon
  - Error message text
  - Optional dismiss button
- **Handled interactions**:
  - `@dismiss` - Clears the error message
- **Handled validation**: None
- **Types**: None
- **Props**:
  - `message: string` - Error message to display
  - `dismissible?: boolean` - Whether user can dismiss the banner

## 5. Types

### DTOs (matching backend schemas)

```typescript
// Request DTO - matches backend LoginRequest
interface LoginRequest {
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
interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

// Form validation errors
interface LoginFormErrors {
  email?: string;
  password?: string;
  general?: string; // For API errors
}

// Form state
interface LoginFormState {
  data: LoginFormData;
  errors: LoginFormErrors;
  isLoading: boolean;
  isSubmitted: boolean;
}
```

### Zod Validation Schema

```typescript
import { z } from 'zod';

const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
  rememberMe: z.boolean().default(false)
});

type LoginFormData = z.infer<typeof loginSchema>;
```

## 6. State Management

### Local Component State (LoginForm)

```typescript
const formData = ref<LoginFormData>({
  email: '',
  password: '',
  rememberMe: false
});

const errors = ref<LoginFormErrors>({});
const isLoading = ref(false);
const isSubmitted = ref(false);
```

### Pinia Store (authStore)

The LoginForm interacts with `authStore` for authentication:

```typescript
// authStore actions used
interface AuthStore {
  // State
  user: AuthUserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  
  // Actions
  login(credentials: LoginRequest, rememberMe: boolean): Promise<void>;
  setTokens(accessToken: string, refreshToken: string): void;
  setUser(user: AuthUserResponse): void;
}
```

### Custom Composable: useLoginForm

```typescript
// composables/useLoginForm.ts
export function useLoginForm() {
  const authStore = useAuthStore();
  const router = useRouter();
  
  const formData = ref<LoginFormData>({ ... });
  const errors = ref<LoginFormErrors>({});
  const isLoading = ref(false);
  
  const validate = (): boolean => { ... };
  const validateField = (field: keyof LoginFormData): void => { ... };
  const handleSubmit = async (): Promise<void> => { ... };
  const clearErrors = (): void => { ... };
  
  return {
    formData,
    errors,
    isLoading,
    validate,
    validateField,
    handleSubmit,
    clearErrors
  };
}
```

## 7. API Integration

### Endpoint

```
POST /api/v1/auth/login
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

### Response (200 OK)

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

### Error Response (401 Unauthorized)

```typescript
{
  "success": false,
  "data": null,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

### API Service Function

```typescript
// services/api/auth.ts
import axios from '@/lib/axios';
import type { LoginRequest, AuthResponse } from '@/types/auth';

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = await axios.post<APIResponse<AuthResponse>>(
    '/api/v1/auth/login',
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
| Blur email field | Email input | `@blur` validates email | Show error if invalid |
| Enter password | Password input | `@input` updates formData | formData.password updated |
| Blur password field | Password input | `@blur` validates password | Show error if invalid |
| Toggle remember me | Checkbox | `@change` updates formData | formData.rememberMe toggled |
| Click submit | Submit button | `@click` triggers handleSubmit | Validate → API call → Redirect |
| Press Enter | Form | `@submit.prevent` | Same as click submit |
| Click register link | Link | Vue Router navigation | Navigate to /register |
| Dismiss error | ErrorBanner | `@dismiss` clears error | Error banner hidden |

### Detailed Interaction Flow

1. **Page Load**:
   - Check if user is authenticated
   - If authenticated, redirect to `/dashboard`
   - Autofocus on email input

2. **Form Filling**:
   - User enters email and password
   - Validation on blur for each field
   - Real-time error clearing when user starts typing

3. **Form Submission**:
   - User clicks "Sign In" or presses Enter
   - Button shows loading spinner, inputs disabled
   - Client-side validation runs
   - If invalid, show errors and focus first error field
   - If valid, make API call

4. **Success**:
   - Store tokens (localStorage or sessionStorage based on rememberMe)
   - Store user data in authStore
   - Redirect to `/dashboard` (or return URL if provided)

5. **Error**:
   - Show error banner with message
   - Re-enable form
   - Focus on email field
   - User can retry

## 9. Conditions and Validation

### Client-Side Validation

| Field | Condition | Error Message | Component |
|-------|-----------|---------------|-----------|
| Email | Required | "Email is required" | FormField (email) |
| Email | Valid format | "Please enter a valid email address" | FormField (email) |
| Password | Required | "Password is required" | FormField (password) |
| Password | Min 8 chars | "Password must be at least 8 characters" | FormField (password) |

### Validation Timing

- **On blur**: Validate individual field when user leaves it
- **On input (after blur)**: Re-validate field as user types (after first blur)
- **On submit**: Validate entire form before API call

### Form State Effects

| Condition | Effect |
|-----------|--------|
| Form has errors | Submit button visually enabled, but shows errors on click |
| isLoading = true | Submit button shows spinner, inputs disabled |
| API error returned | ErrorBanner displayed, form re-enabled |
| Validation error | Inline error under field, field border turns red |

## 10. Error Handling

### Validation Errors

```typescript
// Handle Zod validation errors
try {
  loginSchema.parse(formData.value);
} catch (error) {
  if (error instanceof z.ZodError) {
    error.errors.forEach((err) => {
      const field = err.path[0] as keyof LoginFormErrors;
      errors.value[field] = err.message;
    });
  }
}
```

### API Errors

| Error Code | Status | User Message | Action |
|------------|--------|--------------|--------|
| AUTH_INVALID_CREDENTIALS | 401 | "Invalid email or password" | Show in ErrorBanner |
| VALIDATION_ERROR | 400 | Map to field errors | Show inline errors |
| INTERNAL_ERROR | 500 | "Something went wrong. Please try again." | Show in ErrorBanner |
| Network Error | - | "Unable to connect. Please check your internet connection." | Show in ErrorBanner with retry |

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
    await authStore.login(
      { email: formData.value.email, password: formData.value.password },
      formData.value.rememberMe
    );
    router.push({ name: 'dashboard' });
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const apiError = error.response?.data?.error;
      if (apiError?.code === 'AUTH_INVALID_CREDENTIALS') {
        errors.value.general = 'Invalid email or password';
      } else if (apiError?.code === 'VALIDATION_ERROR') {
        // Map server validation errors to form fields
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

1. **Create Types and Schemas**
   - Create `src/types/auth.ts` with DTOs (LoginRequest, AuthResponse, AuthUserResponse)
   - Create `src/schemas/auth.ts` with Zod validation schema for login form

2. **Create Auth API Service**
   - Create `src/services/api/auth.ts` with login function
   - Configure axios instance with base URL and interceptors

3. **Create Auth Store**
   - Create `src/stores/auth.ts` with Pinia store
   - Implement login action, token management, user state

4. **Create Base Components** (if not existing)
   - Create `src/components/common/BaseInput.vue`
   - Create `src/components/common/BaseButton.vue`
   - Create `src/components/common/BaseCheckbox.vue`
   - Create `src/components/common/FormField.vue`
   - Create `src/components/common/ErrorBanner.vue`

5. **Create Login Form Composable**
   - Create `src/composables/useLoginForm.ts`
   - Implement form state, validation, and submission logic

6. **Create Login Form Component**
   - Create `src/components/auth/LoginForm.vue`
   - Use composable for logic
   - Implement template with form fields and error handling

7. **Create Login Page View**
   - Create `src/views/auth/LoginPage.vue`
   - Add page layout, branding, and LoginForm

8. **Configure Router**
   - Add login route to `src/router/index.ts`
   - Implement auth guard to redirect authenticated users

9. **Add Accessibility Features**
   - Add proper ARIA labels and roles
   - Implement focus management
   - Test keyboard navigation

10. **Style with Tailwind**
    - Apply responsive styling
    - Add focus states and error states
    - Ensure dark mode support

11. **Write Tests**
    - Unit tests for validation logic
    - Component tests for LoginForm
    - Integration tests for login flow

12. **Manual Testing**
    - Test valid login flow
    - Test invalid credentials
    - Test network error handling
    - Test remember me functionality
    - Test accessibility with screen reader
