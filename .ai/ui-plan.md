# UI Architecture for AllWorkouts

## 1. UI Structure Overview

AllWorkouts is a responsive web application built with Vue 3, Tailwind CSS, and Pinia for state management. The application follows a mobile-first design philosophy for workout session views (optimized for gym usage) while maintaining desktop-optimized layouts for plan management and history browsing.

### Core Design Principles

- **Dark mode by default** with optional light mode toggle
- **Mobile-first workout logging** with large touch targets and accessible controls
- **Desktop-optimized management** for plans, history, and statistics
- **Offline resilience** with localStorage backup for active workout sessions
- **Progressive disclosure** showing relevant information at appropriate moments

### Responsive Breakpoints

| Breakpoint | Width | Layout Characteristics |
|------------|-------|------------------------|
| Mobile | <640px | Single column, bottom nav, full-width cards |
| Tablet | 640-1024px | Two-column layouts, top nav |
| Desktop | >1024px | Max-width 1280px, multi-column grids |

### State Management Architecture

| Store | Purpose |
|-------|---------|
| `authStore` | User authentication, tokens, login/logout/refresh actions |
| `profileStore` | User preferences (units, dark mode), equipment ownership |
| `planStore` | Workout plans list, active plan, CRUD operations |
| `sessionStore` | Active workout session state, persisted to localStorage |
| `exerciseStore` | Exercise search results, substitutes cache |
| `uiStore` | Toasts, modals, loading states, dark mode toggle |

---

## 2. View List

### 2.1 Login Page

- **Path**: `/login`
- **Purpose**: Authenticate existing users and provide access to the application
- **Key Information**:
  - Email and password input fields
  - "Remember me" option for extended session
  - Link to registration page
  - Error messages for failed authentication

**Key View Components**:
- Email input with validation
- Password input (masked)
- "Remember me" checkbox
- Submit button with loading state
- Error banner for authentication failures
- Registration link

**UX Considerations**:
- Clear error messaging for invalid credentials
- Loading state on submit button to prevent double-clicks
- Autofocus on email field

**Accessibility**:
- Proper form labels and associations
- Focus states for all interactive elements
- Error messages linked to inputs via aria-describedby
- Keyboard navigation support

**Security**:
- Password field masking
- Rate limiting feedback for failed attempts
- No password hints or recovery on this page

---

### 2.2 Registration Page

- **Path**: `/register`
- **Purpose**: Create new user accounts
- **Key Information**:
  - User name, email, and password inputs
  - Password requirements display
  - Validation feedback
  - Link to login for existing users

**Key View Components**:
- Name input (1-100 characters)
- Email input with uniqueness validation
- Password input with strength requirements (min 8 chars)
- Password confirmation input
- Submit button with loading state
- Inline validation messages
- Login link

**UX Considerations**:
- Real-time validation feedback on blur
- Password strength indicator
- Clear error messages for validation failures

**Accessibility**:
- Field labels and descriptions
- Error announcements for screen readers
- Focus management on validation errors

**Security**:
- Password requirements clearly displayed
- No password echoing
- HTTPS-only form submission

---

### 2.3 Onboarding Page

- **Path**: `/onboarding`
- **Purpose**: Collect mandatory user preferences after registration (units and equipment)
- **Key Information**:
  - Step 1: Unit system preference (metric/imperial)
  - Step 2: Available equipment selection by category

**Key View Components**:
- Progress indicator (Step 1/2, Step 2/2)
- Step 1:
  - Unit toggle (Metric kg/cm | Imperial lbs/in)
  - Visual examples of each unit system
- Step 2:
  - Equipment checkboxes grouped by category (Free Weights, Machines, Cables, Other)
  - Select all/none per category
- Next/Complete navigation buttons
- Back button on Step 2

**UX Considerations**:
- Cannot skip onboarding (mandatory for proper app function)
- Clear visual indication of current step
- Sensible defaults (no equipment pre-selected)

**Accessibility**:
- Step progress announced to screen readers
- Keyboard navigation through equipment categories
- Clear focus indicators
- Grouped checkboxes with fieldset/legend

