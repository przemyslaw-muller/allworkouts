"""
Exercise API routes.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models import (
    Equipment,
    Exercise,
    ExerciseEquipment,
    PersonalRecord,
    UserEquipment,
)
from app.schemas import (
    APIResponse,
    EquipmentBrief,
    ExerciseCreate,
    ExerciseDetailResponse,
    ExerciseListItem,
    ExerciseListResponse,
    ExerciseResponse,
    ExerciseSubstituteItem,
    ExerciseUpdate,
    PaginationInfo,
    PersonalRecordBrief,
)

router = APIRouter(prefix="/exercises", tags=["Exercises"])


def get_exercise_equipment(db: Session, exercise_id: UUID) -> List[EquipmentBrief]:
    """Helper to get equipment for an exercise"""
    equipment_links = (
        db.query(Equipment)
        .join(ExerciseEquipment)
        .filter(ExerciseEquipment.exercise_id == exercise_id)
        .all()
    )
    return [
        EquipmentBrief(id=eq.id, name=eq.name, description=eq.description) for eq in equipment_links
    ]


@router.get(
    "",
    response_model=APIResponse[ExerciseListResponse],
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
    """
    List exercises with optional filtering.

    Includes global exercises (is_custom=false) and user's custom exercises.

    Query Parameters:
    - search: Filter by name (case-insensitive partial match)
    - muscle_group: Filter by primary muscle group
    - equipment_id: Filter by required equipment
    - user_can_perform: Filter by user's owned equipment (true/false)
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 100)
    """
    # Validate pagination
    if limit > 100:
        limit = 100
    if page < 1:
        page = 1

    # Base query: global exercises OR user's custom exercises
    query = db.query(Exercise).filter(
        or_(
            Exercise.is_custom == False,  # noqa: E712 - SQLAlchemy requires == for comparison
            Exercise.user_id == user_id,
        )
    )

    # Apply search filter
    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))

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
        equipment = get_exercise_equipment(db, ex.id)
        equipment_ids = {eq.id for eq in equipment}

        # Filter by user_can_perform if specified
        if user_can_perform is not None:
            can_perform = len(equipment_ids) == 0 or equipment_ids.issubset(
                user_owned_equipment_ids
            )
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
                is_custom=ex.is_custom,
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
    "/{exercise_id}",
    response_model=APIResponse[ExerciseDetailResponse],
)
async def get_exercise(
    exercise_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get single exercise details with equipment and personal records.
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    # Get equipment for this exercise
    equipment = get_exercise_equipment(db, exercise_id)

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
            is_custom=exercise.is_custom,
            user_id=exercise.user_id,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
        )
    )


@router.get(
    "/{exercise_id}/substitutes",
    response_model=APIResponse[List[ExerciseSubstituteItem]],
)
async def get_exercise_substitutes(
    exercise_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get exercise substitution suggestions.

    Business Logic:
    1. Find exercises with overlapping muscle groups
    2. Filter by user's owned equipment
    3. Exclude the original exercise
    4. Sort by muscle group overlap (more overlap = better match)
    """
    # Get the original exercise
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
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
    other_exercises = db.query(Exercise).filter(Exercise.id != exercise_id).all()

    substitutes = []
    for ex in other_exercises:
        # Get equipment for this exercise
        equipment = get_exercise_equipment(db, ex.id)
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
            match_score = (0.7 * primary_overlap / max_primary) + (
                0.3 * secondary_overlap / max_total
            )

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


