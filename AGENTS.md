# Development Guidelines - AllWorkouts

For technical stack details, dependencies, project structure, and environment setup, see [.ai/tech_stack.md](.ai/tech_stack.md).

## Build & Test Commands

### Backend
Do NOT run backend app directly, always use Docker.

```bash
# Start backend services
docker-compose up -d

# Run backend tests
docker-compose exec backend pytest

# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision -m "description"
```

### Frontend
```bash
# Development server
npm run dev

# Run tests
npm run test

# Lint
npm run lint
```

## Code Style Guidelines

### Backend (Python)

#### Code Organization
- All routes in `app/api.py`
- Database models in `app/models.py`
- Pydantic schemas in `app/schemas.py`
- Authentication logic in `app/auth.py`

#### Style Rules
- Use Python 3.9+ features
- Include basic type hints
- Follow Black formatting with 4 space indentation, no tabs, use single quotes
- Use ruff for linting (see tech_stack.md for details)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Prefix private functions/variables with underscore

#### Error Handling
- Use FastAPI's HTTPException for API errors
- Include error codes and messages in responses
- Log errors with appropriate severity
- Handle database errors gracefully

### Frontend (Vue)

#### Component Structure
- Use Composition API
- Keep components focused and small
- Place shared components in components/common
- Use views/ for page components

#### Style Rules
- Follow Vue style guide priorities
- Use PascalCase for component names
- Use kebab-case for events
- Prefix component events with 'on'
- Use Tailwind classes for styling
- 2 space indentation, no tabs, use single quotes
- ESLint + Prettier for formatting (see tech_stack.md for details)

#### State Management
- Use Pinia for global state
- Keep component state local when possible
- Define clear actions and mutations
- Use computed properties for derived data

## Database Guidelines

### Tables
- Use singular form for table names
- Include created_at/updated_at timestamps
- Use UUID for primary keys
- Add appropriate indexes

### Relationships
- Define foreign key constraints
- Use cascade delete where appropriate
- Include relationship back-references

## API Guidelines

### Endpoints
- Use plural nouns for resources
- Follow REST conventions
- Include API version in path
- Document with OpenAPI annotations

### Response Format
```json
{
  "success": boolean,
  "data": object | null,
  "error": {
    "code": string,
    "message": string
  } | null
}
```

### Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Testing Requirements

### Backend Tests
- Unit tests for business logic
- API tests for endpoints
- Test database operations
- Minimum 80% coverage

### Frontend Tests
- Component unit tests
- Basic integration tests
- Test user interactions
- Verify state management

## Security Requirements

### Authentication
- JWT-based authentication
- Secure password hashing
- Token refresh mechanism
- Session management

### Data Protection
- Input validation
- SQL injection prevention
- XSS protection
- CORS configuration

## Performance Guidelines

### Database
- Optimize queries
- Use appropriate indexes
- Implement pagination
- Cache where necessary

### API
- Rate limiting
- Response compression
- Efficient serialization
- Request validation

### Frontend
- Lazy loading
- Asset optimization
- State management efficiency
- Component optimization