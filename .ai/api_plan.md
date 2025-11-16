# REST API Plan - AllWorkouts

## Overview

This document defines the REST API endpoints for AllWorkouts based on:
- Database schema (`.ai/db_structure.md`)
- Product requirements (`.ai/prd.md`)
- Tech stack (FastAPI, PostgreSQL)

## Authentication

All endpoints except `/auth/register` and `/auth/login` require JWT authentication via Bearer token in Authorization header.

### Auth Endpoints

#### POST /api/v1/auth/register
Create new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2025-01-15T10:00:00Z"
    },
    "access_token": "jwt_token",
    "refresh_token": "jwt_refresh_token"
  },
  "error": null
}
```

**Validation:**
- Email: valid format, unique
- Password: min 8 chars
- Name: 1-100 chars

#### POST /api/v1/auth/login
Authenticate user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "access_token": "jwt_token",
    "refresh_token": "jwt_refresh_token"
  },
  "error": null
}
```

#### POST /api/v1/auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "new_jwt_token"
  },
  "error": null
}
```

---

## Equipment

### GET /api/v1/equipment
List all available equipment.

**Query params:**
- `search` (optional): Filter by name
- `user_owned` (optional): Filter by user ownership (true/false)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Barbell",
      "category": "free_weights",
      "is_user_owned": true
    }
  ],
  "error": null
}
```

### POST /api/v1/equipment
Create custom equipment (admin/future feature).

**Request:**
```json
{
  "name": "Resistance Band",
  "category": "other"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Resistance Band",
    "category": "other"
  },
  "error": null
}
```

### PUT /api/v1/equipment/{equipment_id}/ownership
Mark equipment as owned/not owned by user.

**Request:**
```json
{
  "is_owned": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "equipment_id": "uuid",
    "is_owned": true
  },
  "error": null
}
```

---

## Exercises

### GET /api/v1/exercises
List exercises with filtering.

**Query params:**
- `search` (optional): Search by name
- `muscle_group` (optional): Filter by muscle group enum value
- `equipment_id` (optional): Filter by required equipment
- `user_can_perform` (optional): Filter by user's owned equipment (true/false)
- `page` (default: 1): Page number
- `limit` (default: 50): Items per page

**Response (200):**
```json
{
  "success": true,
  "data": {
    "exercises": [
      {
        "id": "uuid",
        "name": "Barbell Squat",
        "description": "Compound lower body exercise",
        "muscle_groups": ["quadriceps", "glutes"],
        "equipment": [
          {
            "id": "uuid",
            "name": "Barbell",
            "category": "free_weights"
          }
        ],
        "video_url": "https://...",
        "is_custom": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 150,
      "total_pages": 3
    }
  },
  "error": null
}
```

### GET /api/v1/exercises/{exercise_id}
Get single exercise details.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Barbell Squat",
    "description": "Compound lower body exercise",
    "muscle_groups": ["quadriceps", "glutes"],
    "equipment": [...],
    "video_url": "https://...",
    "is_custom": false,
    "personal_records": [
      {
        "id": "uuid",
        "record_type": "one_rep_max",
        "value": 225.0,
        "unit": "lbs",
        "achieved_at": "2025-01-10T14:30:00Z"
      }
    ]
  },
  "error": null
}
```

### POST /api/v1/exercises
Create custom exercise.

**Request:**
```json
{
  "name": "Bulgarian Split Squat",
  "description": "Single leg exercise",
  "muscle_groups": ["quadriceps", "glutes"],
  "equipment_ids": ["uuid1", "uuid2"],
  "video_url": "https://..."
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Bulgarian Split Squat",
    "is_custom": true,
    "user_id": "uuid",
    "created_at": "2025-01-15T10:00:00Z"
  },
  "error": null
}
```

**Validation:**
- Name: 1-200 chars, unique per user
- Muscle groups: valid enum values
- Equipment IDs: must exist

### PUT /api/v1/exercises/{exercise_id}
Update custom exercise (only if is_custom=true and user is owner).

**Request:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "muscle_groups": ["chest"],
  "equipment_ids": ["uuid"],
  "video_url": "https://..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "updated_at": "2025-01-15T11:00:00Z"
  },
  "error": null
}
```

