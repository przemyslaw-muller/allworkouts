# E2E Tests

End-to-end tests for AllWorkouts application using Playwright.

## Setup

1. Install dependencies:
```bash
cd e2e
uv pip install -e .
python -m playwright install
```

Or using requirements.txt:
```bash
cd e2e
uv pip install -r requirements.txt
python -m playwright install
```

2. Set environment variables:
```bash
# Create .env file in e2e directory
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

3. Ensure backend and frontend are running before running tests

## Running Tests

```bash
# From e2e directory
cd e2e

# Run all tests
pytest

# Run specific test
pytest tests/test_workout_flow.py

# Run with headed browser (see what's happening)
pytest --headed

# Run with slower execution for debugging
pytest --headed --slowmo 1000

# Run only smoke tests
pytest -m smoke
```

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `fixtures/` - Test data fixtures
- `pages/` - Page Object Model classes
- `tests/` - Test files
