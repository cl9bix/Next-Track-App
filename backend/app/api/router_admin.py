from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models import Event
from app.admin_models import AdminUser
from app.schemas import AdminLoginIn, TokenOut, EventCreate, EventUpdate, EventOut
from app.security import create_access_token, verify_password, decode_token

router = APIRouter(prefix="/admin", tags=["admin"])

# ===== Helpers
def get_current_admin(
        db: Session = Depends(get_db),
        authorization: Optional[str] = Header(None)
) -> AdminUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("No sub in token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admin = db.query(AdminUser).filter(AdminUser.username == sub).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    return admin

# ===== Auth




@router.post("/login", response_model=TokenOut)
def admin_login(data: AdminLoginIn, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == data.username).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials")
    token = create_access_token({"sub": admin.username})
    return TokenOut(access_token=token)

# ===== Events (own only)
@router.get("/events", response_model=List[EventOut])
def list_events(me: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = db.query(Event).filter(Event.organisator_id == me.organisator_id).order_by(Event.start_date.desc().nullslast())
    return q.all()

@router.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, me: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    if not me.organisator_id:
        raise HTTPException(status_code=400, detail="Admin is not bound to an organiser")
    e = Event(
        title=payload.title,
        preview=payload.preview,
        start_date=payload.start_date,
        end_date=payload.end_date,
        dj_id=payload.dj_id,
        organisator_id=me.organisator_id,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

def _get_owned_event(db: Session, me: AdminUser, event_id: int) -> Event:
    e = db.query(Event).filter(Event.id == event_id, Event.organisator_id == me.organisator_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    return e

@router.put("/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventUpdate, me: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    e = _get_owned_event(db, me, event_id)
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(e, k, v)
    db.commit()
    db.refresh(e)
    return e

@router.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, me: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    e = _get_owned_event(db, me, event_id)
    db.delete(e)
    db.commit()
    return