@router.post(
    "",
    response_model=APIResponse[ExerciseResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_custom_exercise(
    exercise_data: ExerciseCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Create a new custom exercise.

    Custom exercises are only visible to the creating user.
    Name must be unique per user (can duplicate global exercise names).
    """
    # Check for name uniqueness for this user's custom exercises
    existing = (
        db.query(Exercise)
        .filter(
            Exercise.name == exercise_data.name,
            Exercise.user_id == user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a custom exercise with this name",
        )

    # Create the exercise
    exercise = Exercise(
        name=exercise_data.name,
        primary_muscle_groups=exercise_data.primary_muscle_groups,
        secondary_muscle_groups=exercise_data.secondary_muscle_groups,
        default_weight=exercise_data.default_weight,
        default_reps=exercise_data.default_reps,
        default_rest_time_seconds=exercise_data.default_rest_time_seconds,
        description=exercise_data.description,
        is_custom=True,
        user_id=user_id,
    )
    db.add(exercise)
    db.flush()

    # Add equipment links if provided
    if exercise_data.equipment_ids:
        for equipment_id in exercise_data.equipment_ids:
            # Verify equipment exists
            equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
            if not equipment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Equipment with id {equipment_id} not found",
                )
            exercise_equipment = ExerciseEquipment(
                exercise_id=exercise.id,
                equipment_id=equipment_id,
            )
            db.add(exercise_equipment)

    db.commit()
    db.refresh(exercise)

    return APIResponse.success_response(
        ExerciseResponse(
            id=exercise.id,
            name=exercise.name,
            primary_muscle_groups=exercise.primary_muscle_groups,
            secondary_muscle_groups=exercise.secondary_muscle_groups or [],
            default_weight=exercise.default_weight,
            default_reps=exercise.default_reps,
            default_rest_time_seconds=exercise.default_rest_time_seconds,
            description=exercise.description,
            is_custom=exercise.is_custom,
            user_id=exercise.user_id,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
        )
    )


@router.put(
    "/{exercise_id}",
    response_model=APIResponse[ExerciseResponse],
)
async def update_custom_exercise(
    exercise_id: UUID,
    exercise_data: ExerciseUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Update a custom exercise.

    Only the owner can update their custom exercises.
    Global exercises cannot be modified.
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    # Check ownership
    if not exercise.is_custom:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify global exercises",
        )

    if exercise.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own custom exercises",
        )

    # Check name uniqueness if changing name
    if exercise_data.name is not None and exercise_data.name != exercise.name:
        existing = (
            db.query(Exercise)
            .filter(
                Exercise.name == exercise_data.name,
                Exercise.user_id == user_id,
                Exercise.id != exercise_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a custom exercise with this name",
            )

    # Update fields
    if exercise_data.name is not None:
        exercise.name = exercise_data.name
    if exercise_data.primary_muscle_groups is not None:
        exercise.primary_muscle_groups = exercise_data.primary_muscle_groups
    if exercise_data.secondary_muscle_groups is not None:
        exercise.secondary_muscle_groups = exercise_data.secondary_muscle_groups
    if exercise_data.default_weight is not None:
        exercise.default_weight = exercise_data.default_weight
    if exercise_data.default_reps is not None:
        exercise.default_reps = exercise_data.default_reps
    if exercise_data.default_rest_time_seconds is not None:
        exercise.default_rest_time_seconds = exercise_data.default_rest_time_seconds
    if exercise_data.description is not None:
        exercise.description = exercise_data.description

    # Update equipment links if provided
    if exercise_data.equipment_ids is not None:
        # Remove existing links
        db.query(ExerciseEquipment).filter(ExerciseEquipment.exercise_id == exercise_id).delete()

        # Add new links
        for equipment_id in exercise_data.equipment_ids:
            equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
            if not equipment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Equipment with id {equipment_id} not found",
                )
            exercise_equipment = ExerciseEquipment(
                exercise_id=exercise.id,
                equipment_id=equipment_id,
            )
            db.add(exercise_equipment)

    db.commit()
    db.refresh(exercise)

    return APIResponse.success_response(
        ExerciseResponse(
            id=exercise.id,
            name=exercise.name,
            primary_muscle_groups=exercise.primary_muscle_groups,
            secondary_muscle_groups=exercise.secondary_muscle_groups or [],
            default_weight=exercise.default_weight,
            default_reps=exercise.default_reps,
            default_rest_time_seconds=exercise.default_rest_time_seconds,
            description=exercise.description,
            is_custom=exercise.is_custom,
            user_id=exercise.user_id,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
        )
    )


@router.delete(
    "/{exercise_id}",
    response_model=APIResponse[None],
)
async def delete_custom_exercise(
    exercise_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Delete a custom exercise.

    Only the owner can delete their custom exercises.
    Global exercises cannot be deleted.
    Exercise cannot be deleted if used in any workout plans.
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found",
        )

    # Check ownership
    if not exercise.is_custom:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete global exercises",
        )

    if exercise.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own custom exercises",
        )

    # Check if used in any workout plans
    from app.models import WorkoutExercise

    usage_count = (
        db.query(WorkoutExercise).filter(WorkoutExercise.exercise_id == exercise_id).count()
    )
    if usage_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete exercise that is used in workout plans. Remove it from plans first.",
        )

    # Delete equipment links first
    db.query(ExerciseEquipment).filter(ExerciseEquipment.exercise_id == exercise_id).delete()

    # Delete personal records for this exercise
    db.query(PersonalRecord).filter(PersonalRecord.exercise_id == exercise_id).delete()

    # Delete the exercise
    db.delete(exercise)
    db.commit()

    return APIResponse.success_response(None)
