from __future__ import annotations

from game_service.domain.models import Game, Genre, Platform, Screenshot
from game_service.repo.sql import models as m


def game_to_domain(model: m.GameModel) -> Game:
    return Game(
        id=model.id,
        rawg_id=model.rawg_id,
        slug=model.slug,
        name=model.name,
        description=model.description,
        metacritic=model.metacritic,
        rating=model.rating,
        release_date=model.release_date,
        developer=model.developer,
        publisher=model.publisher,
        background_image=model.background_image,
        website=model.website,
        playtime=model.playtime,
        age_rating=model.age_rating,
        platforms=[Platform(id=idx, name=p.name) for idx, p in enumerate(model.platforms, start=1)],
        genres=[Genre(id=idx, name=g.name) for idx, g in enumerate(model.genres, start=1)],
        tags=[t.name for t in model.tags],
        screenshots=[Screenshot(id=s.id, game_id=model.id, url=s.url) for s in model.screenshots],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def game_to_model(domain: Game) -> m.GameModel:
    model = m.GameModel(
        id=domain.id,
        rawg_id=domain.rawg_id,
        slug=domain.slug,
        name=domain.name,
        description=domain.description,
        metacritic=domain.metacritic,
        rating=domain.rating,
        release_date=domain.release_date,
        developer=domain.developer,
        publisher=domain.publisher,
        background_image=domain.background_image,
        website=domain.website,
        playtime=domain.playtime,
        age_rating=domain.age_rating,
    )

    model.platforms = [m.PlatformModel(name=p.name) for p in domain.platforms]
    model.genres = [m.GenreModel(name=g.name) for g in domain.genres]
    model.tags = [m.TagModel(name=name) for name in domain.tags]
    model.screenshots = [m.ScreenshotModel(url=s.url) for s in domain.screenshots]

    return model
