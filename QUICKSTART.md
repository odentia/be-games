# Быстрый старт

## 1. Установка зависимостей
```powershell
uv sync
```

## 2. Настройка базы данных PostgreSQL

Установите PostgreSQL и создайте базу данных, затем настройте переменные окружения:

```powershell
# Установите переменные окружения с вашими данными PostgreSQL
$env:DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/games"
$env:ALEMBIC_DATABASE_URL = "postgresql://user:pass@localhost:5432/games"
uv run alembic upgrade head
```

**Создание базы данных:**
```sql
CREATE DATABASE games;
CREATE USER games_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE games TO games_user;
```

## 3. Запуск приложения
```powershell
$env:DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/games"
$env:ALEMBIC_DATABASE_URL = "postgresql://user:pass@localhost:5432/games"
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

- Микросервис использует PostgreSQL (требуется настройка DATABASE_URL)
- Для синхронизации игр из RAWG нужен валидный API ключ
- База данных должна быть создана до запуска миграций

## Дополнительная документация

- **Подробное руководство по API**: см. файл `API_USAGE.md`
- **Примеры использования**: запустите `.\examples.ps1` для демонстрации всех возможностей API

