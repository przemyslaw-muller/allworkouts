# AllWorkouts PostgreSQL Database Schema

## Overview
This document defines the complete PostgreSQL database schema for AllWorkouts MVP. The schema supports user authentication, workout plan management, exercise logging, and performance tracking with row-level security (RLS) policies for data isolation.
This expands on @.ai/db_plan.md

---

## PostgreSQL Custom Types

### ENUM Types

```sql
-- Muscle group enumeration
CREATE TYPE muscle_group_enum AS ENUM (
  'chest',
  'back',
  'shoulders',
  'biceps',
  'triceps',
  'forearms',
  'legs',
  'glutes',
  'core',
  'traps',
  'lats'
);

-- Unit system preference
CREATE TYPE unit_system_enum AS ENUM (
  'metric',
  'imperial'
);

-- AI parsing confidence level
CREATE TYPE confidence_level_enum AS ENUM (
  'high',
  'medium',
  'low'
);

-- Workout session status
CREATE TYPE session_status_enum AS ENUM (
  'in_progress',
  'completed',
  'abandoned'
);

-- Personal record type
CREATE TYPE record_type_enum AS ENUM (
  '1rm',
  'set_volume',
  'total_volume'
);
```

---

## Table Definitions

### 1. User Table
Stores user account information and preferences.

```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  unit_system unit_system_enum NOT NULL DEFAULT 'metric',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON "user"(email);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `email`: User email address (unique, required)
- `password_hash`: Hashed password (required)
- `unit_system`: Unit preference ('metric' or 'imperial', default 'metric')
- `created_at`: Account creation timestamp (immutable)
- `updated_at`: Last modification timestamp

**Constraints:**
- Primary Key: `id`
- Unique: `email`
- Not Null: `email`, `password_hash`, `unit_system`

**Indexes:**
- `idx_user_email`: For fast email lookups during authentication

---

### 2. Equipment Table
Global reference table for all available equipment.

```sql
CREATE TABLE equipment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_name ON equipment(name);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `name`: Equipment name (unique, required)
- `description`: Optional equipment description
- `created_at`: Creation timestamp

**Constraints:**
- Primary Key: `id`
- Unique: `name`
- Not Null: `name`

**Indexes:**
- `idx_equipment_name`: For fast equipment lookups

**Special Records:**
- A 'Bodyweight' equipment record should be created for bodyweight exercises

---

### 3. Exercise Table
Global exercise database with muscle groups and default parameters.

```sql
CREATE TABLE exercise (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL UNIQUE,
  primary_muscle_groups muscle_group_enum[] NOT NULL,
  secondary_muscle_groups muscle_group_enum[] DEFAULT '{}',
  default_weight NUMERIC(10, 2),
  default_reps INTEGER,
  default_rest_time_seconds INTEGER,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exercise_name ON exercise(name);
CREATE INDEX idx_exercise_primary_muscle_groups ON exercise USING GIN(primary_muscle_groups);
CREATE INDEX idx_exercise_secondary_muscle_groups ON exercise USING GIN(secondary_muscle_groups);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `name`: Exercise name (unique, required)
- `primary_muscle_groups`: Array of primary muscle groups (required)
- `secondary_muscle_groups`: Array of secondary muscle groups (default empty)
- `default_weight`: Default weight in metric units (nullable)
- `default_reps`: Default reps (nullable)
- `default_rest_time_seconds`: Default rest time (nullable)
- `description`: Optional exercise description
- `created_at`: Creation timestamp (immutable)
- `updated_at`: Last modification timestamp

**Constraints:**
- Primary Key: `id`
- Unique: `name`
- Not Null: `name`, `primary_muscle_groups`

**Indexes:**
- `idx_exercise_name`: For exercise lookups
- `idx_exercise_primary_muscle_groups`: GIN index for muscle group containment queries
- `idx_exercise_secondary_muscle_groups`: GIN index for muscle group containment queries

---

### 4. Exercise Equipment Junction Table
Links exercises to required equipment (many-to-many).

```sql
CREATE TABLE exercise_equipment (
  exercise_id UUID NOT NULL REFERENCES exercise(id),
  equipment_id UUID NOT NULL REFERENCES equipment(id),
  PRIMARY KEY (exercise_id, equipment_id)
);

