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


from datetime import datetime
from pydantic import BaseModel, ConfigDict

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    title: str
    preview: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime | None = None


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

class AdminClubOut(BaseModel):
    id: int
    name: str
    slug: str

class AdminMeOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    telegram_id: Optional[int] = None
    role: str
    is_active: bool
    max_club_count: int
    clubs: list[AdminClubOut]


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

class ClubSettingsUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    background_image_url: Optional[str] = None
    max_suggestions_per_user: Optional[int] = None
    voting_duration_sec: Optional[int] = None
    allow_explicit: Optional[bool] = None
    auto_play: Optional[bool] = None

class ClubResponse(ClubCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SuggestIn(BaseModel):
    track_id: str | None = None
    title: str
    artist: str | None = None
    cover_url: str | None = None
    duration_sec: int | None = None
