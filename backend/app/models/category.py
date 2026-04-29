import enum
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedColumn

from app.database import Base

class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(Base):
    __tablename__ = "categories"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String(100), index=True)
    type:Mapped[CategoryType]
    parent_id:Mapped[int|None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    # Самореференция: для присвоения дочерней записи id родителя
    parent = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent")
    transactions = relationship("Transaction", back_populates="category")