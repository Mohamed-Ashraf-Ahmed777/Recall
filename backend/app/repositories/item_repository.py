from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.tag import Tag


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, item: Item) -> Item:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, item_id: int) -> Item | None:
        return self.db.query(Item).filter(Item.id == item_id).first()

    def update(self, item: Item) -> Item:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Item) -> None:
        self.db.delete(item)
        self.db.commit()

    def list_items(
        self,
        limit: int = 50,
        offset: int = 0,
        q: Optional[str] = None,
        content_type: Optional[str] = None,
        processing_status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> list[Item]:
        query = self.db.query(Item)
        if tag and tag.strip():
            clean_tag = tag.strip().lower()
            query = query.join(Item.tags).filter(Tag.name == clean_tag)
        if content_type:
            query = query.filter(Item.content_type == content_type)
        if processing_status:
            query = query.filter(Item.processing_status == processing_status)
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    Item.title.ilike(pattern),
                    Item.description.ilike(pattern),
                    Item.original_filename.ilike(pattern),
                    Item.original_url.ilike(pattern),
                )
            )
        return query.distinct().order_by(Item.id.desc()).offset(offset).limit(limit).all()
