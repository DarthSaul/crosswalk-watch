import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import Settings, get_settings
from app.schemas import JobRecord, JobResponse, JobStatus
from app.storage import jobs as job_store
from app.thumbnails import ThumbnailError, extract_thumbnail


router = APIRouter(prefix="/api", tags=["videos"])


CHUNK_SIZE = 1024 * 1024


def _suffix(filename: str | None) -> str:
    if not filename:
        return ".mp4"
    suffix = Path(filename).suffix.lower()
    return suffix if suffix else ".mp4"


@router.post("/videos", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> JobResponse:
    content_type = file.content_type or ""
    if not content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"expected a video upload, got content-type {content_type!r}",
        )

    settings.ensure_dirs()
    job_id = uuid.uuid4().hex
    suffix = _suffix(file.filename)
    video_path = settings.uploads_dir / f"{job_id}{suffix}"
    thumb_path = settings.uploads_dir / f"{job_id}.jpg"

    max_bytes = settings.max_upload_mb * 1024 * 1024
    bytes_written = 0

    try:
        with video_path.open("wb") as out:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"upload exceeds {settings.max_upload_mb} MB",
                    )
                out.write(chunk)
    except HTTPException:
        video_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to save upload: {exc}",
        ) from exc
    finally:
        await file.close()

    try:
        await asyncio.to_thread(
            extract_thumbnail, video_path, thumb_path, settings.thumbnail_seconds
        )
    except ThumbnailError as exc:
        video_path.unlink(missing_ok=True)
        thumb_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    record = JobRecord(
        id=job_id,
        status=JobStatus.UPLOADED,
        original_filename=file.filename or f"{job_id}{suffix}",
        video_path=video_path,
        thumbnail_path=thumb_path,
        created_at=datetime.now(timezone.utc),
    )
    await job_store.create(record)
    return JobResponse.from_record(record)
