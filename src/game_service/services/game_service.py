from __future__ import annotations

from typing import Optional

from game_service.clients.rawg_client import RAWGClient
from game_service.domain.models import Game
from game_service.domain.repositories import GameRepository
from game_service.domain.services import GameFactory
from game_service.dtos.http import GameDetailResponse, GameListItem, GameListResponse, GameQuery
from game_service.core.config import Settings


class GameAppService:
    def __init__(self, game_repo: GameRepository, rawg_client: RAWGClient, settings: Settings):
        self.game_repo = game_repo
        self.rawg_client = rawg_client
        self.settings = settings

    async def list_games(self, query: GameQuery) -> GameListResponse:
        offset = (query.page - 1) * query.page_size
        games = await self.game_repo.list_games(
            search=query.search,
            platform=query.platform,
            genre=query.genre,
            age_rating=query.age_rating,
            year_from=query.year_from,
            year_to=query.year_to,
            rating_from=query.rating_from,
            rating_to=query.rating_to,
            limit=query.page_size,
            offset=offset,
        )
        total = await self.game_repo.count_games(
            search=query.search,
            platform=query.platform,
            genre=query.genre,
            age_rating=query.age_rating,
            year_from=query.year_from,
            year_to=query.year_to,
            rating_from=query.rating_from,
            rating_to=query.rating_to,
        )
        items = [
            GameListItem(
                id=game.id,
                name=game.name,
                slug=game.slug,
                release_date=game.release_date,
                metacritic=game.metacritic,
                rating=game.rating,
                background_image=game.background_image,
                platforms=[p.name for p in game.platforms],
                genres=[g.name for g in game.genres],
            )
            for game in games
        ]
        return GameListResponse(total=total, items=items)

    async def get_game(self, identifier: str) -> Optional[GameDetailResponse]:
        game = await self.game_repo.get_by_id(identifier)
        if not game:
            game = await self.game_repo.get_by_slug(identifier)
        return self._to_detail_response(game) if game else None

    async def sync_game(
        self, *, rawg_id: Optional[int] = None, slug: Optional[str] = None
    ) -> GameDetailResponse:
        data = await self.rawg_client.fetch_game(slug=slug, rawg_id=rawg_id)
        screenshots_data = await self.rawg_client.fetch_screenshots(data["id"])
        data["short_screenshots"] = screenshots_data.get("results", [])
        domain_game = GameFactory.from_rawg(data)
        domain_game.id = slug or str(domain_game.rawg_id) or domain_game.id
        saved = await self.game_repo.upsert_game(domain_game)
        return self._to_detail_response(saved)

    async def sync_games_batch(
        self,
        *,
        start_page: int = 1,
        pages: int = 1,
        page_size: int = 40,
        load_details: bool = False,
        details_limit: int = 0,
    ) -> dict:
        """
        Массовая синхронизация игр из RAWG API.

        Стратегия:
        - Использует дешевый запрос list_games (1 запрос на страницу)
        - Сохраняет краткую информацию об играх
        - Опционально загружает детали для популярных игр (если load_details=True)

        Args:
            start_page: Начальная страница для синхронизации
            pages: Количество страниц для синхронизации
            page_size: Размер страницы (максимум 40 для RAWG)
            load_details: Загружать ли детальную информацию (дорого - 2 запроса на игру)
            details_limit: Максимум игр для загрузки деталей (0 = все)

        Returns:
            dict с статистикой синхронизации
        """
        total_synced = 0
        total_updated = 0
        total_new = 0
        requests_used = 0
        details_loaded = 0

        for page in range(start_page, start_page + pages):
            # Получаем список игр (1 запрос)
            list_data = await self.rawg_client.list_games(
                page=page,
                page_size=page_size,
                ordering="-rating",  # Популярные сначала
            )
            requests_used += 1

            games_list = list_data.get("results", [])

            # Сохраняем игры из списка (краткая информация)
            for game_data in games_list:
                domain_game = GameFactory.from_rawg_list_item(game_data)
                domain_game.id = str(domain_game.rawg_id) or domain_game.slug

                # Проверяем, существует ли игра с деталями
                existing = await self.game_repo.get_by_id(domain_game.id)
                is_new = existing is None
                has_details = existing is not None and existing.description is not None

                # Сохраняем только если игра новая или нет деталей
                if is_new or not has_details:
                    await self.game_repo.upsert_game(domain_game)
                    if is_new:
                        total_new += 1
                    else:
                        total_updated += 1

                total_synced += 1

                # Загружаем детали для популярных игр (если нужно и ещё нет деталей)
                if (
                    load_details
                    and not has_details
                    and (details_limit == 0 or details_loaded < details_limit)
                ):
                    try:
                        # Загружаем детали (2 запроса: game + screenshots)
                        full_data = await self.rawg_client.fetch_game(rawg_id=domain_game.rawg_id)
                        screenshots_data = await self.rawg_client.fetch_screenshots(
                            domain_game.rawg_id
                        )
                        full_data["short_screenshots"] = screenshots_data.get("results", [])
                        full_game = GameFactory.from_rawg(full_data)
                        full_game.id = domain_game.id
                        await self.game_repo.upsert_game(full_game)
                        requests_used += 2
                        details_loaded += 1
                    except Exception:
                        # Игнорируем ошибки при загрузке деталей
                        pass

        return {
            "total_synced": total_synced,
            "new_games": total_new,
            "updated_games": total_updated,
            "details_loaded": details_loaded,
            "requests_used": requests_used,
            "pages_processed": pages,
        }

    def _to_detail_response(self, game: Optional[Game]) -> Optional[GameDetailResponse]:
        if not game:
            return None
        return GameDetailResponse(
            id=game.id,
            name=game.name,
            slug=game.slug,
            description=game.description,
            metacritic=game.metacritic,
            rating=game.rating,
            release_date=game.release_date,
            developer=game.developer,
            publisher=game.publisher,
            background_image=game.background_image,
            website=game.website,
            playtime=game.playtime,
            age_rating=game.age_rating,
            platforms=[p.name for p in game.platforms],
            genres=[g.name for g in game.genres],
            tags=game.tags,
            screenshots=[s.url for s in game.screenshots],
            created_at=game.created_at,
            updated_at=game.updated_at,
        )
