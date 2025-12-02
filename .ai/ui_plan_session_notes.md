# UI Architecture Planning Session Notes - AllWorkouts MVP

## Conversation Summary

### Decisions

1. **Dashboard Layout**: Dashboard with active plan button, preview next workout button, view history, view stats. Smaller button for importing new data.
2. **Import Wizard**: Use 3-step wizard pattern (paste text -> review matches -> confirm/edit -> save).
3. **Workout Session UI**: Hybrid approach with collapsible exercise accordion.
4. **Mobile Responsiveness**: Mobile-first design for workout session views, desktop-first for plan management.
5. **Rest Timer**: Persistent floating timer component with audio/vibration options.
6. **Confidence Indicators**: Color-coded badges (green/yellow/red) with icons for high/medium/low confidence.
7. **Equipment Warnings**: Non-blocking warnings allowing creation with alerts.
8. **Token Management**: Silent token refresh using axios interceptors with localStorage backup.
9. **Error Handling**: Tiered approach (inline, banners, toasts) based on error type.
10. **State Management**: Domain-specific Pinia stores with localStorage persistence for session store.
11. **Navigation Structure**: Top navbar for desktop, bottom navigation for mobile.
12. **History View**: Chronological list with filter chips and mini-calendar widget.
13. **Workout Plan Detail**: Vertical scrollable layout (not tabs or accordion).
14. **PR Display**: Both during session (inline indicator) and at completion (celebratory modal).
15. **Onboarding**: Mandatory 2-step wizard (units, equipment).
16. **Exercise Substitution**: Slide-over panel sorted by match_score then name, with equipment group filter chips.
17. **Stats Overview**: Compact cards on dashboard, expanded visualizations on dedicated Stats page.
18. **Loading States**: Skeleton loaders for lists, button states for forms, optimistic updates for workout.
19. **Accessibility**: Semantic HTML, keyboard navigation, ARIA labels, color contrast, focus management.
20. **Offline Handling**: localStorage persistence for active session, retry with exponential backoff.
21. **Form Inputs**: Direct numeric fields pre-filled with previous data, no quick-increment buttons.
22. **Set Completion**: Explicit "Log Set" button required.
23. **Profile/Settings**: Single Profile page with collapsible sections.
24. **Empty States**: Encouraging design with illustration, explanation, and primary action button.
25. **Session Exit**: Confirmation modal when navigating away from active session.
26. **Date Format**: Relative time for recent items, locale-aware absolute dates for older items.
27. **Plan Activation**: Highlighted active badge, confirmation when switching plans.
28. **Filter Persistence**: URL query parameters for shareable/bookmarkable filtered views.
29. **Exercise Details During Workout**: Info icon with slide-over panel for details.
30. **Confirmation Dialogs**: Modals for destructive high-impact actions, toast+undo for correctable changes.
31. **Breakpoints**: Three primary breakpoints (mobile <640px, tablet 640-1024px, desktop >1024px).
32. **Dark Mode**: Implemented with Tailwind `darkMode: 'class'`, dark mode as default.
33. **Typography**: Tailwind default scale with consistent application.
34. **Icons**: Heroicons as Vue components.
35. **Form Validation**: Progressive validation (blur, then change after error, full on submit).
36. **Loading Buttons**: Spinner + contextual text, maintain width to prevent layout shift.
37. **Pagination**: "Load More" button pattern for lists.
38. **Unit Storage**: All weights stored in metric (kg), converted for display based on user preference.
39. **Session Recovery**: Persistent banner for in-progress sessions with Resume/Abandon options.
40. **Micro-interactions**: Minimal purposeful animations, respect prefers-reduced-motion.
41. **Exercise Filter Chips**: Two rows - muscle groups and equipment groups, with "My Equipment Only" toggle.
42. **Skip RPE Input**: Not included in MVP.
43. **Skip Notes Fields**: Not included in MVP.
44. **Testing Strategy**: Prioritize E2E tests using Playwright (later priority).

### Matched Recommendations

