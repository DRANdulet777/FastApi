from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str  # В открытом виде (для учебных целей)

# Pydantic-схемы
class UserCreate(SQLModel):
    username: str
    password: str

class UserLogin(SQLModel):
    username: str
    password: str
