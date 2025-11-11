# Frontend Development Rules - AllWorkouts

## Stack Overview
- **Framework**: Vue 3
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: axios
- **Validation**: zod

For complete stack details, see [../tech_stack.md](../tech_stack.md).

## Code Organization

### Project Structure
```
frontend/src/
├── components/
│   ├── common/          # Reusable components
│   │   ├── Button.vue
│   │   ├── Modal.vue
│   │   └── ...
│   └── features/        # Feature-specific components
│       ├── auth/
│       ├── workouts/
│       └── ...
├── views/               # Page components
│   ├── Home.vue
│   ├── Login.vue
│   └── ...
├── stores/              # Pinia state management
│   ├── auth.ts
│   ├── workouts.ts
│   └── ...
├── services/            # API services
│   ├── api.ts
│   ├── authService.ts
│   └── workoutService.ts
├── composables/         # Reusable composition functions
│   ├── useAuth.ts
│   ├── useForm.ts
│   └── ...
├── types/               # TypeScript types
│   ├── auth.ts
│   ├── workouts.ts
│   └── index.ts
├── utils/               # Utility functions
│   ├── formatters.ts
│   ├── validators.ts
│   └── ...
├── App.vue
├── main.ts
└── router.ts
```

### File Organization Rules
- **Components**: One component per file
- **Small components**: Can live in `components/common/`
- **Feature components**: Organized by feature in `components/features/`
- **Views**: Page-level components only
- **Stores**: One store per domain
- **Services**: API communication layer
- **Composables**: Reusable logic (like hooks)

## Code Style Guidelines

### Formatting & Indentation
- **Indentation**: 2 spaces, no tabs
- **String quotes**: Single quotes (`'string'`)
- **Line length**: 100 characters (Prettier default)
- **Formatter**: Prettier
- **Linter**: ESLint
- **Framework linter**: @vue/eslint-config-prettier

### Naming Conventions
- **Components**: `PascalCase`
  - ✓ `UserCard.vue`, `WorkoutList.vue`
  - ✗ `userCard.vue`, `workout_list.vue`
- **Component files**: Match component name
  - ✓ `UserCard.vue` exports `UserCard`
  - ✗ `userCard.vue` exports `UserCard`
- **Functions & variables**: `camelCase`
  - ✓ `getUserData()`, `isActive`
  - ✗ `get_user_data()`, `IsActive`
- **Constants**: `UPPER_SNAKE_CASE`
  - ✓ `const MAX_RETRIES = 3`
  - ✗ `const maxRetries = 3`
- **Private/internal**: Prefix with underscore
  - ✓ `_handleInternalLogic()`
  - ✓ `_internalState`
- **Events**: Use descriptive names prefixed with `on`
  - ✓ `@on-user-select="handleUserSelect"`
  - ✗ `@click-handler="handleClick"`
- **Stores/composables**: Use descriptive names
  - ✓ `useAuthStore()`, `useFormValidation()`
  - ✗ `store()`, `validation()`

### Component Structure
```vue
<template>
  <div class="user-card">
    <h2>{{ user.name }}</h2>
    <p>{{ user.email }}</p>
    <button @click="handleEdit">Edit</button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { User } from '@/types/auth'

interface Props {
  user: User
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  'on-edit': [id: string]
}>()

// Reactive state
const isLoading = ref(false)

// Computed properties
const displayName = computed(() => props.user.name.toUpperCase())

// Methods
const handleEdit = () => {
  emit('on-edit', props.user.id)
}
</script>

<style scoped>
.user-card {
  @apply rounded-lg border border-gray-200 p-4;
}
</style>
```

### Key Points
- Use Composition API with `<script setup>`
- Define `Props` and emit types with TypeScript interfaces
- Group reactive state, computed properties, and methods logically
- Use Tailwind classes with `@apply` in scoped styles
- Prefer `const` over `let`, avoid `var`

## TypeScript Guidelines

### Type Definitions
- **Create type files**: Define all types in `types/` folder
  ```typescript
  // types/auth.ts
  export interface User {
    id: string
    email: string
    name: string
    createdAt: Date
  }

  export interface LoginRequest {
    email: string
    password: string
  }

  export interface LoginResponse {
    user: User
    token: string
    expiresIn: number
  }
  ```
