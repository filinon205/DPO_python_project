from sqlalchemy import extract
from sqlalchemy.engine import row
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
import pandas as pd

def get_summary(db: Session, year: int, month:int) -> dict:
    rows = (db.query(Transaction).filter(Transaction.type.in_([TransactionType.INCOME, TransactionType.EXPENSE]),
                                        extract('year', Transaction.date)==year,
                                        extract('month', Transaction.date)==month,).all())

    if not rows:
        return {"income":0,"expense":0,"balance":0}

    df = pd.DataFrame([{"amount":row.amount, "type":row.type.value} for row in rows])

    income = float(df[df["type"] == "income"]["amount"].sum())
    expense = float(df[df["type"] == "expense"]["amount"].sum())

    return {"income": income, "expense": expense, "balance": income - expense}

def get_by_category(db: Session, year: int, month: int) -> list:
    rows = db.query(Transaction).filter(
        Transaction.type == TransactionType.EXPENSE,
        extract('year', Transaction.date)==year,
        extract('month', Transaction.date)==month,
    ).all()

    if not rows:
        return []

    df = pd.DataFrame([{"category":row.category.name if row.category else "Без категории",
                       "amount":row.amount,} for row in rows])
    grouped  =  df.groupby("category")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)

    return grouped.rename(columns={"amount": "total"}).to_dict(orient="records") # Переименовываем колонку amount в total

def get_monthly_trend(db: Session, year: int) -> list:
    rows = db.query(Transaction).filter(
        Transaction.type.in_([TransactionType.INCOME, TransactionType.EXPENSE]),
        extract('year', Transaction.date)==year,
    ).all()

    if not rows:
        return []

    df = pd.DataFrame([{"month": row.date.month,"type": row.type.value,"amount": row.amount,} for row in rows])
    grouped = df.groupby(['month', 'type'])['amount'].sum().reset_index()
    pivot =  grouped.pivot(index='month', columns='type', values='amount').fillna(0) # pivot это разворот таблицы. Было: строки с колонками month, type, amount. Стало: строки = месяцы, колонки = типы (INCOME, EXPENSE), значения = суммы
    pivot = pivot.reset_index()

    if "income" not in pivot.columns: # Защита: если за весь год нет ни одной транзакции типа INCOME, колонка INCOME вообще не появится в pivot. Добавляем её вручную с нулями
        pivot["income"] = 0.0
    if "expense" not in pivot.columns: # аналогично
        pivot["expense"] = 0.0

    result = []
    for _, row in pivot.iterrows():
        result.append({"month": int(row["month"]),"income": float(row["income"]),"expense": float(row["expense"]),}) #Возвращаем словарь, он автоматически станет JSON в роутере

    return result