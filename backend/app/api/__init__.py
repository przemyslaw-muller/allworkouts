'''
API routes package for AllWorkouts application.

This module aggregates all API sub-routers and exposes a single router
with the /api/v1 prefix.
'''

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.equipment import router as equipment_router
from app.api.exercises import router as exercises_router
from app.api.personal_records import router as personal_records_router
from app.api.stats import router as stats_router
from app.api.workout_plans import router as workout_plans_router
from app.api.workout_sessions import router as workout_sessions_router

# Create main API router with v1 prefix
router = APIRouter(prefix='/api/v1')

# Include all sub-routers
router.include_router(auth_router)
router.include_router(equipment_router)
router.include_router(exercises_router)
router.include_router(workout_plans_router)
router.include_router(workout_sessions_router)
router.include_router(personal_records_router)
router.include_router(stats_router)
