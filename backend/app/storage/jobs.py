import threading
from typing import Any

from app.schemas import JobRecord


_jobs: dict[str, JobRecord] = {}
_lock = threading.Lock()


def create(record: JobRecord) -> None:
    with _lock:
        _jobs[record.id] = record


def get(job_id: str) -> JobRecord | None:
    with _lock:
        return _jobs.get(job_id)


def update(job_id: str, **fields: Any) -> JobRecord:
    with _lock:
        record = _jobs[job_id]
        updated = record.model_copy(update=fields)
        _jobs[job_id] = updated
        return updated


def list_all() -> list[JobRecord]:
    with _lock:
        return list(_jobs.values())
