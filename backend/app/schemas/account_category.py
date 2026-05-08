from pydantic import BaseModel, ConfigDict, field_validator

from app.models.category import CategoryType

class AccountCreate(BaseModel):
    name:str
    currency:str = "RUB"
    balance:float = 0.0

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Название счёта не может быть пустым')
        return v.strip()

class AccountOut(AccountCreate):
    id:int
    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name:str
    type:CategoryType
    parent_id: int|None = None

class CategoryOut(CategoryCreate):
    id:int
    model_config = ConfigDict(from_attributes=True)
