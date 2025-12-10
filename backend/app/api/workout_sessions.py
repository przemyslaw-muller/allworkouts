"""
Workout Session API routes.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.enums import RecordTypeEnum, SessionStatusEnum
from app.models import (
    Exercise,
    ExerciseSession,
    PersonalRecord,
    Workout,
    WorkoutExercise,
    WorkoutPlan,
    WorkoutSession,
)
from app.schemas import (
    APIResponse,
    CompleteSessionRequest,
    CompleteSessionResponse,
    ExerciseBrief,
    ExerciseContextInfo,
    ExerciseSessionDetail,
    LogExerciseRequest,
    LogExerciseResponse,
    NewPersonalRecordInfo,
    PaginationInfo,
    PersonalRecordBrief,
    PlannedExerciseWithContext,
    RecentSessionInfo,
    RecentSetInfo,
    SkipSessionRequest,
    SkipSessionResponse,
    WorkoutBrief,
    WorkoutPlanBrief,
    WorkoutSessionDetailResponse,
    WorkoutSessionListItem,
    WorkoutSessionListResponse,
    WorkoutSessionStartRequest,
    WorkoutSessionStartResponse,
)

router = APIRouter(prefix="/workout-sessions", tags=["Workout Sessions"])


@router.get(
    "",
    response_model=APIResponse[WorkoutSessionListResponse],
)
async def list_workout_sessions(
    workout_plan_id: Optional[UUID] = None,
    workout_id: Optional[UUID] = None,
    status_filter: Optional[SessionStatusEnum] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 20,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    List workout sessions (history).

    Query Parameters:
    - workout_plan_id: Filter by workout plan
    - workout_id: Filter by specific workout
    - status_filter: Filter by status (in_progress, completed, skipped)
    - start_date: Filter by date range start
    - end_date: Filter by date range end
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    """
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
    if workout_id:
        query = query.filter(WorkoutSession.workout_id == workout_id)
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

        # Get workout plan and workout info
        workout_plan = session.workout_plan
        workout = session.workout

        session_list.append(
            WorkoutSessionListItem(
                id=session.id,
                workout_plan=WorkoutPlanBrief(
                    id=workout_plan.id,
                    name=workout_plan.name,
                ),
                workout=WorkoutBrief(
                    id=workout.id,
                    name=workout.name,
                    day_number=workout.day_number,
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
    "/current",
    response_model=APIResponse[WorkoutSessionStartResponse],
)
async def get_current_workout_session(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get the current in-progress workout session if any.

    Returns the session with exercise context (like start session).
    Returns 404 if no active session.
    """
    # Find in-progress session for the user
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.user_id == user_id,
            WorkoutSession.status == SessionStatusEnum.IN_PROGRESS,
            WorkoutSession.deleted_at.is_(None),
        )
        .order_by(WorkoutSession.created_at.desc())
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active workout session",
        )

    workout_plan = session.workout_plan
    workout = session.workout

    # Get planned exercises for this workout
    workout_exercises = (
        db.query(WorkoutExercise)
        .join(Exercise)
        .filter(WorkoutExercise.workout_id == session.workout_id)
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
                    "date": es.workout_session.created_at,
                    "sets": [],
                }
            sessions_dict[ws_id]["sets"].append(RecentSetInfo(reps=es.reps, weight=es.weight))

        recent_sessions = [
            RecentSessionInfo(date=s["date"], sets=s["sets"]) for s in sessions_dict.values()
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
            workout=WorkoutBrief(
                id=workout.id,
                name=workout.name,
                day_number=workout.day_number,
            ),
            started_at=session.created_at,
            exercises=exercises_with_context,
        )
    )


@router.get(
    "/{session_id}",
    response_model=APIResponse[WorkoutSessionDetailResponse],
)
async def get_workout_session(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Get workout session details with all exercise sessions.
    """
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
            detail="Workout session not found",
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
    workout = session.workout

    return APIResponse.success_response(
        WorkoutSessionDetailResponse(
            id=session.id,
            workout_plan=WorkoutPlanBrief(
                id=workout_plan.id,
                name=workout_plan.name,
            ),
            workout=WorkoutBrief(
                id=workout.id,
                name=workout.name,
                day_number=workout.day_number,
            ),
            status=session.status,
            exercise_sessions=exercise_session_details,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
    )


@router.post(
    "/start",
    response_model=APIResponse[WorkoutSessionStartResponse],
    status_code=status.HTTP_201_CREATED,
)
async def start_workout_session(
    request: WorkoutSessionStartRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Start a new workout session.

    Creates a session with status=in_progress and returns
    exercise context (PRs and recent sessions).
    """
    # Verify workout exists and belongs to user
    workout = (
        db.query(Workout)
        .join(WorkoutPlan)
        .filter(
            Workout.id == request.workout_id,
            WorkoutPlan.user_id == user_id,
            WorkoutPlan.deleted_at.is_(None),
        )
        .first()
    )

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found",
        )

    workout_plan = workout.workout_plan

    # Create new session
    session = WorkoutSession(
        user_id=user_id,
        workout_plan_id=workout_plan.id,
        workout_id=workout.id,
        status=SessionStatusEnum.IN_PROGRESS,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Get planned exercises for this workout
    workout_exercises = (
        db.query(WorkoutExercise)
        .join(Exercise)
        .filter(WorkoutExercise.workout_id == workout.id)
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
                    "date": es.workout_session.created_at,
                    "sets": [],
                }
            sessions_dict[ws_id]["sets"].append(RecentSetInfo(reps=es.reps, weight=es.weight))

        recent_sessions = [
            RecentSessionInfo(date=s["date"], sets=s["sets"]) for s in sessions_dict.values()
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
            workout=WorkoutBrief(
                id=workout.id,
                name=workout.name,
                day_number=workout.day_number,
            ),
            started_at=session.created_at,
            exercises=exercises_with_context,
        )
    )


@router.post(
    "/{session_id}/exercises",
    response_model=APIResponse[LogExerciseResponse],
    status_code=status.HTTP_201_CREATED,
)
async def log_exercise(
    session_id: UUID,
    request: LogExerciseRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Log exercise sets during a workout session.

    Creates exercise session records for each set.
    """
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
            detail="Workout session not found",
        )

    # Verify session is in progress
    if session.status != SessionStatusEnum.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot log exercises to a session that is not in progress",
        )

    # Verify exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == request.exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise not found",
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


@router.post(
    "/{session_id}/complete",
    response_model=APIResponse[CompleteSessionResponse],
)
async def complete_workout_session(
    session_id: UUID,
    request: CompleteSessionRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Complete a workout session.

    Calculates duration, checks for new PRs, and updates status.
    """
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
            detail="Workout session not found",
        )

    # Verify session is in progress
    if session.status != SessionStatusEnum.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not in progress",
        )

    # Update session status
    session.status = SessionStatusEnum.COMPLETED
    completed_at = datetime.now(timezone.utc)

    # Calculate duration
    duration_seconds = int((completed_at - session.created_at).total_seconds())

    # Check for new PRs
    # Get all exercise sessions for this workout
    exercise_sessions = (
        db.query(ExerciseSession).filter(ExerciseSession.workout_session_id == session_id).all()
    )

    new_prs = []
    # Group by exercise to find max weight/reps
    exercise_max = {}
    for es in exercise_sessions:
        if es.exercise_id not in exercise_max:
            exercise_max[es.exercise_id] = {
                "max_weight": es.weight,
                "max_reps": es.reps,
                "best_session": es,
            }
        else:
            # Check for higher weight or higher reps at same weight
            current = exercise_max[es.exercise_id]
            if es.weight > current["max_weight"]:
                current["max_weight"] = es.weight
                current["best_session"] = es
            elif es.weight == current["max_weight"] and es.reps > current["max_reps"]:
                current["max_reps"] = es.reps
                current["best_session"] = es

    # Check against existing PRs and create new ones if needed
    for exercise_id, data in exercise_max.items():
        best_session = data["best_session"]

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
                    unit="kg",  # Default to kg
                    exercise_session_id=best_session.id,
                    achieved_at=completed_at,
                )
                db.add(new_pr)

            new_prs.append(
                NewPersonalRecordInfo(
                    exercise_name=exercise.name,
                    record_type=RecordTypeEnum.ONE_RM,
                    value=round(estimated_1rm, 2),
                    unit="kg",
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


@router.post(
    "/{session_id}/skip",
    response_model=APIResponse[SkipSessionResponse],
)
async def skip_workout_session(
    session_id: UUID,
    request: SkipSessionRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Skip a workout session.
    """
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
            detail="Workout session not found",
        )

    # Verify session is in progress
    if session.status != SessionStatusEnum.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not in progress",
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
    "/{session_id}",
    response_model=APIResponse[None],
)
async def delete_workout_session(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Soft delete a workout session.
    """
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
            detail="Workout session not found",
        )

    # Soft delete
    session.deleted_at = datetime.utcnow()
    db.commit()

    return APIResponse.success_response(None)
