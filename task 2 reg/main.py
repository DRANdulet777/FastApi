from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, create_engine, Session, select
from models import User, UserCreate, UserLogin

DATABASE_URL = "postgresql://postgres:password@localhost:5432/testdb"
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()

# Создание таблицы
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Зависимость сессии
def get_session():
    with Session(engine) as session:
        yield session

@app.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):
    # Проверка уникальности
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Создание нового пользователя
    new_user = User(username=user.username, password=user.password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if not existing_user or existing_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "username": existing_user.username}
