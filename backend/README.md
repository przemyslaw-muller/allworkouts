# AllWorkouts Backend

FastAPI backend for the AllWorkouts strength training tracker application with AI-powered workout plan parsing.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings (Pydantic V2)
│   ├── database.py          # Database connection and session management
│   ├── enums.py             # Enum type definitions (muscle groups, session status, etc.)
│   ├── models.py            # SQLAlchemy ORM models (12 models)
│   ├── auth.py              # Authentication utilities (JWT, password hashing)
│   ├── exceptions.py        # Custom exception handlers
│   ├── api/                 # API route modules
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── equipment.py     # Equipment management
│   │   ├── exercises.py     # Exercise CRUD and substitutions
│   │   ├── workout_plans.py # Workout plan management with AI parsing
│   │   ├── workout_sessions.py # Workout logging and tracking
│   │   ├── personal_records.py # PR tracking endpoints
│   │   └── stats.py         # Statistics and analytics
│   ├── schemas/             # Pydantic validation schemas (modular)
│   │   ├── auth.py          # Authentication schemas
│   │   ├── base.py          # Base schemas and pagination
│   │   ├── equipment.py     # Equipment schemas
│   │   ├── exercises.py     # Exercise schemas
│   │   ├── workout_plans.py # Workout plan schemas
│   │   ├── workout_sessions.py # Session logging schemas
│   │   ├── personal_records.py # PR schemas
│   │   ├── stats.py         # Statistics schemas
│   │   ├── user.py          # User profile schemas
│   │   └── import_logs.py   # Import audit log schemas
│   └── services/            # Business logic services
│       ├── llm_service.py   # LLM integration (OpenAI via LiteLLM)
│       ├── parser_service.py # Workout plan text parsing
│       └── exercise_matcher.py # Fuzzy exercise matching
├── alembic/
│   ├── env.py               # Alembic environment configuration
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files (7 migrations)
│       ├── 001_initial.py   # Initial schema with all tables
│       ├── 002_seed_data.py # Reference data seeding (equipment & exercises)
│       ├── 003_nullable_exercise_session_id.py
│       ├── 004_add_workout_hierarchy.py
│       ├── 005_add_user_name.py
│       ├── 20251210_1808_*.py # Custom exercise fields
│       ├── 20251214_1324_*.py # Import log status
│       └── 20251214_1630_*.py # Set configurations
├── tests/                   # Pytest test suite
│   ├── conftest.py          # Test fixtures and configuration
│   ├── test_auth.py         # Authentication tests
│   ├── test_equipment.py    # Equipment endpoint tests
│   ├── test_exercises.py    # Exercise endpoint tests
│   ├── test_workout_plans.py # Workout plan tests
│   ├── test_workout_sessions.py # Session logging tests
│   ├── test_personal_records.py # PR tracking tests
│   ├── test_stats.py        # Statistics tests
│   └── test_parser_services.py # Parser service tests
├── docs/                    # Documentation
│   ├── parser_setup.md      # Parser configuration guide
│   ├── parser_usage.md      # Parser API usage
│   └── parser_examples.md   # Parser example outputs
├── Dockerfile               # Docker image configuration
├── entrypoint.sh           # Container startup script
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # uv dependencies
├── seed_equipment.json     # Equipment seed data
├── seed_exercises.json     # Exercise seed data
└── .env.example            # Example environment variables
```

## Database Models

The application includes 12 SQLAlchemy models:

1. **User** - User accounts with authentication, name, and unit preferences
2. **Equipment** - Global equipment catalog
3. **Exercise** - Exercise database with muscle groups, defaults, and custom exercise support
4. **ExerciseEquipment** - Exercise-equipment relationships
5. **UserEquipment** - User's available equipment (soft delete)
6. **WorkoutPlan** - User workout plan templates (soft delete, active status)
7. **Workout** - Individual workouts within a plan (day-based organization)
8. **WorkoutExercise** - Exercises within workouts with set configurations and confidence levels
9. **WorkoutSession** - Workout execution records (soft delete, status tracking)
10. **ExerciseSession** - Individual logged sets with rest times
11. **PersonalRecord** - Denormalized PR tracking (1RM, set volume, total volume)
12. **WorkoutImportLog** - AI parsing audit trail with confidence scores

## Setup

### Prerequisites

- Docker & Docker Compose
- PostgreSQL 13+ (if running locally)
- Python 3.10+ (if running locally)

### Using Docker Compose (Recommended)

From the project root directory:

```bash
# Start all services (database + backend + frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after dependency changes
docker-compose up -d --build backend
```

### Running Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision -m "description"

# Downgrade migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

### Running Tests

```bash
# Run all tests with coverage
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run with verbose output
docker-compose exec backend pytest -v

# Run tests matching pattern
docker-compose exec backend pytest -k "test_parser"
```

### Local Development (Without Docker)

1. Install dependencies using uv:
```bash
# Install uv if not already installed
pip install uv

# Install project dependencies
uv pip install -e .
uv pip install -e ".[dev]"
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL
# - JWT_SECRET_KEY
# - LLM_API_KEY (for AI parsing)
# - LLM_PROVIDER (openai, anthropic, etc.)
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access the auto-generated API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### Main API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user profile
- `PUT /api/auth/me` - Update user profile

#### Equipment
- `GET /api/equipment` - List equipment with ownership status
- `POST /api/equipment/{id}/ownership` - Update equipment ownership

#### Exercises
- `GET /api/exercises` - List exercises (with filtering by muscle group, equipment)
- `GET /api/exercises/{id}` - Get exercise details
- `POST /api/exercises` - Create custom exercise
- `PUT /api/exercises/{id}` - Update custom exercise
- `DELETE /api/exercises/{id}` - Delete custom exercise
- `GET /api/exercises/{id}/substitutes` - Get exercise substitutions

