from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.core.redis_client import redis_client
from app.services.event_keys import k_state, k_queue, k_score, k_voted, k_candidates
from app.services.live_bus import publish_event  # у тебе вже є


DEFAULT_TRACK_SECONDS = 180
VOTE_CLOSE_BEFORE_SECONDS = 30
STATE_TTL_SECONDS = 60 * 60 * 12  # 12 год, щоб не висіло вічно


@dataclass(frozen=True)
class Track:
    """
    Трек не зберігаємо в БД — лише в Redis в JSON.
    track_id — унікальний (можеш брати provider:id, типу "deezer:123").
    """
    track_id: str
    title: str
    artist: str | None = None
    cover_url: str | None = None
    duration_sec: int | None = None  # якщо нема — дефолт


def _now() -> int:
    return int(time.time())


def _track_key(track_id: str) -> str:
    return f"track:{track_id}"


async def _store_track(track: Track, ttl: int) -> None:
    # зберігаємо payload треку лише на час життя раунду/івенту
    payload = {
        "track_id": track.track_id,
        "title": track.title,
        "artist": track.artist,
        "cover_url": track.cover_url,
        "duration_sec": track.duration_sec,
    }
    await redis_client.set(_track_key(track.track_id), json.dumps(payload, ensure_ascii=False), ex=ttl)


async def _load_track(track_id: str) -> Optional[dict]:
    raw = await redis_client.get(_track_key(track_id))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return {"track_id": track_id}


async def enqueue_track(event_id: int, track: Track) -> None:
    """
    Додає трек в кінець черги + кешує його дані в Redis на TTL.
    """
    # TTL прив’яжемо до івенту (state TTL), щоб все само чистилось
    ttl = STATE_TTL_SECONDS
    await _store_track(track, ttl=ttl)

    await redis_client.rpush(k_queue(event_id), track.track_id)
    await redis_client.expire(k_queue(event_id), ttl)
    await redis_client.expire(k_score(event_id), ttl)

    await publish_event(event_id, {"type": "queue_added", "track_id": track.track_id})


async def get_queue_snapshot(event_id: int, limit: int = 10) -> List[dict]:
    ids = await redis_client.lrange(k_queue(event_id), 0, max(0, limit - 1))
    out: List[dict] = []
    for tid in ids:
        t = await _load_track(tid)
        out.append(t or {"track_id": tid})
    return out


async def start_event_if_needed(event_id: int) -> None:
    """
    Якщо івент не live — робимо live і стартуємо перший трек (якщо є).
    """
    st = await redis_client.hgetall(k_state(event_id))
    if st and st.get("status") in ("live", "ended"):
        return

    now = _now()
    await redis_client.hset(
        k_state(event_id),
        mapping={
            "status": "live",
            "current_track_id": "",
            "track_started_at": "0",
            "track_ends_at": "0",
            "vote_closes_at": "0",
            "voting_open": "0",
            "updated_at": str(now),
        },
    )
    await redis_client.expire(k_state(event_id), STATE_TTL_SECONDS)

    await publish_event(event_id, {"type": "event_live"})

    # одразу пробуємо перейти на трек
    await advance_to_next_track(event_id)


async def end_event(event_id: int) -> None:
    await redis_client.hset(k_state(event_id), mapping={"status": "ended", "voting_open": "0", "updated_at": str(_now())})
    await publish_event(event_id, {"type": "event_ended"})


async def _reset_voting(event_id: int, ttl: int) -> None:
    # чистимо кандидатів та score для поточного раунду
    await redis_client.delete(k_candidates(event_id))
    await redis_client.delete(k_score(event_id))
    await redis_client.expire(k_candidates(event_id), ttl)
    await redis_client.expire(k_score(event_id), ttl)


async def _prepare_candidates(event_id: int, top_n: int = 4) -> List[str]:
    """
    Кандидати — перші N треків з queue. Голосування йде тільки по ним.
    """
    ids = await redis_client.lrange(k_queue(event_id), 0, top_n - 1)
    if ids:
        await redis_client.delete(k_candidates(event_id))
        await redis_client.rpush(k_candidates(event_id), *ids)
        await redis_client.expire(k_candidates(event_id), STATE_TTL_SECONDS)
    return ids


async def open_voting_for_candidates(event_id: int, candidates: List[str], close_at: int) -> None:
    await redis_client.hset(
        k_state(event_id),
        mapping={
            "voting_open": "1",
            "vote_closes_at": str(close_at),
            "updated_at": str(_now()),
        },
    )
    payload = {"type": "voting_open", "vote_closes_at": close_at, "candidate_ids": candidates}
    await publish_event(event_id, payload)


async def close_voting(event_id: int) -> None:
    await redis_client.hset(k_state(event_id), mapping={"voting_open": "0", "updated_at": str(_now())})
    await publish_event(event_id, {"type": "voting_closed"})


async def pick_winner(event_id: int, candidates: List[str]) -> Optional[str]:
    """
    Переможець = max votes. Якщо ніхто не голосував — беремо першого кандидата.
    """
    if not candidates:
        return None

    scores = await redis_client.hmget(k_score(event_id), candidates)
    best_id = candidates[0]
    best_score = -1

    for tid, raw in zip(candidates, scores):
        try:
            v = int(raw or 0)
        except Exception:
            v = 0
        if v > best_score:
            best_score = v
            best_id = tid

    return best_id


