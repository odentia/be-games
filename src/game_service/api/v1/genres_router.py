from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from game_service.api.deps import get_session
from game_service.repo.sql.repositories import SQLGameRepository
from game_service.core.logging import get_logger

log = get_logger(__name__)

genres_router = APIRouter(prefix="/genres", tags=["Genres"])


@genres_router.get("/")
async def list_genres(
    session: AsyncSession = Depends(get_session),
):
    """
    Получить список всех доступных жанров/категорий игр.
    """
    try:
        repo = SQLGameRepository(session)
        genres = await repo.list_genres()
        return {"genres": genres, "total": len(genres)}
    except Exception as e:
        log.error(f"Error in list_genres: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@genres_router.get("/platforms")
async def list_platforms(
    session: AsyncSession = Depends(get_session),
):
    """
    Получить список всех доступных платформ.
    """
    try:
        repo = SQLGameRepository(session)
        platforms = await repo.list_platforms()
        return {"platforms": platforms, "total": len(platforms)}
    except Exception as e:
        log.error(f"Error in list_platforms: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@genres_router.get("/age-ratings")
async def list_age_ratings(
    session: AsyncSession = Depends(get_session),
):
    """
    Получить список всех доступных возрастных рейтингов (ESRB).

    Примеры рейтингов: "Everyone", "Everyone 10+", "Teen", "Mature", "Adults Only", "Rating Pending"
    """
    try:
        repo = SQLGameRepository(session)
        age_ratings = await repo.list_age_ratings()
        return {"age_ratings": age_ratings, "total": len(age_ratings)}
    except Exception as e:
        log.error(f"Error in list_age_ratings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