### DELETE /api/v1/exercises/{exercise_id}
Delete custom exercise (only if is_custom=true, user is owner, and not used in any plans).

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

### GET /api/v1/exercises/{exercise_id}/substitutes
Get exercise substitution suggestions.

**Business Logic:**
1. Find exercises with overlapping muscle groups
2. Filter by user's owned equipment
3. Exclude the original exercise
4. Sort by muscle group overlap (more overlap = better match)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Goblet Squat",
      "muscle_groups": ["quadriceps", "glutes"],
      "equipment": [...],
      "match_score": 1.0
    }
  ],
  "error": null
}
```

---

## Workout Plans

### GET /api/v1/workout-plans
List user's workout plans.

**Query params:**
- `is_active` (optional): Filter by active status
- `page` (default: 1)
- `limit` (default: 20)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "id": "uuid",
        "name": "5x5 Strength Program",
        "description": "Linear progression",
        "is_active": true,
        "is_editable": true,
        "created_at": "2025-01-01T00:00:00Z",
        "workout_count": 3
      }
    ],
    "pagination": {...}
  },
  "error": null
}
```

### GET /api/v1/workout-plans/{plan_id}
Get workout plan details with full workout structure.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "5x5 Strength Program",
    "description": "Linear progression",
    "is_active": true,
    "is_editable": true,
    "created_at": "2025-01-01T00:00:00Z",
    "workouts": [
      {
        "id": "uuid",
        "name": "Workout A",
        "day_number": 1,
        "order_index": 0,
        "exercises": [
          {
            "id": "uuid",
            "exercise": {
              "id": "uuid",
              "name": "Barbell Squat",
              "muscle_groups": ["quadriceps", "glutes"]
            },
            "order_index": 0,
            "sets": 5,
            "reps": "5",
            "rest_seconds": 180,
            "notes": "Add 5lbs each session"
          }
        ]
      }
    ]
  },
  "error": null
}
```

### POST /api/v1/workout-plans/parse
Parse workout plan from text/image (Step 1 of import).

**Request (multipart/form-data):**
- `file`: image file (optional)
- `text`: text content (optional)

**Business Logic:**
1. Extract text from image using OCR or accept direct text
2. Parse structure: plan name, workouts, exercises, sets, reps
3. Match exercises to database (fuzzy matching)
4. Return structured data for user review

**Response (200):**
```json
{
  "success": true,
  "data": {
    "parsed_plan": {
      "name": "5x5 Strength Program",
      "description": "Extracted from image",
      "workouts": [
        {
          "name": "Workout A",
          "day_number": 1,
          "exercises": [
            {
              "matched_exercise_id": "uuid",
              "matched_exercise_name": "Barbell Squat",
              "original_text": "Squat",
              "confidence": 0.95,
              "sets": 5,
              "reps": "5",
              "rest_seconds": 180,
              "notes": "Add 5lbs each session"
            }
          ]
        }
      ]
    }
  },
  "error": null
}
```

### POST /api/v1/workout-plans
Create workout plan (Step 2 of import or manual creation).

**Request:**
```json
{
  "name": "5x5 Strength Program",
  "description": "Linear progression",
  "is_editable": true,
  "workouts": [
    {
      "name": "Workout A",
      "day_number": 1,
      "order_index": 0,
      "exercises": [
        {
          "exercise_id": "uuid",
          "order_index": 0,
          "sets": 5,
          "reps": "5",
          "rest_seconds": 180,
          "notes": "Add 5lbs each session"
        }
      ]
    }
  ]
}
```

**Validation:**
- Name: 1-200 chars
- Workouts: at least 1
- Exercises per workout: at least 1
- Exercise IDs: must exist
- Sets: 1-50
- Reps: 1-200 chars (allows "5-8", "AMRAP", etc.)
- Rest seconds: 0-3600

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "5x5 Strength Program",
    "created_at": "2025-01-15T10:00:00Z"
  },
  "error": null
}
```

