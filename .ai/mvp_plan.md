# MVP Implementation Plan - AllWorkouts

This document tracks the remaining work needed to complete the MVP based on gap analysis performed on 2025-01-10.

## Status Legend
- [ ] Not started
- [x] Completed
- [~] In progress

---

## Priority 1: Critical MVP Blockers

### 1.1 Backend: Restructure Workout Plans (Plan → Workouts → Exercises)
**Estimated: 6-8 hours** ✓ COMPLETED

- [x] Create new `Workout` model (id, plan_id, name, day_number, order_index)
- [x] Update `PlannedExercise` to reference `workout_id` instead of `plan_id`
- [x] Create Alembic migration for schema changes
- [x] Update workout plan schemas for nested structure
- [x] Update workout plan API endpoints:
  - [x] GET /workout-plans returns nested workouts
  - [x] GET /workout-plans/{id} returns full workout structure
  - [x] POST /workout-plans accepts nested workout structure
  - [x] PUT /workout-plans/{id} updates nested structure
- [x] Update parser service to output nested structure
- [x] Update seed data if needed
- [x] Update all related tests

### 1.2 Backend: Add is_active field and toggle endpoint
**Estimated: 2-3 hours** ✓ COMPLETED

- [x] Add `is_active` boolean field to WorkoutPlan model
- [x] Add migration for is_active field (included in 004_add_workout_hierarchy)
- [x] Include `is_active` in all plan response schemas
- [x] Create `PATCH /workout-plans/{id}/active` endpoint
- [x] Implement auto-deactivation of other plans when one is activated
- [x] Update tests

### 1.3 Frontend: Complete OnboardingView with equipment selection
**Estimated: 3-4 hours**

- [ ] Convert to 2-step wizard with StepIndicator component
- [ ] Step 1: Unit selection (update existing)
- [ ] Step 2: Equipment selection by category
  - [ ] Fetch equipment list from API
  - [ ] Group equipment by category
  - [ ] Checkbox grid for each category
  - [ ] Select all/none per category
- [ ] Navigation: Next/Back/Complete buttons
- [ ] Call equipment ownership API on completion
- [ ] Redirect to dashboard after completion
- [ ] Add onboarding_completed flag check to auth flow

### 1.4 Frontend: Implement StatsView with real data
**Estimated: 4-6 hours**

- [ ] Connect to statsService.getOverview()
- [ ] Display key metrics cards:
  - [ ] Total workouts
  - [ ] Total duration (formatted)
  - [ ] Current streak
  - [ ] Total PRs
- [ ] Workout frequency visualization (simple CSS-based bars)
  - [ ] Show last 6 months
  - [ ] Display count per month
- [ ] Muscle group distribution (simple CSS-based pie/donut or horizontal bars)
- [ ] Add date range filter (optional, can be deferred)
- [ ] Loading skeletons
- [ ] Error state handling

### 1.5 Frontend: Add localStorage persistence for active workout
**Estimated: 2-3 hours**

- [ ] Create workout session storage utilities in workout store
- [ ] Save to localStorage on:
  - [ ] Session start
  - [ ] Each set log
  - [ ] Exercise navigation
- [ ] Restore session state on app initialization
- [ ] Update dashboard recovery banner to use stored data
- [ ] Clear localStorage on:
  - [ ] Session complete
  - [ ] Session skip/abandon
  - [ ] Explicit abandon from recovery banner
- [ ] Handle stale session detection (>24 hours old)

---

## Priority 2: Important Features

### 2.1 Backend: Add name field to User model
**Estimated: 1 hour** ✓ COMPLETED

- [x] Add nullable `name` field to User model
- [x] Create migration
- [x] Include name in register request schema
- [x] Include name in user response schemas
- [x] Update auth endpoints

### 2.2 Frontend: Add name field to registration
**Estimated: 30 minutes**

- [ ] Add name input field to RegisterView
- [ ] Add validation (1-100 characters)
- [ ] Update register API call

### 2.3 Frontend: Add active plan indicator and toggle
**Estimated: 1-2 hours**

- [ ] Show active badge on PlansListView cards
- [ ] Add "Set Active" action to plan options menu
- [ ] Create setActive() in workoutPlanService
- [ ] Call API and refresh list on activation
- [ ] Show confirmation when switching active plans

### 2.4 Frontend: Add PR indicators to SessionDetailView
**Estimated: 2 hours**

- [ ] Fetch PRs achieved in session (may need new API or include in session detail)
- [ ] Show PR badge/icon on relevant sets
- [ ] Add "New PRs" summary section at top if any achieved
- [ ] Style PR highlights consistently with WorkoutCompleteView

### 2.5 Backend: Add custom exercise CRUD
**Estimated: 3-4 hours** ✓ COMPLETED

- [x] Add `is_custom` and `user_id` fields to Exercise model (if not present)
- [x] Create migration
- [x] Implement `POST /exercises` - create custom exercise
  - [x] Validate name uniqueness per user
  - [x] Set is_custom=true, user_id=current_user
