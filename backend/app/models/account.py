from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Account(Base):
    __tablename__ = 'accounts'

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(100))
    currency:Mapped[str] = mapped_column(String(3), default="RUB")
    initial_balance:Mapped[float] = mapped_column(Numeric(12,2), default=0.0)

    transactions = relationship("Transaction", foreign_keys="[Transaction.account_id]", back_populates="account")
    incoming_transfers = relationship("Transaction", foreign_keys="[Transaction.to_account_id]")

    @property
    def balance(self) -> float:
        from app.models.transaction import TransactionType
        total = float(self.initial_balance)
        for t in self.transactions:
            if t.type == TransactionType.INCOME:
                total += float(t.amount)
            elif t.type in (TransactionType.EXPENSE, TransactionType.TRANSFER, TransactionType.DEBT):
                total -= float(t.amount)
        for t in self.incoming_transfers:
            total += float(t.amount)
        return total