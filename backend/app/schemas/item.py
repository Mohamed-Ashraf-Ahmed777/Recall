from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source_name: Optional[str] = None


class LinkCreate(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content_type: str
    original_filename: Optional[str] = None
    storage_path: Optional[str] = None
    original_url: Optional[str] = None
    source_name: Optional[str] = None
    created_at: datetime
    captured_at: Optional[datetime] = None
    updated_at: datetime
    processing_status: str
    processing_error: Optional[str] = None
    file_size: Optional[int] = None
    checksum: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
