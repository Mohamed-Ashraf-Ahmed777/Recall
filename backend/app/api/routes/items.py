from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.schemas.item import ItemResponse, LinkCreate, NoteCreate
from app.schemas.item_update import ItemUpdate
from app.services.item_service import ItemService


router = APIRouter(prefix="/items", tags=["items"])


@router.post("/notes", response_model=ItemResponse, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.create_note(payload)


@router.post("/links", response_model=ItemResponse, status_code=201)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.create_link(payload)


@router.post("/files", response_model=ItemResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(default=None),
    description: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    content_bytes = await file.read()
    if len(content_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds maximum allowed size")
    service = ItemService(db)
    return service.create_file_item(
        filename=file.filename or "upload.bin",
        content_bytes=content_bytes,
        mime_type=file.content_type,
        title=title,
        description=description,
    )


@router.post("/{item_id}/process", response_model=ItemResponse)
def process_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.process_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.update_item(item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    deleted = service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=204)


@router.get("", response_model=list[ItemResponse])
def list_items(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    q: Optional[str] = Query(default=None),
    content_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    service = ItemService(db)
    return service.list_items(
        limit=limit,
        offset=offset,
        q=q,
        content_type=content_type,
        processing_status=status,
        tag=tag,
    )


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
