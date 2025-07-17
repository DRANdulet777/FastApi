from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from database import get_session
from models import User
from sqlmodel import Session, select
from auth import SECRET_KEY, ALGORITHM

def get_current_user(token: str = Depends(lambda: None), session: Session = Depends(get_session)):
    if token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
