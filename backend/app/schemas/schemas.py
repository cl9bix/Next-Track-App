from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, ConfigDict, constr


# ============================================================
# Event
# ============================================================

class EventBase(BaseModel):
    title: str
    preview: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    club_id: int


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventResponse(EventBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ❗️ Публічний івент — НЕ ORM
class PublicEventResponse(BaseModel):
    id: int
    title: str
    club_slug: str
    club_name: str
    preview: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ============================================================
# Rounds / Songs / Votes
# ============================================================

class RoundResponse(BaseModel):
    id: int
    number: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    winner_song_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SongCreate(BaseModel):
    name: str


class SongResponse(BaseModel):
    id: int
    name: str
    round_id: int
    votes: int

    model_config = ConfigDict(from_attributes=True)


class VoteCreate(BaseModel):
    song_id: int


class StateResponse(BaseModel):
    event: EventResponse
    round: RoundResponse
    songs: List[SongResponse]
    user_voted_song_ids: List[int] = []


# ============================================================
# Organisator
# ============================================================

class OrganisatorBase(BaseModel):
    name: str
    username: constr(strip_whitespace=True, min_length=3, max_length=100)


class OrganisatorCreate(OrganisatorBase):
    password: constr(min_length=6)
    telegram_id: Optional[int] = None


class OrganisatorResponse(BaseModel):
    id: int
    name: str
    username: str
    telegram_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    username: str
    password: str


# ============================================================
# Club
# ============================================================

class ClubCreate(BaseModel):
    name: str
    slug: str
    tg_username: str
    site_url: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Dict[str, Any] = {}


class ClubUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    tg_username: Optional[str] = None
    site_url: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Optional[Dict[str, Any]] = None


class ClubResponse(ClubCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
