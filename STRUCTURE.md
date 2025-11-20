# Структура game-service

```
game-service/
├── pyproject.toml
├── README.md
├── Makefile
├── .env.example
├── infra/docker/Dockerfile
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_create_games_tables.py
└── src/
    └── game_service/
        ├── domain/
        │   ├── models.py
        │   ├── repositories.py
        │   ├── services.py
        │   └── events.py
        ├── dtos/
        │   ├── http.py
        │   └── events.py
        ├── repo/
        │   └── sql/
        │       ├── models.py
        │       ├── repositories.py
        │       └── mappers.py
        ├── clients/
        │   └── rawg_client.py
        ├── mq/
        │   ├── consumer.py
        │   └── publisher.py
        ├── services/
        │   └── game_service.py
        ├── api/
        │   ├── __main__.py
        │   ├── app.py
        │   ├── deps.py
        │   ├── lifespan.py
        │   └── v1/
        │       ├── routers.py
        │       └── games_router.py
        └── core/
            ├── config.py
            └── db.py
```

## TODO

- Подключить contracts/http и events пакеты
- Использовать common-config, common-logging, common-http, common-mq
- Добавить клиентов к другим сервисам при необходимости
