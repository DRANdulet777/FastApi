from fastapi import FastAPI
from app.celery_worker import send_email

app = FastAPI()

@app.get("/")
def root():
    return {"message": "App is working"}

@app.post("/send-email/")
def trigger_email(email: str):
    task = send_email.delay(email)
    return {"task_id": task.id, "status": "Email task triggered"}
