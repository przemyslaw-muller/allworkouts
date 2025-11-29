'''
API routes for AllWorkouts application.
'''

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.database import get_db
from app.enums import RecordTypeEnum, SessionStatusEnum
from app.models import (
    Equipment,
    Exercise,
    ExerciseEquipment,
    ExerciseSession,
    PersonalRecord,
    User,
    UserEquipment,
    WorkoutExercise,
    WorkoutPlan,
    WorkoutSession,
)
from app.schemas import (
    APIResponse,
    AuthResponse,
    AuthUserResponse,
    CompleteSessionRequest,
    CompleteSessionResponse,
    EquipmentBrief,
    EquipmentListItem,
    EquipmentOwnershipRequest,
    EquipmentOwnershipResponse,
    ExerciseBrief,
    ExerciseContextInfo,
    ExerciseDetailResponse,
    ExerciseHistoryResponse,
    ExerciseHistorySession,
    ExerciseHistorySet,
    ExerciseListItem,
    ExerciseListResponse,
    ExerciseSessionDetail,
    ExerciseSubstituteItem,
    LogExerciseRequest,
    LogExerciseResponse,
    LoginRequest,
    MonthlyWorkoutCount,
    MuscleGroupTrainingCount,
    NewPersonalRecordInfo,
    PaginationInfo,
    PersonalRecordBrief,
    PersonalRecordCreateRequest,
    PersonalRecordCreateResponse,
    PersonalRecordExerciseInfo,
    PersonalRecordListItem,
    PersonalRecordListResponse,
    PlannedExerciseWithContext,
    RecentSessionInfo,
    RecentSetInfo,
    RefreshResponse,
    RefreshTokenRequest,
    RegisterRequest,
    SkipSessionRequest,
    SkipSessionResponse,
    StatsOverviewResponse,
    WorkoutExerciseDetail,
    WorkoutPlanBrief,
    WorkoutPlanCreateRequest,
    WorkoutPlanCreateResponse,
    WorkoutPlanDetailResponse,
    WorkoutPlanListItem,
    WorkoutPlanListResponse,
    WorkoutPlanUpdateRequest,
    WorkoutPlanUpdateResponse,
    WorkoutSessionDetailResponse,
    WorkoutSessionListItem,
    WorkoutSessionListResponse,
    WorkoutSessionStartRequest,
    WorkoutSessionStartResponse,
)

# Create API router with v1 prefix
router = APIRouter(prefix='/api/v1')


# =============================================================================
# Authentication Endpoints
# =============================================================================


@router.post(
    '/auth/register',
    response_model=APIResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
    tags=['Authentication'],
)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    '''
    Register a new user account.

    Returns user data and JWT tokens on success.
    '''
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return APIResponse.error_response(
            code='VALIDATION_EMAIL_EXISTS',
            message='Email already registered',
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return APIResponse.success_response(
        AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )
    )


@router.post(
    '/auth/login',
    response_model=APIResponse[AuthResponse],
    tags=['Authentication'],
)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    '''
    Authenticate user and return JWT tokens.
    '''
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return APIResponse.error_response(
            code='AUTH_INVALID_CREDENTIALS',
            message='Invalid email or password',
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        return APIResponse.error_response(
            code='AUTH_INVALID_CREDENTIALS',
            message='Invalid email or password',
        )

    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return APIResponse.success_response(
        AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                created_at=user.created_at,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )
    )


@router.post(
    '/auth/refresh',
    response_model=APIResponse[RefreshResponse],
    tags=['Authentication'],
)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    '''
    Refresh access token using a valid refresh token.
    '''
    # Verify refresh token
    user_id = verify_refresh_token(request.refresh_token)
    if user_id is None:
        return APIResponse.error_response(
            code='AUTH_TOKEN_INVALID',
            message='Invalid or expired refresh token',
        )

    # Verify user still exists
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        return APIResponse.error_response(
            code='AUTH_TOKEN_INVALID',
            message='User not found',
        )

    # Generate new access token
    access_token = create_access_token(str(user.id))

    return APIResponse.success_response(
        RefreshResponse(access_token=access_token)
    )


# =============================================================================
# Equipment Endpoints
# =============================================================================