async def advance_to_next_track(event_id: int) -> None:
    """
    Розумна логіка:
    - беремо candidates (перші 4 з черги)
    - відкриваємо голосування (якщо треків >= 2)
    - коли час — вибираємо переможця і робимо його current
    """
    # якщо event ended — нічого не робимо
    st = await redis_client.hgetall(k_state(event_id))
    if st.get("status") == "ended":
        return

    # якщо черга пуста — просто повідомляємо
    qlen = await redis_client.llen(k_queue(event_id))
    if qlen <= 0:
        await redis_client.hset(k_state(event_id), mapping={"current_track_id": "", "updated_at": str(_now())})
        await publish_event(event_id, {"type": "queue_empty"})
        return

    candidates = await _prepare_candidates(event_id, top_n=4)

    # якщо в черзі 1 трек — ставимо його автоматом (без голосування)
    if len(candidates) == 1:
        winner_id = candidates[0]
        await _set_current_track(event_id, winner_id, reason="single_track")
        return

    # якщо >= 2 — відкриваємо голосування на кандидати
    # голосування закриваємо через vote_close_seconds, а трек стартує коли голосування закрилось
    now = _now()
    # мінімальний час голосування, щоб люди встигли (наприклад 20 секунд)
    close_at = now + 20
    await _reset_voting(event_id, ttl=STATE_TTL_SECONDS)
    await open_voting_for_candidates(event_id, candidates, close_at=close_at)


async def _set_current_track(event_id: int, track_id: str, reason: str) -> None:
    t = await _load_track(track_id) or {"track_id": track_id}
    dur = int(t.get("duration_sec") or 0)
    if dur <= 0:
        dur = DEFAULT_TRACK_SECONDS

    now = _now()
    ends_at = now + dur
    vote_closes_at = max(now, ends_at - VOTE_CLOSE_BEFORE_SECONDS)

    await redis_client.hset(
        k_state(event_id),
        mapping={
            "current_track_id": track_id,
            "track_started_at": str(now),
            "track_ends_at": str(ends_at),
            "vote_closes_at": str(vote_closes_at),
            "voting_open": "0",
            "updated_at": str(now),
        },
    )
    await redis_client.expire(k_state(event_id), STATE_TTL_SECONDS)

    # IMPORTANT: переміщаємо winner на початок списку (він стає "current"),
    # а потім коли трек завершиться — просто LPOP.
    # Тут зробимо так: winner має бути першим елементом queue.
    # Для цього:
    # - видаляємо winner з queue (LREM)
    # - додаємо його на початок (LPUSH)
    await redis_client.lrem(k_queue(event_id), 0, track_id)
    await redis_client.lpush(k_queue(event_id), track_id)

    await publish_event(event_id, {"type": "track_started", "track": t, "ends_at": ends_at, "reason": reason})


async def confirm_winner_and_start_track(event_id: int) -> Optional[dict]:
    """
    Викликається коли голосування закрилось: обираємо winner -> ставимо current.
    """
    candidates = await redis_client.lrange(k_candidates(event_id), 0, -1)
    if not candidates:
        # fallback: беремо перший з черги
        first = await redis_client.lindex(k_queue(event_id), 0)
        if not first:
            return None
        await _set_current_track(event_id, first, reason="fallback_first")
        return await _load_track(first)

    winner_id = await pick_winner(event_id, candidates)
    if not winner_id:
        return None

    await _set_current_track(event_id, winner_id, reason="voted_winner")
    return await _load_track(winner_id)


async def vote(event_id: int, telegram_id: int, track_id: str) -> None:
    """
    1 голос на раунд (простий варіант): ключ voted:{telegram_id} існує => вже голосував.
    """
    st = await redis_client.hgetall(k_state(event_id))
    if st.get("status") != "live":
        raise ValueError("Event is not live")
    if st.get("voting_open") != "1":
        raise ValueError("Voting is closed")

    # перевіряємо що track_id серед кандидатів
    candidates = await redis_client.lrange(k_candidates(event_id), 0, -1)
    if track_id not in candidates:
        raise ValueError("Track is not votable")

    voted_key = k_voted(event_id, telegram_id)
    ok = await redis_client.set(voted_key, "1", nx=True, ex=STATE_TTL_SECONDS)
    if not ok:
        raise ValueError("Already voted in this round")

    await redis_client.hincrby(k_score(event_id), track_id, 1)

    # для UI шлемо оновлення лічильника
    new_score = await redis_client.hget(k_score(event_id), track_id)
    await publish_event(event_id, {"type": "vote", "track_id": track_id, "votes": int(new_score or 0)})


async def tick_event(event_id: int) -> None:
    """
    Один "тик": перевіряє таймінги та робить переходи.
    """
    st = await redis_client.hgetall(k_state(event_id))
    if not st:
        return
    if st.get("status") != "live":
        return

    now = _now()
    voting_open = st.get("voting_open") == "1"
    vote_closes_at = int(st.get("vote_closes_at") or 0)
    ends_at = int(st.get("track_ends_at") or 0)
    current_track_id = st.get("current_track_id") or ""

    # 1) Якщо є голосування і воно має закритись
    if voting_open and vote_closes_at and now >= vote_closes_at:
        await close_voting(event_id)
        await confirm_winner_and_start_track(event_id)
        return

    # 2) Якщо трек грає і закінчився — прибираємо його і зсуваємо чергу, потім відкриваємо наступне голосування
    if (not voting_open) and current_track_id and ends_at and now >= ends_at:
        # видаляємо зі списку (він стоїть першим)
        await redis_client.lpop(k_queue(event_id))
        await publish_event(event_id, {"type": "track_finished", "track_id": current_track_id})

        # переходимо до наступного раунду
        await advance_to_next_track(event_id)
        return


async def ticker_loop(event_id: int, stop_event: asyncio.Event) -> None:
    """
    Background loop: запускай на старті івенту (або при підключенні DJ).
    """
    while not stop_event.is_set():
        try:
            await tick_event(event_id)
        except Exception as e:
            # не валимо цикл
            await publish_event(event_id, {"type": "ticker_error", "error": str(e)})
        await asyncio.sleep(1.0)
