from __future__ import annotations

from typing import Annotated, AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from game_service.clients.rawg_client import RAWGClient
from game_service.core.config import Settings
from game_service.services.game_service import GameAppService
from game_service.repo.sql.repositories import SQLGameRepository


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def _get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if not session_factory:
        raise RuntimeError("Session factory is not initialized")
    return session_factory


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = _get_session_factory(request)
    async with session_factory() as session:
        yield session


def get_game_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SQLGameRepository:
    return SQLGameRepository(session)


async def get_rawg_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncIterator[RAWGClient]:
    client = RAWGClient(settings.rawg_base_url, settings.rawg_api_key)
    try:
        yield client
    finally:
        await client.close()


def get_game_service(
    game_repo: Annotated[SQLGameRepository, Depends(get_game_repository)],
    rawg_client: Annotated[RAWGClient, Depends(get_rawg_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> GameAppService:
    return GameAppService(game_repo=game_repo, rawg_client=rawg_client, settings=settings)
