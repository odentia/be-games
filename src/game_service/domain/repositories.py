from __future__ import annotations

from typing import List, Optional, Protocol

from game_service.domain.models import Game, Screenshot


class GameRepository(Protocol):
    """Репозиторий для работы с играми"""

    async def list_games(
        self,
        *,
        search: Optional[str] = None,
        platform: Optional[str] = None,
        genre: Optional[str] = None,
        age_rating: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        rating_from: Optional[float] = None,
        rating_to: Optional[float] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Game]:
        ...

    async def count_games(
        self,
        *,
        search: Optional[str] = None,
        platform: Optional[str] = None,
        genre: Optional[str] = None,
        age_rating: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        rating_from: Optional[float] = None,
        rating_to: Optional[float] = None,
    ) -> int:
        ...

    async def get_by_id(self, game_id: str) -> Optional[Game]:
        ...

    async def get_by_slug(self, slug: str) -> Optional[Game]:
        ...

    async def upsert_game(self, game: Game) -> Game:
        ...


class ScreenshotRepository(Protocol):
    """Репозиторий для скриншотов"""

    async def list_by_game(self, game_id: str) -> List[Screenshot]:
        ...

    async def replace_for_game(
        self,
        game_id: str,
        screenshots: List[Screenshot],
    ) -> None:
        ...