@router.get(
    '/equipment',
    response_model=APIResponse[List[EquipmentListItem]],
    tags=['Equipment'],
)
async def list_equipment(
    search: Optional[str] = None,
    user_owned: Optional[bool] = None,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    List all available equipment with user ownership status.

    Query Parameters:
    - search: Filter by name (case-insensitive partial match)
    - user_owned: Filter by user ownership (true/false)
    '''
    # Base query for all equipment
    query = db.query(Equipment)

    # Apply search filter
    if search:
        query = query.filter(Equipment.name.ilike(f'%{search}%'))

    # Get all equipment
    all_equipment = query.order_by(Equipment.name).all()

    # Get user's owned equipment IDs (excluding soft-deleted)
    user_owned_ids = set(
        row[0]
        for row in db.query(UserEquipment.equipment_id)
        .filter(
            UserEquipment.user_id == user_id,
            UserEquipment.deleted_at.is_(None),
        )
        .all()
    )

    # Build response with ownership status
    equipment_list = []
    for eq in all_equipment:
        is_owned = eq.id in user_owned_ids

        # Apply user_owned filter if specified
        if user_owned is not None and is_owned != user_owned:
            continue

        equipment_list.append(
            EquipmentListItem(
                id=eq.id,
                name=eq.name,
                description=eq.description,
                is_user_owned=is_owned,
            )
        )

    return APIResponse.success_response(equipment_list)


@router.put(
    '/equipment/{equipment_id}/ownership',
    response_model=APIResponse[EquipmentOwnershipResponse],
    tags=['Equipment'],
)
async def update_equipment_ownership(
    equipment_id: UUID,
    request: EquipmentOwnershipRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Mark equipment as owned or not owned by the current user.

    Uses soft delete pattern for ownership tracking.
    '''
    # Verify equipment exists
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Equipment not found',
        )

    # Find existing ownership record (including soft-deleted)
    user_equipment = (
        db.query(UserEquipment)
        .filter(
            UserEquipment.user_id == user_id,
            UserEquipment.equipment_id == equipment_id,
        )
        .first()
    )

    if request.is_owned:
        # User wants to own this equipment
        if user_equipment is None:
            # Create new ownership record
            user_equipment = UserEquipment(
                user_id=user_id,
                equipment_id=equipment_id,
            )
            db.add(user_equipment)
        else:
            # Restore soft-deleted record
            user_equipment.deleted_at = None
    else:
        # User wants to remove ownership
        if user_equipment is not None and user_equipment.deleted_at is None:
            # Soft delete the ownership record
            user_equipment.deleted_at = datetime.utcnow()

    db.commit()

    return APIResponse.success_response(
        EquipmentOwnershipResponse(
            equipment_id=equipment_id,
            is_owned=request.is_owned,
        )
    )


# =============================================================================
# Exercise Endpoints
# =============================================================================


def _get_exercise_equipment(db: Session, exercise_id: UUID) -> List[EquipmentBrief]:
    '''Helper to get equipment for an exercise'''
    equipment_links = (
        db.query(Equipment)
        .join(ExerciseEquipment)
        .filter(ExerciseEquipment.exercise_id == exercise_id)
        .all()
    )
    return [
        EquipmentBrief(id=eq.id, name=eq.name, description=eq.description)
        for eq in equipment_links
    ]


@router.get(
    '/exercises',
    response_model=APIResponse[ExerciseListResponse],
    tags=['Exercises'],
)
async def list_exercises(
    search: Optional[str] = None,
    muscle_group: Optional[str] = None,
    equipment_id: Optional[UUID] = None,
    user_can_perform: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    List exercises with optional filtering.

    Query Parameters:
    - search: Filter by name (case-insensitive partial match)
    - muscle_group: Filter by primary muscle group
    - equipment_id: Filter by required equipment
    - user_can_perform: Filter by user's owned equipment (true/false)
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 100)
    '''
    # Validate pagination
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1

    # Base query
    query = db.query(Exercise)

    # Apply search filter
    if search:
        query = query.filter(Exercise.name.ilike(f'%{search}%'))

    # Apply muscle group filter
    if muscle_group:
        query = query.filter(Exercise.primary_muscle_groups.any(muscle_group))

    # Apply equipment filter
    if equipment_id:
        query = query.join(ExerciseEquipment).filter(ExerciseEquipment.equipment_id == equipment_id)

    # Get user's owned equipment IDs for filtering
    user_owned_equipment_ids = set()
    if user_can_perform is not None:
        user_owned_equipment_ids = set(
            row[0]
            for row in db.query(UserEquipment.equipment_id)
            .filter(
                UserEquipment.user_id == user_id,
                UserEquipment.deleted_at.is_(None),
            )
            .all()
        )

    # Get total count before pagination
    total = query.count()
    total_pages = (total + limit - 1) // limit

    # Apply pagination
    offset = (page - 1) * limit
    exercises = query.order_by(Exercise.name).offset(offset).limit(limit).all()

    # Build response
    exercise_list = []
    for ex in exercises:
        # Get equipment for this exercise
        equipment = _get_exercise_equipment(db, ex.id)
        equipment_ids = {eq.id for eq in equipment}

        # Filter by user_can_perform if specified
        if user_can_perform is not None:
            can_perform = len(equipment_ids) == 0 or equipment_ids.issubset(user_owned_equipment_ids)
            if user_can_perform and not can_perform:
                continue
            if not user_can_perform and can_perform:
                continue

        exercise_list.append(
            ExerciseListItem(
                id=ex.id,
                name=ex.name,
                description=ex.description,
                primary_muscle_groups=ex.primary_muscle_groups,
                secondary_muscle_groups=ex.secondary_muscle_groups or [],
                equipment=equipment,
            )
        )

    return APIResponse.success_response(
        ExerciseListResponse(
            exercises=exercise_list,
            pagination=PaginationInfo(
                page=page,
                limit=limit,
                total=total,
                total_pages=total_pages,
            ),
        )
    )


@router.get(
    '/exercises/{exercise_id}',
    response_model=APIResponse[ExerciseDetailResponse],
    tags=['Exercises'],
)
async def get_exercise(
    exercise_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Get single exercise details with equipment and personal records.
    '''
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Exercise not found',
        )

    # Get equipment for this exercise
    equipment = _get_exercise_equipment(db, exercise_id)

    # Get user's personal records for this exercise
    prs = (
        db.query(PersonalRecord)
        .filter(
            PersonalRecord.user_id == user_id,
            PersonalRecord.exercise_id == exercise_id,
        )
        .all()
    )
    personal_records = [
        PersonalRecordBrief(
            id=pr.id,
            record_type=pr.record_type,
            value=pr.value,
            unit=pr.unit,
            achieved_at=pr.achieved_at,
        )
        for pr in prs
    ]

    return APIResponse.success_response(
        ExerciseDetailResponse(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            primary_muscle_groups=exercise.primary_muscle_groups,
            secondary_muscle_groups=exercise.secondary_muscle_groups or [],
            default_weight=exercise.default_weight,
            default_reps=exercise.default_reps,
            default_rest_time_seconds=exercise.default_rest_time_seconds,
            equipment=equipment,
            personal_records=personal_records,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
        )
    )


