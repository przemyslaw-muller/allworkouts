'''
Personal Records API routes.
'''

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user_id
from app.database import get_db
from app.enums import RecordTypeEnum
from app.models import Exercise, PersonalRecord
from app.schemas import (
    APIResponse,
    PaginationInfo,
    PersonalRecordCreateRequest,
    PersonalRecordCreateResponse,
    PersonalRecordExerciseInfo,
    PersonalRecordListItem,
    PersonalRecordListResponse,
)

router = APIRouter(prefix='/personal-records', tags=['Personal Records'])


@router.get(
    '',
    response_model=APIResponse[PersonalRecordListResponse],
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
    '',
    response_model=APIResponse[PersonalRecordCreateResponse],
    status_code=status.HTTP_201_CREATED,
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
    '/{record_id}',
    response_model=APIResponse[None],
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
