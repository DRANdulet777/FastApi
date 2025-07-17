from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

@celery.task
def send_email(email: str):
    print(f"Sending email to {email}...")
    return f"Email sent to {email}"
