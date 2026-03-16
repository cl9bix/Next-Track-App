from __future__ import annotations

import enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.session import Base


# ===================== ENUMS =====================

class AdminRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"


class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    live = "live"
    ended = "ended"


# ===================== CLUB / ADMINS =====================

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)

    admin_links = relationship(
        "AdminClub",
        back_populates="club",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    events = relationship(
        "Event",
        back_populates="club",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    club_settings = relationship(
        "ClubSettings",
        back_populates="club",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_clubs_name", "name"),
    )


class ClubSettings(Base):
    __tablename__ = "club_settings"

    id = Column(Integer, primary_key=True)

    club_id = Column(
        Integer,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    description = Column(String(2000), nullable=True)

    max_suggestions_per_user = Column(Integer, nullable=False, server_default="3")
    voting_duration_sec = Column(Integer, nullable=False, server_default="60")
    background_image_url = Column(String(1024), nullable=True)
    allow_explicit = Column(Boolean,    nullable=False, server_default="false")
    auto_play = Column(Boolean, nullable=False, server_default="false")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    club = relationship("Club", back_populates="club_settings")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    display_name = Column(String(120), nullable=True)

    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    role = Column(
        SAEnum(AdminRole, name="admin_role"),
        nullable=False,
        server_default=AdminRole.admin.value,
    )

    is_active = Column(Boolean, nullable=False, server_default="true")
    max_club_count = Column(Integer, nullable=False, server_default="1")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    admin_clubs = relationship(
        "AdminClub",
        back_populates="admin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_admin_users_is_active", "is_active"),
    )


class AdminClub(Base):
    __tablename__ = "admin_clubs"

    admin_id = Column(
        Integer,
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    club_id = Column(
        Integer,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        primary_key=True,
    )

    admin = relationship("AdminUser", back_populates="admin_clubs")
    club = relationship("Club", back_populates="admin_links")

    __table_args__ = (
        UniqueConstraint("admin_id", "club_id", name="uq_admin_club"),
        Index("ix_admin_clubs_admin_id", "admin_id"),
        Index("ix_admin_clubs_club_id", "club_id"),
    )


# ===================== EVENTS / DJS =====================

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    club_id = Column(
        Integer,
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(255), nullable=False, index=True)
    preview = Column(String(2048), nullable=True)
    # background_image_url = Column(String(1024), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True, index=True)
    end_date = Column(DateTime(timezone=True), nullable=True, index=True)

    status = Column(
        SAEnum(EventStatus, name="event_status"),
        nullable=False,
        server_default=EventStatus.scheduled.value,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    club = relationship("Club", back_populates="events")

    event_djs = relationship(
        "EventDJ",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    rounds = relationship(
        "Round",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_events_club_start", "club_id", "start_date"),
        Index("ix_events_club_created", "club_id", "created_at"),
        Index("ix_events_club_status", "club_id", "status"),
    )


class Dj(Base):
    __tablename__ = "djs"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event_links = relationship(
        "EventDJ",
        back_populates="dj",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_djs_name", "name"),
    )


class EventDJ(Base):
    __tablename__ = "event_djs"

    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dj_id = Column(
        Integer,
        ForeignKey("djs.id", ondelete="CASCADE"),
        primary_key=True,
    )

    event = relationship("Event", back_populates="event_djs")
    dj = relationship("Dj", back_populates="event_links")

    __table_args__ = (
        UniqueConstraint("event_id", "dj_id", name="uq_event_dj"),
        Index("ix_event_djs_event", "event_id"),
        Index("ix_event_djs_dj", "dj_id"),
    )


# ===================== ROUNDS / SONGS / VOTES =====================

class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True)

    event_id = Column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    number = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Без ForeignKey на songs, щоб уникнути циклу в initial migration
    winner_song_id = Column(Integer, nullable=True)

    event = relationship("Event", back_populates="rounds", foreign_keys=[event_id])

    songs = relationship(
        "Song",
        back_populates="round",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="Song.round_id",
        primaryjoin="Round.id == Song.round_id",
    )

    votes = relationship(
        "Vote",
        back_populates="round",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="Vote.round_id",
    )

    __table_args__ = (
        UniqueConstraint("event_id", "number", name="uq_round_event_number"),
        Index("ix_round_event", "event_id"),
        Index("ix_round_event_number", "event_id", "number"),
    )


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)

    round_id = Column(
        Integer,
        ForeignKey("rounds.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=True)

    source = Column(String(32), nullable=True)
    source_id = Column(String(128), nullable=True)
    cover_url = Column(String(1024), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    round = relationship(
        "Round",
        back_populates="songs",
        foreign_keys=[round_id],
        primaryjoin="Song.round_id == Round.id",
    )

    votes = relationship(
        "Vote",
        back_populates="song",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("round_id", "title", "artist", name="uq_song_round_title_artist"),
        Index("ix_song_round", "round_id"),
        Index("ix_song_source_source_id", "source", "source_id"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    notifications = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    votes = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    round_id = Column(
        Integer,
        ForeignKey("rounds.id", ondelete="CASCADE"),
        nullable=False,
    )
    song_id = Column(
        Integer,
        ForeignKey("songs.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="votes")
    song = relationship("Song", back_populates="votes")
    round = relationship("Round", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "round_id", name="uq_vote_user_round"),
        Index("ix_votes_round_song", "round_id", "song_id"),
        Index("ix_votes_user_round", "user_id", "round_id"),
        Index("ix_votes_song_id", "song_id"),
    )