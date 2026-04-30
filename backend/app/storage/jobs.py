import asyncio
from typing import Any

from app.schemas import JobRecord


_jobs: dict[str, JobRecord] = {}
_lock = asyncio.Lock()


async def create(record: JobRecord) -> None:
    async with _lock:
        _jobs[record.id] = record


async def get(job_id: str) -> JobRecord | None:
    async with _lock:
        return _jobs.get(job_id)


async def update(job_id: str, **fields: Any) -> JobRecord:
    async with _lock:
        record = _jobs[job_id]
        updated = record.model_copy(update=fields)
        _jobs[job_id] = updated
        return updated


async def list_all() -> list[JobRecord]:
    async with _lock:
        return list(_jobs.values())
