from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EquipmentBase(BaseModel):
    '''Base equipment schema'''

    name: str
    description: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    '''Schema for equipment creation'''

    pass


class EquipmentResponse(EquipmentBase):
    '''Schema for equipment response'''

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentListItem(BaseModel):
    '''Equipment item in list response with ownership status'''

    id: UUID
    name: str
    description: Optional[str] = None
    is_user_owned: bool = False

    model_config = ConfigDict(from_attributes=True)


class EquipmentOwnershipRequest(BaseModel):
    '''Request for updating equipment ownership'''

    is_owned: bool


class EquipmentOwnershipResponse(BaseModel):
    '''Response for equipment ownership update'''

    equipment_id: UUID
    is_owned: bool


class EquipmentBrief(BaseModel):
    '''Brief equipment info for exercise list'''

    id: UUID
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
