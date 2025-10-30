import os, datetime
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.session import get_async_session as get_db
from app.models.models import Organisator

PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("ORG_JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("ORG_JWT_EXPIRES_MIN", "60"))  # 60 хв за замовч.

def hash_password(password: str) -> str:
    return PWD.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return PWD.verify(password, password_hash)

def create_token(org: Organisator) -> str:
    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRES_MIN)
    payload = {"sub": str(org.id), "username": org.username, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_organisator(db: Session = Depends(get_db), token: str | None = None):
    """
    Токен беремо з cookie 'org_token' або з Authorization: Bearer
    """
    from fastapi import Request
    def _resolver(request: Request):
        t = token
        if not t:
            t = request.cookies.get("org_token")
        if not t:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                t = auth.split(" ", 1)[1]
        if not t:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        try:
            data = jwt.decode(t, JWT_SECRET, algorithms=[JWT_ALG])
            org_id = int(data.get("sub"))
        except (JWTError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        org = db.query(Organisator).get(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return org
    return _resolver  # FastAPI підхопить як залежність callable
