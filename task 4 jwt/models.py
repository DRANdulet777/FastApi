from sqlmodel import SQLModel, Field
from typing import Optional

# Модель таблицы пользователя
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str  # хранится в виде хеша

# Схема для регистрации
class UserCreate(SQLModel):
    username: str
    password: str

# Схема для входа
class UserLogin(SQLModel):
    username: str
    password: str
