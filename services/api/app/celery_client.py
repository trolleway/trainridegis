"""Celery-клиент для FastAPI.

Этот модуль НЕ загружает задачи воркера. Он используется только для:
  - публикации задач в очередь по строковому имени через send_task(...)
  - чтения результата по task_id из бэкенда результатов.
"""

import os

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_client = Celery(
    "fastapi_client",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Общая конфигурация совместимости с воркером
celery_client.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)