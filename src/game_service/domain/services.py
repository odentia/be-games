from __future__ import annotations

from datetime import datetime
from typing import List

from game_service.domain.models import Game, Genre, Platform, Screenshot


class GameFactory:
    """Фабрика для создания доменных моделей из RAWG данных"""

    @staticmethod
    def from_rawg_list_item(data: dict) -> Game:
        """
        Создать игру из кратких данных списка игр RAWG (дешевый запрос).
        Не содержит полного описания, скриншотов и некоторых деталей.
        """
        platforms = [
            Platform(id=entry["platform"]["id"], name=entry["platform"]["name"])
            for entry in data.get("platforms", [])
            if entry.get("platform")
        ]
        genres = [
            Genre(id=genre["id"], name=genre["name"])
            for genre in data.get("genres", [])
        ]
        screenshots = [
            Screenshot(
                id=shot.get("id", 0),
                game_id=str(data.get("id")),
                url=shot.get("image") or shot.get("url") or "",
            )
            for shot in data.get("short_screenshots", [])
            if shot.get("image")
        ]
        release_date = None
        if data.get("released"):
            try:
                release_date = datetime.fromisoformat(data["released"]).date()
            except ValueError:
                release_date = None

        return Game(
            id=str(data.get("id")),
            rawg_id=data.get("id"),
            slug=data.get("slug", ""),
            name=data.get("name", ""),
            description=None,  # Нет в списке
            metacritic=data.get("metacritic"),
            rating=data.get("rating"),
            release_date=release_date,
            developer=None,  # Нет в списке
            publisher=None,  # Нет в списке
            background_image=data.get("background_image"),
            website=None,  # Нет в списке
            playtime=None,  # Нет в списке
            age_rating=None,  # Нет в списке
            platforms=platforms,
            genres=genres,
            tags=[],  # Нет в списке
            screenshots=screenshots,
        )

    @staticmethod
    def from_rawg(data: dict) -> Game:
        platforms = [
            Platform(id=entry["platform"]["id"], name=entry["platform"]["name"])
            for entry in data.get("platforms", [])
            if entry.get("platform")
        ]
        genres = [
            Genre(id=genre["id"], name=genre["name"])
            for genre in data.get("genres", [])
        ]
        screenshots = [
            Screenshot(
                id=shot.get("id", 0),
                game_id=str(data.get("id")),
                url=shot.get("image") or shot.get("url") or "",
            )
            for shot in data.get("short_screenshots", [])
            if shot.get("image")
        ]
        release_date = None
        if data.get("released"):
            try:
                release_date = datetime.fromisoformat(data["released"]).date()
            except ValueError:
                release_date = None

        return Game(
            id=str(data.get("id")),
            rawg_id=data.get("id"),
            slug=data.get("slug", ""),
            name=data.get("name", ""),
            description=data.get("description_raw") or data.get("description"),
            metacritic=data.get("metacritic"),
            rating=data.get("rating"),
            release_date=release_date,
            developer=(data.get("developers") or [{}])[0].get("name") if data.get("developers") else None,
            publisher=(data.get("publishers") or [{}])[0].get("name") if data.get("publishers") else None,
            background_image=data.get("background_image"),
            website=data.get("website"),
            playtime=data.get("playtime"),
            age_rating=(data.get("esrb_rating") or {}).get("name"),
            platforms=platforms,
            genres=genres,
            tags=[tag.get("name") for tag in (data.get("tags") or []) if tag.get("name")],
            screenshots=screenshots,
        )
