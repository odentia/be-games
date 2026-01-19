# Развертывание

## GitHub Secrets

**Обязательные секреты** (Settings → Secrets and variables → Actions → New repository secret):

1. **DEPLOY_HOST** - IP или домен вашего сервера
   - Пример: `192.168.1.100` или `example.com`

2. **DEPLOY_USER** - пользователь SSH для подключения к серверу
   - Пример: `root` или `deploy`

3. **DEPLOY_SSH_KEY** - приватный SSH ключ (см. инструкцию ниже)
   - Файл: `~/.ssh/id_rsa` (без `.pub`)

4. **POSTGRES_DB** - название базы данных (опционально, по умолчанию `games`)
   - Пример: `games`

5. **POSTGRES_USER** - пользователь PostgreSQL (опционально, по умолчанию `games_user`)
   - Пример: `games_user`

6. **POSTGRES_PASSWORD** - пароль для PostgreSQL (обязательно)
   - Пример: `your_secure_password_123`

7. **DATABASE_URL** - строка подключения к базе данных PostgreSQL (async)
   - Формат: `postgresql+asyncpg://user:password@postgres:5432/database_name`
   - Пример: `postgresql+asyncpg://games_user:your_secure_password_123@postgres:5432/games`
   - **Важно:** используйте `postgres` как хост (имя сервиса в Docker)

8. **ALEMBIC_DATABASE_URL** - строка подключения для миграций Alembic (sync)
   - Формат: `postgresql://user:password@postgres:5432/database_name`
   - Пример: `postgresql://games_user:your_secure_password_123@postgres:5432/games`
   - **Важно:** без `+asyncpg`, используйте `postgres` как хост

9. **RAWG_API_KEY** - API ключ от RAWG API
   - Получить можно на: https://rawg.io/apidocs
   - Пример: `abc123def456ghi789`

10. **RABBITMQ_URL** - строка подключения к существующему RabbitMQ (обязательно)
    - Формат: `amqp://user:password@host:5672/`
    - Если RabbitMQ на том же хосте: `amqp://user:password@host.docker.internal:5672/`
    - Если RabbitMQ в другой Docker сети: `amqp://user:password@имя_контейнера:5672/`
    - Если RabbitMQ на другом сервере: `amqp://user:password@ip_или_домен:5672/`
    - Пример: `amqp://rabbitmq_user:your_password@host.docker.internal:5672/`
    - **Важно:** RabbitMQ должен быть уже запущен на сервере!

**Опциональные секреты:**

- **DEPLOY_PORT** - SSH порт (по умолчанию 22)
  - Пример: `2222`

- **GHCR_TOKEN** (обязательно, если пакет приватный):
  - **Repository secret** - если пакет используется только в этом репозитории
  - **Organization secret** - если пакет в организации (Organization Settings → Secrets and variables → Actions)
  - Создайте PAT на https://github.com/settings/tokens с правами `read:packages`

## Первоначальная настройка (один раз)

**1. Настройте SSH ключи:**

На локальной машине создайте ключ:
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions"
# Нажмите Enter для сохранения в ~/.ssh/id_rsa
# Можно оставить passphrase пустым
```

Добавьте публичный ключ на сервер:
```bash
# Скопируйте публичный ключ
cat ~/.ssh/id_rsa.pub
```

На сервере VNC/SSH:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Вставьте публичный ключ (одна строка, начинается с ssh-rsa AAAA...)
chmod 600 ~/.ssh/authorized_keys
```

**Важно:** Используйте тот же ключ, который добавите в GitHub Secrets!

Проверьте подключение с лоальной машины:
```bash
ssh -i ~/.ssh/id_rsa ваш-пользователь@ваш-сервер
# Должно подключиться без пароля
```

Добавьте содержимое `~/.ssh/id_rsa` в GitHub Secrets как `DEPLOY_SSH_KEY`

**Важно при добавлении ключа в GitHub Secrets:**
- Откройте файл `~/.ssh/id_rsa` (приватный ключ, БЕЗ `.pub`)
- Скопируйте **весь** файл, включая строки `-----BEGIN OPENSSH PRIVATE KEY-----` и `-----END OPENSSH PRIVATE KEY-----`
- Убедитесь, что нет лишних пробелов в начале/конце
- В GitHub Secrets вставьте ключ как есть, одной строкой или многострочным текстом (оба варианта работают)

**2. Настройка базы данных PostgreSQL и RabbitMQ**

PostgreSQL автоматически разворачивается в Docker вместе с приложением. 

**RabbitMQ:** Должен быть уже запущен на сервере. Укажите `RABBITMQ_URL` в GitHub Secrets для подключения к существующему RabbitMQ.

**Примеры значений для GitHub Secrets:**

Предположим, вы хотите:
- База данных: `games`
- Пользователь: `games_user`
- Пароль: `my_secure_password_123`

Тогда добавьте в GitHub Secrets:

- **POSTGRES_DB**: `games` (опционально, можно не указывать)
- **POSTGRES_USER**: `games_user` (опционально, можно не указывать)
- **POSTGRES_PASSWORD**: `my_secure_password_123` (обязательно!)
- **DATABASE_URL**: `postgresql+asyncpg://games_user:my_secure_password_123@postgres:5432/games`
- **ALEMBIC_DATABASE_URL**: `postgresql://games_user:my_secure_password_123@postgres:5432/games`

