#!/bin/bash

set -e

if [ -f "/tmp/game-service.tar.gz" ]; then
    docker load < /tmp/game-service.tar.gz
    rm /tmp/game-service.tar.gz
fi

docker-compose down || true
docker-compose run --rm game-service uv run alembic upgrade head || true
docker-compose up -d
sleep 5
docker-compose ps