@router.get(
    '/exercises/{exercise_id}/substitutes',
    response_model=APIResponse[List[ExerciseSubstituteItem]],
    tags=['Exercises'],
)
async def get_exercise_substitutes(
    exercise_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Get exercise substitution suggestions.

    Business Logic:
    1. Find exercises with overlapping muscle groups
    2. Filter by user's owned equipment
    3. Exclude the original exercise
    4. Sort by muscle group overlap (more overlap = better match)
    '''
    # Get the original exercise
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Exercise not found',
        )

    # Get user's owned equipment
    user_owned_equipment_ids = set(
        row[0]
        for row in db.query(UserEquipment.equipment_id)
        .filter(
            UserEquipment.user_id == user_id,
            UserEquipment.deleted_at.is_(None),
        )
        .all()
    )

    # Get original exercise muscle groups
    original_primary = set(exercise.primary_muscle_groups or [])
    original_secondary = set(exercise.secondary_muscle_groups or [])
    original_all = original_primary | original_secondary

    # Find all other exercises
    other_exercises = (
        db.query(Exercise)
        .filter(Exercise.id != exercise_id)
        .all()
    )

    substitutes = []
    for ex in other_exercises:
        # Get equipment for this exercise
        equipment = _get_exercise_equipment(db, ex.id)
        equipment_ids = {eq.id for eq in equipment}

        # Check if user can perform this exercise (has required equipment or no equipment needed)
        can_perform = len(equipment_ids) == 0 or equipment_ids.issubset(user_owned_equipment_ids)
        if not can_perform:
            continue

        # Calculate muscle group overlap
        ex_primary = set(ex.primary_muscle_groups or [])
        ex_secondary = set(ex.secondary_muscle_groups or [])
        ex_all = ex_primary | ex_secondary

        # Calculate match score based on overlap
        if len(original_all) == 0:
            match_score = 0.0
        else:
            # Primary muscle overlap is weighted more heavily
            primary_overlap = len(original_primary & ex_primary)
            secondary_overlap = len((original_all & ex_all) - (original_primary & ex_primary))

            # Score: 70% primary overlap, 30% secondary overlap
            max_primary = max(len(original_primary), 1)
            max_total = max(len(original_all), 1)
            match_score = (0.7 * primary_overlap / max_primary) + (0.3 * secondary_overlap / max_total)

        # Only include if there's some overlap
        if match_score > 0:
            substitutes.append(
                ExerciseSubstituteItem(
                    id=ex.id,
                    name=ex.name,
                    description=ex.description,
                    primary_muscle_groups=ex.primary_muscle_groups,
                    secondary_muscle_groups=ex.secondary_muscle_groups or [],
                    equipment=equipment,
                    match_score=round(match_score, 2),
                )
            )

    # Sort by match score (highest first)
    substitutes.sort(key=lambda x: x.match_score, reverse=True)

    # Limit to top 10 substitutes
    return APIResponse.success_response(substitutes[:10])


# =============================================================================
# Workout Plan Endpoints
# =============================================================================


@router.get(
    '/workout-plans',
    response_model=APIResponse[WorkoutPlanListResponse],
    tags=['Workout Plans'],
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
    '/workout-plans/{plan_id}',
    response_model=APIResponse[WorkoutPlanDetailResponse],
    tags=['Workout Plans'],
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
    '/workout-plans',
    response_model=APIResponse[WorkoutPlanCreateResponse],
    status_code=status.HTTP_201_CREATED,
    tags=['Workout Plans'],
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
    '/workout-plans/{plan_id}',
    response_model=APIResponse[WorkoutPlanUpdateResponse],
    tags=['Workout Plans'],
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
    '/workout-plans/{plan_id}',
    response_model=APIResponse[None],
    tags=['Workout Plans'],
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


# =============================================================================
# Workout Session Endpoints
# =============================================================================


@router.get(
    '/workout-sessions',
    response_model=APIResponse[WorkoutSessionListResponse],
    tags=['Workout Sessions'],
)
async def list_workout_sessions(
    workout_plan_id: Optional[UUID] = None,
    status_filter: Optional[SessionStatusEnum] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 20,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    List workout sessions (history).

    Query Parameters:
    - workout_plan_id: Filter by workout plan
    - status_filter: Filter by status (in_progress, completed, skipped)
    - start_date: Filter by date range start
    - end_date: Filter by date range end
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    '''
    # Validate pagination
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1

    # Base query
    query = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.deleted_at.is_(None),
    )

    # Apply filters
    if workout_plan_id:
        query = query.filter(WorkoutSession.workout_plan_id == workout_plan_id)
    if status_filter:
        query = query.filter(WorkoutSession.status == status_filter)
    if start_date:
        query = query.filter(WorkoutSession.created_at >= start_date)
    if end_date:
        query = query.filter(WorkoutSession.created_at <= end_date)

    # Get total count
    total = query.count()
    total_pages = (total + limit - 1) // limit

    # Apply pagination (order by most recent first)
    offset = (page - 1) * limit
    sessions = query.order_by(WorkoutSession.created_at.desc()).offset(offset).limit(limit).all()

    # Build response
    session_list = []
    for session in sessions:
        # Get exercise count for this session
        exercise_count = (
            db.query(ExerciseSession)
            .filter(ExerciseSession.workout_session_id == session.id)
            .distinct(ExerciseSession.exercise_id)
            .count()
        )

        # Get workout plan info
        workout_plan = session.workout_plan

        session_list.append(
            WorkoutSessionListItem(
                id=session.id,
                workout_plan=WorkoutPlanBrief(
                    id=workout_plan.id,
                    name=workout_plan.name,
                ),
                status=session.status,
                exercise_count=exercise_count,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
        )

    return APIResponse.success_response(
        WorkoutSessionListResponse(
            sessions=session_list,
            pagination=PaginationInfo(
                page=page,
                limit=limit,
                total=total,
                total_pages=total_pages,
            ),
        )
    )


@router.get(
    '/workout-sessions/{session_id}',
    response_model=APIResponse[WorkoutSessionDetailResponse],
    tags=['Workout Sessions'],
)
async def get_workout_session(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Get workout session details with all exercise sessions.
    '''
    # Get the session
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
            WorkoutSession.deleted_at.is_(None),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout session not found',
        )

    # Get exercise sessions with exercise details
    exercise_sessions = (
        db.query(ExerciseSession)
        .join(Exercise)
        .filter(ExerciseSession.workout_session_id == session_id)
        .order_by(ExerciseSession.set_number)
        .all()
    )

    exercise_session_details = []
    for es in exercise_sessions:
        exercise = es.exercise
        exercise_session_details.append(
            ExerciseSessionDetail(
                id=es.id,
                exercise=ExerciseBrief(
                    id=exercise.id,
                    name=exercise.name,
                    primary_muscle_groups=exercise.primary_muscle_groups,
                    secondary_muscle_groups=exercise.secondary_muscle_groups or [],
                ),
                set_number=es.set_number,
                weight=es.weight,
                reps=es.reps,
                rest_time_seconds=es.rest_time_seconds,
                created_at=es.created_at,
            )
        )

    workout_plan = session.workout_plan

    return APIResponse.success_response(
        WorkoutSessionDetailResponse(
            id=session.id,
            workout_plan=WorkoutPlanBrief(
                id=workout_plan.id,
                name=workout_plan.name,
            ),
            status=session.status,
            exercise_sessions=exercise_session_details,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    )


@router.post(
    '/workout-sessions/start',
    response_model=APIResponse[WorkoutSessionStartResponse],
    status_code=status.HTTP_201_CREATED,
    tags=['Workout Sessions'],
)
async def start_workout_session(
    request: WorkoutSessionStartRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Start a new workout session.

    Creates a session with status=in_progress and returns
    exercise context (PRs and recent sessions).
    '''
    # Verify workout plan exists and belongs to user
    workout_plan = (
        db.query(WorkoutPlan)
        .filter(
            WorkoutPlan.id == request.workout_plan_id,
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.deleted_at.is_(None),
        )
        .first()
    )

    if not workout_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout plan not found',
        )

    # Create new session
    session = WorkoutSession(
        user_id=user_id,
        workout_plan_id=request.workout_plan_id,
        status=SessionStatusEnum.IN_PROGRESS,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Get planned exercises for this workout plan
    workout_exercises = (
        db.query(WorkoutExercise)
        .join(Exercise)
        .filter(WorkoutExercise.workout_plan_id == request.workout_plan_id)
        .order_by(WorkoutExercise.sequence)
        .all()
    )

    exercises_with_context = []
    for we in workout_exercises:
        exercise = we.exercise

        # Get PR for this exercise
        pr = (
            db.query(PersonalRecord)
            .filter(
                PersonalRecord.user_id == user_id,
                PersonalRecord.exercise_id == exercise.id,
                PersonalRecord.record_type == RecordTypeEnum.ONE_RM,
            )
            .first()
        )

        pr_brief = None
        if pr:
            pr_brief = PersonalRecordBrief(
                id=pr.id,
                record_type=pr.record_type,
                value=pr.value,
                unit=pr.unit,
                achieved_at=pr.achieved_at,
            )

        # Get recent sessions for this exercise (last 3 workouts)
        recent_exercise_sessions = (
            db.query(ExerciseSession)
            .join(WorkoutSession)
            .filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.deleted_at.is_(None),
                WorkoutSession.status == SessionStatusEnum.COMPLETED,
                ExerciseSession.exercise_id == exercise.id,
            )
            .order_by(WorkoutSession.created_at.desc())
            .limit(15)  # Get enough sets to cover 3 workouts
            .all()
        )

        # Group sets by workout session (up to 3 sessions)
        sessions_dict = {}
        for es in recent_exercise_sessions:
            ws_id = es.workout_session_id
            if ws_id not in sessions_dict:
                if len(sessions_dict) >= 3:
                    break
                sessions_dict[ws_id] = {
                    'date': es.workout_session.created_at,
                    'sets': [],
                }
            sessions_dict[ws_id]['sets'].append(
                RecentSetInfo(reps=es.reps, weight=es.weight)
            )

        recent_sessions = [
            RecentSessionInfo(date=s['date'], sets=s['sets'])
            for s in sessions_dict.values()
        ]

        exercises_with_context.append(
            PlannedExerciseWithContext(
                planned_exercise_id=we.id,
                exercise=ExerciseBrief(
                    id=exercise.id,
                    name=exercise.name,
                    primary_muscle_groups=exercise.primary_muscle_groups,
                    secondary_muscle_groups=exercise.secondary_muscle_groups or [],
                ),
                planned_sets=we.sets,
                planned_reps_min=we.reps_min,
                planned_reps_max=we.reps_max,
                rest_seconds=we.rest_time_seconds,
                context=ExerciseContextInfo(
                    personal_record=pr_brief,
                    recent_sessions=recent_sessions,
                ),
            )
        )

    return APIResponse.success_response(
        WorkoutSessionStartResponse(
            session_id=session.id,
            workout_plan=WorkoutPlanBrief(
                id=workout_plan.id,
                name=workout_plan.name,
            ),
            started_at=session.created_at,
            exercises=exercises_with_context,
        )
    )


@router.post(
    '/workout-sessions/{session_id}/exercises',
    response_model=APIResponse[LogExerciseResponse],
    status_code=status.HTTP_201_CREATED,
    tags=['Workout Sessions'],
)
async def log_exercise(
    session_id: UUID,
    request: LogExerciseRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Log exercise sets during a workout session.

    Creates exercise session records for each set.
    '''
    # Get the session and verify ownership
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
            WorkoutSession.deleted_at.is_(None),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout session not found',
        )

    # Verify session is in progress
    if session.status != SessionStatusEnum.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot log exercises to a session that is not in progress',
        )

    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == request.exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Exercise not found',
        )

    # Create exercise session records for each set
    exercise_session_ids = []
    for set_item in request.sets:
        exercise_session = ExerciseSession(
            workout_session_id=session_id,
            exercise_id=request.exercise_id,
            weight=set_item.weight,
            reps=set_item.reps,
            set_number=set_item.set_number,
            rest_time_seconds=set_item.rest_time_seconds,
        )
        db.add(exercise_session)
        db.flush()  # Get the ID
        exercise_session_ids.append(exercise_session.id)

    db.commit()

    return APIResponse.success_response(
        LogExerciseResponse(exercise_session_ids=exercise_session_ids)
    )


@router.put(
    '/workout-sessions/{session_id}/complete',
    response_model=APIResponse[CompleteSessionResponse],
    tags=['Workout Sessions'],
)
async def complete_workout_session(
    session_id: UUID,
    request: CompleteSessionRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Complete a workout session.

    Calculates duration, checks for new PRs, and updates status.
    '''
    # Get the session
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
            WorkoutSession.deleted_at.is_(None),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout session not found',
        )

    # Verify session is in progress
    if session.status != SessionStatusEnum.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session is not in progress',
        )

    # Update session status
    session.status = SessionStatusEnum.COMPLETED
    completed_at = datetime.utcnow()

    # Calculate duration
    duration_seconds = int((completed_at - session.created_at).total_seconds())

    # Check for new PRs
    # Get all exercise sessions for this workout
    exercise_sessions = (
        db.query(ExerciseSession)
        .filter(ExerciseSession.workout_session_id == session_id)
        .all()
    )

    new_prs = []
    # Group by exercise to find max weight/reps
    exercise_max = {}
    for es in exercise_sessions:
        if es.exercise_id not in exercise_max:
            exercise_max[es.exercise_id] = {
                'max_weight': es.weight,
                'max_reps': es.reps,
                'best_session': es,
            }
        else:
            # Check for higher weight or higher reps at same weight
            current = exercise_max[es.exercise_id]
            if es.weight > current['max_weight']:
                current['max_weight'] = es.weight
                current['best_session'] = es
            elif es.weight == current['max_weight'] and es.reps > current['max_reps']:
                current['max_reps'] = es.reps
                current['best_session'] = es

    # Check against existing PRs and create new ones if needed
    for exercise_id, data in exercise_max.items():
        best_session = data['best_session']

        # Calculate estimated 1RM using Epley formula: weight * (1 + reps/30)
        estimated_1rm = float(best_session.weight) * (1 + best_session.reps / 30)

        # Get existing PR for this exercise
        existing_pr = (
            db.query(PersonalRecord)
            .filter(
                PersonalRecord.user_id == user_id,
                PersonalRecord.exercise_id == exercise_id,
                PersonalRecord.record_type == RecordTypeEnum.ONE_RM,
            )
            .first()
        )

        if existing_pr is None or estimated_1rm > float(existing_pr.value):
            # Get exercise name
            exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

            if existing_pr:
                # Update existing PR
                existing_pr.value = estimated_1rm
                existing_pr.exercise_session_id = best_session.id
                existing_pr.achieved_at = completed_at
            else:
                # Create new PR
                new_pr = PersonalRecord(
                    user_id=user_id,
                    exercise_id=exercise_id,
                    record_type=RecordTypeEnum.ONE_RM,
                    value=estimated_1rm,
                    unit='kg',  # Default to kg
                    exercise_session_id=best_session.id,
                    achieved_at=completed_at,
                )
                db.add(new_pr)

            new_prs.append(
                NewPersonalRecordInfo(
                    exercise_name=exercise.name,
                    record_type=RecordTypeEnum.ONE_RM,
                    value=round(estimated_1rm, 2),
                    unit='kg',
                )
            )

    db.commit()

    return APIResponse.success_response(
        CompleteSessionResponse(
            session_id=session.id,
            status=session.status,
            duration_seconds=duration_seconds,
            new_personal_records=new_prs,
        )
    )