- **Use interfaces for objects**: More readable than types
  ```typescript
  // ✓ Good for objects
  interface User {
    id: string
    name: string
  }

  // ✓ Good for unions/functions
  type Status = 'idle' | 'loading' | 'error' | 'success'
  type Callback = (error: Error | null) => void
  ```
- **Avoid `any`**: Always use specific types
  ```typescript
  // ✗ Bad
  const data: any = response.data

  // ✓ Good
  interface ApiResponse {
    success: boolean
    data: User[]
  }
  const data: ApiResponse = response.data
  ```

### Props & Emits
```typescript
// ✓ Good - Typed with interface
interface Props {
  user: User
  isLoading?: boolean
  maxRetries?: number
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  maxRetries: 3,
})

// Define emits with types
const emit = defineEmits<{
  'on-save': [user: User]
  'on-cancel': []
}>()
```

## State Management (Pinia)

### Store Structure
```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/auth'
import authService from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const userName = computed(() => user.value?.name || 'Guest')

  // Actions
  async function login(email: string, password: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await authService.login(email, password)
      user.value = response.user
      isAuthenticated.value = true
      // Store token (implementation depends on your needs)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      isAuthenticated.value = false
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await authService.logout()
      user.value = null
      isAuthenticated.value = false
    } catch (err) {
      console.error('Logout failed:', err)
    }
  }

  return {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,
    // Computed
    userName,
    // Actions
    login,
    logout,
  }
})
```

### Store Usage in Components
```vue
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Access state
console.log(authStore.user)
console.log(authStore.isLoading)

// Call actions
await authStore.login('user@example.com', 'password')

// Use computed properties
const name = authStore.userName
</script>
```

### Best Practices
- **One store per domain**: auth, workouts, ui, etc.
- **Keep stores focused**: Single responsibility principle
- **State in store**: Shared across components
- **Local state in components**: Component-specific only
- **Use actions for side effects**: API calls, async operations
- **No direct state mutations**: Always use actions

## Composables (Reusable Logic)

### Composable Structure
```typescript
// composables/useFormValidation.ts
import { ref, computed } from 'vue'
import { z } from 'zod'

interface ValidationResult {
  isValid: boolean
  errors: Record<string, string>
}

export function useFormValidation<T>(schema: z.ZodSchema<T>) {
  const errors = ref<Record<string, string>>({})

  const validate = (data: unknown): ValidationResult => {
    try {
      schema.parse(data)
      errors.value = {}
      return { isValid: true, errors: {} }
    } catch (err) {
      if (err instanceof z.ZodError) {
        const formattedErrors: Record<string, string> = {}
        err.errors.forEach((error) => {
          const path = error.path.join('.')
          formattedErrors[path] = error.message
        })
        errors.value = formattedErrors
        return { isValid: false, errors: formattedErrors }
      }
      throw err
    }
  }

  const hasErrors = computed(() => Object.keys(errors.value).length > 0)

  return {
    errors,
    validate,
    hasErrors,
    clearErrors: () => (errors.value = {}),
  }
}
```

### Composable Usage
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { z } from 'zod'

const formSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

const { validate, errors, clearErrors } = useFormValidation(formSchema)

const formData = ref({ email: '', password: '' })

const handleSubmit = () => {
  const result = validate(formData.value)
  if (result.isValid) {
    // Submit form
  }
}
</script>
```

## API Integration

### API Service Structure
```typescript
// services/api.ts
import axios, { AxiosInstance, AxiosError } from 'axios'
import type { ApiResponse } from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### Feature-Specific Services
```typescript
// services/authService.ts
import apiClient from './api'
import type { User, LoginRequest, LoginResponse } from '@/types/auth'

export default {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/users/login', {
      email,
      password,
    })
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/users/logout')
  },

  async getProfile(): Promise<User> {
    const response = await apiClient.get<User>('/users/profile')
    return response.data
  },
}
```

## Validation (zod)

### Schema Definition
```typescript
// types/auth.ts
import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain uppercase letter')
    .regex(/[0-9]/, 'Password must contain number'),
})

export type LoginFormData = z.infer<typeof loginSchema>

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string(),
  createdAt: z.coerce.date(),
})

export type User = z.infer<typeof userSchema>
```

