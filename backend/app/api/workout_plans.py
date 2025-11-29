'''
Workout Plan API routes.
'''

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models import Exercise, WorkoutExercise, WorkoutPlan
from app.schemas import (
    APIResponse,
    ExerciseBrief,
    PaginationInfo,
    WorkoutExerciseDetail,
    WorkoutPlanCreateRequest,
    WorkoutPlanCreateResponse,
    WorkoutPlanDetailResponse,
    WorkoutPlanListItem,
    WorkoutPlanListResponse,
    WorkoutPlanUpdateRequest,
    WorkoutPlanUpdateResponse,
)

router = APIRouter(prefix='/workout-plans', tags=['Workout Plans'])


@router.get(
    '',
    response_model=APIResponse[WorkoutPlanListResponse],
)
async def list_workout_plans(
    page: int = 1,
    limit: int = 20,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    List user's workout plans.

    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    '''
    # Validate pagination
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1

    # Query user's workout plans (exclude soft-deleted)
    query = db.query(WorkoutPlan).filter(
        WorkoutPlan.user_id == user_id,
        WorkoutPlan.deleted_at.is_(None),
    )

    # Get total count
    total = query.count()
    total_pages = (total + limit - 1) // limit

    # Apply pagination
    offset = (page - 1) * limit
    plans = query.order_by(WorkoutPlan.created_at.desc()).offset(offset).limit(limit).all()

    # Build response with exercise counts
    plan_list = []
    for plan in plans:
        exercise_count = (
            db.query(WorkoutExercise)
            .filter(WorkoutExercise.workout_plan_id == plan.id)
            .count()
        )
        plan_list.append(
            WorkoutPlanListItem(
                id=plan.id,
                name=plan.name,
                description=plan.description,
                exercise_count=exercise_count,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
            )
        )

    return APIResponse.success_response(
        WorkoutPlanListResponse(
            plans=plan_list,
            pagination=PaginationInfo(
                page=page,
                limit=limit,
                total=total,
                total_pages=total_pages,
            ),
        )
    )


@router.get(
    '/{plan_id}',
    response_model=APIResponse[WorkoutPlanDetailResponse],
)
async def get_workout_plan(
    plan_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Get workout plan details with all exercises.
    '''
    # Get the workout plan
    plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.deleted_at.is_(None),
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout plan not found',
        )

    # Get exercises with their details
    workout_exercises = (
        db.query(WorkoutExercise)
        .join(Exercise)
        .filter(WorkoutExercise.workout_plan_id == plan_id)
        .order_by(WorkoutExercise.sequence)
        .all()
    )

    exercise_details = []
    for we in workout_exercises:
        exercise = we.exercise
        exercise_details.append(
            WorkoutExerciseDetail(
                id=we.id,
                exercise=ExerciseBrief(
                    id=exercise.id,
                    name=exercise.name,
                    primary_muscle_groups=exercise.primary_muscle_groups,
                    secondary_muscle_groups=exercise.secondary_muscle_groups or [],
                ),
                sequence=we.sequence,
                sets=we.sets,
                reps_min=we.reps_min,
                reps_max=we.reps_max,
                rest_time_seconds=we.rest_time_seconds,
                confidence_level=we.confidence_level,
            )
        )

    return APIResponse.success_response(
        WorkoutPlanDetailResponse(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            exercises=exercise_details,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )
    )


@router.post(
    '',
    response_model=APIResponse[WorkoutPlanCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_workout_plan(
    request: WorkoutPlanCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Create a new workout plan with exercises.

    Validation:
    - Name: 1-200 chars
    - At least 1 exercise required
    - All exercise IDs must exist
    - Sets: 1-50, Reps: 1-200, Rest: 0-3600 seconds
    '''
    # Validate all exercise IDs exist
    exercise_ids = [ex.exercise_id for ex in request.exercises]
    existing_exercises = (
        db.query(Exercise.id).filter(Exercise.id.in_(exercise_ids)).all()
    )
    existing_ids = {ex.id for ex in existing_exercises}
    missing_ids = set(exercise_ids) - existing_ids

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Exercise IDs not found: {[str(id) for id in missing_ids]}',
        )

    # Create workout plan
    plan = WorkoutPlan(
        user_id=user_id,
        name=request.name,
        description=request.description,
    )
    db.add(plan)
    db.flush()  # Get the plan ID

    # Create workout exercises
    for ex in request.exercises:
        workout_exercise = WorkoutExercise(
            workout_plan_id=plan.id,
            exercise_id=ex.exercise_id,
            sequence=ex.sequence,
            sets=ex.sets,
            reps_min=ex.reps_min,
            reps_max=ex.reps_max,
            rest_time_seconds=ex.rest_time_seconds,
            confidence_level=ex.confidence_level,
        )
        db.add(workout_exercise)

    db.commit()
    db.refresh(plan)

    return APIResponse.success_response(
        WorkoutPlanCreateResponse(
            id=plan.id,
            name=plan.name,
            created_at=plan.created_at,
        )
    )


@router.put(
    '/{plan_id}',
    response_model=APIResponse[WorkoutPlanUpdateResponse],
)
async def update_workout_plan(
    plan_id: UUID,
    request: WorkoutPlanUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Update an existing workout plan.

    All fields are optional - only provided fields will be updated.
    If exercises are provided, all existing exercises are replaced.
    '''
    # Get the workout plan
    plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.deleted_at.is_(None),
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout plan not found',
        )

    # Update name and description if provided
    if request.name is not None:
        plan.name = request.name
    if request.description is not None:
        plan.description = request.description

    # Replace exercises if provided
    if request.exercises is not None:
        # Validate all exercise IDs exist
        exercise_ids = [ex.exercise_id for ex in request.exercises]
        existing_exercises = (
            db.query(Exercise.id).filter(Exercise.id.in_(exercise_ids)).all()
        )
        existing_ids = {ex.id for ex in existing_exercises}
        missing_ids = set(exercise_ids) - existing_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Exercise IDs not found: {[str(id) for id in missing_ids]}',
            )

        # Delete existing workout exercises
        db.query(WorkoutExercise).filter(
            WorkoutExercise.workout_plan_id == plan_id
        ).delete()

        # Create new workout exercises
        for ex in request.exercises:
            workout_exercise = WorkoutExercise(
                workout_plan_id=plan_id,
                exercise_id=ex.exercise_id,
                sequence=ex.sequence,
                sets=ex.sets,
                reps_min=ex.reps_min,
                reps_max=ex.reps_max,
                rest_time_seconds=ex.rest_time_seconds,
                confidence_level=ex.confidence_level,
            )
            db.add(workout_exercise)

    db.commit()
    db.refresh(plan)

    return APIResponse.success_response(
        WorkoutPlanUpdateResponse(
            id=plan.id,
            updated_at=plan.updated_at,
        )
    )


@router.delete(
    '/{plan_id}',
    response_model=APIResponse[None],
)
async def delete_workout_plan(
    plan_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Soft delete a workout plan.

    The plan and its exercises are not permanently deleted,
    but marked as deleted and excluded from queries.
    '''
    # Get the workout plan
    plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.deleted_at.is_(None),
        )
        .first()
    )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout plan not found',
        )

    # Soft delete the plan
    plan.deleted_at = datetime.utcnow()
    db.commit()

    return APIResponse.success_response(None)