- [x] Implement `PUT /exercises/{id}` - update custom exercise
  - [x] Only allow if is_custom=true and user is owner
- [x] Implement `DELETE /exercises/{id}` - delete custom exercise
  - [x] Only allow if is_custom=true and user is owner
  - [x] Check not used in any plans (or soft delete)
- [x] Update exercise list to include user's custom exercises
- [x] Add tests

### 2.6 Frontend: Add custom exercise creation
**Estimated: 2-3 hours**

- [ ] Add create/update/delete methods to exerciseService
- [ ] Create "Add Custom Exercise" button in exercise picker
- [ ] Create custom exercise form modal
  - [ ] Name input
  - [ ] Description textarea
  - [ ] Muscle groups multi-select
  - [ ] Equipment multi-select
- [ ] Allow editing/deleting custom exercises from exercise detail

---

## Priority 3: Nice-to-Have (Post-MVP)

### 3.1 Frontend: ProfileView improvements
**Estimated: 3-4 hours**

- [ ] Add collapsible sections
- [ ] Group equipment by category
- [ ] Add Change Password modal
  - [ ] Current password field
  - [ ] New password field
  - [ ] Confirm password field
- [ ] Add Danger Zone section
  - [ ] Delete Account button
  - [ ] Confirmation dialog with consequences
  - [ ] Soft delete API call

### 3.2 Backend: Add soft delete for users
**Estimated: 2 hours**

- [ ] Add `deleted_at` timestamp to User model
- [ ] Create migration
- [ ] Update DELETE /auth/me to set deleted_at instead of hard delete
- [ ] Exclude soft-deleted users from login
- [ ] Add data retention policy consideration

### 3.3 Frontend: History mini-calendar
**Estimated: 2-3 hours**

- [ ] Create MiniCalendar component
- [ ] Show current month with workout days highlighted
- [ ] Navigate between months
- [ ] Click date to filter history list

### 3.4 Frontend: Login "Remember me" checkbox
**Estimated: 1 hour**

- [ ] Add checkbox to LoginView
- [ ] Pass flag to login API
- [ ] Backend extends refresh token expiration (30 days vs 7 days)

### 3.5 Frontend: Update for new workout structure
**Estimated: 4-6 hours**

After backend restructure (1.1), update frontend:
- [ ] Update TypeScript types for nested workout structure
- [ ] Update PlanDetailView to show workouts with exercises
- [ ] Update PlanEditView for nested editing
- [ ] Update PlanImportView for nested structure
- [ ] Update ActiveWorkoutView to work with specific workout
- [ ] Update workoutPlanService response handling
- [ ] Update workout store

---

## Dependencies

```
1.1 (Backend restructure) 
  └── 3.5 (Frontend update for new structure)

1.2 (Backend is_active)
  └── 2.3 (Frontend active plan toggle)

2.1 (Backend name field)
  └── 2.2 (Frontend name field)

2.5 (Backend custom exercises)
  └── 2.6 (Frontend custom exercises)

3.2 (Backend soft delete)
  └── 3.1 (Frontend delete account)
```

---

## Recommended Implementation Order

**Phase 1: Backend Foundation**
1. 1.1 - Backend restructure (largest, blocks frontend work)
2. 1.2 - Backend is_active field
3. 2.1 - Backend name field
4. 2.5 - Backend custom exercises

**Phase 2: Frontend Critical**
5. 3.5 - Frontend update for new structure
6. 1.3 - Onboarding equipment selection
7. 1.4 - Stats view
8. 1.5 - localStorage persistence

**Phase 3: Frontend Features**
9. 2.2 - Registration name field
10. 2.3 - Active plan toggle
11. 2.4 - Session detail PRs
12. 2.6 - Custom exercise UI

**Phase 4: Polish (Post-MVP)**
13. 3.1 - Profile improvements
14. 3.2 - Backend soft delete
15. 3.3 - History calendar
16. 3.4 - Remember me

---

## Notes

- All backend changes require corresponding test updates
- Frontend changes should include loading states and error handling
- Run `docker-compose exec backend pytest` after backend changes
- Run `npm run lint` after frontend changes
- Charts in StatsView use simple CSS-based visualizations (no external chart library)
- User deletion is soft delete (sets deleted_at timestamp)

---

## Changelog

| Date | Item | Status | Notes |
|------|------|--------|-------|
| 2025-01-10 | Plan created | - | Initial gap analysis |
| 2025-01-10 | 1.1 Backend restructure | ✓ Completed | Workout hierarchy implemented |
| 2025-01-10 | 1.2 Backend is_active | ✓ Completed | Toggle endpoint added |
| 2025-01-10 | 2.1 Backend name field | ✓ Completed | User name with auth support |
| 2025-01-10 | 2.5 Backend custom exercises | ✓ Completed | CRUD with user ownership |
