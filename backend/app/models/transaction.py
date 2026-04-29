from datetime import datetime
import enum

from sqlalchemy import Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    DEBT = "debt"

class Periodicity(str, enum.Enum):
    ONE_TIME = "one_time"
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class Transaction(Base):
    __tablename__ = "transactions"
    id:Mapped[int] = mapped_column(primary_key=True)
    type:Mapped[TransactionType]
    amount:Mapped[float] = mapped_column(Numeric(12, 2))
    date:Mapped[datetime] = mapped_column(Date)
    description:Mapped[str|None] = mapped_column(Text, nullable=True)
    periodicity:Mapped[Periodicity] = mapped_column(default=Periodicity.ONE_TIME)

    account_id:Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    category_id:Mapped[int|None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    to_account_id:Mapped[int|None] = mapped_column(ForeignKey("accounts.id"), nullable=True)

    account = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    to_account = relationship("Account", foreign_keys=[to_account_id])
    category = relationship("Category", foreign_keys=[category_id], back_populates="transactions")