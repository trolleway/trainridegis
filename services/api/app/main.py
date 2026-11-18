"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from celery.result import AsyncResult

from app.core.config import settings

from app.celery_client import celery_client
import os
import redis.asyncio as redis

IMAGE_GENERATE_TASK = "render.generate_png"


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="This is description in pydantic model for prompt field")

@app.get("/health", tags=["health"])
def health() -> dict:
    """Проверка живости сервиса (критерий Этапа 0)."""
    return {"status": "ok", "service": "api", "env": settings.app_env}
    
@app.get("/echo/{text}", 
summary="For developing",
 description="Returns text from {text}",
tags=["health"])
def echo(text='variable default') -> dict:
    return {"status": "ok", "service": "api", "text":text,"env": settings.app_env}
    
@app.post("/generate", status_code=202)
def generate_image(req: GenerateRequest):
    """Отправляет задачу в очередь по строковому имени и мгновенно возвращает task_id."""
    async_result = celery_client.send_task(
        IMAGE_GENERATE_TASK,
        args=[req.prompt],
    )
    return {
        "task_id": async_result.id,
        "status": "PENDING",
        "message": f"Задача {IMAGE_GENERATE_TASK} поставлена в очередь",
    }


@app.get("/queue-length", tags=["queue"])
async def queue_length():
    """Возвращает длину очереди Celery в Redis (число ожидающих задач).

    Брокер Celery — Redis: очередь хранится как список (list) с ключом,
    равным имени очереди (по умолчанию ``celery``), поэтому длина
    получается командой LLEN. Если воркер занят, задачи дополнительно
    лежат в hash-ключе ``unacked`` (HLEN) до подтверждения получения.
    """
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        queue_name = celery_client.conf.task_default_queue or "celery"
        pending = await client.llen(queue_name)
        unacked = await client.hlen("unacked")
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": "redis_unavailable", "message": str(exc)},
        ) from exc
    finally:
        await client.aclose()

    return {
        "queue": queue_name,
        "pending": pending,
        "in_flight": unacked,
        "total": pending + unacked,
    }


@app.get("/status/{task_id}")
def get_status(task_id: str):
    """Проверяет статус задачи по task_id."""
    result = AsyncResult(task_id, app=celery_client)

    # Позволяет отличить несуществующую задачу от просто ещё не выполненной
    if not result.ready():
        meta = result.info if isinstance(result.info, dict) else {}
                
        return {
                    "task_id": task_id,
                    "status": result.status,
                    "progress": {
                        "step": meta.get("step"),
                        "total": meta.get("total"),
                        "prompt": meta.get("prompt"),
                    },
                    "result": None,
                }

    if result.successful():
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
        }

    raise HTTPException(
        status_code=500,
        detail={
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
        },
    )
    
    

