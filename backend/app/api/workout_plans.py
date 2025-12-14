"""
Workout Plan API routes.
"""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models import Exercise, Workout, WorkoutExercise, WorkoutImportLog, WorkoutPlan
from app.schemas import (
    APIResponse,
    ExerciseBrief,
    PaginationInfo,
    WorkoutDetail,
    WorkoutExerciseDetail,
    WorkoutPlanCreateRequest,
    WorkoutPlanCreateResponse,
    WorkoutPlanDetailResponse,
    WorkoutPlanFromParsedRequest,
    WorkoutPlanListItem,
    WorkoutPlanListResponse,
    WorkoutPlanParseRequest,
    WorkoutPlanParseResponse,
    WorkoutPlanToggleActiveRequest,
    WorkoutPlanToggleActiveResponse,
    WorkoutPlanUpdateRequest,
    WorkoutPlanUpdateResponse,
)
from app.services.parser_service import ParserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workout-plans", tags=["Workout Plans"])


@router.get(
    "",
    response_model=APIResponse[WorkoutPlanListResponse],
)
async def list_workout_plans(
    page: int = 1,
    limit: int = 20,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    List user's workout plans.

    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    """
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

    # Build response with workout and exercise counts
    plan_list = []
    for plan in plans:
        # Count workouts in this plan
        workout_count = db.query(Workout).filter(Workout.workout_plan_id == plan.id).count()

        # Count total exercises across all workouts in this plan
        exercise_count = (
            db.query(WorkoutExercise)
            .join(Workout)
            .filter(Workout.workout_plan_id == plan.id)
            .count()
        )

        plan_list.append(
            WorkoutPlanListItem(
                id=plan.id,
                name=plan.name,
                description=plan.description,
                is_active=plan.is_active,
                workout_count=workout_count,
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
    "/{plan_id}",
    response_model=APIResponse[WorkoutPlanDetailResponse],
)
async def get_workout_plan(
    plan_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get workout plan details with all workouts and exercises.
    """
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
            detail="Workout plan not found",
        )

    # Get all workouts in this plan, ordered by order_index
    workouts = (
        db.query(Workout)
        .filter(Workout.workout_plan_id == plan_id)
        .order_by(Workout.order_index)
        .all()
    )

    workout_details = []
    for workout in workouts:
        # Get exercises for this workout
        workout_exercises = (
            db.query(WorkoutExercise)
            .join(Exercise)
            .filter(WorkoutExercise.workout_id == workout.id)
            .order_by(WorkoutExercise.sequence)
            .all()
        )

        exercise_details = []
        for we in workout_exercises:
            exercise = we.exercise
            from app.schemas.workout_plans import SetConfig
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
                    set_configurations=[
                        SetConfig(**config) for config in we.set_configurations
                    ],
                    rest_time_seconds=we.rest_time_seconds,
                    confidence_level=we.confidence_level,
                )
            )

        workout_details.append(
            WorkoutDetail(
                id=workout.id,
                name=workout.name,
                day_number=workout.day_number,
                order_index=workout.order_index,
                exercises=exercise_details,
                created_at=workout.created_at,
                updated_at=workout.updated_at,
            )
        )

    return APIResponse.success_response(
        WorkoutPlanDetailResponse(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            is_active=plan.is_active,
            workouts=workout_details,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )
    )


