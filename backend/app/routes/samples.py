import re
from pathlib import Path

import cv2
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.config import Settings, get_settings
from app.schemas import (
    CreateFromSampleRequest,
    JobResponse,
    SampleInfo,
)
from app.services.jobs import (
    JobCreationError,
    copy_file_async,
    new_job_paths,
    thumbnail_and_register,
)
from app.thumbnails import ThumbnailError, extract_thumbnail


router = APIRouter(prefix="/api", tags=["samples"])

SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+\.mp4$")
THUMB_DIR_NAME = ".thumbs"


def _safe_sample_path(filename: str, samples_dir: Path) -> Path:
    if not SAFE_FILENAME_RE.match(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid sample filename",
        )
    target = (samples_dir / filename).resolve()
    samples_root = samples_dir.resolve()
    if samples_root not in target.parents and target != samples_root:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sample path escapes samples directory",
        )
    if not target.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="sample not found"
        )
    return target


def _probe_video(path: Path) -> tuple[float | None, int | None, int | None, float | None]:
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            return None, None, None, None
        fps = cap.get(cv2.CAP_PROP_FPS) or None
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        raw_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        raw_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = int(raw_w) if raw_w is not None else None
        height = int(raw_h) if raw_h is not None else None
        duration = (frame_count / fps) if fps and frame_count else None
        return duration, width, height, fps
    finally:
        cap.release()


def _ensure_sample_thumbnail(sample_path: Path, settings: Settings) -> Path:
    thumb_dir = settings.samples_dir / THUMB_DIR_NAME
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = thumb_dir / f"{sample_path.stem}.jpg"
    if thumb_path.exists() and thumb_path.stat().st_mtime >= sample_path.stat().st_mtime:
        return thumb_path
    try:
        extract_thumbnail(sample_path, thumb_path, settings.thumbnail_seconds)
    except ThumbnailError:
        thumb_path.unlink(missing_ok=True)
        raise
    return thumb_path


@router.get("/samples", response_model=list[SampleInfo])
async def list_samples(settings: Settings = Depends(get_settings)) -> list[SampleInfo]:
    settings.ensure_dirs()
    out: list[SampleInfo] = []
    for path in sorted(settings.samples_dir.glob("*.mp4")):
        if not SAFE_FILENAME_RE.match(path.name):
            continue
        duration, width, height, fps = _probe_video(path)
        try:
            _ensure_sample_thumbnail(path, settings)
        except ThumbnailError:
            continue
        out.append(
            SampleInfo(
                filename=path.name,
                size_bytes=path.stat().st_size,
                duration_seconds=duration,
                width=width,
                height=height,
                fps=fps,
                thumbnail_url=f"/api/samples/{path.name}/thumbnail",
            )
        )
    return out


@router.get("/samples/{filename}/thumbnail")
async def sample_thumbnail(
    filename: str, settings: Settings = Depends(get_settings)
) -> FileResponse:
    sample_path = _safe_sample_path(filename, settings.samples_dir)
    try:
        thumb_path = _ensure_sample_thumbnail(sample_path, settings)
    except ThumbnailError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return FileResponse(thumb_path, media_type="image/jpeg")


@router.post(
    "/videos/from-sample",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_from_sample(
    request: CreateFromSampleRequest,
    settings: Settings = Depends(get_settings),
) -> JobResponse:
    settings.ensure_dirs()
    sample_path = _safe_sample_path(request.filename, settings.samples_dir)
    job_id, video_path, thumbnail_path = new_job_paths(settings, sample_path.suffix)

    try:
        await copy_file_async(sample_path, video_path)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed to copy sample: {exc}",
        ) from exc

    try:
        record = await thumbnail_and_register(
            job_id=job_id,
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            original_filename=request.filename,
            settings=settings,
        )
    except JobCreationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return JobResponse.from_record(record)