1. **Dashboard**: 4 primary action areas with import as secondary action, matching user's request for simpler dashboard.
2. **Import Wizard**: 3-step wizard with confidence badges and equipment warnings.
3. **Workout Logging**: Collapsible accordion with current exercise expanded, previous collapsed.
4. **Mobile-First Workout**: Large touch targets, accessible timer, responsive utilities.
5. **Rest Timer**: Floating bottom-center, MM:SS display, progress ring, +30s/-30s, skip, audio option.
6. **Confidence System**: Green checkmark (80%+), yellow warning (50-80%), red question (<50%).
7. **Equipment Compatibility**: Amber alert banner, non-blocking, links to update or find substitutes.
8. **Auth Handling**: Axios interceptors for silent refresh, localStorage backup for workout sessions.
9. **Error States**: Field-level inline, form-level banners, system errors as toasts with retry.
10. **Pinia Stores**: authStore, profileStore, planStore, sessionStore, exerciseStore, uiStore.
11. **Navigation**: Top navbar desktop, bottom nav mobile, 4 main destinations.
12. **History View**: Chronological list with status/workout/date filters, mini-calendar visualization.
13. **Plan Detail**: Vertical scrollable layout with all workouts visible.
14. **PR Celebration**: Inline indicator during workout, modal with animation at completion.
15. **Onboarding**: 2 mandatory steps - unit toggle, equipment checkboxes by category.
16. **Substitution Panel**: Slide-over with match percentage, sorted by score then name.
17. **Exercise Picker Filters**: Muscle group chips + equipment group chips + "My Equipment Only" toggle.
18. **Stats Page**: Key metric cards, workout frequency bar chart, muscle group distribution.
19. **Skeleton Loaders**: Match layout structure for lists and card grids.
20. **Accessibility**: ARIA live regions, keyboard navigation, focus management, contrast compliance.
21. **Offline Mode**: localStorage persistence, connectivity indicator, queue and retry failed requests.
22. **Form Inputs**: Direct numeric input pre-filled from previous session context.
23. **Set Logging**: Explicit "Log Set" button, row transforms to read-only after logging.
24. **Profile Page**: Collapsible sections (Preferences, Equipment, Account, Danger Zone).
25. **Empty States**: Friendly illustration, explanation, primary CTA.
26. **Session Exit**: Confirmation modal with "Continue Workout" and "Leave" options.
27. **Date Display**: Relative time recent, locale-aware absolute older, "1h 15m" duration format.
28. **Plan Activation**: Active badge highlight, confirmation modal when switching.
29. **Filter Persistence**: URL query params synced with component state.
30. **Exercise Info**: Info icon opening slide-over with details, video if available.
31. **Confirmations**: Modals for delete/abandon, toast+undo for in-edit removals.
32. **Responsive**: Three breakpoints aligned with Tailwind defaults.
33. **Dark Mode**: `darkMode: 'class'`, dark as default, semantic color system, toggle in Profile.
34. **Typography**: Tailwind scale - display, heading, subheading, body, small, caption.
35. **Icons**: Heroicons, 16/20/24px sizes, aria-labels for icon-only buttons.
36. **Form Validation**: Progressive with Zod schemas matching API validation.
37. **Loading Buttons**: Spinner + contextual text, min-width to prevent shift.
38. **Pagination**: "Load More" hybrid pattern, mobile-friendly.
39. **Unit Conversion**: Store in kg, `useUnitConversion` composable for display conversion.
40. **Session Recovery**: Check on app load, persistent banner, resume or abandon options.
41. **Animations**: Fade transitions, slide panels, set completion checkmark, PR pulse.
42. **E2E Testing**: Playwright for critical flows, page object pattern, later priority.

### UI Architecture Planning Summary

#### Main UI Architecture Requirements

The AllWorkouts MVP requires a responsive web application built with Vue 3, Tailwind CSS, and Pinia for state management. The application must support:

- **Dark mode by default** with optional light mode toggle
- **Mobile-first design** for workout session views (gym usage)
- **Desktop-optimized layouts** for plan management and history browsing
- **Offline resilience** for workout logging with localStorage backup
- **JWT-based authentication** with silent token refresh

#### Key Views, Screens, and User Flows

**Authentication Flow:**
- Login page with email/password, "Remember me" checkbox
- Registration page with validation
- Mandatory 2-step onboarding: unit preference (metric/imperial) -> equipment selection by category

**Main Navigation (4 destinations):**
- Dashboard (home)
- Plans (list and management)
- History (workout sessions)
- Profile (settings)

**Dashboard:**
- Active Plan button (primary action)
- Next Workout preview button
- View History link
- View Stats link
- Import Plan button (smaller, secondary)
- Active session banner when workout in progress

**Workout Plan Management:**
- Plans list with cards showing name, workout count, active badge
- Plan detail: vertical scrollable layout showing all workouts
- Plan edit: dedicated page with inline editing, drag-to-reorder, swap/delete exercises
- Import wizard: 3 steps (text input -> match review with confidence badges -> confirm & save)

**Workout Session (Critical Flow):**
- Fixed header: workout name, elapsed timer, exit button
- Scrollable body: exercise accordion (completed collapsed, current expanded, pending visible)
- Set logging: direct numeric inputs pre-filled from previous session, explicit "Log Set" button
- Floating rest timer: MM:SS countdown, progress ring, +30s, skip, audio option
- Fixed footer: progress bar, "Complete Workout" button
- Completion screen: summary with duration, volume, PR celebration modal if applicable

**Exercise Picker (Slide-over Panel):**
- Search input with debounced API calls
- Two rows of filter chips: muscle groups + equipment groups
- "My Equipment Only" toggle
- Results sorted by match_score then name for substitutions
- "Create Custom Exercise" link at bottom

