from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.storage import jobs as job_store


router = APIRouter(prefix="/api/jobs", tags=["media"])


@router.get("/{job_id}/thumbnail")
async def get_thumbnail(job_id: str) -> FileResponse:
    record = await job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    if record.thumbnail_path is None or not record.thumbnail_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="thumbnail not available"
        )
    return FileResponse(record.thumbnail_path, media_type="image/jpeg")
