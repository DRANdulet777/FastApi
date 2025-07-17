from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, create_engine, select
from models import User, UserCreate, UserLogin
from auth import get_password_hash, verify_password
from token import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

DATABASE_URL = "postgresql://postgres:password@localhost:5432/testdb"
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ Создание токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
