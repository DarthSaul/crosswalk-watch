# Crosswalk Watch

A fullstack computer-vision playground for analyzing intersection videos:
upload a clip, draw polygon zones on a frame, and get back an annotated MP4
plus per-zone analytics — entries, average dwell time, peak occupancy, and
occupancy over time.

## Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, OpenCV, Ultralytics YOLO11n,
  ByteTrack, [supervision](https://supervision.roboflow.com), ffmpeg. Managed
  with [`uv`](https://docs.astral.sh/uv/).
- **Frontend:** Nuxt 3 + TypeScript, [Chart.js](https://www.chartjs.org).
  Managed with [`pnpm`](https://pnpm.io/).
- **Communication:** REST + polling (no WebSockets).

## Prerequisites

Install once, system-wide:

- `uv` — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `ffmpeg` — `brew install ffmpeg` (macOS) or your distro's package
- `pnpm` ≥ 9 and Node ≥ 20

## Run it locally

```sh
# terminal 1 — backend
cd backend
uv sync                                              # ~1 GB on first run (torch + ultralytics)
uv run uvicorn app.main:app --reload --port 8000

# terminal 2 — frontend
cd frontend
pnpm install
pnpm dev
```

Open <http://localhost:3000>. The first analysis pulls YOLO11n weights
(~5 MB, automatic).

## Daily flow

1. **Pick or upload a clip.** From the home page, choose one of the sample
   clips or drop in your own `.mp4` (up to 200 MB by default). You'll land on
   a job page with a thumbnail at t≈1s.
2. **Draw zones (optional).** On the thumbnail, click points around an area
   of interest, then double-click to close the polygon (or press Enter).
   Press Esc to cancel a draft. Rename or delete zones in the sidebar.
   Skipping zones still gives you a tracked annotated video — just no
   per-zone stats.
3. **Analyze.** Click **Analyze**. The job moves through `processing` with a
   live progress bar; on completion you get an annotated MP4 with bounding
   boxes, per-track labels, motion traces, and your zones overlaid in their
   chosen colors. Below the player, a Chart.js line shows per-zone occupancy
   over time, plus a table with entries, avg dwell, and peak concurrent.
4. **Iterate.** Click **Re-analyze** to re-run with different zones.

## Sample clips

Drop any `.mp4` files into `backend/data/samples/` and they'll show up in
the sample picker on the home page.

There's a helper that copies samples from a repo-root `samples/` directory
into the backend (and falls back to a small Pexels download set if neither
exists):

```sh
./scripts/fetch_samples.sh
```

## Configuration

| Where | Var | Default | Notes |
|---|---|---|---|
| frontend | `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | |
| backend | `CROSSWALK_MAX_UPLOAD_MB` | `200` | |
| backend | `CROSSWALK_THUMBNAIL_SECONDS` | `1.0` | |
| backend | `CROSSWALK_DATA_DIR` | `data` | |
| backend | `CROSSWALK_YOLO_WEIGHTS` | `yolo11n.pt` | nano (~5 MB). Try `yolo11s.pt` (~22 MB) for better small-object recall. |
| backend | `CROSSWALK_YOLO_IMGSZ` | `640` | Inference resolution. Bumping to `1280` 3-4× the runtime but picks up far-away pedestrians. |
| backend | `CROSSWALK_YOLO_CONF` | `0.25` | Detection confidence floor. Lower (e.g. `0.15`) catches more tentative detections. |

Backend env vars are also honored through `backend/.env`. See [.env.example](.env.example).

If pedestrians are getting missed in a clip — common when people are small in the
frame relative to the vehicles — bump `CROSSWALK_YOLO_IMGSZ=1280` first; that
alone fixes most cases. If that's still not enough, swap to `yolo11s.pt` and/or
drop the confidence floor.

## Layout

```
backend/
  app/
    main.py            # FastAPI app + CORS + router mount
    config.py          # settings (paths, limits, CORS origins)
    schemas.py         # Pydantic v2 DTOs
    thumbnails.py      # OpenCV frame extraction
    routes/
      upload.py        # POST /api/videos
      jobs.py          # GET /api/jobs/{id}
      media.py         # GET /api/jobs/{id}/{thumbnail,result}
      analyze.py       # POST /api/jobs/{id}/analyze
      samples.py       # GET /api/samples (+ /thumbnail), POST /api/videos/from-sample
    pipeline/
      detector.py      # YOLO11n loader + COCO class allowlist
      tracker.py       # sv.ByteTrack factory
      annotators.py    # box / label / trace stack
      zones.py         # PolygonZone runtime + per-zone summarization
      processor.py     # process_video — full pipeline + ffmpeg transcode
    services/jobs.py   # shared job-creation helpers
    storage/jobs.py    # in-memory job store
  data/                # gitignored runtime data
    uploads/  outputs/  samples/
  tests/
    test_pipeline.py   # smoke test on a 5-second clip
  Dockerfile

frontend/
  pages/
    index.vue              # hero, how-it-works, sample picker, uploader
    jobs/[id].vue          # zone drawing → analysis → results
  components/
    VideoUploader.vue
    SamplePicker.vue
    ZoneDrawer.vue         # SVG overlay, polygon-click-to-add
    ZoneList.vue           # sidebar of zones
    AnalysisProgress.vue
    ResultPlayer.vue
    StatsPanel.vue         # Chart.js occupancy + per-zone table
  composables/
    useJobApi.ts
    useZoneDrawing.ts
  types/api.ts

scripts/fetch_samples.sh
```

## Tests

A single backend smoke test runs the pipeline on a 5-second clip:

```sh
cd backend
uv run pytest tests/test_pipeline.py -v
```

It searches ancestor `samples/` and `data/samples/` directories, or honors
`CROSSWALK_SAMPLE_PATH=/abs/path/to/clip.mp4`.

## Docker (backend)

```sh
cd backend
docker build -t crosswalk-watch-backend .
docker run --rm -p 8000:8000 \
  -v "$PWD/data:/app/data" \
  crosswalk-watch-backend
```

The image installs `ffmpeg` and runs `uvicorn` on port 8000. Mount
`backend/data` so uploads, outputs, and samples persist across container
runs.

## Notes

- COCO classes are filtered to person, bicycle, car, truck.
- Annotated videos are re-encoded to H.264 + faststart so they play in
  Safari and inline `<video>` tags.
- The job store is in-memory — restarting the backend forgets jobs (but the
  uploaded videos and outputs stay on disk).
