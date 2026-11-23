from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class ItemTagsAssign(BaseModel):
    tags: list[str]


class TagResponse(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
