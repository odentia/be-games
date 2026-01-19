import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from game_service.core.config import Settings
from game_service.core.db import init_engine, init_session_factory, close_engine, get_session_factory
from game_service.core.logging import get_logger
from game_service.mq.consumer import EventConsumer
from game_service.mq.publisher import EventPublisher
from game_service.repo.sql.repositories import SQLGameRepository

log = get_logger(__name__)


async def handle_comment_deleted(event_data: dict):
    """Обработчик события удаления комментария - можно использовать для обновления статистики"""
    try:
        entity_id = event_data.get("entity_id")
        entity_type = event_data.get("entity_type")
        
        if entity_type != "game":
            return
        
        if not entity_id:
            log.warning(f"Invalid event data for comment_deleted: {event_data}")
            return
        
        # Здесь можно добавить логику обновления статистики игры
        # Например, обновление счетчика комментариев
        log.debug(f"Comment deleted for game {entity_id}")
                
    except Exception as e:
        log.error(f"Error handling comment_deleted event: {e}")


async def start_consumer(consumer: EventConsumer):
    """Запуск consumer в фоновом режиме"""
    try:
        await consumer.start_consuming()
    except asyncio.CancelledError:
        log.info("Consumer cancelled")
    except Exception as e:
        log.error(f"Consumer error: {e}")


def build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # --- Startup ---
        log.info("Starting service...", extra={"app": settings.app_name, "env": settings.env})
        consumer_task = None

        try:
            # DB engine & session factory
            engine = await init_engine(settings.database_url, echo=settings.sql_echo)
            sf = init_session_factory(engine)
            app.state.engine = engine
            app.state.session_factory = sf

            # Initialize event publisher
            publisher = EventPublisher(settings)
            await publisher.connect()
            app.state.event_publisher = publisher
            log.info("Event publisher initialized successfully")

            # Initialize event consumer
            consumer = EventConsumer(settings)
            await consumer.connect()
            
            # Регистрируем обработчики событий
            consumer.register_handler("comment_deleted", handle_comment_deleted)
            
            # Запускаем consumer в фоновой задаче
            consumer_task = asyncio.create_task(start_consumer(consumer))
            app.state.consumer = consumer
            app.state.consumer_task = consumer_task
            log.info("Event consumer started successfully")

            app.state.settings = settings
            app.state.ready = True
            log.info("Service is up")

        except Exception as e:
            log.error(f"Failed to start service: {e}")
            raise

        try:
            yield
        finally:
            # --- Shutdown ---
            log.info("Shutting down service...")
            app.state.ready = False

            # Останавливаем consumer
            if hasattr(app.state, 'consumer_task') and app.state.consumer_task:
                app.state.consumer_task.cancel()
                try:
                    await app.state.consumer_task
                except asyncio.CancelledError:
                    pass
            
            if hasattr(app.state, 'consumer'):
                await app.state.consumer.close()
                log.info("Event consumer closed")

            # Close event publisher
            if hasattr(app.state, 'event_publisher'):
                await app.state.event_publisher.close()
                log.info("Event publisher closed")

            # Close DB engine
            await close_engine(engine)

            log.info("Bye")

    return lifespan
