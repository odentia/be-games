from __future__ import annotations

from typing import List, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from game_service.domain.models import Game, Screenshot
from game_service.domain.repositories import GameRepository, ScreenshotRepository
from game_service.repo.sql import models as m
from game_service.repo.sql import mappers


class SQLGameRepository(GameRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_games(
        self,
        *,
        search: Optional[str] = None,
        platform: Optional[str] = None,
        genre: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Game]:
        query = select(m.GameModel).options(
            selectinload(m.GameModel.platforms),
            selectinload(m.GameModel.genres),
            selectinload(m.GameModel.tags),
            selectinload(m.GameModel.screenshots),
        )
        if search:
            query = query.where(m.GameModel.name.ilike(f"%{search}%"))
        if platform:
            query = query.join(m.GameModel.platforms).where(m.PlatformModel.name.ilike(f"%{platform}%"))
        if genre:
            query = query.join(m.GameModel.genres).where(m.GenreModel.name.ilike(f"%{genre}%"))
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().unique().all()
        return [mappers.game_to_domain(model) for model in models]

    async def count_games(
        self,
        *,
        search: Optional[str] = None,
        platform: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> int:
        query = select(func.count(m.GameModel.id))
        if search:
            query = query.where(m.GameModel.name.ilike(f"%{search}%"))
        if platform:
            query = query.join(m.GameModel.platforms).where(m.PlatformModel.name.ilike(f"%{platform}%"))
        if genre:
            query = query.join(m.GameModel.genres).where(m.GenreModel.name.ilike(f"%{genre}%"))
        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def get_by_id(self, game_id: str) -> Optional[Game]:
        query = select(m.GameModel).options(
            selectinload(m.GameModel.platforms),
            selectinload(m.GameModel.genres),
            selectinload(m.GameModel.tags),
            selectinload(m.GameModel.screenshots),
        ).where(m.GameModel.id == game_id)
        result = await self.session.execute(query)
        if model := result.scalars().first():
            return mappers.game_to_domain(model)
        return None

    async def get_by_slug(self, slug: str) -> Optional[Game]:
        query = select(m.GameModel).options(
            selectinload(m.GameModel.platforms),
            selectinload(m.GameModel.genres),
            selectinload(m.GameModel.tags),
            selectinload(m.GameModel.screenshots),
        ).where(m.GameModel.slug == slug)
        result = await self.session.execute(query)
        model = result.scalars().first()
        return mappers.game_to_domain(model) if model else None

    async def upsert_game(self, game: Game) -> Game:
        query = select(m.GameModel).options(
            selectinload(m.GameModel.platforms),
            selectinload(m.GameModel.genres),
            selectinload(m.GameModel.tags),
            selectinload(m.GameModel.screenshots),
        ).where(m.GameModel.rawg_id == game.rawg_id)
        existing = await self.session.execute(query)
        model = existing.scalars().first()
        if model:
            model.name = game.name
            model.slug = game.slug
            model.description = game.description
            model.metacritic = game.metacritic
            model.rating = game.rating
            model.release_date = game.release_date
            model.developer = game.developer
            model.publisher = game.publisher
            model.background_image = game.background_image
            model.website = game.website
            model.playtime = game.playtime
            model.age_rating = game.age_rating
            model.platforms = [m.PlatformModel(name=p.name) for p in game.platforms]
            model.genres = [m.GenreModel(name=g.name) for g in game.genres]
            model.tags = [m.TagModel(name=name) for name in game.tags]
            model.screenshots = [m.ScreenshotModel(url=s.url) for s in game.screenshots]
        else:
            model = mappers.game_to_model(game)
            self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model, ["platforms", "genres", "tags", "screenshots"])
        return mappers.game_to_domain(model)


class SQLScreenshotRepository(ScreenshotRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_game(self, game_id: str) -> List[Screenshot]:
        result = await self.session.execute(
            select(m.ScreenshotModel).join(m.GameModel).where(m.GameModel.id == game_id)
        )
        models = result.scalars().all()
        return [Screenshot(id=shot.id, game_id=game_id, url=shot.url) for shot in models]

    async def replace_for_game(self, game_id: str, screenshots: List[Screenshot]) -> None:
        await self.session.execute(
            delete(m.ScreenshotModel).where(m.ScreenshotModel.game_id == game_id)
        )
        for shot in screenshots:
            self.session.add(m.ScreenshotModel(game_id=game_id, url=shot.url))
        await self.session.commit()
