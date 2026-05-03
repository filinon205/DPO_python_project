from sqlalchemy.orm import Session

from app.models.category import Category

class CategoryService:
    def __init__(self, db: Session):
        self._db = db

    def get_all(self)->list[Category]:
        return self._db.query(Category).all()
