# Руководство по использованию API

## Базовый URL
```
http://localhost:8010
```

## Доступные эндпоинты

### 1. Проверка работоспособности
**GET** `/api/v1/healthz`

Проверяет, что сервис работает.

**Пример запроса:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/healthz" -Method GET
```

**Ответ:**
```json
{
  "status": "ok"
}
```

---

### 2. Получить список игр
**GET** `/api/v1/games`

Возвращает список игр с пагинацией и фильтрацией.

**Параметры запроса (query parameters):**
- `search` (опционально) - поиск по названию игры
- `platform` (опционально) - фильтр по платформе
- `genre` (опционально) - фильтр по жанру
- `page` (по умолчанию: 1) - номер страницы (начиная с 1)
- `page_size` (по умолчанию: 20) - количество игр на странице (1-100)

**Примеры запросов:**

```powershell
# Получить все игры (первая страница)
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games" -Method GET

# Поиск по названию
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games?search=grand" -Method GET

# Фильтр по платформе
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games?platform=PC" -Method GET

# Фильтр по жанру
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games?genre=Action" -Method GET

# Комбинация фильтров + пагинация
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games?search=theft&platform=PC&page=1&page_size=10" -Method GET
```

**Ответ:**
```json
{
  "total": 1,
  "items": [
    {
      "id": "grand-theft-auto-v",
      "name": "Grand Theft Auto V",
      "slug": "grand-theft-auto-v",
      "release_date": "2013-09-17",
      "metacritic": 97,
      "rating": 4.48,
      "background_image": "https://...",
      "platforms": ["PC", "PlayStation 4", "Xbox One"],
      "genres": ["Action", "Adventure"]
    }
  ]
}
```

---

### 3. Получить детальную информацию об игре
**GET** `/api/v1/games/{game_id}`

Возвращает подробную информацию об игре по ID или slug.

**Параметры пути:**
- `game_id` - ID игры (строка) или slug игры

**Примеры запросов:**

```powershell
# По ID
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/grand-theft-auto-v" -Method GET

# По slug
Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/gta-v" -Method GET
```

**Ответ:**
```json
{
  "id": "grand-theft-auto-v",
  "name": "Grand Theft Auto V",
  "slug": "grand-theft-auto-v",
  "description": "Grand Theft Auto V...",
  "metacritic": 97,
  "rating": 4.48,
  "release_date": "2013-09-17",
  "developer": "Rockstar North",
  "publisher": "Rockstar Games",
  "background_image": "https://...",
  "website": "https://...",
  "playtime": 45,
  "age_rating": "M",
  "platforms": ["PC", "PlayStation 4", "Xbox One"],
  "genres": ["Action", "Adventure"],
  "tags": ["open-world", "crime", "multiplayer"],
  "screenshots": ["https://...", "https://..."],
  "created_at": "2024-11-20T21:00:00Z",
  "updated_at": "2024-11-20T21:00:00Z"
}
```

**Ошибки:**
- `404` - игра не найдена

---

### 4. Синхронизировать игру из RAWG
**POST** `/api/v1/games/sync`

Загружает данные об игре из RAWG API и сохраняет в базу данных.

**Требования:**
- Должен быть установлен валидный `RAWG_API_KEY` в переменных окружения
- Получить ключ можно на https://rawg.io/apidocs

**Тело запроса (JSON):**
```json
{
  "rawg_slug": "grand-theft-auto-v"  // или
  "rawg_id": 3498
}
```

Нужно указать либо `rawg_slug`, либо `rawg_id`.

**Примеры запросов:**

```powershell
# Синхронизация по slug
$body = @{
    rawg_slug = "grand-theft-auto-v"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/sync" -Method POST -Body $body -ContentType "application/json"

# Синхронизация по ID
$body = @{
    rawg_id = 3498
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/sync" -Method POST -Body $body -ContentType "application/json"
```

**Ответ:**
Аналогичен ответу от `GET /api/v1/games/{game_id}` - возвращает детальную информацию об игре.

**Ошибки:**
- `400` - не указан `rawg_slug` или `rawg_id`
- `500` - ошибка при запросе к RAWG API (неверный ключ, игра не найдена и т.д.)

---

### 5. Массовая синхронизация игр из RAWG
**POST** `/api/v1/games/sync/batch`

Массовая синхронизация игр с оптимизацией запросов. Использует дешевые запросы для получения списка игр (1 запрос на страницу).

**Требования:**
- Должен быть установлен валидный `RAWG_API_KEY` в переменных окружения

**Тело запроса (JSON):**
```json
{
  "start_page": 1,
  "pages": 100,
  "page_size": 40,
  "load_details": false,
  "details_limit": 0
}
```

**Параметры:**
- `start_page` (int, default: 1) - Начальная страница
- `pages` (int, default: 1, max: 500) - Количество страниц
- `page_size` (int, default: 40, max: 40) - Размер страницы
- `load_details` (bool, default: false) - Загружать детальную информацию (дорого - 2 запроса на игру)
- `details_limit` (int, default: 0) - Максимум игр для загрузки деталей (0 = все)

**Примеры запросов:**

```powershell
# Синхронизация 100 страниц (4000 игр, 100 запросов)
$body = @{
    start_page = 1
    pages = 100
    page_size = 40
    load_details = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/sync/batch" -Method POST -Body $body -ContentType "application/json"

# Синхронизация с деталями для топ-100 игр (203 запроса)
$body = @{
    start_page = 1
    pages = 3
    page_size = 40
    load_details = $true
    details_limit = 100
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8010/api/v1/games/sync/batch" -Method POST -Body $body -ContentType "application/json"
```

**Ответ:**
```json
{
  "total_synced": 4000,
  "new_games": 3950,
  "updated_games": 50,
  "details_loaded": 0,
  "requests_used": 100,
  "pages_processed": 100
}
```

**Стратегия оптимизации:**
- Используйте `load_details=false` для массовой синхронизации (1 запрос на страницу)
- Используйте `load_details=true` с `details_limit` для загрузки деталей только топ-игр
- См. подробности в `SYNC_STRATEGY.md`

**Ошибки:**
- `500` - ошибка при запросе к RAWG API

---

## Использование через Swagger UI (рекомендуется)

Самый простой способ - использовать интерактивную документацию:

1. Запустите приложение
2. Откройте в браузере: http://localhost:8010/docs
3. Выберите нужный эндпоинт
4. Нажмите "Try it out"
5. Заполните параметры и нажмите "Execute"

## Использование через curl (если установлен)

```bash
# Список игр
curl http://localhost:8010/api/v1/games

# Поиск
curl "http://localhost:8010/api/v1/games?search=grand"

# Детали игры
curl http://localhost:8010/api/v1/games/grand-theft-auto-v

# Синхронизация
curl -X POST http://localhost:8010/api/v1/games/sync \
  -H "Content-Type: application/json" \
  -d '{"rawg_slug": "grand-theft-auto-v"}'
```

## Примеры популярных игр для синхронизации

- `grand-theft-auto-v` - Grand Theft Auto V
- `the-witcher-3-wild-hunt` - The Witcher 3
- `cyberpunk-2077` - Cyberpunk 2077
- `red-dead-redemption-2` - Red Dead Redemption 2
- `minecraft` - Minecraft
- `counter-strike-2` - Counter-Strike 2

Полный список можно найти на https://rawg.io