**Security**:
- Protected route (requires authenticated user)
- Preferences stored server-side

---

### 2.4 Dashboard

- **Path**: `/dashboard`
- **Purpose**: Central hub for quick actions, status overview, and primary navigation
- **Key Information**:
  - Active plan status and next workout
  - Active session recovery (if applicable)
  - Quick statistics summary
  - Quick access to main features

**Key View Components**:
- Active session recovery banner (conditional):
  - Session name and time elapsed
  - "Resume" and "Abandon" buttons
- Active Plan card:
  - Plan name
  - "Start Workout" primary action button
  - Next workout preview
- Quick stats cards:
  - Total workouts this month
  - Current streak
  - Recent PRs count
- Action links:
  - "View History" link
  - "View Stats" link
  - "View Plans" link
- "Import Plan" secondary button
- Empty state (for new users):
  - Illustration
  - "Import your first workout plan" message
  - Primary "Import Plan" button

**UX Considerations**:
- Session recovery banner is persistent and prominent
- Primary action (Start Workout) is visually emphasized
- Import action is secondary to avoid overwhelming new users
- Quick stats provide immediate value without navigation

**Accessibility**:
- Logical heading hierarchy
- Landmark regions for main content areas
- Action buttons with descriptive labels
- ARIA live region for session recovery banner

**Security**:
- Protected route
- User-specific data only

---

### 2.5 Plans List

- **Path**: `/plans`
- **Purpose**: View and manage all user workout plans
- **Key Information**:
  - List of all plans with key metadata
  - Active plan indicator
  - Quick actions for each plan

**Key View Components**:
- Plan cards (grid on desktop, list on mobile):
  - Plan name
  - Workout count badge
  - Active badge (highlighted, for active plan only)
  - Last used date
  - Options menu (Edit, Delete, Set Active)
- "Import Plan" action button
- Empty state:
  - Illustration
  - "No workout plans yet" message
  - "Import Plan" primary button
- Confirmation modal for delete
- Confirmation modal for activate (when switching from another active plan)

**UX Considerations**:
- Active plan visually distinguished
- Destructive actions require confirmation
- Quick access to common actions via options menu
- Cards are clickable for detail view

**Accessibility**:
- Cards are focusable and keyboard-activatable
- Options menu accessible via keyboard
- Confirmation modals trap focus
- Delete confirmation clearly states consequences

**Security**:
- Only user's own plans displayed
- Cascade delete warning in confirmation

---

### 2.6 Plan Detail

- **Path**: `/plans/:id`
- **Purpose**: View complete workout plan structure with all workouts and exercises
- **Key Information**:
  - Plan name and metadata
  - All workouts in the plan
  - Exercise details for each workout (sets, reps, rest)
  - Equipment requirements

**Key View Components**:
- Header:
  - Plan name
  - Active badge (if active)
  - "Edit Plan" button
  - "Start Workout" button
- Vertical scrollable workout list:
  - Workout section header (name, day number)
  - Exercise rows:
    - Exercise name
    - Sets × Reps (e.g., "5 × 5")
    - Rest time
    - Equipment icons
- Equipment requirements summary
- Back navigation

**UX Considerations**:
- All workouts visible without tabs or accordion (per session notes)
- Clear visual hierarchy between workouts
- Equipment icons for quick reference
- "Start Workout" allows selecting which workout to start

**Accessibility**:
- Proper heading hierarchy (h1 for plan, h2 for workouts)
- Exercise data in accessible table or definition list format
- Equipment icons have text alternatives

**Security**:
- Validates plan belongs to current user
- 404 for non-existent or unauthorized plans

---

### 2.7 Plan Edit

- **Path**: `/plans/:id/edit`
- **Purpose**: Modify plan structure including workouts and exercises
- **Key Information**:
  - Editable plan name
  - Editable workout structure
  - Exercise add/remove/swap functionality
  - Unsaved changes tracking

