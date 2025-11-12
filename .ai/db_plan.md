# Database Planning Summary - AllWorkouts MVP

## Overview
This document summarizes the database schema planning decisions for the AllWorkouts MVP, a strength training workout tracking application. The application uses PostgreSQL as the database with FastAPI backend and Vue 3 frontend.

---

## Conversation Summary

<conversation_summary>

<decisions>

1. **Exercise Sets Editability**: Exercise set records (`exercise_set`/`exercise_session`) should be mutable and editable to allow users to correct data entry errors. Include `updated_at` timestamp to track modifications.

2. **Equipment Linking Strategy**: Equipment should only be linked statically with global exercises. Do not save `equipment_id` in actual session data (`exercise_session`). Equipment is determined by the exercise chosen, not tracked separately during logging.

3. **Exercise Customization**: Do not implement user-specific custom exercises in the MVP. Use only a global `exercise` table shared across all users with static equipment links.

4. **Muscle Group Storage**: Store muscle groups as ARRAY of ENUM types directly in the `exercise` table with `primary_muscle_groups` and `secondary_muscle_groups` fields instead of using junction tables.

5. **Cascade Deletions**: Never use ON DELETE CASCADE. All deletion logic should be handled at the API layer with appropriate validation and error responses.

</decisions>

<matched_recommendations>

1. **User-Workout Plan Relationship**: Users should have a one-to-many relationship with workout plans to track ownership and maintain data isolation. Combined with RLS policies, this allows each user to access only their own data.

2. **Equipment Data Model**: Create a dedicated `equipment` reference table with many-to-many relationship to exercises through `exercise_equipment` junction table. Users define their available equipment via `user_equipment` junction table.

3. **Confidence Level Storage**: Store AI parsing confidence levels as an ENUM type (`confidence_level`) with values ('high', 'medium', 'low') in the `workout_exercise` entity during plan import.

4. **Exercise Sets Mutability**: Design `exercise_session` records as mutable with `created_at` and `updated_at` timestamps. Allow editing to support data correction without data loss.

5. **Workout Session Cardinality**: Design one-to-many relationship where one `workout_plan` has many `workout_session` instances (one per execution date). Each `workout_session` contains child `exercise_session` records that log actual performance.

6. **Personal Records Storage**: Create a `personal_record` table with denormalized PR data. Calculate PRs on every set log and update the table. Index by `user_id` and `exercise_id` for fast retrieval during workout logging.

7. **Incomplete Session Handling**: Add `status` ENUM field ('in_progress', 'completed', 'abandoned') to `workout_session` to track completion state explicitly.

8. **History Tracking Indexes**: Create composite indexes on `workout_session(user_id, status, created_at)` and `workout_session(user_id, created_at DESC)` for efficient pagination and filtering.

9. **Muscle Group Arrays with Indexing**: Store muscle groups as PostgreSQL ARRAY types with GIN indexes on `exercise.primary_muscle_groups` and `exercise.secondary_muscle_groups` to optimize substitution queries.

10. **Row-Level Security**: Implement RLS policies on all user-scoped tables (`workout_plan`, `workout_session`, `exercise_session`, `personal_record`) using user context filtering.

11. **Exercise Ordering**: Add `sequence` integer field to `workout_exercise` to preserve exercise order. Apply UNIQUE constraint on `(workout_plan_id, sequence)`.

12. **Equipment Substitution**: Equipment is statically linked to exercises. Users substitute entire exercises (not just equipment) to equivalent ones with same primary/secondary muscle groups using different equipment.

13. **Unit System Storage**: Add `unit_system` ENUM field ('metric', 'imperial') to `user` table. Store all measurements in database in consistent units (metric) and convert during API serialization.

14. **Global Exercise Table**: Create a global `exercise` table shared across all users for the MVP. No user-specific custom exercises.

15. **Rest Time Tracking**: Store `rest_time_seconds` in both `workout_exercise` (plan level default) and `exercise_session` (actual logged) to compare planned vs actual rest.

16. **Import Audit Logging**: Create `workout_import_log` table storing `user_id`, `raw_text`, `parsed_exercises` (JSONB), `confidence_scores` (JSONB), `created_at`, and `workout_plan_id` for debugging and audit purposes.

17. **Previous Workout Values**: No explicit relationship needed. Query previous `exercise_session` records using `exercise_id`, `user_id`, and `ORDER BY created_at DESC LIMIT 1`.

18. **Set Logging Flexibility**: No database enforcement of set logging order. Allow flexibility at data layer; implement UI guidance at application layer.

19. **Pagination Strategy**: Design all list endpoints with cursor-based or offset-based pagination. Use indexes on `(user_id, created_at DESC)` for efficient retrieval.

20. **Soft Deletes**: Implement soft deletes for `workout_plan` and `workout_session` with `deleted_at` timestamp to preserve historical data and support recovery.

