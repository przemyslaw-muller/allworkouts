# AllWorkouts Backend

FastAPI backend for the AllWorkouts strength training tracker application.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session management
│   ├── enums.py             # Enum type definitions
│   ├── models.py            # SQLAlchemy ORM models (11 models)
│   ├── schemas.py           # Pydantic validation schemas
│   └── auth.py              # Authentication utilities (JWT, password hashing)
├── alembic/
│   ├── env.py               # Alembic environment configuration
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files
│       ├── 001_initial.py   # Initial schema with all tables
│       └── 002_seed_data.py # Reference data seeding
├── Dockerfile               # Docker image configuration
├── alembic.ini             # Alembic configuration
├── pyproject.toml          # Poetry dependencies
└── .env.example            # Example environment variables
```

## Database Models

The application includes 11 SQLAlchemy models:

1. **User** - User accounts with authentication
2. **Equipment** - Global equipment catalog
3. **Exercise** - Exercise database with muscle groups
4. **ExerciseEquipment** - Exercise-equipment relationships
5. **UserEquipment** - User's available equipment (soft delete)
6. **WorkoutPlan** - User workout plan templates (soft delete)
7. **WorkoutExercise** - Exercises within workout plans
8. **WorkoutSession** - Workout execution records (soft delete)
9. **ExerciseSession** - Individual logged sets
10. **PersonalRecord** - Denormalized PR tracking
11. **WorkoutImportLog** - AI parsing audit trail

## Setup

### Using Docker Compose (Recommended)

From the project root directory:

```bash
# Start all services (database + backend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Running Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision -m "description"

# Downgrade migration
docker-compose exec backend alembic downgrade -1
```

### Local Development (Without Docker)

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, access the auto-generated API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

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

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT token generation
- `DEBUG` - Enable debug mode (true/false)

## Technologies

- **FastAPI** - Modern Python web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **PostgreSQL 13** - Relational database
- **JWT** - Token-based authentication
- **Poetry** - Dependency management
- **Uvicorn** - ASGI server

## Development Guidelines

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Format code with Black (line length 100)
- Lint with ruff
- 4 space indentation, no tabs, single quotes
- Write tests for new features (pytest)

## Current Status

✅ Database schema fully implemented
✅ All 11 models created with proper relationships
✅ Initial migrations ready
✅ Health check endpoint functional
⏳ API endpoints (to be implemented)
⏳ Authentication flow (to be implemented)
⏳ Business logic (to be implemented)

This is a skeleton backend - the data layer is complete and ready for endpoint implementation.