### PUT /api/v1/workout-plans/{plan_id}
Update workout plan (only if is_editable=true).

**Request:** Same as POST

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "updated_at": "2025-01-15T11:00:00Z"
  },
  "error": null
}
```

### PUT /api/v1/workout-plans/{plan_id}/active
Set plan as active (deactivates other plans automatically).

**Request:**
```json
{
  "is_active": true
}
```

**Business Logic:**
- Set is_active=false for all other user's plans
- Set is_active=true for this plan

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "is_active": true
  },
  "error": null
}
```

### DELETE /api/v1/workout-plans/{plan_id}
Delete workout plan (cascade deletes workouts and planned exercises).

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## Workout Sessions

### GET /api/v1/workout-sessions
List workout sessions (history).

**Query params:**
- `workout_plan_id` (optional): Filter by plan
- `workout_id` (optional): Filter by specific workout
- `status` (optional): Filter by status (in_progress, completed, skipped)
- `start_date` (optional): Filter by date range start
- `end_date` (optional): Filter by date range end
- `page` (default: 1)
- `limit` (default: 20)
- `sort` (default: "started_at"): Sort field
- `order` (default: "desc"): Sort order

**Response (200):**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "uuid",
        "workout_name": "Workout A",
        "workout_plan_name": "5x5 Strength Program",
        "status": "completed",
        "started_at": "2025-01-15T09:00:00Z",
        "completed_at": "2025-01-15T10:30:00Z",
        "duration_seconds": 5400,
        "exercise_count": 5,
        "notes": "Felt strong today"
      }
    ],
    "pagination": {...}
  },
  "error": null
}
```

### GET /api/v1/workout-sessions/{session_id}
Get workout session details with all exercise sessions and sets.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "workout": {
      "id": "uuid",
      "name": "Workout A"
    },
    "workout_plan": {
      "id": "uuid",
      "name": "5x5 Strength Program"
    },
    "status": "completed",
    "started_at": "2025-01-15T09:00:00Z",
    "completed_at": "2025-01-15T10:30:00Z",
    "notes": "Felt strong today",
    "exercise_sessions": [
      {
        "id": "uuid",
        "exercise": {
          "id": "uuid",
          "name": "Barbell Squat"
        },
        "order_index": 0,
        "notes": "Good form",
        "sets": [
          {
            "id": "uuid",
            "set_number": 1,
            "reps_completed": 5,
            "weight": 185.0,
            "weight_unit": "lbs",
            "is_warmup": false,
            "rpe": 7,
            "notes": null,
            "completed_at": "2025-01-15T09:15:00Z"
          }
        ]
      }
    ]
  },
  "error": null
}
```

### POST /api/v1/workout-sessions/start
Start a new workout session.

**Request:**
```json
{
  "workout_id": "uuid",
  "started_at": "2025-01-15T09:00:00Z"
}
```

**Business Logic:**
1. Check if user has active session (warn if exists)
2. Get workout plan exercises
3. Get context data for each exercise:
   - Last 3 sessions for this exercise
   - Current PR for this exercise
4. Create session with status=in_progress
5. Return session with context data

