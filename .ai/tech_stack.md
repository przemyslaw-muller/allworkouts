# Technical Stack - AllWorkouts

## Overview
AllWorkouts is built using a modern web stack with clear separation between frontend and backend services.

## Backend Stack

### Core Framework
- FastAPI
  - Modern, fast Python web framework
  - Built-in OpenAPI documentation
  - Type hints and data validation
  - Async support for high performance

### Database
- PostgreSQL
  - Robust relational database
  - Strong data integrity
  - JSON support for flexible workout templates
  - Full-text search capabilities for exercise matching

### Python Dependencies
- poetry - dependency management
- SQLAlchemy - ORM for database operations
- Alembic - Database migrations
- Pydantic - Data validation
- python-jose - JWT token handling
- passlib - Password hashing
- psycopg2-binary - PostgreSQL adapter

## Frontend Stack

### Core Framework
- Vue 3
  - Composition API for better code organization
  - TypeScript support
  - Built-in state management with Pinia

### Styling
- Tailwind CSS
  - Utility-first CSS framework
  - Easy responsive design
  - Custom design system support

### Development Tools
- Vite - Modern build tool
- Vue Router - Route management
- Pinia - State management
- axios - API client
- ESLint + Prettier - Code formatting

## Development Environment

### Docker Setup
- docker-compose for local development
- Separate containers for:
  - Backend (FastAPI)
  - Frontend (Vue3)
  - Database (PostgreSQL)
  - PgAdmin (Database management)

### Local Development URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PgAdmin: http://localhost:5050

## Project Structure

```
allworkouts/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   └── schemas/
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── router/
│   │   ├── stores/
│   │   └── views/
│   ├── package.json
│   └── vite.config.ts
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── postgres.Dockerfile
└── docker-compose.yml
```

## Development Workflow

### First-time Setup
```bash
# Clone repository
git clone [repository-url]

# Start services
docker-compose up -d

# Apply database migrations
docker-compose exec backend alembic upgrade head

# Install frontend dependencies
docker-compose exec frontend npm install
```

### Daily Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Testing
```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm run test
```

## Coding Standards

### Backend (Python)
- Python 3.11+
- Type hints required
- ruff for linting
- pytest for testing

### Frontend (Vue/TypeScript)
- TypeScript for all components
- Vue 3 Composition API
- ESLint + Prettier configuration
- Jest for unit testing
- Playwright for E2E testing

## CI/CD Considerations
- GitHub Actions for CI/CD
- Automated testing on PR
- Code quality checks
- Docker image builds
- Automated deployments