@router.post(
    "",
    response_model=APIResponse[WorkoutPlanCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_workout_plan(
    request: WorkoutPlanCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new workout plan with nested workouts and exercises.

    Validation:
    - Name: 1-200 chars
    - At least 1 workout required
    - Each workout must have at least 1 exercise
    - All exercise IDs must exist
    - Sets: 1-50, Reps: 1-200, Rest: 0-3600 seconds
    """
    # Collect all exercise IDs from all workouts
    all_exercise_ids = []
    for workout in request.workouts:
        for ex in workout.exercises:
            all_exercise_ids.append(ex.exercise_id)

    # Validate all exercise IDs exist
    if all_exercise_ids:
        existing_exercises = db.query(Exercise.id).filter(Exercise.id.in_(all_exercise_ids)).all()
        existing_ids = {ex.id for ex in existing_exercises}
        missing_ids = set(all_exercise_ids) - existing_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exercise IDs not found: {[str(id) for id in missing_ids]}",
            )

    # Create workout plan
    plan = WorkoutPlan(
        user_id=user_id,
        name=request.name,
        description=request.description,
    )
    db.add(plan)
    db.flush()  # Get the plan ID

    # Create workouts and their exercises
    for workout_data in request.workouts:
        workout = Workout(
            workout_plan_id=plan.id,
            name=workout_data.name,
            day_number=workout_data.day_number,
            order_index=workout_data.order_index,
        )
        db.add(workout)
        db.flush()  # Get the workout ID

        # Create workout exercises
        for ex in workout_data.exercises:
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=ex.exercise_id,
                sequence=ex.sequence,
                set_configurations=[
                    {"set_number": s.set_number, "reps_min": s.reps_min, "reps_max": s.reps_max}
                    for s in ex.set_configurations
                ],
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
    "/{plan_id}",
    response_model=APIResponse[WorkoutPlanUpdateResponse],
)
async def update_workout_plan(
    plan_id: UUID,
    request: WorkoutPlanUpdateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update an existing workout plan.

    All fields are optional - only provided fields will be updated.
    If workouts are provided, all existing workouts and exercises are replaced.
    """
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
            detail="Workout plan not found",
        )

    # Update name and description if provided
    if request.name is not None:
        plan.name = request.name
    if request.description is not None:
        plan.description = request.description

    # Replace workouts if provided
    if request.workouts is not None:
        # Collect all exercise IDs from all workouts
        all_exercise_ids = []
        for workout in request.workouts:
            for ex in workout.exercises:
                all_exercise_ids.append(ex.exercise_id)

        # Validate all exercise IDs exist
        if all_exercise_ids:
            existing_exercises = (
                db.query(Exercise.id).filter(Exercise.id.in_(all_exercise_ids)).all()
            )
            existing_ids = {ex.id for ex in existing_exercises}
            missing_ids = set(all_exercise_ids) - existing_ids

            if missing_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Exercise IDs not found: {[str(id) for id in missing_ids]}",
                )

        # Delete existing workouts (cascade deletes workout_exercises)
        db.query(Workout).filter(Workout.workout_plan_id == plan_id).delete()

        # Create new workouts and their exercises
        for workout_data in request.workouts:
            workout = Workout(
                workout_plan_id=plan_id,
                name=workout_data.name,
                day_number=workout_data.day_number,
                order_index=workout_data.order_index,
            )
            db.add(workout)
            db.flush()  # Get the workout ID

            # Create workout exercises
            for ex in workout_data.exercises:
                workout_exercise = WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=ex.exercise_id,
                    sequence=ex.sequence,
                    set_configurations=[
                        {"set_number": s.set_number, "reps_min": s.reps_min, "reps_max": s.reps_max}
                        for s in ex.set_configurations
                    ],
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


@router.patch(
    "/{plan_id}/active",
    response_model=APIResponse[WorkoutPlanToggleActiveResponse],
)
async def toggle_workout_plan_active(
    plan_id: UUID,
    request: WorkoutPlanToggleActiveRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Toggle the active status of a workout plan.

    Only one plan can be active at a time per user.
    Setting a plan as active will deactivate any other active plan.
    """
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
            detail="Workout plan not found",
        )

    if request.is_active:
        # Deactivate all other plans for this user
        db.query(WorkoutPlan).filter(
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.deleted_at.is_(None),
            WorkoutPlan.id != plan_id,
        ).update({"is_active": False})

    # Set the active status
    plan.is_active = request.is_active

    db.commit()
    db.refresh(plan)

    return APIResponse.success_response(
        WorkoutPlanToggleActiveResponse(
            id=plan.id,
            is_active=plan.is_active,
            updated_at=plan.updated_at,
        )
    )


@router.delete(
    "/{plan_id}",
    response_model=APIResponse[None],
)
async def delete_workout_plan(
    plan_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Soft delete a workout plan.

    The plan and its workouts/exercises are not permanently deleted,
    but marked as deleted and excluded from queries.
    """
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
            detail="Workout plan not found",
        )

    # Soft delete the plan
    plan.deleted_at = datetime.utcnow()
    # Also deactivate if it was active
    plan.is_active = False
    db.commit()

    return APIResponse.success_response(None)


@router.post(
    "/parse",
    response_model=APIResponse[dict],
    status_code=status.HTTP_202_ACCEPTED,
)
async def parse_workout_plan(
    request: WorkoutPlanParseRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Parse workout plan from text using AI (Step 1 of import).

    This endpoint:
    1. Creates an import log with 'pending' status
    2. Starts background processing
    3. Returns import_log_id immediately for polling

    Client should poll /parse/status/{import_log_id} for results.

    Rate limit: 10 requests per hour per user
    """
    # Create import log with pending status
    import_log = WorkoutImportLog(
        user_id=user_id,
        raw_text=request.text,
        status='pending',
        created_at=datetime.utcnow(),
    )
    db.add(import_log)
    db.commit()
    db.refresh(import_log)

    # Start background task
    import asyncio
    from app.database import SessionLocal
    
    async def process_parsing():
        # Create new DB session for background task
        bg_db = SessionLocal()
        try:
            # Update status to processing
            bg_import_log = bg_db.query(WorkoutImportLog).filter(
                WorkoutImportLog.id == import_log.id
            ).first()
            bg_import_log.status = 'processing'
            bg_db.commit()
            
            # Parse the workout
            parser = ParserService(bg_db, user_id)
            result = await parser.parse_workout_plan(request.text)
            
            # Update import log with result
            bg_import_log.status = 'completed'
            bg_import_log.result = {
                'parsed_plan': result.parsed_plan.model_dump(mode='json'),
                'total_exercises': result.total_exercises,
                'high_confidence_count': result.high_confidence_count,
                'medium_confidence_count': result.medium_confidence_count,
                'low_confidence_count': result.low_confidence_count,
                'unmatched_count': result.unmatched_count,
            }
            bg_import_log.parsed_exercises = result.parsed_plan.model_dump(mode='json').get('workouts', [])
            bg_import_log.confidence_scores = {
                'high_confidence': result.high_confidence_count,
                'medium_confidence': result.medium_confidence_count,
                'low_confidence': result.low_confidence_count,
                'unmatched': result.unmatched_count,
            }
            bg_db.commit()
            logger.info(f"Parse completed for import_log {import_log.id}")
        except Exception as e:
            logger.error(f"Parse failed for import_log {import_log.id}: {str(e)}")
            bg_import_log = bg_db.query(WorkoutImportLog).filter(
                WorkoutImportLog.id == import_log.id
            ).first()
            if bg_import_log:
                bg_import_log.status = 'failed'
                bg_import_log.error = str(e)
                bg_db.commit()
        finally:
            bg_db.close()
    
    # Fire and forget the background task
    asyncio.create_task(process_parsing())
    
    return APIResponse.success_response({
        'import_log_id': str(import_log.id),
        'status': 'pending',
        'message': 'Parsing started. Poll /parse/status/{import_log_id} for results.'
    })


@router.get(
    "/parse/status/{import_log_id}",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def get_parse_status(
    import_log_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get the status of a workout plan parsing operation.

    Poll this endpoint to check if parsing is complete.

    Status values:
    - pending: Queued for processing
    - processing: Currently being parsed
    - completed: Parsing finished successfully
    - failed: Parsing failed with an error
    """
    import_log = db.query(WorkoutImportLog).filter(
        WorkoutImportLog.id == import_log_id,
        WorkoutImportLog.user_id == user_id,
    ).first()

    if not import_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import log not found",
        )

    response_data = {
        'import_log_id': str(import_log.id),
        'status': import_log.status,
    }

    if import_log.status == 'completed' and import_log.result:
        response_data['result'] = import_log.result
    elif import_log.status == 'failed' and import_log.error:
        response_data['error'] = import_log.error

    return APIResponse.success_response(response_data)


@router.post(
    "/from-parsed",
    response_model=APIResponse[WorkoutPlanCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_workout_plan_from_parsed(
    request: WorkoutPlanFromParsedRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create workout plan from parsed data (Step 2 of import).

    This endpoint takes the import_log_id from the parse response
    and creates the actual workout plan with user-confirmed workouts and exercises.
    """
    # Verify import log exists and belongs to user
    import_log = (
        db.query(WorkoutImportLog)
        .filter(
            WorkoutImportLog.id == request.import_log_id,
            WorkoutImportLog.user_id == user_id,
        )
        .first()
    )

    if not import_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import log not found",
        )

    if import_log.workout_plan_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workout plan already created from this import",
        )

    # Collect all exercise IDs from all workouts
    all_exercise_ids = []
    for workout in request.workouts:
        for ex in workout.exercises:
            all_exercise_ids.append(ex.exercise_id)

    # Validate all exercise IDs exist
    if all_exercise_ids:
        existing_exercises = db.query(Exercise.id).filter(Exercise.id.in_(all_exercise_ids)).all()
        existing_ids = {ex.id for ex in existing_exercises}
        missing_ids = set(all_exercise_ids) - existing_ids

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exercise IDs not found: {[str(id) for id in missing_ids]}",
            )

    # Create workout plan
    plan = WorkoutPlan(user_id=user_id, name=request.name, description=request.description)
    db.add(plan)
    db.flush()

    # Create workouts and their exercises
    for workout_data in request.workouts:
        workout = Workout(
            workout_plan_id=plan.id,
            name=workout_data.name,
            day_number=workout_data.day_number,
            order_index=workout_data.order_index,
        )
        db.add(workout)
        db.flush()  # Get the workout ID

        # Create workout exercises
        for ex in workout_data.exercises:
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=ex.exercise_id,
                sequence=ex.sequence,
                set_configurations=[
                    {"set_number": s.set_number, "reps_min": s.reps_min, "reps_max": s.reps_max}
                    for s in ex.set_configurations
                ],
                rest_time_seconds=ex.rest_time_seconds,
                confidence_level=ex.confidence_level,
            )
            db.add(workout_exercise)

    # Link import log to created plan
    import_log.workout_plan_id = plan.id

    db.commit()
    db.refresh(plan)

    logger.info(f"Created workout plan {plan.id} from import log {import_log.id}")

    return APIResponse.success_response(
        WorkoutPlanCreateResponse(
            id=plan.id,
            name=plan.name,
            created_at=plan.created_at,
        )
    )