**Response (201):**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "workout": {
      "id": "uuid",
      "name": "Workout A"
    },
    "started_at": "2025-01-15T09:00:00Z",
    "exercises": [
      {
        "planned_exercise_id": "uuid",
        "exercise": {
          "id": "uuid",
          "name": "Barbell Squat"
        },
        "planned_sets": 5,
        "planned_reps": "5",
        "rest_seconds": 180,
        "context": {
          "personal_record": {
            "record_type": "one_rep_max",
            "value": 225.0,
            "unit": "lbs",
            "achieved_at": "2025-01-10T14:30:00Z"
          },
          "recent_sessions": [
            {
              "date": "2025-01-13T09:00:00Z",
              "sets": [
                {"reps": 5, "weight": 185.0, "unit": "lbs"}
              ]
            }
          ]
        }
      }
    ]
  },
  "error": null
}
```

### POST /api/v1/workout-sessions/{session_id}/exercises
Log exercise session during workout.

**Request:**
```json
{
  "exercise_id": "uuid",
  "order_index": 0,
  "notes": "Good form",
  "sets": [
    {
      "set_number": 1,
      "reps_completed": 5,
      "weight": 185.0,
      "weight_unit": "lbs",
      "is_warmup": false,
      "rpe": 7,
      "notes": null,
      "completed_at": "2025-01-15T09:15:00Z"
    }
  ]
}
```

**Validation:**
- Session must be in_progress
- Exercise ID must exist
- Weight: positive number
- Weight unit: valid enum (lbs, kg)
- RPE: 1-10 or null
- Reps completed: positive integer

**Response (201):**
```json
{
  "success": true,
  "data": {
    "exercise_session_id": "uuid",
    "set_ids": ["uuid1", "uuid2", "uuid3"]
  },
  "error": null
}
```

### PUT /api/v1/workout-sessions/{session_id}/complete
Complete workout session.

**Request:**
```json
{
  "completed_at": "2025-01-15T10:30:00Z",
  "notes": "Felt strong today"
}
```

**Business Logic:**
1. Set status=completed
2. Calculate duration
3. Check for new PRs (1RM, volume, etc.)
4. Create PR records if applicable
5. Update denormalized PR fields on personal_record table

**Response (200):**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "completed",
    "duration_seconds": 5400,
    "new_personal_records": [
      {
        "exercise_name": "Barbell Squat",
        "record_type": "one_rep_max",
        "value": 235.0,
        "unit": "lbs"
      }
    ]
  },
  "error": null
}
```

### PUT /api/v1/workout-sessions/{session_id}/skip
Skip workout session.

**Request:**
```json
{
  "notes": "Feeling unwell"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "status": "skipped"
  },
  "error": null
}
```

### DELETE /api/v1/workout-sessions/{session_id}
Delete workout session and all associated data.

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## Personal Records

### GET /api/v1/personal-records
List personal records.

**Query params:**
- `exercise_id` (optional): Filter by exercise
- `record_type` (optional): Filter by type (one_rep_max, total_volume, etc.)
- `page` (default: 1)
- `limit` (default: 50)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "id": "uuid",
        "exercise": {
          "id": "uuid",
          "name": "Barbell Squat"
        },
        "record_type": "one_rep_max",
        "value": 235.0,
        "unit": "lbs",
        "achieved_at": "2025-01-15T10:30:00Z",
        "exercise_session_id": "uuid",
        "notes": "New PR!"
      }
    ],
    "pagination": {...}
  },
  "error": null
}
```

### POST /api/v1/personal-records
Manually create personal record.

**Request:**
```json
{
  "exercise_id": "uuid",
  "record_type": "one_rep_max",
  "value": 235.0,
  "unit": "lbs",
  "achieved_at": "2025-01-15T10:30:00Z",
  "notes": "New PR!"
}
```

**Validation:**
- Exercise ID must exist
- Record type: valid enum
- Value: positive number
- Unit: valid enum (lbs, kg, seconds, meters)

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "record_type": "one_rep_max",
    "value": 235.0
  },
  "error": null
}
```

### DELETE /api/v1/personal-records/{record_id}
Delete personal record.

**Response (200):**
```json
{
  "success": true,
  "data": null,
  "error": null
}
```

---

## Statistics & Analytics

### GET /api/v1/stats/overview
Get user's workout statistics overview.

**Query params:**
- `start_date` (optional): Filter by date range
- `end_date` (optional): Filter by date range

