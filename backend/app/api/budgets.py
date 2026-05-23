from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/", response_model=list[BudgetOut])
def list_budgets(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
):
    return BudgetService(db=db).get_all(month=month, year=year)


@router.post("/", response_model=BudgetOut, status_code=201)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    return BudgetService(db=db).create(payload=payload)


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(budget_id: int, payload: BudgetUpdate, db: Session = Depends(get_db)):
    obj = BudgetService(db=db).update(budget_id=budget_id, payload=payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    return obj


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    ok = BudgetService(db=db).delete(budget_id=budget_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Бюджет не найден")