# AllWorkouts

A web application for strength training enthusiasts to import, manage, and track workout programs with AI-powered parsing and performance analytics.

## Demo:
<https://allworkouts.fly.dev/login>

**Status**: MVP Development
**License**: MIT

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running the Application](#running-the-application)
- [Available Scripts](#available-scripts)
- [Project Scope](#project-scope)
- [Documentation](#documentation)
- [Development](#development)

---

## Overview

AllWorkouts solves key challenges faced by strength training enthusiasts:

- **Manual entry burden**: Automatically converts text-based workout plans into structured data
- **Progress tracking difficulty**: Logs performance metrics and tracks personal records (1RM, set volume, total volume)
- **Inconsistent history management**: Maintains organized, filterable workout history with completion status

The MVP focuses on three core capabilities:
1. AI-powered parsing of plain text workout plans
2. Structured workout logging with performance tracking
3. Training history management and review

---

## Features

### User Authentication
- Email-based registration and login
- Unit preference selection (kg/cm or lbs/inches)
- Equipment availability management in user profile

### Workout Plan Management
- AI-powered parsing of plain text workout plans
- Exercise matching against database with confidence levels (high/medium/low)
- Three-state confidence system with 80%+ threshold for acceptance
- Exercise substitution recommendations based on available equipment and muscle groups
- Complete CRUD operations for workout plans
- Equipment compatibility verification

### Workout Logging
- Set-by-set performance recording (sets, reps, weights)
- Pre-filled values from previous workouts or exercise defaults
- Rest timer after logging each set
- PR tracking for:
  - One Rep Max (1RM)
  - Set volume (weight × reps)
  - Total volume (weight × total reps)
- Incomplete workout saves (allows partial logging)

### History Tracking
- Chronological list of completed workouts
- Filtering by completion status and workout name
- Detailed session views with performance metrics
- Progress metrics display

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 13
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose) + Password hashing (passlib)
- **Validation**: Pydantic
- **Code Quality**: ruff (linting), Black (formatting)
- **Testing**: pytest
- **Dependency Management**: poetry

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: axios
- **Validation**: zod
- **Code Quality**: ESLint + Prettier
- **Testing**: Jest

### Development
- **Containerization**: Docker & Docker Compose
- **Version Control**: Git

---

## Getting Started

### Prerequisites

Ensure you have the following installed:
- **Docker** and **Docker Compose** (for backend + database)
- **Node.js** and **npm** (for frontend)
- **Python 3.9+** (if running backend locally without Docker)

### Backend Setup

The backend uses Docker for easy local development:

```bash
# Start backend and database services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create a new migration (if needed)
docker-compose exec backend alembic revision -m "description"
```

The backend will be available at `http://localhost:8000` with API documentation at `http://localhost:8000/docs` (Swagger UI).

**Environment Variables** (backend):
```
DATABASE_URL=postgresql://user:pass@db/allworkouts
SECRET_KEY=your-secret-key-here
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Running the Application

Once both services are running:

1. **Backend API**: http://localhost:8000
2. **Frontend Application**: http://localhost:3000
3. **API Documentation**: http://localhost:8000/docs (interactive Swagger UI)

---

## Available Scripts

### Backend Commands

```bash
# Start backend services (Docker)
docker-compose up -d

# Stop services
docker-compose down

# Run backend tests
docker-compose exec backend pytest

# Run tests with coverage
docker-compose exec backend pytest --cov=app

# Format code (Black)
docker-compose exec backend black app/

# Lint code (ruff)
docker-compose exec backend ruff check app/

# Database migrations
docker-compose exec backend alembic upgrade head        # Apply migrations
docker-compose exec backend alembic downgrade -1        # Rollback last migration
docker-compose exec backend alembic current             # Check current version
docker-compose exec backend alembic revision -m "msg"   # Create new migration
```

### Frontend Commands

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

---

## Project Scope

### MVP Features ✓
- Web application interface
- Plain text workout plan import with AI parsing
- Basic CRUD operations for workout plans
- Exercise substitution recommendations
- Essential progress tracking and history
- User authentication and profile management
- Email-based unit and equipment preferences

### Out of Scope ✗
- Mobile application
- Offline mode / Progressive Web App
- Social features (sharing, friends, competition)
- Advanced analytics and charts
- AI-generated workout plans
- Warm-up set tracking
- Supersets / Circuit training support
- Mobile responsiveness (MVP focuses on desktop)

---

## Documentation

### Development Guidelines
- **Backend Rules**: [.ai/rules/backend.md](.ai/rules/backend.md)
- **Frontend Rules**: [.ai/rules/frontend.md](.ai/rules/frontend.md)
- **Development Guidelines**: [AGENTS.md](AGENTS.md)

### Project Documentation
- **Product Requirements**: [.ai/prd.md](.ai/prd.md)
- **Technical Stack**: [.ai/tech_stack.md](.ai/tech_stack.md)

---

## Development

### Code Style Guidelines

**Backend (Python)**
- 4 spaces indentation, no tabs, single quotes
- Type hints required for all functions
- Use snake_case for functions/variables, PascalCase for classes
- Follow Black formatting and ruff linting

**Frontend (Vue 3)**
- 2 spaces indentation, no tabs, single quotes
- Use Composition API with `<script setup>`
- TypeScript for all components
- Follow ESLint + Prettier formatting
- Tailwind CSS for styling

### Project Structure

```
allworkouts/
├── backend/                  # FastAPI backend service
│   ├── app/
│   │   ├── api.py           # All route definitions
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── auth.py          # Authentication logic
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test files
│   └── pyproject.toml       # Python dependencies
├── frontend/                 # Vue 3 frontend application
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia stores
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   └── App.vue
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Docker services configuration
├── .ai/                     # AI agent rules and documentation
├── AGENTS.md                # Development guidelines
└── README.md
```

### Testing

**Backend**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app

# Run specific test file
pytest tests/unit/test_auth.py
```

**Frontend**
```bash
# Run tests
npm run test

# Watch mode
npm run test:watch
```

### Git Workflow

- Use feature branches with descriptive names
- Write clear commit messages explaining the "why"
- All commits should reference related issue numbers
- Run tests and linting before committing:
  ```bash
  # Backend
  docker-compose exec backend pytest
  docker-compose exec backend ruff check app/
  docker-compose exec backend black app/

  # Frontend
  npm run test
  npm run lint
  npm run format
  ```

### Security

- JWT-based authentication with secure token handling
- Password hashing using bcrypt via passlib
- PostgreSQL security best practices
- CORS configuration in FastAPI
- Input validation using Pydantic and zod

---

## Success Metrics

- **Import Success**: 80%+ AI parsing confidence threshold
- **User Engagement**: Successful workout imports and complete logging rates
- **System Reliability**: Accurate PR calculations and consistent history tracking
- **Exercise Matching**: Reliable exercise matching and equipment compatibility validation

---

## Troubleshooting

### Backend Issues

```bash
# Check if backend is running
curl http://localhost:8000/docs

# View backend logs
docker-compose logs backend

# Restart services
docker-compose restart

# Reset database
docker-compose down -v  # Warning: removes all data
docker-compose up -d
```

### Frontend Issues

```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Port already in use (port 3000)
npm run dev -- --port 3001
```

---

## Contributing

When contributing to AllWorkouts:

1. Follow the code style guidelines in [.ai/rules/backend.md](.ai/rules/backend.md) and [.ai/rules/frontend.md](.ai/rules/frontend.md)
2. Ensure all tests pass before submitting PR
3. Include tests for new features
4. Update documentation if needed
5. Reference related issues in commit messages

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Check existing documentation in [.ai/prd.md](.ai/prd.md)
- Review development guidelines in [AGENTS.md](AGENTS.md)
