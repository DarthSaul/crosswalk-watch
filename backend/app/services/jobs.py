import asyncio
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import Settings
from app.schemas import JobRecord, JobStatus
from app.storage import jobs as job_store
from app.thumbnails import ThumbnailError, extract_thumbnail


class JobCreationError(Exception):
    pass


def new_job_paths(settings: Settings, suffix: str) -> tuple[str, Path, Path]:
    job_id = uuid.uuid4().hex
    safe_suffix = suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
    video_path = settings.uploads_dir / f"{job_id}{safe_suffix}"
    thumbnail_path = settings.uploads_dir / f"{job_id}.jpg"
    return job_id, video_path, thumbnail_path


async def copy_file_async(src: Path, dst: Path) -> None:
    await asyncio.to_thread(shutil.copyfile, str(src), str(dst))


async def thumbnail_and_register(
    *,
    job_id: str,
    video_path: Path,
    thumbnail_path: Path,
    original_filename: str,
    settings: Settings,
) -> JobRecord:
    try:
        await asyncio.to_thread(
            extract_thumbnail,
            video_path,
            thumbnail_path,
            settings.thumbnail_seconds,
        )
    except ThumbnailError as exc:
        video_path.unlink(missing_ok=True)
        thumbnail_path.unlink(missing_ok=True)
        raise JobCreationError(str(exc)) from exc

    record = JobRecord(
        id=job_id,
        status=JobStatus.UPLOADED,
        original_filename=original_filename,
        video_path=video_path,
        thumbnail_path=thumbnail_path,
        created_at=datetime.now(timezone.utc),
    )
    job_store.create(record)
    return record
