# Backend Development Rules - AllWorkouts

## Stack Overview
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Python Version**: 3.9+
- **Dependency Manager**: poetry

For complete stack details, see [../tech_stack.md](../tech_stack.md).

## Code Organization

### Project Structure
```
backend/
├── app/
│   ├── api.py          # All routes
│   ├── models.py       # Database models
│   ├── schemas.py      # Pydantic schemas
│   └── auth.py         # Authentication logic
├── alembic/            # Database migrations
├── tests/              # Test files
├── pyproject.toml      # Dependencies
└── Dockerfile
```

### File Organization Rules
- **Keep concerns separated**: Each file has a specific responsibility
- **API routes**: All route definitions in `app/api.py` with clear naming
- **Database layer**: Models in `app/models.py`, schemas in `app/schemas.py`
- **Auth logic**: Centralize authentication in `app/auth.py`
- **Tests**: Mirror app structure in `tests/` directory

## Code Style Guidelines

### Formatting & Indentation
- **Indentation**: 4 spaces, no tabs
- **String quotes**: Single quotes (`'string'`)
- **Line length**: Follow Black's default (88 characters)
- **Formatter**: Black
- **Linter**: ruff

### Naming Conventions
- **Functions & variables**: `snake_case`
  - ✓ `get_user_by_id()`
  - ✗ `getUserById()`
- **Classes**: `PascalCase`
  - ✓ `class UserModel`
  - ✗ `class user_model`
- **Constants**: `UPPER_SNAKE_CASE`
  - ✓ `MAX_RETRY_ATTEMPTS = 3`
  - ✗ `max_retry_attempts = 3`
- **Private functions/variables**: Prefix with underscore
  - ✓ `_internal_helper()`
  - ✓ `self._private_value`
- **Module names**: `lowercase_with_underscores`
  - ✓ `database_utils.py`
  - ✗ `databaseUtils.py`

### Type Hints
- **Mandatory**: Include type hints for all function parameters and return values
- **Format**:
  ```python
  def get_user(user_id: int) -> User:
      """Retrieve user by ID."""
      pass
  
  def process_data(items: list[str], count: int = 5) -> dict[str, any]:
      """Process data items."""
      pass
  ```
- **Optional types**: Use `Optional[Type]` for nullable values
  ```python
  def find_user(email: str) -> Optional[User]:
      pass
  ```
- **Use Python 3.9+ features**:
  ```python
  # ✓ Use this (Python 3.9+)
  items: list[str] = []
  config: dict[str, int] = {}
  
  # ✗ Not this (older style)
  items: List[str] = []
  config: Dict[str, int] = {}
  ```

### Comments & Documentation
- **Docstrings**: Use triple-quoted docstrings for functions and classes
  ```python
  def create_user(email: str, password: str) -> User:
      """
      Create a new user in the system.
      
      Args:
          email: User email address
          password: User password (will be hashed)
      
      Returns:
          User: Created user object
      
      Raises:
          ValueError: If email already exists
      """
      pass
  ```
- **Inline comments**: Keep them brief and meaningful
  ```python
  # ✓ Good
  # Use exponential backoff for retries
  wait_time = base_delay * (2 ** attempt)
  
  # ✗ Bad
  # increment count
  count += 1
  ```

## Database Guidelines

### Models (SQLAlchemy)
- **Table naming**: Use singular form
  - ✓ `user` table
  - ✗ `users` table
- **Primary keys**: Use UUID type for all primary keys
  ```python
  from sqlalchemy import Column, String
  from sqlalchemy.dialects.postgresql import UUID
  import uuid
  
  class User(Base):
      __tablename__ = "user"
      id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  ```
- **Timestamps**: Always include created_at and updated_at
  ```python
  from datetime import datetime
  
  created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
  ```
- **Relationships**: Define both forward and back references
  ```python
  class User(Base):
      workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
  
  class Workout(Base):
      user = relationship("User", back_populates="workouts")
  ```

### Migrations (Alembic)
- **Create migration**: `alembic revision -m "descriptive message"`
- **Run migration**: `alembic upgrade head`
- **Rollback**: `alembic downgrade -1`
- **Message format**: Use imperative mood
  - ✓ "Add user email column"
  - ✗ "Added user email column"

### Schemas (Pydantic)
- **Input validation**: Define request schemas
  ```python
  class UserCreate(BaseModel):
      email: str
      password: str
      
      class Config:
          from_attributes = True
  ```
- **Response schemas**: Define response models
  ```python
  class UserResponse(BaseModel):
      id: str
      email: str
      created_at: datetime
      
      class Config:
          from_attributes = True
  ```
- **Validation rules**: Use Pydantic validators
  ```python
  from pydantic import field_validator, EmailStr
  
  class UserCreate(BaseModel):
      email: EmailStr
      password: str
      
      @field_validator('password')
      @classmethod
      def password_strong(cls, v: str) -> str:
          if len(v) < 8:
              raise ValueError('Password must be at least 8 characters')
          return v
  ```

## API Guidelines

### Route Organization
- **Endpoint naming**: Use plural nouns for resources
  - ✓ `/api/v1/users`, `/api/v1/workouts`
  - ✗ `/api/v1/user`, `/api/v1/getWorkout`
