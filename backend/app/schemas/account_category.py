from pydantic import BaseModel, ConfigDict

from app.models.category import CategoryType

class AccountCreate(BaseModel):
    name:str
    currency:str = "RUB"
    balance:float = 0.0

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