@router.put(
    '/workout-sessions/{session_id}/skip',
    response_model=APIResponse[SkipSessionResponse],
    tags=['Workout Sessions'],
)
async def skip_workout_session(
    session_id: UUID,
    request: SkipSessionRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Skip a workout session.
    '''
    # Get the session
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
            WorkoutSession.deleted_at.is_(None),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout session not found',
        )

    # Verify session is in progress
    if session.status != SessionStatusEnum.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session is not in progress',
        )

    # Update session status
    session.status = SessionStatusEnum.ABANDONED
    db.commit()

    return APIResponse.success_response(
        SkipSessionResponse(
            session_id=session.id,
            status=session.status,
        )
    )


@router.delete(
    '/workout-sessions/{session_id}',
    response_model=APIResponse[None],
    tags=['Workout Sessions'],
)
async def delete_workout_session(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Soft delete a workout session.
    '''
    # Get the session
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
            WorkoutSession.deleted_at.is_(None),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Workout session not found',
        )

    # Soft delete
    session.deleted_at = datetime.utcnow()
    db.commit()

    return APIResponse.success_response(None)


# =============================================================================
# Personal Records endpoints
# =============================================================================


@router.get(
    '/personal-records',
    response_model=APIResponse[PersonalRecordListResponse],
    tags=['Personal Records'],
)
async def list_personal_records(
    exercise_id: Optional[UUID] = Query(default=None, description='Filter by exercise'),
    record_type: Optional[RecordTypeEnum] = Query(
        default=None, description='Filter by record type'
    ),
    page: int = Query(default=1, ge=1, description='Page number'),
    limit: int = Query(default=50, ge=1, le=100, description='Items per page'),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    List personal records with optional filtering.
    '''
    # Build query
    query = db.query(PersonalRecord).filter(
        PersonalRecord.user_id == user_id,
    )

    # Apply filters
    if exercise_id:
        query = query.filter(PersonalRecord.exercise_id == exercise_id)
    if record_type:
        query = query.filter(PersonalRecord.record_type == record_type)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    records = (
        query.options(joinedload(PersonalRecord.exercise))
        .order_by(PersonalRecord.achieved_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Build response
    record_items = []
    for record in records:
        record_items.append(
            PersonalRecordListItem(
                id=record.id,
                exercise=PersonalRecordExerciseInfo(
                    id=record.exercise.id,
                    name=record.exercise.name,
                ),
                record_type=record.record_type,
                value=record.value,
                unit=record.unit,
                achieved_at=record.achieved_at,
                exercise_session_id=record.exercise_session_id,
            )
        )

    return APIResponse.success_response(
        PersonalRecordListResponse(
            records=record_items,
            pagination=PaginationInfo(
                page=page,
                limit=limit,
                total=total,
                total_pages=(total + limit - 1) // limit,
            ),
        )
    )


@router.post(
    '/personal-records',
    response_model=APIResponse[PersonalRecordCreateResponse],
    status_code=status.HTTP_201_CREATED,
    tags=['Personal Records'],
)
async def create_personal_record(
    request: PersonalRecordCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Manually create a personal record.
    '''
    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == request.exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Exercise not found',
        )

    # Check if a record of this type already exists for this exercise
    existing_record = (
        db.query(PersonalRecord)
        .filter(
            PersonalRecord.user_id == user_id,
            PersonalRecord.exercise_id == request.exercise_id,
            PersonalRecord.record_type == request.record_type,
        )
        .first()
    )

    achieved_at = request.achieved_at or datetime.utcnow()

    if existing_record:
        # Update existing record only if new value is greater
        if request.value > existing_record.value:
            existing_record.value = request.value
            existing_record.unit = request.unit
            existing_record.achieved_at = achieved_at
            existing_record.exercise_session_id = None  # Manual entry
            db.commit()
            db.refresh(existing_record)
            return APIResponse.success_response(
                PersonalRecordCreateResponse(
                    id=existing_record.id,
                    record_type=existing_record.record_type,
                    value=existing_record.value,
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Existing record ({existing_record.value}) is higher than submitted value ({request.value})',
            )
    else:
        # Create new record
        new_record = PersonalRecord(
            user_id=user_id,
            exercise_id=request.exercise_id,
            record_type=request.record_type,
            value=request.value,
            unit=request.unit,
            achieved_at=achieved_at,
            exercise_session_id=None,  # Manual entry
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return APIResponse.success_response(
            PersonalRecordCreateResponse(
                id=new_record.id,
                record_type=new_record.record_type,
                value=new_record.value,
            )
        )


@router.delete(
    '/personal-records/{record_id}',
    response_model=APIResponse[None],
    tags=['Personal Records'],
)
async def delete_personal_record(
    record_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Delete a personal record.
    '''
    record = (
        db.query(PersonalRecord)
        .filter(
            PersonalRecord.id == record_id,
            PersonalRecord.user_id == user_id,
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Personal record not found',
        )

    db.delete(record)
    db.commit()

    return APIResponse.success_response(None)


# =============================================================================
# Statistics endpoints
# =============================================================================


@router.get(
    '/stats/overview',
    response_model=APIResponse[StatsOverviewResponse],
    tags=['Statistics'],
)
async def get_stats_overview(
    start_date: Optional[datetime] = Query(default=None, description='Filter by start date'),
    end_date: Optional[datetime] = Query(default=None, description='Filter by end date'),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Get user workout statistics overview.
    '''
    # Build base query for completed sessions
    session_query = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.status == SessionStatusEnum.COMPLETED,
        WorkoutSession.deleted_at.is_(None),
    )

    if start_date:
        session_query = session_query.filter(WorkoutSession.created_at >= start_date)
    if end_date:
        session_query = session_query.filter(WorkoutSession.created_at <= end_date)

    sessions = session_query.all()

    # Calculate total workouts
    total_workouts = len(sessions)

    # Calculate total duration (in seconds)
    total_duration_seconds = 0
    for session in sessions:
        if session.created_at and session.updated_at:
            duration = (session.updated_at - session.created_at).total_seconds()
            total_duration_seconds += int(duration)

    # Get session IDs for exercise session queries
    session_ids = [s.id for s in sessions]

    # Calculate total volume
    total_volume_kg = Decimal('0')
    muscle_group_counts = defaultdict(int)

    if session_ids:
        exercise_sessions = (
            db.query(ExerciseSession)
            .options(joinedload(ExerciseSession.exercise))
            .filter(ExerciseSession.workout_session_id.in_(session_ids))
            .all()
        )

        for es in exercise_sessions:
            # Calculate volume: weight * reps
            volume = Decimal(str(es.weight)) * Decimal(str(es.reps))
            total_volume_kg += volume

            # Count muscle groups
            if es.exercise:
                for mg in es.exercise.primary_muscle_groups:
                    muscle_group_counts[mg] += 1
                for mg in es.exercise.secondary_muscle_groups:
                    muscle_group_counts[mg] += 1

    # Calculate workouts by month
    workouts_by_month = defaultdict(int)
    for session in sessions:
        month_key = session.created_at.strftime('%Y-%m')
        workouts_by_month[month_key] += 1

    monthly_counts = [
        MonthlyWorkoutCount(month=month, count=count)
        for month, count in sorted(workouts_by_month.items(), reverse=True)
    ]

    # Get most trained muscle groups (top 5)
    sorted_muscle_groups = sorted(muscle_group_counts.items(), key=lambda x: x[1], reverse=True)
    most_trained = [
        MuscleGroupTrainingCount(muscle_group=mg, session_count=count)
        for mg, count in sorted_muscle_groups[:5]
    ]

    # Calculate current streak
    current_streak_days = 0
    if sessions:
        from datetime import timedelta

        # Sort sessions by date descending
        sorted_sessions = sorted(sessions, key=lambda s: s.created_at, reverse=True)
        today = datetime.utcnow().date()
        last_workout_date = sorted_sessions[0].created_at.date()

        # Check if last workout was today or yesterday
        if (today - last_workout_date).days <= 1:
            current_streak_days = 1
            prev_date = last_workout_date

            for session in sorted_sessions[1:]:
                session_date = session.created_at.date()
                diff = (prev_date - session_date).days

                if diff == 0:
                    # Same day, continue
                    continue
                elif diff == 1:
                    # Consecutive day
                    current_streak_days += 1
                    prev_date = session_date
                else:
                    # Streak broken
                    break

    # Get personal records count
    pr_count = db.query(PersonalRecord).filter(PersonalRecord.user_id == user_id).count()

    return APIResponse.success_response(
        StatsOverviewResponse(
            total_workouts=total_workouts,
            total_duration_seconds=total_duration_seconds,
            total_volume_kg=round(total_volume_kg, 2),
            workouts_by_month=monthly_counts,
            most_trained_muscle_groups=most_trained,
            current_streak_days=current_streak_days,
            personal_records_count=pr_count,
        )
    )


@router.get(
    '/stats/exercise/{exercise_id}/history',
    response_model=APIResponse[ExerciseHistoryResponse],
    tags=['Statistics'],
)
async def get_exercise_history(
    exercise_id: UUID,
    start_date: Optional[datetime] = Query(default=None, description='Filter by start date'),
    end_date: Optional[datetime] = Query(default=None, description='Filter by end date'),
    limit: int = Query(default=50, ge=1, le=100, description='Max sessions to return'),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Get exercise performance history.
    '''
    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Exercise not found',
        )

    # Get completed workout sessions for this user
    session_query = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.status == SessionStatusEnum.COMPLETED,
        WorkoutSession.deleted_at.is_(None),
    )

    if start_date:
        session_query = session_query.filter(WorkoutSession.created_at >= start_date)
    if end_date:
        session_query = session_query.filter(WorkoutSession.created_at <= end_date)

    sessions = session_query.order_by(WorkoutSession.created_at.desc()).all()
    session_ids = [s.id for s in sessions]

    # Get exercise sessions for this exercise
    if not session_ids:
        return APIResponse.success_response(
            ExerciseHistoryResponse(
                exercise=PersonalRecordExerciseInfo(id=exercise.id, name=exercise.name),
                sessions=[],
            )
        )

    # Get all exercise sessions for this exercise in these workout sessions
    exercise_sessions = (
        db.query(ExerciseSession)
        .filter(
            ExerciseSession.exercise_id == exercise_id,
            ExerciseSession.workout_session_id.in_(session_ids),
        )
        .order_by(ExerciseSession.created_at.desc())
        .all()
    )

    # Group by workout session
    session_groups = defaultdict(list)
    for es in exercise_sessions:
        session_groups[es.workout_session_id].append(es)

    # Build response
    history_sessions = []
    session_map = {s.id: s for s in sessions}

    for session_id, exercise_sets in list(session_groups.items())[:limit]:
        workout_session = session_map.get(session_id)
        if not workout_session:
            continue

        # Calculate aggregates
        total_volume = Decimal('0')
        total_reps = 0
        max_weight = Decimal('0')
        sets_data = []

        for es in sorted(exercise_sets, key=lambda x: x.set_number):
            weight = Decimal(str(es.weight))
            reps = es.reps
            total_volume += weight * reps
            total_reps += reps
            if weight > max_weight:
                max_weight = weight

            sets_data.append(
                ExerciseHistorySet(
                    reps=reps,
                    weight=weight,
                    unit='kg',
                )
            )

        history_sessions.append(
            ExerciseHistorySession(
                date=workout_session.created_at,
                total_volume=round(total_volume, 2),
                total_reps=total_reps,
                max_weight=max_weight,
                sets=sets_data,
            )
        )

    return APIResponse.success_response(
        ExerciseHistoryResponse(
            exercise=PersonalRecordExerciseInfo(id=exercise.id, name=exercise.name),
            sessions=history_sessions,
        )
    )