**Key View Components**:
- Editable plan name input
- Workout sections:
  - Editable workout name
  - Draggable exercise rows (with keyboard alternative)
  - Each exercise row:
    - Exercise name (clickable to swap)
    - Sets input
    - Reps input
    - Rest seconds input
    - Remove button
  - "Add Exercise" button (opens exercise picker)
  - Remove workout button
- "Add Workout" button
- Fixed footer:
  - "Cancel" button
  - "Save Changes" button
- Unsaved changes warning modal (on navigation away)
- Toast with undo for removed exercises

**UX Considerations**:
- Drag-and-drop with keyboard alternative for reordering
- Inline editing reduces navigation
- Undo for accidental removals
- Auto-save consideration (deferred to future)

**Accessibility**:
- Drag-and-drop has keyboard equivalent (move up/down buttons)
- Focus management when adding/removing items
- Form inputs properly labeled
- Unsaved changes announced

**Security**:
- Only editable if plan.is_editable is true
- Validates user ownership

---

### 2.8 Plan Import Wizard

- **Path**: `/plans/import`
- **Purpose**: Convert plain text workout plan into structured data via AI parsing
- **Key Information**:
  - Step 1: Text input
  - Step 2: AI-matched exercises with confidence levels
  - Step 3: Review and save

**Key View Components**:
- Step indicator (Step 1/3, 2/3, 3/3)
- Step 1 - Text Input:
  - Large textarea for pasting workout text
  - Example format hint/tooltip
  - "Parse" button with loading state
  - Cancel/back navigation
- Step 2 - Review Matches:
  - Matched exercises list:
    - Original text
    - Matched exercise name
    - Confidence badge (green checkmark 80%+, yellow warning 50-80%, red question <50%)
    - "Change" button for low confidence matches
  - Equipment compatibility warnings (amber banner, non-blocking)
  - "Update Equipment" link
  - "Continue" button
- Step 3 - Confirm:
  - Plan preview (similar to detail view)
  - Plan name input
  - "Save Plan" button
- Back navigation between steps

**UX Considerations**:
- Clear progress indication
- Confidence levels help users identify items needing attention
- Equipment warnings are non-blocking but informative
- Users can edit before saving

**Accessibility**:
- Step progress announced to screen readers
- Confidence levels have text alternatives (not just color)
- Focus moves to first item needing attention
- Error messages clearly associated with inputs

**Security**:
- Rate limiting on parse endpoint (10 requests/hour)
- Sanitized text input

---

### 2.9 History List

- **Path**: `/history`
- **Purpose**: Browse chronological workout session history with filtering
- **Key Information**:
  - List of past workout sessions
  - Session status (completed, incomplete, skipped)
  - Session metadata (date, duration, exercise count)
  - Filtering and search options

**Key View Components**:
- Filter section:
  - Status filter chips (All, Completed, Incomplete, Skipped)
  - Workout name filter (dropdown or chips)
  - Date range picker (optional)
- Mini-calendar visualization (shows workout days)
- Session cards:
  - Workout name
  - Plan name
  - Date (relative for recent, absolute for older)
  - Duration (formatted as "1h 15m")
  - Status badge
  - Exercise count
- "Load More" pagination button
- Empty state:
  - Illustration
  - "No workouts logged yet" message
  - "Start your first workout" button

**UX Considerations**:
- Filters persist in URL for shareable/bookmarkable views
- Relative dates for recent sessions ("Today", "Yesterday", "3 days ago")
- Mini-calendar provides visual overview of workout frequency
- Load more pattern for mobile-friendly pagination

**Accessibility**:
- Filter state announced when changed
- Date format is screen reader friendly
- Cards are keyboard-navigable
- Empty state is properly announced

**Security**:
- Only user's own sessions displayed
- Protected route

---

### 2.10 Session Detail

- **Path**: `/history/:sessionId`
- **Purpose**: View detailed information about a completed workout session
- **Key Information**:
  - Session metadata (date, duration, status)
  - Complete exercise breakdown with sets
  - PRs achieved during session
  - Session notes