CREATE INDEX idx_exercise_equipment_equipment_id ON exercise_equipment(equipment_id);
```

**Columns:**
- `exercise_id`: Foreign key to exercise (part of composite key)
- `equipment_id`: Foreign key to equipment (part of composite key)

**Constraints:**
- Primary Key: `(exercise_id, equipment_id)`
- Foreign Keys (no cascade):
  - `exercise_id` → `exercise.id`
  - `equipment_id` → `equipment.id`

**Indexes:**
- Composite PK index handles exercise_id lookups
- `idx_exercise_equipment_equipment_id`: For reverse lookups

---

### 5. User Equipment Junction Table
Links users to their available equipment (many-to-many, with soft delete).

```sql
CREATE TABLE user_equipment (
  user_id UUID NOT NULL REFERENCES "user"(id),
  equipment_id UUID NOT NULL REFERENCES equipment(id),
  deleted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, equipment_id)
);

CREATE INDEX idx_user_equipment_user_id ON user_equipment(user_id)
  WHERE deleted_at IS NULL;
CREATE INDEX idx_user_equipment_equipment_id ON user_equipment(equipment_id);
```

**Columns:**
- `user_id`: Foreign key to user (part of composite key)
- `equipment_id`: Foreign key to equipment (part of composite key)
- `deleted_at`: Soft delete timestamp (nullable)
- `created_at`: Creation timestamp

**Constraints:**
- Primary Key: `(user_id, equipment_id)`
- Foreign Keys (no cascade):
  - `user_id` → `user.id`
  - `equipment_id` → `equipment.id`

**Indexes:**
- Composite PK index
- `idx_user_equipment_user_id`: Partial index for active records
- `idx_user_equipment_equipment_id`: For reverse lookups

---

### 6. Workout Plan Table
User-owned workout plan templates with soft delete support.

```sql
CREATE TABLE workout_plan (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  deleted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_plan_user_id ON workout_plan(user_id)
  WHERE deleted_at IS NULL;
CREATE INDEX idx_workout_plan_created_at ON workout_plan(user_id, created_at DESC);
CREATE INDEX idx_workout_plan_name ON workout_plan(user_id, name)
  WHERE deleted_at IS NULL;
```

**Columns:**
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to user (required)
- `name`: Workout plan name (required)
- `description`: Optional plan description
- `deleted_at`: Soft delete timestamp (nullable)
- `created_at`: Creation timestamp (immutable)
- `updated_at`: Last modification timestamp

**Constraints:**
- Primary Key: `id`
- Foreign Key (no cascade):
  - `user_id` → `user.id`
- Not Null: `user_id`, `name`

**Indexes:**
- `idx_workout_plan_user_id`: Partial index for active plans by user
- `idx_workout_plan_created_at`: For chronological ordering
- `idx_workout_plan_name`: For plan name search

**RLS Policy:**
```sql
CREATE POLICY workout_plan_rls ON workout_plan
  USING (user_id = current_user_id);
```

---

### 7. Workout Exercise Junction Table
Exercises within a specific workout plan with plan-specific parameters.

```sql
CREATE TABLE workout_exercise (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workout_plan_id UUID NOT NULL REFERENCES workout_plan(id),
  exercise_id UUID NOT NULL REFERENCES exercise(id),
  sequence INTEGER NOT NULL,
  sets INTEGER NOT NULL,
  reps_min INTEGER NOT NULL,
  reps_max INTEGER NOT NULL,
  rest_time_seconds INTEGER,
  confidence_level confidence_level_enum NOT NULL DEFAULT 'medium',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (workout_plan_id, sequence)
);

CREATE INDEX idx_workout_exercise_workout_plan_id ON workout_exercise(workout_plan_id);
CREATE INDEX idx_workout_exercise_exercise_id ON workout_exercise(exercise_id);
CREATE INDEX idx_workout_exercise_sequence ON workout_exercise(workout_plan_id, sequence);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `workout_plan_id`: Foreign key to workout plan (required)
- `exercise_id`: Foreign key to exercise (required)
- `sequence`: Order within the plan (required)
- `sets`: Number of sets (required)
- `reps_min`: Minimum reps target (required)
- `reps_max`: Maximum reps target (required)
- `rest_time_seconds`: Planned rest between sets (nullable)
- `confidence_level`: AI parsing confidence ('high', 'medium', 'low', default 'medium')
- `created_at`: Creation timestamp (immutable)
- `updated_at`: Last modification timestamp

**Constraints:**
- Primary Key: `id`
- Foreign Keys (no cascade):
  - `workout_plan_id` → `workout_plan.id`
  - `exercise_id` → `exercise.id`
- Unique: `(workout_plan_id, sequence)`
- Not Null: `workout_plan_id`, `exercise_id`, `sequence`, `sets`, `reps_min`, `reps_max`, `confidence_level`

**Indexes:**
- `idx_workout_exercise_workout_plan_id`: For plan exercises
- `idx_workout_exercise_exercise_id`: For exercise lookups
- `idx_workout_exercise_sequence`: For ordered retrieval

---

### 8. Workout Session Table
Individual workout execution records with status tracking.

```sql
CREATE TABLE workout_session (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id),
  workout_plan_id UUID NOT NULL REFERENCES workout_plan(id),
  status session_status_enum NOT NULL DEFAULT 'in_progress',
  deleted_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_session_user_id ON workout_session(user_id)
  WHERE deleted_at IS NULL;
CREATE INDEX idx_workout_session_user_status_created ON workout_session(user_id, status, created_at DESC)
  WHERE deleted_at IS NULL;
CREATE INDEX idx_workout_session_user_created ON workout_session(user_id, created_at DESC)
  WHERE deleted_at IS NULL;
CREATE INDEX idx_workout_session_workout_plan_id ON workout_session(workout_plan_id);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to user (required)
- `workout_plan_id`: Foreign key to workout plan (required)
- `status`: Workout status ('in_progress', 'completed', 'abandoned', default 'in_progress')
- `deleted_at`: Soft delete timestamp (nullable)
- `created_at`: Session start timestamp (immutable)
- `updated_at`: Last modification timestamp

**Constraints:**
- Primary Key: `id`
- Foreign Keys (no cascade):
  - `user_id` → `user.id`
  - `workout_plan_id` → `workout_plan.id`
- Not Null: `user_id`, `workout_plan_id`, `status`

**Indexes:**
- `idx_workout_session_user_id`: Partial index for user's active sessions
- `idx_workout_session_user_status_created`: Composite for filtering and pagination
- `idx_workout_session_user_created`: For chronological ordering
- `idx_workout_session_workout_plan_id`: For plan lookups

**RLS Policy:**
```sql
CREATE POLICY workout_session_rls ON workout_session
  USING (user_id = current_user_id);
```

---

### 9. Exercise Session Table
Individual logged sets within a workout session (mutable records).

```sql
CREATE TABLE exercise_session (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workout_session_id UUID NOT NULL REFERENCES workout_session(id),
  exercise_id UUID NOT NULL REFERENCES exercise(id),
  weight NUMERIC(10, 2) NOT NULL,
  reps INTEGER NOT NULL,
  rest_time_seconds INTEGER,
  set_number INTEGER NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exercise_session_workout_session_id ON exercise_session(workout_session_id);
CREATE INDEX idx_exercise_session_exercise_id ON exercise_session(exercise_id);
CREATE INDEX idx_exercise_session_user_exercise ON exercise_session(workout_session_id, exercise_id);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `workout_session_id`: Foreign key to workout session (required)
- `exercise_id`: Foreign key to exercise (required)
- `weight`: Weight lifted in metric units (required)
- `reps`: Number of repetitions (required)
- `rest_time_seconds`: Actual rest taken (nullable)
- `set_number`: Set sequence within the exercise (required)
- `created_at`: Log creation timestamp (immutable)
- `updated_at`: Last modification timestamp (mutable)

**Constraints:**
- Primary Key: `id`
- Foreign Keys (no cascade):
  - `workout_session_id` → `workout_session.id`
  - `exercise_id` → `exercise.id`
- Not Null: `workout_session_id`, `exercise_id`, `weight`, `reps`, `set_number`

**Indexes:**
- `idx_exercise_session_workout_session_id`: For session exercises
- `idx_exercise_session_exercise_id`: For exercise lookups
- `idx_exercise_session_user_exercise`: For previous workout queries

**RLS Policy:**
```sql
CREATE POLICY exercise_session_rls ON exercise_session
  USING (
    EXISTS (
      SELECT 1 FROM workout_session ws
      WHERE ws.id = workout_session_id
      AND ws.user_id = current_user_id
    )
  );
```

---

### 10. Personal Record Table
Denormalized personal record tracking for fast retrieval.

```sql
CREATE TABLE personal_record (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id),
  exercise_id UUID NOT NULL REFERENCES exercise(id),
  record_type record_type_enum NOT NULL,
  value NUMERIC(10, 2) NOT NULL,
  unit VARCHAR(10),
  exercise_session_id UUID NOT NULL REFERENCES exercise_session(id),
  achieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, exercise_id, record_type)
);

CREATE INDEX idx_personal_record_user_exercise ON personal_record(user_id, exercise_id);
CREATE INDEX idx_personal_record_user_id ON personal_record(user_id);
CREATE INDEX idx_personal_record_achieved_at ON personal_record(user_id, achieved_at DESC);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to user (required)
- `exercise_id`: Foreign key to exercise (required)
- `record_type`: PR type ('1rm', 'set_volume', 'total_volume', required)
- `value`: PR value (required)
- `unit`: Unit of measurement (nullable)
- `exercise_session_id`: Foreign key to the set that achieved the record (required)
- `achieved_at`: Timestamp when record was achieved (required)
- `created_at`: Record creation timestamp (immutable)
- `updated_at`: Last modification timestamp

**Constraints:**
- Primary Key: `id`
- Foreign Keys (no cascade):
  - `user_id` → `user.id`
  - `exercise_id` → `exercise.id`
  - `exercise_session_id` → `exercise_session.id`
- Unique: `(user_id, exercise_id, record_type)`
- Not Null: `user_id`, `exercise_id`, `record_type`, `value`, `exercise_session_id`, `achieved_at`

**Indexes:**
- `idx_personal_record_user_exercise`: For PR lookups during logging
- `idx_personal_record_user_id`: For user's all PRs
- `idx_personal_record_achieved_at`: For PR history ordering

**RLS Policy:**
```sql
CREATE POLICY personal_record_rls ON personal_record
  USING (user_id = current_user_id);
```

---

### 11. Workout Import Log Table
Audit trail for AI parsing and import history.

```sql
CREATE TABLE workout_import_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id),
  workout_plan_id UUID REFERENCES workout_plan(id),
  raw_text TEXT NOT NULL,
  parsed_exercises JSONB,
  confidence_scores JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_import_log_user_id ON workout_import_log(user_id);
CREATE INDEX idx_workout_import_log_workout_plan_id ON workout_import_log(workout_plan_id);
CREATE INDEX idx_workout_import_log_created_at ON workout_import_log(user_id, created_at DESC);
```

**Columns:**
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to user (required)
- `workout_plan_id`: Foreign key to workout plan (nullable, set after successful import)
- `raw_text`: Raw input text (required)
- `parsed_exercises`: Parsed exercises as JSONB (nullable)
- `confidence_scores`: Confidence scores as JSONB (nullable)
- `created_at`: Log creation timestamp

**Constraints:**
- Primary Key: `id`
- Foreign Keys (no cascade):
  - `user_id` → `user.id`
  - `workout_plan_id` → `workout_plan.id` (optional)
- Not Null: `user_id`, `raw_text`

**Indexes:**
- `idx_workout_import_log_user_id`: For user's import history
- `idx_workout_import_log_workout_plan_id`: For tracing imports to plans
- `idx_workout_import_log_created_at`: For chronological import history

**RLS Policy:**
```sql
CREATE POLICY workout_import_log_rls ON workout_import_log
  USING (user_id = current_user_id);
```

---

## Row-Level Security (RLS) Policies

RLS policies enforce user data isolation at the database level. The following policies should be enabled:

### Enable RLS on All User-Scoped Tables

```sql
ALTER TABLE workout_plan ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_session ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_session ENABLE ROW LEVEL SECURITY;
ALTER TABLE personal_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_import_log ENABLE ROW LEVEL SECURITY;
```

### Policy Implementations

```sql
-- Workout Plan: Users can only access their own plans
CREATE POLICY workout_plan_user_isolation ON workout_plan
  FOR ALL
  USING (user_id = current_user_id)
  WITH CHECK (user_id = current_user_id);

-- Workout Session: Users can only access their own sessions
CREATE POLICY workout_session_user_isolation ON workout_session
  FOR ALL
  USING (user_id = current_user_id)
  WITH CHECK (user_id = current_user_id);

-- Exercise Session: Users can only access exercises from their sessions
CREATE POLICY exercise_session_user_isolation ON exercise_session
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM workout_session ws
      WHERE ws.id = workout_session_id
      AND ws.user_id = current_user_id
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM workout_session ws
      WHERE ws.id = workout_session_id
      AND ws.user_id = current_user_id
    )
  );

