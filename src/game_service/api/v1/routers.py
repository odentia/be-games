from fastapi import APIRouter

from game_service.api.v1.games_router import games_router

api_v1 = APIRouter(prefix="/v1", tags=["games"])
api_v1.include_router(games_router)

@api_v1.get("/healthz")
async def healthz():
    return {"status": "ok"}
