from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# --- core ---
class EventBase(BaseModel):
    title: str
    preview: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    dj_id: Optional[int] = None
    organisator_id: Optional[int] = None

class EventCreate(EventBase): pass
class EventUpdate(EventBase): pass

class EventResponse(EventBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

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