### Validation Usage
```typescript
import { loginSchema, type LoginFormData } from '@/types/auth'

try {
  const validData: LoginFormData = loginSchema.parse(formData)
  // Use validated data
} catch (error) {
  if (error instanceof z.ZodError) {
    console.log(error.errors) // Array of validation errors
  }
}
```

## Styling Guidelines

### Tailwind CSS
- **Use utility classes**: Prefer Tailwind over custom CSS
  ```vue
  <!-- ✓ Good -->
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Click me
  </button>

  <!-- ✗ Avoid custom classes -->
  <button class="btn btn-primary">Click me</button>
  ```
- **Responsive design**: Mobile-first approach
  ```vue
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div>Item 1</div>
  </div>
  ```
- **Dark mode support**: Use dark: prefix
  ```vue
  <div class="bg-white dark:bg-gray-900 text-black dark:text-white">
    Content
  </div>
  ```

### Scoped Styles
```vue
<style scoped>
/* Use @apply for complex utilities */
.form-input {
  @apply block w-full px-4 py-2 border border-gray-300 rounded;
}

.form-input:focus {
  @apply border-blue-500 outline-none ring-2 ring-blue-200;
}

/* Regular CSS for component-specific styles */
.card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
```

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── stores/
│   │   └── auth.spec.ts
│   ├── composables/
│   │   └── useFormValidation.spec.ts
│   └── utils/
│       └── formatters.spec.ts
├── components/
│   └── UserCard.spec.ts
└── integration/
    └── auth.spec.ts
```

### Component Testing
```typescript
// tests/components/UserCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '@/components/UserCard.vue'

describe('UserCard', () => {
  it('renders user information', () => {
    const user = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
    }

    const wrapper = mount(UserCard, {
      props: { user },
    })

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
  })

  it('emits on-edit event when edit button clicked', async () => {
    const user = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
    }

    const wrapper = mount(UserCard, {
      props: { user, editable: true },
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('on-edit')?.[0]).toEqual(['1'])
  })
})
```

### Testing Best Practices
- **Test behavior, not implementation**: What does the user see?
- **Use descriptive test names**: Clear intent
- **Isolate tests**: No dependencies between tests
- **Mock API calls**: Don't make real requests
- **Test both happy and error paths**

## Performance Guidelines

### Code Splitting
- **Lazy load routes**:
  ```typescript
  // router.ts
  const Home = () => import('@/views/Home.vue')
  const Workouts = () => import('@/views/Workouts.vue')

  const routes = [
    { path: '/', component: Home },
    { path: '/workouts', component: Workouts },
  ]
  ```
- **Lazy load heavy components**:
  ```typescript
  const HeavyChart = defineAsyncComponent(() =>
    import('@/components/HeavyChart.vue')
  )
  ```

### Optimization
- **Use `v-show` vs `v-if`**: Show for frequently toggled elements
- **Memoization**: Cache computed expensive calculations
  ```typescript
  const cachedValue = computed(() => {
    // Complex computation
    return expensiveCalculation()
  })
  ```
- **Debounce/throttle**: API calls on user input
  ```typescript
  import { debounce } from 'lodash-es'

  const handleSearch = debounce((query: string) => {
    searchAPI(query)
  }, 300)
  ```
- **Image optimization**: Use responsive images, lazy loading
  ```vue
  <img
    v-lazy="imageUrl"
    :alt="alt"
    class="w-full h-auto"
  />
  ```

### Bundle Size
- **Monitor**: Use `npm run build` and analyze
- **Remove unused**: Tree-shake dead code
- **Dynamic imports**: Load on demand

## Environment Configuration

### Environment Variables
```bash
# .env.local
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AllWorkouts

# .env.development
VITE_DEBUG=true

# .env.production
VITE_DEBUG=false
VITE_API_URL=https://api.example.com
```

### Usage in Code
```typescript
const apiUrl = import.meta.env.VITE_API_URL
const isDevelopment = import.meta.env.DEV
```

## Development Workflow

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

### Git Commits
- Write clear commit messages
- Reference related issues: `Fixes #123`
- Keep commits focused

### Before Committing
- Format: `npm run format`
- Lint: `npm run lint`
- Tests: `npm run test`
- Build: `npm run build`
