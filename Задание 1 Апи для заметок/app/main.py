from fastapi import FastAPI, Depends
from app.database import async_session, init_db
from app.models import Note
from app.schemas import NoteCreate, NoteOut
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

# Зависимость
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.post("/notes", response_model=NoteOut)
async def create_note(note: NoteCreate, session: AsyncSession = Depends(get_session)):
    new_note = Note(text=note.text)
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return new_note

@app.get("/notes", response_model=List[NoteOut])
async def get_notes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Note))
    notes = result.scalars().all()
    return notes
