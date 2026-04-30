import threading
from typing import Any

from app.schemas import JobRecord


_jobs: dict[str, JobRecord] = {}
_lock = threading.Lock()


def create(record: JobRecord) -> None:
    with _lock:
        _jobs[record.id] = record.model_copy(deep=True)


def get(job_id: str) -> JobRecord | None:
    with _lock:
        record = _jobs.get(job_id)
        return record.model_copy(deep=True) if record is not None else None


def update(job_id: str, **fields: Any) -> JobRecord:
    with _lock:
        record = _jobs[job_id]
        updated = record.model_copy(update=fields)
        _jobs[job_id] = updated
        return updated.model_copy(deep=True)


def list_all() -> list[JobRecord]:
    with _lock:
        return [record.model_copy(deep=True) for record in _jobs.values()]
