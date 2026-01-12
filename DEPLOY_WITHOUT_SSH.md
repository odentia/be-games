# Деплой без SSH

Если вы не хотите использовать SSH для деплоя, есть несколько альтернативных способов.

## Вариант 1: Docker Registry + Webhook (Рекомендуется для VPS)

В этом варианте GitHub Actions будет собирать Docker образ и пушить его в Docker Hub (или другой registry), а на сервере простой скрипт будет автоматически обновлять контейнер.

### Преимущества:
- ✅ Безопасно (не нужен SSH ключ на GitHub)
- ✅ Простая настройка на сервере
- ✅ Можно использовать веб-интерфейс для управления

### Настройка:

#### 1. Создайте аккаунт на Docker Hub (бесплатно)
- Зайдите на https://hub.docker.com
- Зарегистрируйтесь и создайте репозиторий (например, `ваш-username/game-service`)

#### 2. Настройте GitHub Secrets
Добавьте в GitHub Secrets:
- `DOCKER_USERNAME` - ваш логин на Docker Hub
- `DOCKER_PASSWORD` - ваш пароль Docker Hub (или Access Token)

#### 3. Обновите GitHub Actions workflow

Используйте альтернативный workflow файл (см. `.github/workflows/deploy-registry.yml`)

#### 4. На сервере установите скрипт обновления

```bash
# Создайте директорию для скриптов
mkdir -p ~/scripts
cd ~/scripts

# Создайте скрипт обновления
nano update-service.sh
```

Содержимое скрипта:

```bash
#!/bin/bash
cd ~/game-service

# Загрузка последней версии образа
docker pull ваш-username/game-service:latest

# Остановка старого контейнера
docker-compose down || true

# Запуск новой версии
docker-compose up -d

# Очистка старых образов
docker image prune -f

echo "Service updated at $(date)"
```

Сделайте скрипт исполняемым:

```bash
chmod +x update-service.sh
```

#### 5. Настройте автоматическое обновление

**Вариант A: Через cron (каждые 5 минут проверять обновления)**

```bash
crontab -e
```

Добавьте строку:
```
*/5 * * * * cd ~/game-service && docker pull ваш-username/game-service:latest && docker-compose up -d
```

**Вариант B: Через systemd timer (более надежно)**

Создайте файл `~/scripts/update-service.sh` (см. выше) и настройте systemd.

---

## Вариант 2: Готовые PaaS сервисы (Самый простой)

Используйте готовые платформы, которые автоматически деплоят из GitHub.

### Railway (railway.app)
- ✅ Бесплатный тарифный план
- ✅ Автоматический деплой из GitHub
- ✅ Встроенная база данных
- ✅ Простая настройка

**Как использовать:**
1. Зайдите на https://railway.app
2. Войдите через GitHub
3. Создайте новый проект
4. Выберите "Deploy from GitHub repo"
5. Выберите ваш репозиторий
6. Добавьте переменные окружения
7. Готово!

### Render (render.com)
- ✅ Бесплатный тарифный план
- ✅ Автоматический деплой
- ✅ Встроенная PostgreSQL

### Fly.io (fly.io)
- ✅ Хорошо работает с Docker
- ✅ Глобальная сеть
- ✅ Бесплатный тариф

### Heroku (heroku.com)
- ⚠️ Платный (но есть бесплатные альтернативы)

---

## Вариант 3: Веб-панель управления Docker (Portainer)

Если на вашем VPS есть доступ к веб-интерфейсу или вы можете установить Portainer.

### Установка Portainer:

```bash
docker volume create portainer_data

docker run -d -p 8000:8000 -p 9443:9443 \
  --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

Теперь:
1. Откройте `https://ваш-ip:9443` в браузере
2. Создайте аккаунт администратора
3. Используйте веб-интерфейс для управления Docker

Вы сможете:
- Загружать образы вручную
- Управлять контейнерами через веб-интерфейс
- Просматривать логи
- Обновлять контейнеры

---

## Вариант 4: GitHub Actions + Docker Registry + Watchtower

Watchtower - автоматически обновляет Docker контейнеры при появлении нового образа в registry.

### Настройка:

1. Настройте GitHub Actions для пуша в Docker Registry (как в варианте 1)

2. На сервере запустите Watchtower:

```bash
docker run -d \
  --name watchtower \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 300 \
  --label-enable \
  game-service
```

3. В `docker-compose.yml` добавьте label:

```yaml
services:
  game-service:
    image: ваш-username/game-service:latest
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    # ... остальная конфигурация
```

Watchtower будет автоматически проверять обновления каждые 5 минут и перезапускать контейнеры.

---

## Вариант 5: GitHub Actions + Webhook на сервере

Создайте простой веб-сервер на сервере, который будет принимать запросы от GitHub Actions и обновлять контейнер.

### На сервере:

```bash
# Установите Python (если нет)
apt install python3 python3-pip -y

# Создайте простой веб-сервер
mkdir -p ~/webhook
cd ~/webhook
nano webhook-server.py
```

Содержимое `webhook-server.py`:

```python
#!/usr/bin/env python3
import subprocess
import hmac
import hashlib
from flask import Flask, request, abort
import os

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'ваш-секретный-ключ')

@app.route('/deploy', methods=['POST'])
def deploy():
    # Проверка секрета
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not verify_signature(request.data, signature, WEBHOOK_SECRET):
        abort(403)
    
    # Обновление сервиса
    try:
        subprocess.run(['bash', '~/scripts/update-service.sh'], check=True)
        return 'Deployed successfully', 200
    except Exception as e:
        return f'Error: {str(e)}', 500

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f'sha256={expected}', signature)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
```

Запуск:

```bash
pip3 install flask
python3 webhook-server.py
```

Или через systemd для автозапуска.

В GitHub Actions добавьте шаг отправки webhook после сборки образа.

---

## Сравнение вариантов

| Вариант | Сложность | Безопасность | Автоматизация | Рекомендация |
|---------|-----------|--------------|---------------|--------------|
| Docker Registry + Cron | Средняя | ✅ Высокая | ✅ Полная | ⭐⭐⭐ Рекомендуется |
| PaaS (Railway/Render) | Низкая | ✅ Высокая | ✅ Полная | ⭐⭐⭐⭐ Самый простой |
| Portainer | Низкая | ⚠️ Средняя | ❌ Ручная | ⭐⭐ Для управления |
| Watchtower | Средняя | ✅ Высокая | ✅ Полная | ⭐⭐⭐⭐ Рекомендуется |
| Webhook | Высокая | ⚠️ Средняя | ✅ Полная | ⭐ Для продвинутых |

---

## Рекомендация

**Для начала:** Используйте **Railway** или **Render** - это самый простой способ, не требует настройки сервера.

**Для VPS:** Используйте **Docker Registry + Watchtower** - это даст вам полный контроль и автоматизацию без SSH ключей на GitHub.

Какой вариант вам больше подходит?
