import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session
from models import User, Note
from auth import get_password_hash, create_access_token

test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(test_engine)

def override_get_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

def register_user(username="alice", password="secret"):
    return client.post("/register", json={"username": username, "password": password})

def login_user(username="alice", password="secret"):
    return client.post("/login", json={"username": username, "password": password})

def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}

def test_register_and_login():
    res = register_user()
    assert res.status_code == 200
    assert "access_token" in res.json()

    res = login_user()
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_get_me_protected():
    token = login_user().json()["access_token"]
    res = client.get("/users/me", headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["username"] == "alice"

def test_create_and_list_notes():
    token = login_user().json()["access_token"]
    note = {"title": "Note 1", "content": "Test content"}
    res = client.post("/notes", headers=auth_headers(token), json=note)
    assert res.status_code == 200
    assert res.json()["title"] == "Note 1"

    res = client.get("/notes", headers=auth_headers(token))
    assert res.status_code == 200
    assert len(res.json()) == 1

def test_note_filter_and_pagination():
    token = login_user().json()["access_token"]
    headers = auth_headers(token)
    for i in range(20):
        client.post("/notes", headers=headers, json={"title": f"title {i}", "content": f"content {i}"})

    res = client.get("/notes?skip=5&limit=10", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 10

    res = client.get("/notes?search=title 1", headers=headers)
    assert res.status_code == 200
    assert any("title 1" in note["title"] for note in res.json())

def test_note_is_user_specific():
    register_user("bob", "secret")
    token_alice = login_user().json()["access_token"]
    token_bob = login_user("bob").json()["access_token"]

    note = {"title": "Private", "content": "Only mine"}
    client.post("/notes", headers=auth_headers(token_alice), json=note)

    res = client.get("/notes", headers=auth_headers(token_bob))
    assert res.status_code == 200
    assert res.json() == []