**Key View Components**:
- Session header:
  - Workout name
  - Date and time
  - Duration
  - Status badge
- Exercise list:
  - Exercise name
  - Sets table:
    - Set number
    - Weight
    - Reps
    - PR indicator (if applicable)
  - Exercise notes (if any)
- PRs section (if any achieved):
  - List of new PRs with exercise name, type, value
- Session notes section
- "Repeat Workout" button (starts new session with same workout)
- Back navigation

**UX Considerations**:
- PR achievements highlighted
- Clear data presentation
- Easy to compare with expectations from plan

**Accessibility**:
- Tables have proper headers and captions
- PR indicators have text alternatives
- Logical reading order

**Security**:
- Validates session belongs to current user
- 404 for unauthorized access

---

### 2.11 Active Workout Session

- **Path**: `/workout/:sessionId`
- **Purpose**: Real-time workout logging with set tracking, rest timer, and progress indication
- **Key Information**:
  - Current workout structure
  - Previous session context for each exercise
  - Set logging interface
  - Rest timer
  - Progress tracking

**Key View Components**:
- Fixed header:
  - Workout name
  - Elapsed timer (running)
  - Exit button (with confirmation modal)
- Scrollable exercise accordion:
  - Completed exercises (collapsed, checkmark icon)
  - Current exercise (expanded):
    - Exercise name with info icon (opens detail slide-over)
    - Previous session context:
      - "Last time: 5 sets × 135 lbs × 5 reps"
      - PR info if applicable
    - Set rows:
      - Set number
      - Weight input (pre-filled from previous/plan)
      - Reps input (pre-filled from previous/plan)
      - "Log Set" button
    - Logged sets (read-only, tap to edit)
  - Pending exercises (visible, collapsed)
- Floating rest timer (appears after logging set):
  - MM:SS countdown
  - Progress ring visualization
  - +30s button
  - Skip button
  - Audio toggle
- Fixed footer:
  - Progress bar (sets completed / total sets)
  - "Complete Workout" button (enabled when all sets logged)
- Confirmation modal for exit

**UX Considerations**:
- Mobile-first design with large touch targets
- Pre-filled values reduce input effort
- Accordion keeps focus on current exercise
- Rest timer is non-blocking but prominent
- Progress provides motivation and context
- Can complete with incomplete sets (saved as incomplete)

**Accessibility**:
- ARIA live regions for timer countdown
- Set logging announced for screen readers
- Large touch targets (min 44x44px)
- Focus management on exercise transitions
- Reduced motion support for timer animations
- High contrast mode support

**Security**:
- Session belongs to current user
- localStorage backup for offline resilience
- Auto-save on each set log

---

### 2.12 Workout Completion Summary

- **Path**: `/workout/:sessionId/complete` (or modal overlay)
- **Purpose**: Celebrate workout completion and display summary statistics
- **Key Information**:
  - Workout duration
  - Total volume lifted
  - Sets completed
  - New personal records