**Business Logic:**
Calculate aggregated stats from workout sessions and exercise sessions.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_workouts": 45,
    "total_duration_seconds": 243000,
    "total_volume_lbs": 125000.0,
    "workouts_by_month": [
      {"month": "2025-01", "count": 12}
    ],
    "most_trained_muscle_groups": [
      {"muscle_group": "chest", "session_count": 15}
    ],
    "current_streak_days": 5,
    "personal_records_count": 8
  },
  "error": null
}
```

### GET /api/v1/stats/exercise/{exercise_id}/history
Get exercise performance history.

**Query params:**
- `start_date` (optional)
- `end_date` (optional)
- `limit` (default: 50): Max sessions to return

**Business Logic:**
Get all exercise sessions for this exercise with sets, ordered by date.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "exercise": {
      "id": "uuid",
      "name": "Barbell Squat"
    },
    "sessions": [
      {
        "date": "2025-01-15T09:00:00Z",
        "total_volume": 4625.0,
        "total_reps": 25,
        "max_weight": 185.0,
        "sets": [
          {"reps": 5, "weight": 185.0, "unit": "lbs", "rpe": 7}
        ]
      }
    ]
  },
  "error": null
}
```

---

## Error Codes

### Authentication Errors (401)
- `AUTH_INVALID_CREDENTIALS`: Invalid email or password
- `AUTH_TOKEN_EXPIRED`: JWT token expired
- `AUTH_TOKEN_INVALID`: Invalid JWT token
- `AUTH_UNAUTHORIZED`: Not authenticated

### Authorization Errors (403)
- `AUTH_FORBIDDEN`: User lacks permission for this resource
- `AUTH_NOT_OWNER`: User is not the owner of this resource

### Validation Errors (400)
- `VALIDATION_ERROR`: Request validation failed
- `VALIDATION_EMAIL_EXISTS`: Email already registered
- `VALIDATION_INVALID_FORMAT`: Invalid data format
- `VALIDATION_REQUIRED_FIELD`: Required field missing

### Resource Errors (404)
- `RESOURCE_NOT_FOUND`: Resource does not exist

### Business Logic Errors (400)
- `PLAN_NOT_EDITABLE`: Cannot modify non-editable workout plan
- `SESSION_ALREADY_COMPLETED`: Cannot modify completed session
- `SESSION_NOT_IN_PROGRESS`: Action requires session to be in progress
- `EXERCISE_IN_USE`: Cannot delete exercise used in plans
- `INVALID_WORKOUT_STRUCTURE`: Workout structure validation failed

### Server Errors (500)
- `INTERNAL_ERROR`: Unexpected server error
- `DATABASE_ERROR`: Database operation failed

---

## Rate Limiting

- Authentication endpoints: 5 requests per minute per IP
- All other endpoints: 100 requests per minute per user
- Parse endpoint: 10 requests per hour per user (OCR is expensive)

---

## Pagination

All list endpoints support pagination with:
- `page`: Page number (1-indexed)
- `limit`: Items per page (max 100)

Response includes:
```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

---

## API Versioning

Current version: v1
Base path: `/api/v1`

Future versions will be available at `/api/v2`, etc.

---

## Implementation Notes

### Database Access
- Use PostgreSQL Row Level Security (RLS) for user data isolation
- All queries automatically filtered by authenticated user ID
- No manual WHERE user_id clauses needed in most cases

### Performance
- Use eager loading for relationships (workout -> exercises)
- Implement database indexes per `.ai/db_structure.md`
- Use pagination for all list endpoints
- Cache equipment list (rarely changes)

### Security
- JWT tokens with 1-hour expiration (access) and 7-day expiration (refresh)
- Password hashing with bcrypt (cost factor 12)
- Input validation with Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration for frontend domain only

### Business Logic
- PR calculation: Use 1RM formula (weight × (1 + reps/30))
- Volume calculation: Sum of (sets × reps × weight)
- Exercise matching: Fuzzy string matching with 0.8+ threshold
- Workout streak: Count consecutive days with completed sessions

### Testing Priority
1. Authentication flow
2. Workout session logging with context
3. PR calculation and updates
4. Exercise substitution algorithm
5. Workout plan import/parse
6. RLS policies for data isolation
