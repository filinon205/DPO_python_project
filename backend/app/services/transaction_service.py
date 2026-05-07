from sqlalchemy.orm import Session, joinedload

from app.models.transaction import Transaction, TransactionType # вызываем данные по модели и типы
from app.schemas.transaction import TransactionCreate, TransactionUpdate # вызываем класс транзакции pydentic


class TransactionService:
    """CRUD операции для транзакций"""

    def __init__(self, db: Session)->None:
        self._db = db

    def get_all(self, month: int | None = None, year: int | None = None, account_id: int | None = None):
        """select по month, year, account_id"""
        query = self._db.query(Transaction).options(joinedload(Transaction.category), joinedload(Transaction.account), joinedload(Transaction.to_account)) # как select но еще не сделан запрос на уровень БД
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if year and month:
            from datetime import date
            date_from = date(year=year, month=month, day=1)
            date_to  = date(year=year, month=month+1, day=1) if month < 12 else date(year=year+1, month=1, day=1)
            query = query.filter(Transaction.date >= date_from, Transaction.date < date_to)

        return query.order_by(Transaction.date.desc()).all() # SELECT * FROM transactions ORDER BY date DESC

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        """select по transaction_id"""
        return self._db.get(Transaction, transaction_id)

    def create(self, payload: TransactionCreate) -> Transaction:
        """insert new transaction"""
        object = Transaction(**payload.model_dump()) # распковка аргументов TransactionCreate в словарь и  обратно в аргументы для Transaction sql
        self._db.add(object)
        self._db.commit()
        self._db.refresh(object)
        return object

    def update(self, transaction_id: int, payload: TransactionUpdate) -> Transaction | None:
        """update existing transaction"""
        object = self.get_by_id(transaction_id=transaction_id)
        if not object:
            return None
        for field, value in payload.model_dump(exclude_none=True).items(): # цикл обновляет только то что пришло, параметры с None отбрасываются
            setattr(object, field, value)
        self._db.commit()
        self._db.refresh(object)
        return object

    def delete(self, transaction_id: int) -> bool:
        """delete transaction"""
        object = self.get_by_id(transaction_id=transaction_id)
        if not object:
            return False
        self._db.delete(object)
        self._db.commit()
        return True