**Key View Components**:
- Success message/header
- Stats summary cards:
  - Total duration
  - Total volume (in user's preferred unit)
  - Sets completed
- New PRs section (if any):
  - PR celebration animation
  - List of achievements:
    - Exercise name
    - Record type (1RM, Set Volume, Total Volume)
    - New value
- Action buttons:
  - "View Details" (goes to session detail)
  - "Back to Dashboard" (primary)

**UX Considerations**:
- Celebratory UI for PRs (subtle animation, not overwhelming)
- Clear summary of accomplishment
- Easy navigation to next action

**Accessibility**:
- PR achievements announced for screen readers
- Animations respect prefers-reduced-motion
- Clear button labels

**Security**:
- Session marked complete server-side
- PR calculations done server-side

---

### 2.13 Stats Page

- **Path**: `/stats`
- **Purpose**: View progress statistics and workout analytics
- **Key Information**:
  - Key performance metrics
  - Workout frequency over time
  - Muscle group training distribution
  - Personal records overview

**Key View Components**:
- Date range filter (optional)
- Key metric cards:
  - Total workouts
  - Total duration (formatted)
  - Current streak (days)
  - Total PRs achieved
- Workout frequency chart:
  - Bar chart showing workouts per month
  - Last 6-12 months
- Muscle group distribution:
  - Pie or donut chart
  - Sessions per muscle group
- Loading skeletons during data fetch

**UX Considerations**:
- Charts lazy-loaded for performance
- Date range affects all metrics
- Mobile-friendly chart sizing
- Skeleton loaders match final layout

**Accessibility**:
- Charts have text descriptions/summaries
- Color-blind friendly color palette
- Data tables as alternative to charts (hidden but accessible)

**Security**:
- Only user's own data displayed
- Protected route

---

### 2.14 Profile Page

- **Path**: `/profile`
- **Purpose**: Manage user settings, preferences, equipment, and account
- **Key Information**:
  - Unit preferences
  - Dark mode setting
  - Equipment availability
  - Account settings

**Key View Components**:
- Collapsible sections:
  - **Preferences**:
    - Unit system toggle (Metric/Imperial)
    - Dark mode toggle
  - **Equipment**:
    - Equipment list grouped by category
    - Toggle ownership for each item
    - Visual indicator of owned vs not owned
  - **Account**:
    - Email (read-only display)
    - "Change Password" button (opens modal/form)
  - **Danger Zone**:
    - "Delete Account" button
    - Confirmation modal with consequences
- Save button (if applicable, or auto-save)

**UX Considerations**:
- Collapsible sections reduce cognitive load
- Clear distinction between preferences and danger zone
- Auto-save or explicit save based on section
- Equipment changes reflect immediately in exercise availability

**Accessibility**:
- Collapsible sections use proper ARIA (aria-expanded)
- Toggle switches have visible labels
- Delete confirmation clearly states consequences
- Keyboard navigation for all controls

**Security**:
- Password change requires current password
- Delete account requires confirmation
- Protected route

---

## 3. User Journey Map

### 3.1 First-Time User Journey (Primary)

```
Registration → Onboarding (Units) → Onboarding (Equipment) → Dashboard (Empty)
    ↓
Import Wizard (Text Input) → Import Wizard (Review Matches) → Import Wizard (Confirm)
    ↓
Dashboard (Active Plan) → Start Workout → Active Session → Log Sets → Complete
    ↓
Completion Summary → Dashboard
```

**Detailed Steps**:
1. User registers with email/password/name
2. User completes mandatory onboarding:
   - Selects metric or imperial units
   - Selects available equipment from categorized list
3. User lands on empty dashboard with "Import Plan" CTA
4. User pastes workout plan text
5. User reviews AI-matched exercises, addresses low-confidence matches
6. User confirms and saves plan
7. Dashboard shows active plan with "Start Workout" button
8. User starts first workout session
9. User logs sets with pre-filled values (from plan defaults)
10. Rest timer appears after each set
11. User completes all sets and finishes workout
12. Completion summary shows duration, volume, any PRs
13. User returns to dashboard

### 3.2 Returning User Journey (Secondary)

```
Login → Dashboard → Start Workout → Active Session → Log Sets → Complete → Dashboard
```

**With Session Recovery**:
```
Login → Dashboard (Recovery Banner) → Resume Session → Continue Logging → Complete
```

### 3.3 History Review Journey (Tertiary)

```
Dashboard → History → Filter Sessions → Session Detail → Back to History
```

### 3.4 Plan Management Journey

```
Dashboard → Plans List → Plan Detail → Edit Plan → Save → Plan Detail
```

### 3.5 Equipment Update Journey

```
Profile → Equipment Section → Toggle Equipment → Changes Saved
```

---

## 4. Layout and Navigation Structure

### 4.1 Desktop Navigation (Top Navbar)

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo/Home]     [Plans]     [History]     [Stats]  │  [Profile] │
└─────────────────────────────────────────────────────────────────┘
```

- Logo links to Dashboard
- Main navigation items: Plans, History, Stats
- Profile icon in top-right with dropdown (Profile, Logout)
- Active item visually indicated

### 4.2 Mobile Navigation (Bottom Nav)

```
┌─────────────────────────────────────────────────────────────────┐
│                          [Page Content]                          │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  [Dashboard]    [Plans]    [History]    [Profile]               │
└─────────────────────────────────────────────────────────────────┘
```

- 4 main destinations
- Stats accessible from Dashboard or as tab (space permitting)
- Icons with text labels
- Active item highlighted

### 4.3 Route Structure

```
Public Routes:
  /login
  /register

