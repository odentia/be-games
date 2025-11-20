from __future__ import annotations

import traceback

from fastapi import APIRouter, Depends, HTTPException, Query

from game_service.dtos.http import (
    GameDetailResponse,
    GameListResponse,
    GameListItem,
    GameQuery,
    SyncGameRequest,
    SyncBatchRequest,
    SyncBatchResponse,
)
from game_service.services.game_service import GameAppService
from game_service.api.deps import (
    get_game_service,
)
from game_service.core.logging import get_logger

log = get_logger(__name__)

games_router = APIRouter(prefix="/games", tags=["Games"])


@games_router.get("/", response_model=GameListResponse)
async def list_games(
    query: GameQuery = Depends(),
    game_service: GameAppService = Depends(get_game_service),
):
    try:
        result = await game_service.list_games(query)
        return result
    except Exception as e:
        log.error(f"Error in list_games: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@games_router.get("/{game_id}", response_model=GameDetailResponse)
async def get_game(
    game_id: str,
    game_service: GameAppService = Depends(get_game_service),
):
    try:
        game = await game_service.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        return game
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error in get_game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@games_router.post("/sync", response_model=GameDetailResponse)
async def sync_game(
    payload: SyncGameRequest,
    game_service: GameAppService = Depends(get_game_service),
):
    try:
        if not payload.is_valid:
            raise HTTPException(status_code=400, detail="rawg_slug or rawg_id is required")
        game = await game_service.sync_game(rawg_id=payload.rawg_id, slug=payload.rawg_slug)
        return game
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error in sync_game: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@games_router.post("/sync/batch", response_model=SyncBatchResponse)
async def sync_games_batch(
    payload: SyncBatchRequest,
    game_service: GameAppService = Depends(get_game_service),
):
    """
    Массовая синхронизация игр из RAWG API.
    
    Стратегия оптимизации запросов:
    - Использует дешевый запрос list_games (1 запрос на страницу)
    - Сохраняет краткую информацию об играх
    - Опционально загружает детали для популярных игр (если load_details=True)
    
    Пример: синхронизация 10 страниц по 40 игр = 10 запросов, ~400 игр в базе.
    Если load_details=True и details_limit=100, дополнительно 200 запросов для деталей.
    """
    try:
        result = await game_service.sync_games_batch(
            start_page=payload.start_page,
            pages=payload.pages,
            page_size=payload.page_size,
            load_details=payload.load_details,
            details_limit=payload.details_limit,
        )
        return SyncBatchResponse(**result)
    except Exception as e:
        log.error(f"Error in sync_games_batch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
