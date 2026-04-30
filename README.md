# Crosswalk Watch

A fullstack computer-vision playground for analyzing intersection videos:
upload a clip, draw zones on a frame, get back an annotated video plus per-zone
stats (entries, exits, dwell, line crossings).

> **Phase 1 (current):** upload → store → thumbnail. The detection / tracking /
> zone pipeline lands in Phase 2.

## Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, OpenCV. Managed with `uv`.
- **Frontend:** Nuxt 3 + TypeScript. Managed with `pnpm`.
- **Communication:** REST (no WebSockets in v1).

## Prerequisites

Install once, system-wide:

- [`uv`](https://docs.astral.sh/uv/) — Python toolchain.
  `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [`ffmpeg`](https://ffmpeg.org/) — required for OpenCV video I/O.
  `brew install ffmpeg` (macOS) or your distro's package.
- [`pnpm`](https://pnpm.io/) ≥ 9 and Node ≥ 20.

## Run it

```sh
# backend (terminal 1)
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000

# frontend (terminal 2)
cd frontend
pnpm install
pnpm dev
```

Open <http://localhost:3000>, drag in a video, watch the thumbnail render on
the job page. `GET http://localhost:8000/health` should return `{"status":"ok"}`.

## Layout

```
backend/
  app/
    main.py            # FastAPI app, CORS, router mount
    config.py          # settings (paths, limits, CORS origins)
    schemas.py         # Pydantic v2 DTOs
    thumbnails.py      # OpenCV frame extraction
    routes/
      upload.py        # POST /api/videos
      jobs.py          # GET /api/jobs/{id}
      media.py         # GET /api/jobs/{id}/thumbnail
    storage/jobs.py    # in-memory job store
    pipeline/          # (Phase 2)
  data/                # gitignored runtime data
    uploads/  outputs/  samples/

frontend/
  pages/
    index.vue          # upload
    jobs/[id].vue      # job detail (thumbnail in P1)
  components/VideoUploader.vue
  composables/useJobApi.ts
  types/api.ts
```

## Sample videos

Three NYC-style crosswalk clips ship with the repo at `samples/` (gitignored
because of size). To use them via the upload UI in Phase 1, just drag one in
from your filesystem. Phase 4 will add an in-app picker that reads from
`backend/data/samples/`.

## Configuration

Frontend reads the backend URL from `NUXT_PUBLIC_API_BASE` (defaults to
`http://localhost:8000`). See `.env.example`.

Backend settings are prefixed `CROSSWALK_` and read from `backend/.env` if
present (e.g. `CROSSWALK_MAX_UPLOAD_MB=500`).
