from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class RAWGClient:
    """Клиент для работы с RAWG API"""

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        # Convert AnyHttpUrl to string if needed
        base_url_str = str(base_url).rstrip("/")
        self.base_url = base_url_str
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_game(
        self, *, slug: Optional[str] = None, rawg_id: Optional[int] = None
    ) -> Dict[str, Any]:
        if not slug and not rawg_id:
            raise ValueError("slug or rawg_id is required")

        if slug:
            url = f"/games/{slug}"
        else:
            url = f"/games/{rawg_id}"

        params = {"key": self.api_key}
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def search_games(
        self, *, search: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        params = {
            "key": self.api_key,
            "search": search,
            "page": page,
            "page_size": page_size,
        }
        response = await self._client.get("/games", params=params)
        response.raise_for_status()
        return response.json()

    async def list_games(
        self,
        *,
        page: int = 1,
        page_size: int = 40,
        ordering: Optional[str] = "-rating",  # Сортировка по рейтингу (популярные сначала)
        dates: Optional[str] = None,  # Фильтр по датам, например "2020-01-01,2024-12-31"
        platforms: Optional[str] = None,  # ID платформ через запятую
        genres: Optional[str] = None,  # ID жанров через запятую
    ) -> Dict[str, Any]:
        """
        Получить список игр из RAWG API (дешевый запрос - 1 запрос на страницу).
        Возвращает краткую информацию об играх без деталей.
        """
        params = {
            "key": self.api_key,
            "page": page,
            "page_size": page_size,
        }
        if ordering:
            params["ordering"] = ordering
        if dates:
            params["dates"] = dates
        if platforms:
            params["platforms"] = platforms
        if genres:
            params["genres"] = genres

        response = await self._client.get("/games", params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_screenshots(self, game_id: int) -> Dict[str, Any]:
        params = {"key": self.api_key}
        response = await self._client.get(f"/games/{game_id}/screenshots", params=params)
        response.raise_for_status()
        return response.json()