-- Personal Record: Users can only access their own records
CREATE POLICY personal_record_user_isolation ON personal_record
  FOR ALL
  USING (user_id = current_user_id)
  WITH CHECK (user_id = current_user_id);

-- Workout Import Log: Users can only access their own import logs
CREATE POLICY workout_import_log_user_isolation ON workout_import_log
  FOR ALL
  USING (user_id = current_user_id)
  WITH CHECK (user_id = current_user_id);
```

---

## Indexes Summary

### Primary Key Indexes (Implicit)
All tables have implicit B-tree indexes on their primary key columns.

### User Table
- `idx_user_email`: Email lookup for authentication

### Equipment Table
- `idx_equipment_name`: Equipment name lookup

### Exercise Table
- `idx_exercise_name`: Exercise name lookup
- `idx_exercise_primary_muscle_groups`: GIN index for primary muscle group queries
- `idx_exercise_secondary_muscle_groups`: GIN index for secondary muscle group queries

### Exercise Equipment Table
- Composite PK index for exercise_id lookups
- `idx_exercise_equipment_equipment_id`: Reverse lookup by equipment

### User Equipment Table
- Composite PK index for user_id lookups
- `idx_user_equipment_user_id`: Partial index (active records only)
- `idx_user_equipment_equipment_id`: Reverse lookup by equipment

### Workout Plan Table
- `idx_workout_plan_user_id`: Partial index for user's active plans
- `idx_workout_plan_created_at`: Chronological ordering
- `idx_workout_plan_name`: Plan name search

### Workout Exercise Table
- `idx_workout_exercise_workout_plan_id`: Plan exercises
- `idx_workout_exercise_exercise_id`: Exercise lookups
- `idx_workout_exercise_sequence`: Ordered sequence

### Workout Session Table
- `idx_workout_session_user_id`: Partial index for user's active sessions
- `idx_workout_session_user_status_created`: Composite for filtering and pagination
- `idx_workout_session_user_created`: Chronological ordering
- `idx_workout_session_workout_plan_id`: Plan sessions

### Exercise Session Table
- `idx_exercise_session_workout_session_id`: Session exercises
- `idx_exercise_session_exercise_id`: Exercise lookups
- `idx_exercise_session_user_exercise`: Previous workout queries

### Personal Record Table
- `idx_personal_record_user_exercise`: PR lookups
- `idx_personal_record_user_id`: User's all PRs
- `idx_personal_record_achieved_at`: PR history ordering

### Workout Import Log Table
- `idx_workout_import_log_user_id`: User's import history
- `idx_workout_import_log_workout_plan_id`: Import to plan tracing
- `idx_workout_import_log_created_at`: Chronological history

---

## Relationships Summary

### One-to-Many Relationships
1. **User → Workout Plan**: A user has many workout plans
2. **User → Workout Session**: A user has many workout sessions
3. **User → Personal Record**: A user has many personal records
4. **User → Workout Import Log**: A user has many import logs
5. **Workout Plan → Workout Session**: A plan has many sessions
6. **Workout Plan → Workout Exercise**: A plan has many exercises
7. **Workout Session → Exercise Session**: A session has many logged sets

### Many-to-Many Relationships
1. **Exercise ↔ Equipment** (via `exercise_equipment`): Exercises require multiple equipment
2. **User ↔ Equipment** (via `user_equipment`): Users own multiple equipment

### Foreign Keys (No Cascade Deletions)
All foreign key constraints are defined without `ON DELETE CASCADE`. Deletion logic is handled at the API layer to maintain referential integrity and prevent data loss.

---

## Data Integrity & Validation

### Database-Level Constraints
- **NOT NULL**: Applied to all required fields
- **UNIQUE**:
  - `user.email`: Email uniqueness
  - `exercise.name`: Exercise name uniqueness
  - `workout_exercise.(workout_plan_id, sequence)`: Exercise sequence uniqueness
  - `personal_record.(user_id, exercise_id, record_type)`: One PR per type per exercise
- **FOREIGN KEYS**: All cross-table references with NO CASCADE
- **ENUM TYPES**: Enforce valid values for categorical data

### API-Level Validation
The following validations are enforced at the API layer:
- **Reps/Weight Ranges**: Allow flexible logging outside plan ranges
- **Equipment Availability**: Validate user has required equipment
- **Muscle Group Matching**: Query for equivalent exercises by muscle groups
- **Deletion Dependencies**: Check for related records before deletion
- **Substitution Rules**: Validate exercise substitutions match muscle groups

### Soft Deletes
- **Workout Plan**: `deleted_at` timestamp preserves historical sessions
- **Workout Session**: `deleted_at` timestamp preserves session data
- **User Equipment**: `deleted_at` timestamp tracks removed equipment

Queries should filter: `WHERE deleted_at IS NULL` for active records.

---

## Design Notes & Rationale

### Muscle Groups as Arrays (Not Junction Tables)
- PostgreSQL ARRAY types with GIN indexing enable efficient containment queries
- Simpler schema with fewer joins
- Reduces query complexity for exercise substitution (matching primary muscle groups)
- GIN indexes support `@>` (contains) and `&&` (overlap) operators

### Exercise Session Mutability
- Records are mutable with `updated_at` timestamps for audit trails
- Users can correct data entry errors without losing history
- Simpler than creating correction records
- PRs are recalculated on updates

### No Cascade Deletions
- Preserves data integrity and prevents accidental data loss
- Allows soft deletes for historical tracking
- Forces API layer to handle dependency validation
- Provides explicit error messages to users

### Personal Record Denormalization
- Pre-calculated and stored for O(1) retrieval during workout logging
- Updated on every set log
- Significantly faster than aggregate queries on large datasets
- Unique constraint ensures only one PR per type per exercise

### Soft Deletes with Partial Indexes
- Partial indexes on `WHERE deleted_at IS NULL` optimize active record queries
- Historical data preserved for audit and PR calculations
- Soft-deleted records can be recovered if needed

### RLS Policies
- Policy-based user isolation at database level
- Prevents cross-user data access even with compromised API
- Works with PostgreSQL row security model
- Requires application to set `current_user_id` via security context

### No Equipment Tracking in Sessions
- Equipment is a static property of exercises
- Simplifies session data model
- Eliminates equipment availability validation during logging
- Users substitute exercises (not just equipment) to use different equipment

### GIN Indexes on Arrays
- Efficient for containment queries (`@>`) during exercise substitution
- O(log n) lookup for array element membership
- Better than junction tables for read-heavy muscle group matching

### Composite Indexes for Pagination
- `(user_id, created_at DESC)` enables efficient chronological queries
- `(user_id, status, created_at)` supports filtering by status
- Partial indexes on `deleted_at IS NULL` reduce index size

---

## Sequence of Table Creation

1. Create ENUM types (first, no dependencies)
2. Create reference tables: `user`, `equipment`
3. Create `exercise` with muscle group arrays
4. Create junction tables: `exercise_equipment`, `user_equipment`
5. Create workout planning tables: `workout_plan`, `workout_exercise`
6. Create workout execution tables: `workout_session`, `exercise_session`
7. Create `personal_record` table
8. Create `workout_import_log` table
9. Enable RLS on user-scoped tables
10. Create RLS policies
11. Seed reference data: `equipment`, base `exercise` catalog

---

## Migration Strategy

Using Alembic for database migrations:

1. **Initial Migration (v001)**: Create all tables, indexes, and ENUM types
2. **Seed Migration (v002)**: Insert reference data
   - Equipment catalog
   - Common exercises with muscle groups
3. **RLS Migration (v003)**: Enable RLS and create policies

Each migration should be reversible and tested independently.

---

## Future Extensibility

The schema is designed for simple MVP requirements while maintaining extensibility:

- **Warm-up Sets**: Add `is_warmup` boolean to `exercise_session` without schema migration
- **Supersets**: Add `superset_group_id` to `exercise_session` without major changes
- **Custom Exercises**: Create `user_exercise` table mirroring `exercise` structure
- **Exercise Progression**: Add `progression_level` or variant tracking
- **Advanced Analytics**: JSONB columns in `exercise_session` for extensible data
- **Media**: Add `media_url` fields or separate media tables

The current schema avoids premature optimization while providing solid foundations for growth.
