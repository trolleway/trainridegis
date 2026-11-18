"""Celery-воркер рендера карт.

MVP: рендер — заглушка, задача возвращает метаданные без генерации PNG.
Реальный PyQGIS-рендер (PostGIS -> PNG) подключается пост-MVP без изменения API.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "trainridegis_render",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    timezone="UTC",
)

import time
import uuid

@celery_app.task(name="render.generate_png",    bind=True,
    max_retries=3)
def generate_png(self, route_geojson: str, kind: str = "user") -> dict:
    """Заглушка рендера.

    """
    # Имитация тяжёлой работы
    seconds=15
    for step in range(1, seconds):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={"step": step, "total": seconds},
        )
        
    return {
        "status": "ok",
        "mode": settings.render_mode,
        "kind": kind,
        "output_dir": settings.render_output_dir,
    }
    

