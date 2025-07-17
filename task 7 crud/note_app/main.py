from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from database import init_db, get_session
from models import User, Note
from schemas import UserCreate, UserLogin, Token, NoteCreate, NoteOut, NoteUpdate
from auth import (
    get_password_hash, verify_password,
    create_access_token, get_current_user,
    require_role
)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

# 🔐 REGISTER
@app.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username taken")
    hashed = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

# 🔐 LOGIN
@app.post("/login", response_model=Token)
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# 👤 USER INFO
@app.get("/users/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role}

# 👑 ADMIN ROUTE
@app.get("/admin/users")
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(require_role("admin"))):
    users = session.exec(select(User)).all()
    return users

# 📝 CRUD ЗАМЕТОК
@app.post("/notes", response_model=NoteOut)
def create_note(note: NoteCreate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    new_note = Note(**note.dict(), owner_id=user.id)
    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return new_note

@app.get("/notes", response_model=list[NoteOut])
def list_notes(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notes = session.exec(select(Note).where(Note.owner_id == user.id)).all()
    return notes

@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    note = session.get(Note, note_id)
    if not note or note.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note_data: NoteUpdate, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    note = session.get(Note, note_id)
    if not note or note.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = note_data.title
    note.content = note_data.content
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    note = session.get(Note, note_id)
    if not note or note.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return {"ok": True}
