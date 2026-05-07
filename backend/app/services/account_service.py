from sqlalchemy.orm import Session, joinedload

from app.models.account import Account # модель таблицы orm sql
from app.schemas.account_category import AccountCreate, AccountOut

class AccountService:
    def __init__(self, db: Session):
        self._db = db

    def get_all(self)->list[Account]:
        return self._db.query(Account).options(
            joinedload(Account.transactions),
            joinedload(Account.incoming_transfers),
        ).all()

    def get_by_id(self, account_id: int)->Account | None:
        return self._db.get(Account,account_id)

    def create(self, payload: AccountCreate) -> Account:
        object = Account(name=payload.name, currency=payload.currency, initial_balance=payload.balance)
        self._db.add(object)
        self._db.commit()
        self._db.refresh(object)
        return object

    def delete(self, account_id: int)->bool:
        object = self.get_by_id(account_id)
        if not object:
            return False
        self._db.delete(object)
        self._db.commit()
        return True

