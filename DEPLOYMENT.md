# Развертывание

## GitHub Secrets

Settings → Secrets and variables → Actions → New repository secret:

- **DEPLOY_HOST** - IP или домен сервера
- **DEPLOY_USER** - пользователь SSH (например: `root`, `deploy`)
- **DEPLOY_SSH_KEY** - приватный SSH ключ (`~/.ssh/id_rsa`)
- **DEPLOY_PORT** (опционально) - SSH порт, по умолчанию 22

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

На сервере через VNC/SSH:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Вставьте публичный ключ (одна строка, начинается с ssh-rsa AAAA...)
# Сохраните: Ctrl+X, Y, Enter
chmod 600 ~/.ssh/authorized_keys
```

**Важно:** Используйте тот же ключ, который добавите в GitHub Secrets!

Проверьте подключение с локальной машины:
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

**2. На сервере создайте директорию и файлы:**

```bash
ssh ваш-пользователь@ваш-сервер
mkdir -p ~/game-service
cd ~/game-service
```

Создайте `docker-compose.yml` (замените `YOUR_GITHUB_USERNAME` на ваш GitHub username):
```yaml
version: '3.8'
services:
  game-service:
    image: ghcr.io/YOUR_GITHUB_USERNAME/game-service:latest
    container_name: game-service
    restart: unless-stopped
    ports:
      - "8010:8010"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - ALEMBIC_DATABASE_URL=${ALEMBIC_DATABASE_URL}
      - RAWG_API_KEY=${RAWG_API_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    networks:
      - game-service-network
networks:
  game-service-network:
    driver: bridge
```

Создайте `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/games
ALEMBIC_DATABASE_URL=postgresql://user:password@host:5432/games
RAWG_API_KEY=your_rawg_api_key
LOG_LEVEL=INFO
```

## Деплой

После настройки: при push в `main`/`master` автоматически запускается сборка и деплой.

Вручную: Actions → Build and Push Docker images to GHCR → Run workflow

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
