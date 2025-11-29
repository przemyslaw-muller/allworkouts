'''
Equipment API routes.
'''

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.database import get_db
from app.models import Equipment, UserEquipment
from app.schemas import (
    APIResponse,
    EquipmentListItem,
    EquipmentOwnershipRequest,
    EquipmentOwnershipResponse,
)

router = APIRouter(prefix='/equipment', tags=['Equipment'])


@router.get(
    '',
    response_model=APIResponse[List[EquipmentListItem]],
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
    '/{equipment_id}/ownership',
    response_model=APIResponse[EquipmentOwnershipResponse],
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
