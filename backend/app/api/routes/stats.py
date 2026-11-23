from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.item import Item
from app.models.tag import Tag


router = APIRouter(tags=["stats"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_items = db.query(Item).count()
    total_tags = db.query(Tag).count()
    by_status = {}
    for st in ("PENDING", "PROCESSING", "READY", "FAILED"):
        by_status[st] = db.query(Item).filter(Item.processing_status == st).count()
    return {
        "total_items": total_items,
        "total_tags": total_tags,
        "by_status": by_status,
    }
