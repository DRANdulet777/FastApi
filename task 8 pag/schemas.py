from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    class Config:
        orm_mode = True
