import datetime as dt

from pydantic import BaseModel, ConfigDict
from app.models.transaction import TransactionType, Periodicity

class TransactionBase(BaseModel):
    """обычный Pydantic BaseModel. Содержит все общие поля которые есть и в Create и в Out"""
    type: TransactionType
    amount: float
    date: dt.date
    description: str|None = None
    periodicity: Periodicity = Periodicity.ONE_TIME
    account_id: int
    category_id: int|None = None
    to_account_id: int|None = None

class TransactionCreate(TransactionBase):
    """то что принимаем от пользователя (без id)"""
    pass

class TransactionUpdate(BaseModel):
    """TransactionUpdate не наследуется от Base. Все поля с | None,
    это значит что при обновлении можно передать только те поля
     которые хочешь изменить, остальные останутся прежними."""
    amount: float|None = None
    date: dt.date|None = None
    description: str|None = None
    category_id: int|None = None

class TransactionOut(TransactionBase):
    """то что отдаём пользователю (с id), наследуем из Base и добавляем id,
    его генерирует БД, поэтому при создании его нет, а при ответе он уже есть."""
    id: int
    category_name: str | None = None
    account_name: str | None = None
    to_account_name: str | None = None
    model_config = ConfigDict(from_attributes=True) # Эта настройка говорит: "умей читать атрибуты объекта как поля схемы"