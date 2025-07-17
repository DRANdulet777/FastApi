from fastapi import FastAPI, HTTPException
from app.db import database, metadata, engine
from app.models import notes
from app.redis_client import init_redis, get_cached, set_cache, delete_cache
from pydantic import BaseModel
import json

app = FastAPI()

metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()
    await init_redis()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class NoteIn(BaseModel):
    title: str
    content: str

class NoteOut(NoteIn):
    id: int


@app.get("/notes", response_model=list[NoteOut])
async def get_notes():
    cache_key = "notes_all"
    cached = await get_cached(cache_key)
    if cached:
        return json.loads(cached)

    query = notes.select()
    result = await database.fetch_all(query)
    result_list = [dict(r) for r in result]
    await set_cache(cache_key, json.dumps(result_list))
    return result_list


@app.post("/notes", response_model=NoteOut)
async def create_note(note: NoteIn):
    query = notes.insert().values(title=note.title, content=note.content)
    note_id = await database.execute(query)
    await delete_cache("notes_all")
    return {**note.dict(), "id": note_id}


@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    query = notes.delete().where(notes.c.id == note_id)
    result = await database.execute(query)
    if result == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    await delete_cache("notes_all")
    return {"message": "Note deleted"}
