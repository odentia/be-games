# Быстрый старт

## 1. Установка зависимостей
```powershell
uv sync
```

## 2. Настройка базы данных

### Вариант A: SQLite (проще для разработки)
```powershell
$env:DATABASE_URL = "sqlite+aiosqlite:///./games.db"
uv run alembic upgrade head
```

### Вариант B: PostgreSQL
```powershell
# Установите переменные окружения с вашими данными PostgreSQL
$env:DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/games"
$env:ALEMBIC_DATABASE_URL = "postgresql://user:pass@localhost:5432/games"
uv run alembic upgrade head
```

## 3. Запуск приложения
```powershell
$env:DATABASE_URL = "sqlite+aiosqlite:///./games.db"
$env:RAWG_API_KEY = "ваш_ключ_от_rawg_api"  # Получите на https://rawg.io/apidocs
uv run python -m game_service.api
```

Приложение будет доступно по адресу: http://localhost:8010

## 4. Проверка работоспособности

### Через браузер:
- Откройте http://localhost:8010/docs - интерактивная документация API
- Попробуйте выполнить запрос `GET /api/v1/games` - должен вернуть пустой список

### Через PowerShell:
```powershell
# Список игр
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games" -Method GET

# Синхронизация игры из RAWG (нужен валидный API ключ)
$body = @{
    rawg_slug = "grand-theft-auto-v"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/sync" -Method POST -Body $body -ContentType "application/json"
```

## Примечания

- По умолчанию используется SQLite (`sqlite+aiosqlite:///./games.db`)
- Для синхронизации игр из RAWG нужен валидный API ключ
- База данных создаётся автоматически при первом запуске миграций

## Дополнительная документация

- **Подробное руководство по API**: см. файл `API_USAGE.md`
- **Примеры использования**: запустите `.\examples.ps1` для демонстрации всех возможностей API

