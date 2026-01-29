from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Index,
    Boolean, BigInteger, UniqueConstraint, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
import enum

from app.models.session import Base


class AdminRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"


class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    live = "live"
    ended = "ended"


from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.session import Base


class Club(Base):
    __tablename__ = "clubs"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)

    admins = relationship("AdminUser", back_populates="club", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="club", cascade="all, delete-orphan")


class AdminUser(Base):
    """
    Адмін панелі (owner/admin). Додаєш вручну.
    """
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)

    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)  # можеш лишити optional
    display_name = Column(String(120), nullable=True)

    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    role = Column(Enum(AdminRole, name="admin_role"), nullable=False, server_default=AdminRole.admin.value)

    is_active = Column(Boolean, default=True, nullable=False)

    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    club = relationship("Club", back_populates="admins")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)

    title = Column(String, nullable=False, index=True)
    preview = Column(String(2048), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    club = relationship("Club", back_populates="events")

    djs = relationship("EventDJ", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_events_club_start", "club_id", "start_date"),
    )



class Dj(Base):
    __tablename__ = "djs"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    events = relationship("EventDJ", back_populates="dj", cascade="all, delete-orphan")


class EventDJ(Base):
    """
    M2M: один івент має багато діджеїв.
    """
    __tablename__ = "event_djs"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    dj_id = Column(Integer, ForeignKey("djs.id", ondelete="CASCADE"), primary_key=True)

    event = relationship("Event", back_populates="djs")
    dj = relationship("Dj", back_populates="events")


class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    number = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    winner_song_id = Column(Integer, ForeignKey("songs.id", ondelete="SET NULL"), nullable=True)

    event = relationship("Event", back_populates="rounds", foreign_keys=[event_id])

    songs = relationship(
        "Song",
        back_populates="round",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    winner_song = relationship("Song", foreign_keys=[winner_song_id], uselist=False, post_update=True)

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
    round_id = Column(Integer, ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)

    # MVP: назва + артист (краще ніж просто name)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)

    # якщо ти тягнеш з Deezer/iTunes — зручно зберегти source/id
    source = Column(String(32), nullable=True)  # "deezer" | "itunes" | ...
    source_id = Column(String(128), nullable=True)  # id у провайдера
    cover_url = Column(String(1024), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    round = relationship("Round", back_populates="songs")
    votes = relationship("Vote", back_populates="song", cascade="all, delete-orphan", passive_deletes=True)

    __table_args__ = (
        # щоб не додавали один і той самий трек 20 разів в раунд
        UniqueConstraint("round_id", "title", "artist", name="uq_song_round_title_artist"),
        Index("ix_song_round", "round_id"),
    )


class Vote(Base):
    """
    MVP: 1 голос на раунд (користувач обрав конкретну пісню).
    """
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    round_id = Column(Integer, ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="votes")
    song = relationship("Song", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "round_id", name="uq_vote_user_round"),
        Index("ix_votes_round_song", "round_id", "song_id"),
    )
