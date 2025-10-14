from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Index, Boolean, BigInteger, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.session import Base

class Organisator(Base):
    __tablename__ = "organisators"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    events = relationship("Event", back_populates="organisator")

class Dj(Base):
    __tablename__ = "djs"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    events = relationship("Event", back_populates="dj")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    preview = Column(String(2048))
    start_date = Column(DateTime(timezone=True))
    end_date   = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organisator_id = Column(Integer, ForeignKey("organisators.id", ondelete="SET NULL"))
    dj_id          = Column(Integer, ForeignKey("djs.id", ondelete="SET NULL"))
    current_round_id = Column(Integer, ForeignKey("rounds.id", ondelete="SET NULL"))

    organisator = relationship("Organisator", back_populates="events")
    dj          = relationship("Dj", back_populates="events")
    rounds = relationship("Round", back_populates="event", cascade="all, delete-orphan", passive_deletes=True)
    current_round = relationship("Round", foreign_keys=[current_round_id])

    __table_args__ = (Index("ix_events_start_date_title", "start_date", "title"),)

class Round(Base):
    __tablename__ = "rounds"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at   = Column(DateTime(timezone=True))
    winner_song_id = Column(Integer, ForeignKey("songs.id", ondelete="SET NULL"))
    event = relationship("Event", back_populates="rounds")
    songs = relationship("Song", back_populates="round", cascade="all, delete-orphan", passive_deletes=True)
    __table_args__ = (Index("ix_round_event_number", "event_id", "number", unique=True),)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    notifications = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    round_id = Column(Integer, ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    round = relationship("Round", back_populates="songs")
    votes = relationship("Vote", back_populates="song", cascade="all, delete-orphan", passive_deletes=True)
    __table_args__ = (
        UniqueConstraint("round_id", "name", name="uq_song_round_name"),
        Index("ix_song_event_round", "event_id", "round_id"),
    )

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user = relationship("User", back_populates="votes")
    song = relationship("Song", back_populates="votes")
    __table_args__ = (
        UniqueConstraint("user_id", "song_id", name="uq_vote_user_song"),
        Index("ix_votes_song_user", "song_id", "user_id"),
    )
