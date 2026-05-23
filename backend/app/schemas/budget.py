from pydantic import BaseModel, ConfigDict, field_validator


class BudgetCreate(BaseModel):
    category_id: int
    month: int
    year: int
    limit: float

    @field_validator('month')
    @classmethod
    def month_valid(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError('Месяц должен быть от 1 до 12')
        return v

    @field_validator('limit')
    @classmethod
    def limit_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Лимит должен быть больше нуля')
        return v


class BudgetUpdate(BaseModel):
    limit: float

    @field_validator('limit')
    @classmethod
    def limit_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Лимит должен быть больше нуля')
        return v


class BudgetOut(BudgetCreate):
    id: int
    category_name: str | None = None
    spent: float = 0.0        # сколько потрачено по факту
    remaining: float = 0.0    # лимит - потрачено
    exceeded: bool = False    # превышен ли лимит

    model_config = ConfigDict(from_attributes=True)