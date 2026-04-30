from fastapi import APIRouter, HTTPException, status

from app.schemas import JobResponse
from app.storage import jobs as job_store


router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    record = await job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    return JobResponse.from_record(record)
