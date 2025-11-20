from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class GameListItem(BaseModel):
    id: str
    name: str
    slug: str
    release_date: Optional[date]
    metacritic: Optional[int]
    rating: Optional[float]
    background_image: Optional[str]
    platforms: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)


class GameListResponse(BaseModel):
    total: int
    items: List[GameListItem]


class GameDetailResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    metacritic: Optional[int]
    rating: Optional[float]
    release_date: Optional[date]
    developer: Optional[str]
    publisher: Optional[str]
    background_image: Optional[str]
    website: Optional[str]
    playtime: Optional[int]
    age_rating: Optional[str]
    platforms: List[str]
    genres: List[str]
    tags: List[str]
    screenshots: List[str]
    created_at: datetime
    updated_at: datetime


class GameQuery(BaseModel):
    search: Optional[str] = None
    platform: Optional[str] = None
    genre: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SyncGameRequest(BaseModel):
    rawg_slug: Optional[str] = None
    rawg_id: Optional[int] = None

    @property
    def is_valid(self) -> bool:
        return bool(self.rawg_slug or self.rawg_id)


class SyncBatchRequest(BaseModel):
    start_page: int = Field(default=1, ge=1, description="Начальная страница для синхронизации")
    pages: int = Field(default=1, ge=1, le=500, description="Количество страниц для синхронизации")
    page_size: int = Field(default=40, ge=1, le=40, description="Размер страницы (максимум 40)")
    load_details: bool = Field(default=False, description="Загружать детальную информацию (дорого - 2 запроса на игру)")
    details_limit: int = Field(default=0, ge=0, description="Максимум игр для загрузки деталей (0 = все на страницах)")


class SyncBatchResponse(BaseModel):
    total_synced: int
    new_games: int
    updated_games: int
    details_loaded: int
    requests_used: int
    pages_processed: int
