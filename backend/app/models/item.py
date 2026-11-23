from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.session import Base
from app.models.tag import item_tags


def utc_now():
    return datetime.now(timezone.utc)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False, index=True)
    original_filename = Column(String(255), nullable=True)
    storage_path = Column(String(500), nullable=True)
    original_url = Column(Text, nullable=True)
    source_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    captured_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    processing_status = Column(String(30), default="PENDING", nullable=False, index=True)
    processing_error = Column(Text, nullable=True)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(128), nullable=True, index=True)

    tags = relationship("Tag", secondary=item_tags, backref="items")