**History:**
- Chronological list with session cards
- Filter chips: status (completed/incomplete/skipped), workout name, date range
- Mini-calendar visualization
- "Load More" pagination
- Session detail view: full exercise/set breakdown, PRs highlighted

**Stats Page:**
- Key metric cards (total workouts, streak, PR count)
- Workout frequency bar chart
- Muscle group distribution visualization

**Profile:**
- Collapsible sections: Preferences (units, dark mode), Equipment, Account, Danger Zone

#### API Integration and State Management Strategy

**Pinia Stores:**
| Store | Purpose |
|-------|---------|
| `authStore` | User, tokens, login/logout/refresh actions |
| `profileStore` | Preferences, equipment, unit settings |
| `planStore` | Plans list, active plan, CRUD operations |
| `sessionStore` | Active workout session, exercise states, timer (persisted to localStorage) |
| `exerciseStore` | Search results, substitutes cache |
| `uiStore` | Toasts, modals, loading states, dark mode |

**API Client Architecture:**
- Axios instance with base URL `/api/v1`
- Interceptors for auth token injection and silent refresh
- Organized by domain: auth, plans, sessions, exercises, stats
- Retry logic with exponential backoff (1s, 2s, 4s) for network/5xx errors

**Data Handling:**
- All weights stored in metric (kg) in database
- Conversion to user preference on display via `useUnitConversion` composable
- Cache equipment list (24h), exercise search results (session), plans (5min)

#### Responsiveness, Accessibility, and Security Considerations

**Responsive Design:**
- Mobile (<640px): single column, bottom nav, full-width cards
- Tablet (640-1024px): two-column layouts, top nav
- Desktop (>1024px): max-width 1280px, multi-column grids, data tables

**Accessibility:**
- Semantic HTML with proper heading hierarchy
- Keyboard navigation for all interactive elements
- ARIA labels for icon-only buttons
- ARIA live regions for timer, set logging, PR announcements
- WCAG AA color contrast compliance
- Focus trapping in modals, return focus on close
- Respect `prefers-reduced-motion`

**Security:**
- JWT tokens: 1hr access, 7-day refresh (30-day with "Remember me")
- Silent token refresh via interceptors
- Secure localStorage for tokens (httpOnly cookie if possible)
- CORS configuration for frontend domain only
- Input validation with Zod matching API validation

#### Component Organization

```
components/
├── common/      (Button, Input, Modal, Toast, Badge, Card, Spinner, Skeleton)
├── layout/      (Navbar, BottomNav, PageHeader)
├── workout/     (ExerciseCard, SetRow, RestTimer, SessionProgress)
├── plan/        (PlanCard, WorkoutSection, ExerciseEditor)
└── exercise/    (ExercisePicker, SubstitutionPanel, MuscleGroupChips, EquipmentChips)
```

#### Route Structure

```
/login, /register, /onboarding
/dashboard
/plans, /plans/:id, /plans/:id/edit, /plans/import
/workout/:sessionId
/history, /history/:sessionId
/stats
/profile
```

#### Technical Stack Decisions

| Area | Decision |
|------|----------|
| Framework | Vue 3 with Composition API |
| Styling | Tailwind CSS with dark mode (`class` strategy) |
| State | Pinia with localStorage persistence |
| Router | Vue Router with auth guards |
| API Client | Axios with interceptors |
| Forms | VeeValidate + Zod for complex forms |
| Charts | Chart.js with vue-chartjs (lazy loaded) |
| Dates | date-fns |
| Icons | Heroicons |
| Testing | Playwright E2E (later priority) |

### Unresolved Issues

1. **Video/Image Hosting**: Exercise videos rely on external URLs. No decision on fallback if videos are unavailable beyond placeholder text.

2. **Timer Audio Implementation**: Audio notification option mentioned but specific sound asset and implementation details not discussed.

3. **Haptic Feedback Browser Support**: Recommendation made but actual browser support and fallback behavior not fully specified.

4. **Chart Library Dark Mode Colors**: Specific color palette for charts in dark mode not defined.

5. **Error Tracking Service**: Mentioned Sentry as future consideration but no groundwork decisions made.

6. **Data Export Format**: Deferred to post-MVP, but exact format (JSON/CSV) and structure not specified.

7. **Session Timeout Duration**: 30-minute inactivity warning mentioned, but exact behavior after warning timeout not fully specified.

8. **Equipment Categories Source**: Recommendation to group by category from API, but exact category list and mapping not confirmed against database schema.

9. **Custom Exercise Validation**: Rules for custom exercise creation (name uniqueness, required fields) not fully aligned with API validation.

10. **Concurrent API Requests**: No specific handling discussed for race conditions when multiple tabs are open.
