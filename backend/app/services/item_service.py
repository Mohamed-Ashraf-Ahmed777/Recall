import hashlib
from pathlib import Path
from typing import Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.item import Item
from app.processors.link_extractor import extract_link_metadata
from app.processors.text_extractor import TEXT_EXTENSIONS, extract_text_from_file
from app.repositories.item_repository import ItemRepository
from app.schemas.item import LinkCreate, NoteCreate
from app.schemas.item_update import ItemUpdate


class ItemService:
    def __init__(self, db: Session):
        self.repo = ItemRepository(db)

    def create_note(self, payload: NoteCreate) -> Item:
        item = Item(
            title=payload.title.strip(),
            description=payload.description,
            content_type="note",
            source_name=payload.source_name,
            processing_status="READY",
        )
        return self.repo.create(item)

    def create_link(self, payload: LinkCreate) -> Item:
        clean_url = payload.url.strip()
        derived_title = payload.title.strip() if payload.title and payload.title.strip() else clean_url
        item = Item(
            title=derived_title,
            description=payload.description,
            content_type="link",
            original_url=clean_url,
            processing_status="PENDING",
        )
        return self.repo.create(item)

    def create_file_item(
        self,
        filename: str,
        content_bytes: bytes,
        mime_type: str | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> Item:
        settings.storage_originals_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(filename or "uploaded_file").name
        ext = Path(safe_name).suffix.lower()
        stored_name = f"{uuid4().hex}{ext}"
        dest_path = settings.storage_originals_dir / stored_name
        dest_path.write_bytes(content_bytes)

        checksum = hashlib.sha256(content_bytes).hexdigest()
        file_size = len(content_bytes)
        derived_title = title.strip() if title and title.strip() else safe_name
        detected_type = "file"
        if mime_type and mime_type.startswith("image/"):
            detected_type = "image"
        elif mime_type == "application/pdf" or ext == ".pdf":
            detected_type = "pdf"

        item = Item(
            title=derived_title,
            description=description,
            content_type=detected_type,
            original_filename=safe_name,
            storage_path=str(dest_path),
            processing_status="PENDING",
            file_size=file_size,
            checksum=checksum,
        )
        return self.repo.create(item)

    def process_item(self, item_id: int) -> Item | None:
        item = self.repo.get_by_id(item_id)
        if not item:
            return None
        item.processing_status = "PROCESSING"
        item.processing_error = None
        self.repo.create(item)
        try:
            if item.content_type == "link" and item.original_url:
                meta = extract_link_metadata(item.original_url)
                if meta.get("title") and item.title == item.original_url:
                    item.title = meta["title"]
                if meta.get("description") and not item.description:
                    item.description = meta["description"]
            elif item.storage_path:
                ext = Path(item.storage_path).suffix.lower()
                if ext in TEXT_EXTENSIONS:
                    extracted = extract_text_from_file(item.storage_path).strip()
                    if extracted and not item.description:
                        item.description = extracted[:2000]
            item.processing_status = "READY"
            item.processing_error = None
        except Exception as exc:
            item.processing_status = "FAILED"
            item.processing_error = str(exc)
        return self.repo.create(item)

    def update_item(self, item_id: int, payload: ItemUpdate) -> Item | None:
        item = self.repo.get_by_id(item_id)
        if not item:
            return None
        if payload.title is not None and payload.title.strip():
            item.title = payload.title.strip()
        if payload.description is not None:
            item.description = payload.description
        return self.repo.update(item)

    def delete_item(self, item_id: int) -> bool:
        item = self.repo.get_by_id(item_id)
        if not item:
            return False
        if item.storage_path:
            p = Path(item.storage_path)
            if p.exists() and p.is_file():
                p.unlink()
        self.repo.delete(item)
        return True

    def get_item(self, item_id: int) -> Item | None:
        return self.repo.get_by_id(item_id)

    def list_items(
        self,
        limit: int = 50,
        offset: int = 0,
        q: Optional[str] = None,
        content_type: Optional[str] = None,
        processing_status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> list[Item]:
        return self.repo.list_items(
            limit=limit,
            offset=offset,
            q=q,
            content_type=content_type,
            processing_status=processing_status,
            tag=tag,
        )
