from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkoutImportLogBase(BaseModel):
    '''Base workout import log schema'''

    raw_text: str
    workout_plan_id: Optional[UUID] = None


class WorkoutImportLogCreate(WorkoutImportLogBase):
    '''Schema for workout import log creation'''

    parsed_exercises: Optional[dict] = None
    confidence_scores: Optional[dict] = None


class WorkoutImportLogResponse(WorkoutImportLogBase):
    '''Schema for workout import log response'''

    id: UUID
    user_id: UUID
    parsed_exercises: Optional[dict] = None
    confidence_scores: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
