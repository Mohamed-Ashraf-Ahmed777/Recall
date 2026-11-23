from app.database.session import Base, engine
from app.models.item import Item
from app.models.tag import Tag, item_tags


def init_db():
    Base.metadata.create_all(bind=engine)
