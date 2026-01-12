#!/bin/bash

# Скрипт для обновления сервиса из Docker Registry
# Использование: ./update-from-registry.sh

set -e

DOCKER_USERNAME="${DOCKER_USERNAME:-YOUR_DOCKER_USERNAME}"
IMAGE_NAME="${DOCKER_USERNAME}/game-service:latest"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.registry.yml}"

echo "🔄 Обновление game-service из Docker Registry..."

cd ~/game-service || cd "$(dirname "$0")/.."

# Загрузка последней версии образа
echo "📥 Загрузка образа ${IMAGE_NAME}..."
docker pull "${IMAGE_NAME}"

# Остановка старого контейнера
echo "🛑 Остановка старого контейнера..."
docker-compose -f "${COMPOSE_FILE}" down || true

# Запуск миграций (если нужно)
echo "🗄️  Выполнение миграций базы данных..."
docker-compose -f "${COMPOSE_FILE}" run --rm game-service \
  uv run alembic upgrade head || echo "⚠️  Миграции пропущены"

# Запуск нового контейнера
echo "▶️  Запуск нового контейнера..."
docker-compose -f "${COMPOSE_FILE}" up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервиса..."
sleep 5

# Проверка статуса
echo "✅ Проверка статуса..."
docker-compose -f "${COMPOSE_FILE}" ps

# Очистка старых образов
echo "🧹 Очистка неиспользуемых образов..."
docker image prune -f

echo "🎉 Обновление завершено в $(date)"
