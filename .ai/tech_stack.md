# Technical Stack - AllWorkouts

## Overview
AllWorkouts MVP uses a straightforward web stack that balances development speed with maintainability.

## Backend Stack

### Core Framework
- FastAPI

### Database
- PostgreSQL

### Python Dependencies
- poetry - dependency management
- SQLAlchemy - Database ORM
- Alembic - Migrations
- Pydantic - Data validation
- python-jose - JWT handling
- passlib - Password hashing
- psycopg2-binary - PostgreSQL adapter
- ruff - linter

## Frontend Stack

### Core Framework
- Vue 3
  - Composition API
  - Built-in state management
  - Excellent documentation

### Styling
- Tailwind CSS

### Key Dependencies
- Vite - build tool
- Vue Router - Navigation
- Pinia - State management
- axios - API client
- TypeScript
- zod - schema validation

## Development Environment

### Docker Setup
-- docker-compose for local development
-- Separate containers for:
-  - Backend (FastAPI)
-  - Frontend (Vue3)
-  - Database (PostgreSQL)

Frontend runs locally for faster development.

### Local Development URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure
```
allworkouts/
├── backend/
│   ├── app/
│   │   ├── api.py      # All routes
│   │   ├── models.py   # Database models
│   │   ├── schemas.py  # Pydantic schemas
│   │   └── auth.py     # Authentication
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── store.js
│   └── package.json
└── docker-compose.yml
```

## Local Setup

### Docker Configuration
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/allworkouts
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=allworkouts
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Getting Started
```bash
# Start backend services
docker-compose up -d

# Setup frontend
npm create vue@latest
cd frontend
npm install
npm run dev
```

## Development Workflow

### Backend Development
- Python 3.9+
- Basic type hints
- Simple pytest setup
- Black for formatting
- 4 space indentation, no tabs, use single quotes

### Frontend Development
- Vue 3 Composition API
- TypeScript
- Basic Jest testing
- ESLint + Prettier
- 2 space indentation, no tabs, use single quotes

## Security
- JWT-based authentication
- Password hashing
- PostgreSQL security best practices
- CORS configuration

## Future Considerations
- CI/CD setup
- Advanced testing
- Mobile responsiveness
- Performance optimization