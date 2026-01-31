from __future__ import annotations


def k_state(event_id: int) -> str:
    return f"event:{event_id}:state"


def k_queue_items(event_id: int) -> str:
    """
    HASH:
      field = track_id
      value = json payload Track
    """
    return f"event:{event_id}:queue:items"


def k_queue_order(event_id: int) -> str:
    """
    LIST:
      values = track_id in insertion order
    """
    return f"event:{event_id}:queue:order"


def k_votes(event_id: int) -> str:
    """
    HASH:
      field = track_id
      value = votes int
    """
    return f"event:{event_id}:votes"


def k_user_votes(event_id: int, tg_id: int) -> str:
    """
    SET:
      values = track_id voted by this user
    """
    return f"event:{event_id}:user:{tg_id}:votes"
