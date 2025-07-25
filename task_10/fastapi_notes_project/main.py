from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from app.database import init_db, get_session
from app.models import User, Note
from app.schemas import UserCreate, UserLogin, Token, NoteCreate, NoteUpdate, NoteOut
from app.auth import get_password_hash, verify_password, create_access_token
from app.deps import get_current_user

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/register", response_model=Token)
def register(user: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_pw)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

@app.post("/notes", response_model=NoteOut)
def create_note(note: NoteCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_note = Note(**note.dict(), owner_id=current_user.id)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

@app.get("/notes", response_model=List[NoteOut])
def list_notes(skip: int = 0, limit: int = 10, search: Optional[str] = None, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    stmt = select(Note).where(Note.owner_id == current_user.id)
    if search:
        stmt = stmt.where(Note.title.contains(search) | Note.content.contains(search))
    stmt = stmt.offset(skip).limit(limit)
    return session.exec(stmt).all()

@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note_data: NoteUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = note_data.title
    note.content = note_data.content
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    note = session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return {"ok": True}
