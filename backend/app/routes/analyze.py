import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.pipeline.processor import PipelineError, process_video
from app.schemas import AnalyzeRequest, JobResponse, JobStatus, ZoneDefinition
from app.storage import jobs as job_store


log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["analyze"])


@router.post(
    "/{job_id}/analyze",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def analyze_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    request: AnalyzeRequest = AnalyzeRequest(),
    settings: Settings = Depends(get_settings),
) -> JobResponse:
    record = job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    if record.status not in (JobStatus.UPLOADED, JobStatus.FAILED, JobStatus.COMPLETE):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"job is currently {record.status.value}",
        )

    output_path = settings.outputs_dir / f"{job_id}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    job_store.update(
        job_id,
        status=JobStatus.PROCESSING,
        progress=0.0,
        error=None,
        result_path=output_path,
        stats=None,
        zones=request.zones,
    )

    background_tasks.add_task(
        _run_pipeline, job_id, record.video_path, output_path, request.zones
    )
    refreshed = job_store.get(job_id)
    assert refreshed is not None
    return JobResponse.from_record(refreshed)


def _run_pipeline(
    job_id: str,
    video_path: Path,
    output_path: Path,
    zones: list[ZoneDefinition],
) -> None:
    def on_progress(p: float) -> None:
        job_store.update(job_id, progress=p)

    try:
        stats = process_video(
            video_path,
            output_path,
            zones=zones,
            progress_callback=on_progress,
        )
        job_store.update(
            job_id,
            status=JobStatus.COMPLETE,
            progress=1.0,
            stats=stats,
        )
    except (PipelineError, Exception) as exc:  # noqa: BLE001
        log.exception("pipeline failed for job %s", job_id)
        job_store.update(
            job_id,
            status=JobStatus.FAILED,
            error=str(exc) or exc.__class__.__name__,
        )
