from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Account(Base):
    __tablename__ = 'accounts'

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(100))
    currency:Mapped[str] = mapped_column(String(3), default="RUB")
    balance:Mapped[float] = mapped_column(Numeric(12,2), default=0.0)

    transactions = relationship("Transaction", back_populates="account")