**Важно:** 
- Используйте `postgres` как хост для базы данных (это имя сервиса в Docker)
- **КРИТИЧЕСКИ ВАЖНО:** В конце строки подключения (`/database_name`) должно быть имя **БАЗЫ ДАННЫХ** (`games`), а НЕ имя пользователя (`games_user`)!
  - ✅ Правильно: `postgresql://games_user:password@postgres:5432/games`
  - ❌ Неправильно: `postgresql://games_user:password@postgres:5432/games_user`
- Для RabbitMQ используйте `host.docker.internal` если RabbitMQ на том же хосте, или IP/домен если на другом сервере
- Данные сохраняются в Docker volume: `postgres_data`

**3. Файлы создаются автоматически**

На сервере ничего делать не нужно - workflow автоматически создаст все необходимые файлы (`docker-compose.yml` и `.env`) при первом деплое.

## Деплой

После настройки: при push в `main`/`master` автоматически запускается сборка и деплой.

Вручную: Actions → Build and Push Docker images to GHCR → Run workflow

**Примечание про видимость пакета:**

**Если пакет приватный (по умолчанию):**
- Обязательно добавьте `GHCR_TOKEN` в GitHub Secrets (см. раздел выше)
- Workflow автоматически авторизуется в GHCR перед pull

**Если хотите сделать пакет публичным (не требуется токен):**

*В организации:*
1. Страница организации → **Packages** (слева)
2. Пакет `game-service` → **Package settings** → **Danger Zone** → **Change visibility** → **Public**

*В личном аккаунте:*
1. Профиль → **Packages** или репозиторий → **Packages**
2. Пакет `game-service` → **Package settings** → **Danger Zone** → **Change visibility** → **Public**

## Устранение проблем с SSH

Если получаете ошибку "unable to authenticate", проверьте на сервере:

```bash
# 1. Проверьте, что публичный ключ добавлен
cat ~/.ssh/authorized_keys
# Должна быть строка, начинающаяся с ssh-rsa AAAA...

# 2. Проверьте права доступа
ls -la ~/.ssh
# Должно быть:
# drwx------  (700) для .ssh
# -rw-------  (600) для authorized_keys

# 3. Если права неправильные, исправьте:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 4. Проверьте логи SSH (если доступны)
sudo tail -f /var/log/auth.log
# или
sudo journalctl -u ssh -f
```

**Убедитесь, что публичный ключ в authorized_keys соответствует приватному ключу в GitHub Secrets!**

## Проверка деплоя на сервере

Подключитесь к серверу через VNC/SSH и выполните:

```bash
# Проверка статуса контейнера
docker compose ps

# Просмотр логов
docker compose logs game-service

# Просмотр последних логов в реальном времени
docker compose logs -f --tail=50 game-service

# Проверка, что сервис отвечает
curl http://localhost:8010/docs

# Или через браузер (если есть доступ):
# http://ваш-ip-сервера:8010/docs
```

## Устранение проблем

### Ошибка: "database 'games_user' does not exist"

Эта ошибка возникает, если в строке подключения указано неправильное имя базы данных.

**Проблема:** В `DATABASE_URL` или `ALEMBIC_DATABASE_URL` указано имя пользователя вместо имени базы данных.

**Решение:**

1. Проверьте переменные окружения на сервере:
```bash
docker compose exec game-service env | grep DATABASE_URL
```

2. Убедитесь, что в конце строки подключения указано имя базы данных (`games`), а не пользователя (`games_user`):
   - ✅ Правильно: `postgresql://games_user:password@postgres:5432/games`
   - ❌ Неправильно: `postgresql://games_user:password@postgres:5432/games_user`

3. Исправьте переменные в GitHub Secrets:
   - Обновите `DATABASE_URL` и `ALEMBIC_DATABASE_URL` с правильным именем базы данных
   - Перезапустите деплой

4. Или исправьте локально на сервере (если используете `.env` файл):
```bash
# Проверьте текущие значения переменных
cd ~/game-service
cat .env | grep DATABASE_URL

# Если значения неправильные, отредактируйте .env файл
nano .env

# Убедитесь, что строки выглядят так (ВАЖНО: в конце /games, а НЕ /games_user):
DATABASE_URL=postgresql+asyncpg://games_user:your_password@postgres:5432/games
ALEMBIC_DATABASE_URL=postgresql://games_user:your_password@postgres:5432/games

# Полностью перезапустите контейнеры (удалите и создайте заново)
docker compose down
docker compose up -d

# Проверьте переменные окружения внутри контейнера
docker compose exec game-service env | grep DATABASE_URL
```

**Если проблема сохраняется:**

1. Проверьте переменные в GitHub Secrets еще раз - убедитесь, что в конце `/games`, а не `/games_user`
2. Удалите старый `.env` файл и перезапустите деплой:
```bash
cd ~/game-service
rm .env
# Затем запустите деплой через GitHub Actions - он создаст новый .env файл
```
3. Проверьте логи PostgreSQL для точной диагностики:
```bash
docker compose logs postgres | grep FATAL
```
