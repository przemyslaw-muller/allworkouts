'''
Statistics API routes.
'''

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user_id
from app.database import get_db
from app.enums import SessionStatusEnum
from app.models import Exercise, ExerciseSession, PersonalRecord, WorkoutSession
from app.schemas import (
    APIResponse,
    ExerciseHistoryResponse,
    ExerciseHistorySession,
    ExerciseHistorySet,
    MonthlyWorkoutCount,
    MuscleGroupTrainingCount,
    PersonalRecordExerciseInfo,
    StatsOverviewResponse,
)

router = APIRouter(prefix='/stats', tags=['Statistics'])


@router.get(
    '/overview',
    response_model=APIResponse[StatsOverviewResponse],
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
    '/exercise/{exercise_id}/history',
    response_model=APIResponse[ExerciseHistoryResponse],
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
