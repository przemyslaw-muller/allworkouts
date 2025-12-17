from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.config import settings
from app.schemas import HealthResponse

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description='AllWorkouts API - Strength training workout tracker',
    version='0.1.0',
    docs_url='/docs',
    redoc_url='/redoc',
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:8000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health', response_model=HealthResponse, tags=['Health'])
async def health_check():
    '''Health check endpoint'''
    return HealthResponse(status='ok', timestamp=datetime.utcnow())


# Include API routes
app.include_router(api_router)

# Serve static files (frontend)
static_dir = Path(__file__).parent.parent / 'static'
if static_dir.exists():
    # Mount static assets
    app.mount('/assets', StaticFiles(directory=static_dir / 'assets'), name='assets')

    # Serve index.html for all non-API routes (SPA routing)
    @app.get('/{full_path:path}')
    async def serve_spa(full_path: str):
        # Skip if it's an API route
        if full_path.startswith('api/') or full_path in ['health', 'docs', 'redoc', 'openapi.json']:
            return None

        # Serve index.html for all other routes
        index_file = static_dir / 'index.html'
        if index_file.exists():
            return FileResponse(index_file)

        return {'message': 'Frontend not built'}
