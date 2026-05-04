from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get('/summary')
def summary(year:int, month: int, db: Session = Depends(get_db))->dict:
    return analytics_service.get_summary(db=db,year=year,month=month)

@router.get('/by-category')
def by_category(year: int, month: int, db: Session = Depends(get_db))->list[dict]:
    return analytics_service.get_by_category(db=db,year=year,month=month)

@router.get('/monthly-trend')
def monthly_trend(year: int, db: Session = Depends(get_db))->list[dict]:
    return analytics_service.get_monthly_trend(db=db,year=year)