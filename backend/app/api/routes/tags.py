from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.item import Item
from app.models.tag import Tag
from app.schemas.tag import ItemTagsAssign, TagResponse


router = APIRouter(tags=["tags"])


@router.get("/tags", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).order_by(Tag.name.asc()).all()


@router.post("/items/{item_id}/tags", response_model=list[TagResponse])
def assign_tags_to_item(item_id: int, payload: ItemTagsAssign, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_names = {t.name for t in item.tags}
    for raw_name in payload.tags:
        clean_name = raw_name.strip().lower()
        if not clean_name or clean_name in existing_names:
            continue
        tag = db.query(Tag).filter(Tag.name == clean_name).first()
        if not tag:
            tag = Tag(name=clean_name)
            db.add(tag)
            db.flush()
        item.tags.append(tag)
        existing_names.add(clean_name)

    db.commit()
    db.refresh(item)
    return item.tags
