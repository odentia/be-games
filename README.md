# game-service

Микросервис для управления данными об играх и интеграции с RAWG API.

## Возможности

- Синхронизация информации об играх из RAWG
- Хранение и выдача каталога игр
- Отображение детальной страницы (описание, рейтинги, платформы, скриншоты)
- API для списка игр и детальной информации

## Стек

- FastAPI, Uvicorn
- SQLAlchemy (async) + PostgreSQL/SQLite
- Alembic для миграций
- RAWG API через httpx

## Запуск

```bash
uv sync
uv run alembic upgrade head
uv run python -m game_service.api
```

## Переменные окружения (.env)

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/games
ALEMBIC_DATABASE_URL=postgresql://user:pass@localhost:5432/games
RAWG_BASE_URL=https://api.rawg.io/api
RAWG_API_KEY=<your key>
```

## API

- `GET /api/v1/games` — список игр с фильтрацией по названию, платформе, жанру
- `GET /api/v1/games/{id_or_slug}` — подробная информация об игре
- `POST /api/v1/games/sync` — подтянуть данные об игре из RAWG по id или slug

## Структура

См. файл `STRUCTURE.md`.