21. **Exercise Name Uniqueness**: Add UNIQUE constraint on `exercise.name` at database level to ensure consistent exercise matching during AI parsing.

22. **Equipment Validation**: Create `equipment` reference table. Use `user_equipment` junction table with foreign key constraints to ensure data integrity.

23. **Workout Exercise Parameters**: Store `sets`, `reps_min`, `reps_max`, and `rest_time_seconds` in `workout_exercise` table as plan specifications per exercise.

24. **Plan Editing Relationships**: Use `workout_exercise` junction table with all necessary fields. Allow updates but preserve historical session data (no deletion of past records).

25. **Deletion Constraints**: Do not prevent deletion at database level. Use soft deletes and implement business logic warnings at API layer.

26. **Equipment in Sessions**: Do not store equipment data in `exercise_session`. Equipment is implicit through exercise selection.

27. **Future-Proofing**: Keep schema simple for MVP. Avoid overengineering for features like warm-up sets or supersets.

28. **Timestamp Strategy**: Add `created_at` (immutable) and `updated_at` (mutable) to all user-scoped tables. Use indexed `created_at` for chronological querying.

29. **Personal Record Structure**: Single `personal_record` table with `record_type` ENUM ('1rm', 'set_volume', 'total_volume'), including `exercise_session_id` foreign key to link to achieving set.

30. **Concurrency Control**: Use PostgreSQL row-level locking at application layer. Implement optimistic locking using `version` or `updated_at` fields.

31. **Exercise Defaults**: Store `default_weight`, `default_reps`, and `default_rest_time_seconds` in global `exercise` table as baseline values.

32. **Substitution Validation**: At application layer, query exercises with matching `primary_muscle_groups` array values. Enforce as business logic, not database constraint.

33. **Substitution Tracking**: No separate substitution tracking table. Track implicitly by comparing `workout_exercise.exercise_id` with `exercise_session.exercise_id`.

34. **Equipment Validation**: During plan creation, validate via API that all exercises have equipment user owns through `exercise_equipment` and `user_equipment` join.

35. **Equipment Removal Handling**: No database constraints. At API level, validate during workout logging and display warnings if equipment removed. Use soft-deletion for `user_equipment`.

36. **Muscle Group Normalization**: Create `muscle_group_enum` type with all valid values. Store as ARRAY fields in `exercise` table, not junction tables.

37. **Foreign Key Constraints**: Apply NOT NULL constraints to required foreign keys. Use explicit foreign key constraints WITHOUT ON DELETE CASCADE. Handle deletions at API layer.

38. **Bodyweight Exercises**: Create special `equipment` record with `name = 'Bodyweight'`. Link bodyweight exercises to this equipment for consistency.

39. **Equipment Change Handling**: Validate at API layer during workout logging. Allow substitution if equipment unavailable; prevent logging with appropriate warnings.

40. **Exercise Data Denormalization**: No denormalization for MVP. Store only `exercise_id` in `workout_exercise`. Accept that global exercise modifications affect historical plans.

41. **Range Validation**: Store ranges in `workout_exercise`. No database constraints on actual logged values in `exercise_session`. Validate at API layer but allow flexible logging.

42. **PR Achievement Tracking**: Include `exercise_session_id` and `achieved_at` in `personal_record` to link records to specific sets that achieved them.

</matched_recommendations>

<database_planning_summary>

## Database Planning Summary

### Core Requirements

The AllWorkouts MVP requires a PostgreSQL database schema that supports:

1. **User Management**: Email-based authentication with unit preferences (metric/imperial) and equipment availability
2. **Workout Plan Management**: AI-powered text parsing, exercise matching with confidence levels, and CRUD operations
3. **Workout Logging**: Set/rep/weight recording, rest timers, previous workout value display, and PR tracking (1RM, set volume, total volume)
4. **History Tracking**: Chronological workout list with filtering by completion status and workout name

### Key Entities and Relationships

#### Reference Data (Global)
- **`equipment`**: Global equipment catalog (id, name, description)
- **`muscle_group_enum`**: PostgreSQL ENUM type defining all muscle groups (chest, back, shoulders, legs, etc.)
- **`exercise`**: Global exercise database with:
  - Static equipment links (via `exercise_equipment` junction table)
  - `primary_muscle_groups` and `secondary_muscle_groups` as ARRAY of muscle_group_enum
  - Default values: `default_weight`, `default_reps`, `default_rest_time_seconds`
  - UNIQUE constraint on name

#### User Data
- **`user`**: User accounts with `unit_system` ENUM ('metric', 'imperial')
- **`user_equipment`**: Junction table linking users to available equipment (with soft delete support)

#### Workout Planning
- **`workout_plan`**: User-owned workout templates
  - One-to-many with user
  - Soft delete support (`deleted_at`)
  - RLS policies for user isolation
  
