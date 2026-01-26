from __future__ import annotations

def k_state(event_id: int) -> str:
    return f"event:{event_id}:state"

def k_queue(event_id: int) -> str:
    return f"event:{event_id}:queue"

def k_score(event_id: int) -> str:
    return f"event:{event_id}:score"

def k_voted(event_id: int, telegram_id: int) -> str:
    return f"event:{event_id}:voted:{telegram_id}"
def k_candidates(event_id: int) -> str:
    return f"event:{event_id}:candidates"  
