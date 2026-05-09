from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    month: Mapped[int]
    year: Mapped[int]
    limit: Mapped[float] = mapped_column(Numeric(12, 2))

    category = relationship("Category")

    '''__table_args__ - специальный атрибут SQLAlchemy куда передаются настройки
   таблицы, которые касаются нескольких колонок сразу'''
    __table_args__ = (
        UniqueConstraint("category_id", "month", "year", name="uq_budget_category_month"),
    ) # эта конкретная комбинация значений должна быть уникальной. Без этого пользователь мог бы случайно создать два
 # лимита на "Еда / Май 2026" и непонятно какой применять.