Protected Routes (require authentication):
  /onboarding          (post-registration, mandatory)
  /dashboard           (home)
  /plans               (plans list)
  /plans/:id           (plan detail)
  /plans/:id/edit      (plan edit)
  /plans/import        (import wizard)
  /workout/:sessionId  (active workout)
  /history             (session history)
  /history/:sessionId  (session detail)
  /stats               (statistics)
  /profile             (settings)
```

### 4.4 Navigation Guards

- Unauthenticated users redirected to `/login`
- Authenticated users without onboarding redirected to `/onboarding`
- Active session banner appears on all protected routes (except workout view)

---

## 5. Key Components

### 5.1 Common Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `Button` | Primary, secondary, and danger variants with loading state | All forms and actions |
| `Input` | Text, number, email, password with validation states | Forms |
| `Modal` | Centered overlay with focus trapping | Confirmations, forms |
| `Toast` | Non-blocking notification with optional undo | Success, error, info messages |
| `Badge` | Status indicator (active, completed, confidence) | Plans, sessions, exercises |
| `Card` | Container for grouped content | Plans, sessions, stats |
| `Spinner` | Loading indicator | Buttons, inline loading |
| `Skeleton` | Content placeholder during loading | Lists, cards |
| `Toggle` | On/off switch for binary options | Preferences, equipment |
| `Accordion` | Collapsible content sections | Exercises, profile sections |

### 5.2 Layout Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `Navbar` | Top navigation bar for desktop | Desktop layout |
| `BottomNav` | Bottom navigation bar for mobile | Mobile layout |
| `PageHeader` | Page title with optional actions | All pages |
| `SlideOver` | Side panel overlay | Exercise picker, substitutions, details |

### 5.3 Workout Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `ExerciseCard` | Exercise display with sets/reps | Plan detail, workout session |
| `SetRow` | Set logging input row | Active workout |
| `RestTimer` | Floating countdown timer | Active workout |
| `SessionProgress` | Progress bar with set count | Active workout footer |
| `ExerciseAccordion` | Collapsible exercise section | Active workout |
| `PRIndicator` | Personal record badge | Session, completion |

### 5.4 Plan Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `PlanCard` | Plan summary with actions | Plans list |
| `WorkoutSection` | Workout header with exercises | Plan detail, edit |
| `ExerciseEditor` | Editable exercise row | Plan edit |
| `ConfidenceBadge` | Import match confidence indicator | Import wizard |
| `EquipmentWarning` | Compatibility alert banner | Import wizard |

### 5.5 Exercise Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `ExercisePicker` | Searchable exercise selection panel | Plan edit, import |
| `SubstitutionPanel` | Similar exercises list | Plan edit |
| `MuscleGroupChips` | Filter chips for muscle groups | Exercise search |
| `EquipmentChips` | Filter chips for equipment | Exercise search |
| `ExerciseDetail` | Full exercise information | Info panel |

### 5.6 History Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `SessionCard` | Session summary with status | History list |
| `FilterChips` | Status/workout filter toggles | History list |
| `MiniCalendar` | Workout frequency visualization | History list |
| `ExerciseHistory` | Exercise performance in session | Session detail |

### 5.7 Stats Components

| Component | Description | Usage |
|-----------|-------------|-------|
| `MetricCard` | Key stat display | Dashboard, stats page |
| `FrequencyChart` | Workout frequency bar chart | Stats page |
| `MuscleDistribution` | Muscle group pie chart | Stats page |

---

## 6. Error States and Edge Cases

### 6.1 Authentication Errors

| Error | UI Response |
|-------|-------------|
| Invalid credentials | Inline error message on form |
| Token expired | Silent refresh, fallback to login redirect |
| Network error on auth | Toast with retry option |

### 6.2 Form Validation Errors

| Error | UI Response |
|-------|-------------|
| Field validation failure | Inline error under field (on blur, then on change) |
| Server validation error | Map to field or display as banner |
| Submit with errors | Focus first error field, scroll if needed |

### 6.3 Network and API Errors

| Error | UI Response |
|-------|-------------|
| API unreachable | Toast with retry, offline mode for workout |
| 5xx server error | Toast with retry option |
| Timeout | Toast with retry option |

### 6.4 Resource Errors

| Error | UI Response |
|-------|-------------|
| 404 Not Found | Error page with navigation to parent |
| 403 Forbidden | Redirect to dashboard |
| Resource deleted | Toast notification, refresh list |

### 6.5 Workout Session Edge Cases

| Scenario | UI Response |
|----------|-------------|
| Session interrupted | Recovery banner on return with resume/abandon |
| Network loss during workout | Continue logging, sync on reconnect |
| Tab/browser closed | localStorage preserves state, recovery on return |
| Navigating away | Confirmation modal |
| Timer running when closing | Timer state preserved |

### 6.6 Empty States

| Context | UI Response |
|---------|-------------|
| No plans | Illustration + "Import your first plan" CTA |
| No history | Illustration + "Start your first workout" CTA |
| No PRs | Simple text "No personal records yet" |
| No search results | "No exercises found" with suggestions |
| No equipment selected | Prompt to update in profile |

---

## 7. Accessibility Considerations

### 7.1 Semantic HTML

- Proper heading hierarchy (h1-h6)
- Landmark regions (nav, main, aside, footer)
- Lists for navigation and repetitive content
- Tables for tabular data
- Buttons for actions, links for navigation

### 7.2 Keyboard Navigation

- All interactive elements focusable
- Logical tab order
- Focus visible indicators
- Skip links for main content
- Escape to close modals/panels

### 7.3 Screen Reader Support

- ARIA labels for icon-only buttons
- ARIA live regions for:
  - Rest timer countdown
  - Set logging confirmation
  - PR achievements
  - Toast notifications
- Descriptive link text
- Form field descriptions

### 7.4 Visual Accessibility

- WCAG AA color contrast compliance
- Color not sole indicator (icons/text accompany color)
- Focus indicators visible in all themes
- Reduced motion support (prefers-reduced-motion)
- Text resizable to 200% without loss of function

### 7.5 Forms

- Labels associated with inputs
- Error messages linked via aria-describedby
- Required fields indicated
- Clear validation feedback

---

## 8. Security Considerations

### 8.1 Authentication

- JWT tokens: 1hr access, 7-day refresh (30-day with "Remember me")
- Silent token refresh via axios interceptors
- Secure storage (httpOnly cookies preferred, localStorage fallback)
- Logout clears all tokens

### 8.2 Data Protection

- Input validation with Zod (client) matching Pydantic (server)
- XSS prevention via Vue's automatic escaping
- CORS configuration for frontend domain only
- User data isolation (server-enforced)

### 8.3 Route Protection

- Auth guards on protected routes
- Ownership validation on resource access
- Graceful handling of unauthorized access

---

## 9. Technical Implementation Notes

### 9.1 Unit Conversion

- All weights stored in metric (kg) server-side
- `useUnitConversion` composable for display conversion
- Conversion on input/output, not storage

### 9.2 Caching Strategy

| Data | Cache Duration |
|------|----------------|
| Equipment list | 24 hours |
| Exercise search results | Session |
| Plans list | 5 minutes |
| Active session | localStorage (persistent) |

### 9.3 Loading States

- Skeleton loaders for lists and cards
- Button spinners for form submissions
- Optimistic updates for workout logging

### 9.4 Offline Support

- Active session persisted to localStorage
- Connectivity indicator when offline
- Queue failed requests for retry
- Exponential backoff (1s, 2s, 4s)
