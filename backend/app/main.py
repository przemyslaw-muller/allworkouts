from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health', response_model=HealthResponse, tags=['Health'])
async def health_check():
    '''Health check endpoint'''
    return HealthResponse(status='ok', timestamp=datetime.utcnow())


@app.get('/', tags=['Root'])
async def root():
    '''Root endpoint'''
    return {
        'message': 'AllWorkouts API',
        'version': '0.1.0',
        'docs': '/docs',
        'health': '/health',
    }


# Include API routes
app.include_router(api_router)
