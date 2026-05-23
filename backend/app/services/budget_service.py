from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate


class BudgetService:

    def __init__(self, db: Session) -> None:
        self._db = db

    def _calc_spent(self, category_id: int, month: int, year: int) -> float:
        """Считает сумму расходов по категории за указанный месяц"""
        date_from = date(year=year, month=month, day=1)
        date_to = date(year=year, month=month + 1, day=1) if month < 12 else date(year=year + 1, month=1, day=1)

        rows = (
            self._db.query(Transaction)
            .filter(
                Transaction.category_id == category_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= date_from,
                Transaction.date < date_to,
            )
            .all()
        )
        return sum(float(t.amount) for t in rows)

    def _enrich(self, budget: Budget) -> BudgetOut:
        """Добавляет вычисляемые поля к объекту бюджета"""
        spent = self._calc_spent(budget.category_id, budget.month, budget.year)
        limit = float(budget.limit)
        return BudgetOut(
            id=budget.id,
            category_id=budget.category_id,
            category_name=budget.category.name if budget.category else None,
            month=budget.month,
            year=budget.year,
            limit=limit,
            spent=spent,
            remaining=limit - spent,
            exceeded=spent > limit,
        )

    def get_all(self, month: int | None = None, year: int | None = None) -> list[BudgetOut]:
        query = self._db.query(Budget).options(joinedload(Budget.category))
        if month:
            query = query.filter(Budget.month == month)
        if year:
            query = query.filter(Budget.year == year)
        return [self._enrich(b) for b in query.all()]

    def get_by_id(self, budget_id: int) -> Budget | None:
        return self._db.query(Budget).options(joinedload(Budget.category)).filter(Budget.id == budget_id).first()

    def create(self, payload: BudgetCreate) -> BudgetOut:
        obj = Budget(
            category_id=payload.category_id,
            month=payload.month,
            year=payload.year,
            limit=payload.limit,
        )
        self._db.add(obj)
        self._db.commit()
        self._db.refresh(obj)
        # после refresh relationship не загружен, делаем повторный запрос
        return self._enrich(self.get_by_id(obj.id))

    def update(self, budget_id: int, payload: BudgetUpdate) -> BudgetOut | None:
        obj = self.get_by_id(budget_id)
        if not obj:
            return None
        obj.limit = payload.limit
        self._db.commit()
        self._db.refresh(obj)
        return self._enrich(self.get_by_id(obj.id))

    def delete(self, budget_id: int) -> bool:
        obj = self.get_by_id(budget_id)
        if not obj:
            return False
        self._db.delete(obj)
        self._db.commit()
        return True