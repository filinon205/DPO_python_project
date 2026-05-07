from fastapi import APIRouter, Depends, HTTPException, Query
from h11 import Response
from sqlalchemy.orm import Session
from typing import Optional

from starlette import status

from app.database import get_db
from app.models.account import Account
from app.schemas.account_category import AccountOut, AccountCreate
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db))->list[AccountOut]:
    return AccountService(db=db).get_all()

@router.post('/', response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate,db: Session = Depends(get_db)) -> AccountOut:
    return AccountService(db=db).create(payload)

@router.get('/{account_id}', response_model=AccountOut)
def get_account(self, account_id: int, db: Session = Depends(get_db)) -> AccountOut:
    object = AccountService(db=db).get_by_id(account_id)
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
    return object

@router.delete('/{account_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db))->None:
    object = AccountService(db=db).delete(account_id)
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