- **`workout_exercise`**: Exercises within a plan
  - Links to global `exercise` table
  - Fields: `sequence`, `sets`, `reps_min`, `reps_max`, `rest_time_seconds`
  - UNIQUE constraint on `(workout_plan_id, sequence)`
  - `confidence_level` ENUM ('high', 'medium', 'low') from AI parsing

#### Workout Execution
- **`workout_session`**: Individual workout executions
  - One-to-many relationship with `workout_plan`
  - `status` ENUM ('in_progress', 'completed', 'abandoned')
  - Soft delete support
  - RLS policies for user isolation
  
- **`exercise_session`**: Individual logged sets
  - Links to `workout_session` and `exercise`
  - Fields: `reps`, `weight`, `rest_time_seconds`
  - Mutable/editable records
  - No equipment tracking (implicit through exercise)

#### Performance Tracking
- **`personal_record`**: Denormalized PR storage
  - Fields: `user_id`, `exercise_id`, `record_type` ENUM ('1rm', 'set_volume', 'total_volume')
  - Links to achieving set: `exercise_session_id`, `achieved_at`
  - Calculated and updated on every set log
  - Indexed on `(user_id, exercise_id)` for fast retrieval

#### Audit & Debugging
- **`workout_import_log`**: AI parsing audit trail
  - Stores: `raw_text`, `parsed_exercises` (JSONB), `confidence_scores` (JSONB)
  - Links to resulting `workout_plan_id`

### Key Design Decisions

#### Equipment Strategy
- Equipment is **statically linked** to global exercises only
- No equipment tracking in session data
- Exercise substitution (not equipment substitution) for different equipment availability
- Bodyweight exercises linked to special "Bodyweight" equipment record

#### Muscle Group Modeling
- PostgreSQL ARRAY types instead of junction tables
- Separate arrays for primary and secondary muscle groups
- GIN indexes on arrays for efficient substitution queries (`@>` and `&&` operators)

#### Deletion Strategy
- **No CASCADE deletions** - all handled at API layer
- Soft deletes for `workout_plan`, `workout_session`, `user_equipment`
- API validates dependencies before deletion (409 Conflict if issues)

#### Data Mutability
- Exercise sessions are **editable** (not immutable)
- Include `updated_at` timestamps for audit
- Previous workout values queried dynamically, not pre-stored

#### Security & Isolation
- Row-Level Security (RLS) on all user-scoped tables
- Policy: SELECT/INSERT/UPDATE/DELETE only when `user_id = current_user_id`
- Foreign key constraints WITHOUT cascade (API-managed)

#### Performance Optimizations
- Composite indexes: `(user_id, status, created_at)`, `(user_id, created_at DESC)`
- GIN indexes on muscle group arrays
- PR table denormalization for fast lookup
- Cursor-based pagination support

#### Data Integrity
- NOT NULL constraints on required foreign keys
- UNIQUE constraints: `exercise.name`, `(workout_plan_id, sequence)`
- Foreign key constraints without cascades
- Unit system enforcement at API layer (store metric, convert on serialization)

### Timestamp Strategy
All user-scoped tables include:
- `created_at`: Immutable, set at creation, indexed for chronological queries
- `updated_at`: Mutable, updated on modification

### Validation Approach
- **Database Level**: Foreign keys, NOT NULL, UNIQUE constraints, ENUM types
- **API Level**: Equipment availability, muscle group matching, range validation, deletion dependencies
- **No Database Level**: Set logging order, rep/weight ranges, substitution rules

</database_planning_summary>

<unresolved_issues>

None identified. All key decisions have been made for the MVP schema. The schema is designed to be simple, maintainable, and expandable for future features without requiring major restructuring.

</unresolved_issues>

</conversation_summary>

---

## Next Steps

1. Create initial Alembic migration (version 001) with core schema
2. Create seed migrations for reference data (`equipment`, `muscle_group_enum`, base `exercise` catalog)
3. Implement RLS policies on user-scoped tables
4. Create database indexes as specified
5. Implement API layer validation logic
6. Test concurrency control and optimistic locking
7. Verify equipment validation and substitution queries

---

## Schema Tables Summary

### Core Tables
1. `user` - User accounts and preferences
2. `equipment` - Global equipment catalog
3. `exercise` - Global exercise database
4. `exercise_equipment` - Exercise-equipment junction
5. `user_equipment` - User-equipment junction
6. `workout_plan` - User workout templates
7. `workout_exercise` - Exercises in plans
8. `workout_session` - Workout executions
9. `exercise_session` - Individual logged sets
10. `personal_record` - PR tracking
11. `workout_import_log` - Import audit trail

### PostgreSQL Types
1. `muscle_group_enum` - Muscle group values
2. `unit_system_enum` - 'metric' | 'imperial'
3. `confidence_level_enum` - 'high' | 'medium' | 'low'
4. `session_status_enum` - 'in_progress' | 'completed' | 'abandoned'
5. `record_type_enum` - '1rm' | 'set_volume' | 'total_volume'
