from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class GameEvent(BaseModel):
    """Базовое событие игры"""

    event_type: str
    timestamp: datetime = datetime.utcnow()
    service: str = "game-service"


class GameSyncedEvent(GameEvent):
    """Событие синхронизации игры из RAWG API"""

    event_type: str = "game_synced"
    game_id: str
    rawg_id: int
    name: str
    slug: str
    platforms: List[str] = []
    genres: List[str] = []
    rating: Optional[float] = None
    release_date: Optional[str] = None


class GameUpdatedEvent(GameEvent):
    """Событие обновления игры"""

    event_type: str = "game_updated"
    game_id: str
    rawg_id: int
    name: str
    slug: str
    changes: dict = {}
