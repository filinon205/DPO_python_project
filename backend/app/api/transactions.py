from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionOut # Pydantic-схемы. TransactionCreate: что мы ожидаем получить от клиента. TransactionOut: что мы отдаём обратно.
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=list[TransactionOut])
def list_transactions(self, month: Optional[int] = Query(None, ge=1, le=12)
                      , year: Optional[int] = Query(None, ge=2000),
                      account_id: Optional[int]=None, db: Session = Depends(get_db)):
    return TransactionService(db=db).get_all(month=month, year=year, account_id=account_id) # отдаем на сервис

@router.post("/", response_model=list[TransactionOut])
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)): # db: Session = Depends(get_db) - перед вызовом функции, вызови get_db, возьми что она вернёт и подставь в переменную db
    return TransactionService(db=db).create(payload=payload)

@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    object = TransactionService(db=db).get_by_id(transaction_id)
    if not object:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return object

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    object = TransactionService(db=db).delete(transaction_id)
    if not object:
        raise HTTPException(status_code=404, detail="Transaction not found")