- **HTTP methods**: Follow REST conventions
  - `GET /api/v1/users` - List all
  - `GET /api/v1/users/{id}` - Get one
  - `POST /api/v1/users` - Create
  - `PUT /api/v1/users/{id}` - Update
  - `DELETE /api/v1/users/{id}` - Delete
- **API versioning**: Include version in path
  - ✓ `/api/v1/users`
  - ✗ `/users`

### Route Definition
```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 10) -> list[UserResponse]:
    """List all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str) -> UserResponse:
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user."""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    # ... create user
    return user
```

### Response Format
All API responses follow a consistent structure:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "error": null
}
```

Error response:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Email format is invalid"
  }
}
```

### HTTP Status Codes
- `200 OK` - Successful GET, PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate email)
- `500 Internal Server Error` - Server error

## Error Handling

### Exception Handling
```python
from fastapi import HTTPException, status

# ✓ Good: Clear error details
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User with email 'test@example.com' not found"
)

# ✗ Bad: Generic error
raise HTTPException(status_code=404, detail="Not found")
```

### Logging Errors
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = process_user_data(user_id)
except ValueError as e:
    logger.error(f"Invalid user data for user {user_id}: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.exception(f"Unexpected error processing user {user_id}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Database Errors
```python
from sqlalchemy.exc import IntegrityError

try:
    db.add(user)
    db.commit()
except IntegrityError as e:
    db.rollback()
    if "duplicate key" in str(e):
        raise HTTPException(status_code=409, detail="Email already exists")
    raise HTTPException(status_code=400, detail="Invalid data")
```

## Authentication & Security

### Password Handling
- **Always hash passwords**: Use passlib
  ```python
  from passlib.context import CryptContext
  
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  
  hashed = pwd_context.hash(password)
  verified = pwd_context.verify(password, hashed)
  ```
- **Never store plain text**: Verify hashed value
- **Never log passwords**: Log only user identifier

### JWT Tokens
- **Create token**:
  ```python
  from jose import jwt
  from datetime import datetime, timedelta
  
  def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None):
      if expires_delta:
          expire = datetime.utcnow() + expires_delta
      else:
          expire = datetime.utcnow() + timedelta(hours=24)
      
      to_encode = {"sub": str(user_id), "exp": expire}
      return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  ```
- **Verify token**: Check expiration and signature
- **Token refresh**: Implement refresh token mechanism

### Input Validation
- **Validate all inputs**: Use Pydantic schemas
- **Sanitize strings**: Prevent injection attacks
- **Type checking**: Leverage Pydantic and type hints
- **Length limits**: Set max lengths on string fields

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_models.py
│   └── test_schemas.py
├── integration/
│   ├── test_api_users.py
│   └── test_api_workouts.py
└── conftest.py  # Shared fixtures
```

### Test Guidelines
- **Coverage**: Minimum 80% code coverage
- **Unit tests**: Test business logic and functions in isolation
- **Integration tests**: Test API endpoints with database
- **Naming**: `test_<function>_<scenario>`
  - ✓ `test_create_user_with_valid_email`
  - ✗ `test_user`
- **Fixtures**: Use pytest fixtures for setup/teardown
  ```python
  @pytest.fixture
  def test_user():
      user = User(email="test@example.com")
      db.add(user)
      db.commit()
      yield user
      db.delete(user)
      db.commit()
  ```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_auth.py

# Run specific test
pytest tests/unit/test_auth.py::test_hash_password
```

## Performance Best Practices

### Database Optimization
- **Use indexes**: Define indexes on frequently queried columns
  ```python
  from sqlalchemy import Index
  
  __table_args__ = (
      Index('ix_user_email', 'email', unique=True),
  )
  ```
- **Pagination**: Always implement limit and offset
  ```python
  items = db.query(Item).offset(skip).limit(limit).all()
  ```
- **Eager loading**: Use `joinedload()` to avoid N+1 queries
  ```python
  from sqlalchemy.orm import joinedload
  
  users = db.query(User).options(joinedload(User.workouts)).all()
  ```
- **Lazy loading awareness**: Understand when queries execute

### API Optimization
- **Response compression**: FastAPI handles gzip automatically
- **Caching**: Implement HTTP caching headers when appropriate
  ```python
  from fastapi.responses import Response
  
  @router.get("/users/{id}")
  def get_user(id: str):
      return Response(
          content=json.dumps(user_data),
          headers={"Cache-Control": "max-age=300"}  # 5 minutes
      )
  ```
- **Rate limiting**: Implement for public endpoints
- **Pagination**: Always use for list endpoints

## Dependencies Management

### Poetry Usage
```bash
# Add dependency
poetry add package_name

# Add dev dependency
poetry add --group dev package_name

# Install from lock file
poetry install

# Update dependencies
poetry update
```

### Common Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **python-jose**: JWT handling
- **passlib**: Password hashing
- **pytest**: Testing
- **black**: Code formatting
- **ruff**: Linting

## Development Workflow

### Local Development
1. Activate environment: `poetry shell`
2. Run migrations: `alembic upgrade head`
3. Start server: `uvicorn app.main:app --reload`
4. Access API docs: http://localhost:8000/docs

### Git Commits
- Write clear commit messages explaining the "why"
- Reference related issues: `Fixes #123`
- Keep commits focused on single features/fixes

### Before Committing
- Format code: `black app/`
- Lint code: `ruff check app/`
- Run tests: `pytest`
- Check migrations are created: `alembic current`