#### Workout Plans
- `GET /api/workout-plans` - List workout plans
- `GET /api/workout-plans/{id}` - Get workout plan details
- `POST /api/workout-plans` - Create workout plan
- `POST /api/workout-plans/parse` - Parse text into workout plan (AI-powered)
- `PUT /api/workout-plans/{id}` - Update workout plan
- `DELETE /api/workout-plans/{id}` - Delete workout plan (soft delete)
- `POST /api/workout-plans/{id}/activate` - Set active workout plan

#### Workout Sessions
- `POST /api/workout-sessions/start` - Start workout session
- `POST /api/workout-sessions/{id}/log-exercise` - Log exercise sets
- `POST /api/workout-sessions/{id}/complete` - Complete session
- `POST /api/workout-sessions/{id}/skip` - Skip session
- `GET /api/workout-sessions` - List workout sessions (history)
- `GET /api/workout-sessions/{id}` - Get session details

#### Personal Records
- `GET /api/personal-records` - List personal records
- `GET /api/personal-records/exercise/{exercise_id}` - Get PRs for exercise

#### Statistics
- `GET /api/stats/overview` - Training overview statistics

## Database Schema

The database schema follows the specifications in `.ai/db_structure.md` with:

- UUID primary keys for all tables
- Timestamps (created_at, updated_at) on all tables
- Soft deletes on user-scoped tables (deleted_at)
- PostgreSQL ENUM types for categorical data
- Array types for muscle groups with GIN indexes
- Comprehensive indexing strategy for query optimization
- Foreign key relationships without cascade deletes

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://user:pass@db:5432/allworkouts`)
- `JWT_SECRET_KEY` - Secret key for JWT token generation (change in production!)
- `JWT_ALGORITHM` - JWT algorithm (default: `HS256`)
- `JWT_EXPIRATION_MINUTES` - Token expiration time (default: `10080` = 7 days)

### LLM Configuration (for AI parsing)
- `LLM_PROVIDER` - LLM provider (default: `openai`, supports: anthropic, cohere, etc.)
- `LLM_MODEL` - Model name (default: `gpt-4-turbo-preview`)
- `LLM_API_KEY` - API key for LLM provider
- `LLM_TEMPERATURE` - Temperature for parsing (default: `0.1`)
- `LLM_MAX_TOKENS` - Max tokens for response (default: `16000`)
- `LLM_TIMEOUT` - Request timeout in seconds (default: `120`)

### Parser Configuration
- `EXERCISE_MATCH_THRESHOLD` - Default match threshold (default: `0.80`)
- `EXERCISE_MATCH_HIGH_THRESHOLD` - High confidence threshold (default: `0.90`)
- `EXERCISE_MATCH_LOW_THRESHOLD` - Low confidence threshold (default: `0.70`)

### Optional
- `APP_NAME` - Application name (default: `AllWorkouts API`)
- `DEBUG` - Enable debug mode (default: `false`)

## Technologies

- **FastAPI** - Modern Python web framework with automatic OpenAPI documentation
- **SQLAlchemy 2.0** - ORM with full async support
- **Alembic** - Database migrations with version control
- **Pydantic V2** - Data validation and settings management with ConfigDict
- **PostgreSQL 13+** - Relational database with JSON and array support
- **JWT** - Token-based authentication (python-jose)
- **Passlib** - Password hashing with bcrypt
- **LiteLLM** - Unified LLM API wrapper (supports OpenAI, Anthropic, Cohere, etc.)
- **RapidFuzz** - Fast fuzzy string matching for exercise name matching
- **uv** - Fast Python package installer and dependency resolver
- **Uvicorn** - Lightning-fast ASGI server
- **pytest** - Testing framework with async support

## Key Features

### AI-Powered Workout Parsing
- Natural language processing of workout plans
- Structured JSON output with exercise matching
- Three-level confidence scoring (high/medium/low)
- Support for various rep schemes and set configurations
- Automatic exercise database matching with fuzzy search

### Exercise Matching System
- Fuzzy string matching with configurable thresholds
- Muscle group-based exercise substitutions
- Equipment compatibility checking
- Custom exercise support per user

### Personal Record Tracking
- Automatic PR detection during workout logging
- Multiple record types:
  - One Rep Max (1RM)
  - Set Volume (weight × reps)
  - Total Volume (weight × total reps across all sets)
- Historical PR timeline per exercise

### Workout Session Management
- Real-time workout logging
- Rest timer tracking between sets
- Historical context display (previous sessions, PRs)
- Incomplete session saving
- Status tracking (in-progress, completed, skipped)

## Development Guidelines

See [AGENTS.md](../AGENTS.md) for comprehensive development guidelines.

### Code Style
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Format code with Black (line length 100, single quotes)
- Lint with ruff (E, F, I rules)
- 4 space indentation, no tabs
- Use snake_case for functions and variables
- Use PascalCase for classes
- Prefix private functions/variables with underscore

### Testing
- Write tests for new features using pytest
- Aim for 80%+ code coverage
- Include unit tests for business logic
- Include API tests for endpoints
- Test database operations with fixtures
- Mock external services (LLM calls)

### Database
- Use UUID primary keys for all tables
- Include created_at/updated_at timestamps
- Implement soft deletes where appropriate (deleted_at)
- Add appropriate indexes for queries
- Define foreign key constraints
- Use Alembic for all schema changes

### API Design
- Follow REST conventions
- Use plural nouns for resources
- Return consistent response formats
- Include proper HTTP status codes
- Document with OpenAPI annotations
- Validate input with Pydantic schemas
