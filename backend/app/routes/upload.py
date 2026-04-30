from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import Settings, get_settings
from app.schemas import JobResponse
from app.services.jobs import (
    JobCreationError,
    new_job_paths,
    thumbnail_and_register,
)


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
    job_id, video_path, thumbnail_path = new_job_paths(settings, _suffix(file.filename))

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
        record = await thumbnail_and_register(
            job_id=job_id,
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            original_filename=file.filename or video_path.name,
            settings=settings,
        )
    except JobCreationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return JobResponse.from_record(record)
