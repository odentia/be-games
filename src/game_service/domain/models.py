from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class Platform:
    id: int
    name: str


@dataclass
class Genre:
    id: int
    name: str


@dataclass
class Screenshot:
    id: int
    game_id: str
    url: str


@dataclass
class Game:
    """Доменная модель игры"""
    id: str
    rawg_id: int
    slug: str
    name: str
    description: Optional[str] = None
    metacritic: Optional[int] = None
    rating: Optional[float] = None
    release_date: Optional[date] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    background_image: Optional[str] = None
    website: Optional[str] = None
    playtime: Optional[int] = None
    age_rating: Optional[str] = None
    platforms: List[Platform] = field(default_factory=list)
    genres: List[Genre] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    screenshots: List[Screenshot] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
