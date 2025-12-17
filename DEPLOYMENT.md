# AllWorkouts Deployment

This project includes a production Dockerfile that builds both frontend and backend into a single container.

## Production Build

The root [Dockerfile](Dockerfile) creates a multi-stage build that:
1. Builds the Vue frontend as static files
2. Bundles them with the FastAPI backend
3. Serves the frontend from the backend container

### Building for Production

```bash
# Build the production image
docker build -t allworkouts:latest .

# Run the production container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/dbname \
  -e JWT_SECRET_KEY=your-secret-key \
  allworkouts:latest
```

### Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens

Optional:
- `DEBUG`: Set to "true" for debug mode (default: false)

## Development Setup

For development, use docker-compose which runs backend with hot-reload:

```bash
# Start services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend should be run separately with: cd frontend && npm run dev
```

## How It Works

### Static File Serving

The [backend/app/main.py](backend/app/main.py) is configured to:
- Serve API routes under `/api/`
- Serve static frontend assets under `/assets/`
- Return `index.html` for all other routes (SPA routing)

### API Routes

All API endpoints remain under `/api/` prefix:
- `/api/auth/*` - Authentication
- `/api/workouts/*` - Workout management
- `/api/exercises/*` - Exercise management
- etc.

### Frontend Routes

The frontend router handles all SPA routes, served from the backend:
- `/` - Dashboard
- `/login` - Login page
- `/workouts` - Workouts page
- etc.

## Architecture Benefits

✅ Single container deployment  
✅ Simplified networking (no CORS issues)  
✅ Reduced infrastructure complexity  
✅ Easier deployment to cloud platforms  
✅ Built-in static file caching
