from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class ProcessingStats(BaseModel):
    total_frames: int
    processed_frames: int
    unique_tracks: int
    duration_seconds: float


class JobRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    status: JobStatus
    original_filename: str
    video_path: Path
    thumbnail_path: Path | None = None
    result_path: Path | None = None
    progress: float = 0.0
    stats: ProcessingStats | None = None
    created_at: datetime
    error: str | None = None


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    original_filename: str
    thumbnail_url: str | None
    result_url: str | None
    progress: float
    stats: ProcessingStats | None
    created_at: datetime
    error: str | None

    @classmethod
    def from_record(cls, record: JobRecord) -> "JobResponse":
        thumbnail_url = (
            f"/api/jobs/{record.id}/thumbnail" if record.thumbnail_path else None
        )
        result_url = (
            f"/api/jobs/{record.id}/result"
            if record.status == JobStatus.COMPLETE and record.result_path
            else None
        )
        return cls(
            id=record.id,
            status=record.status,
            original_filename=record.original_filename,
            thumbnail_url=thumbnail_url,
            result_url=result_url,
            progress=record.progress,
            stats=record.stats,
            created_at=record.created_at,
            error=record.error,
        )


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
