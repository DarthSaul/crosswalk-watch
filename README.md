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

```text
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

## Deploy

Recommended split for a portfolio-style demo (~$5/mo all-in):

- **Backend** on [Fly.io](https://fly.io) — runs the existing
  [backend/Dockerfile](backend/Dockerfile), persistent volume for data, machines
  sleep when idle and wake on incoming requests.
- **Frontend** on [Vercel](https://vercel.com) — Nuxt 3 with the Vercel nitro
  preset, free Hobby tier covers it.

### Backend — Fly.io

```sh
brew install flyctl
fly auth login
cd backend

# Use the committed fly.toml; edit `app` to a unique name first
fly launch --copy-config --no-deploy

# Persistent disk for uploads, outputs, sample thumbnails, YOLO weights
fly volumes create crosswalk_data --size 3 --region <your-region>

# CORS for your eventual Vercel URL (JSON list, set as a Fly secret)
fly secrets set \
  CROSSWALK_ALLOWED_ORIGINS='["https://<your-site>.vercel.app"]'

fly deploy
```

`fly.toml` sizes the VM at `shared-cpu-2x` / 2 GB — comfortable for nano YOLO +
ffmpeg. `shared-cpu-1x` will OOM during torch import.

To pre-load sample clips for the picker on the home page, drop short `.mp4`
files into `backend/samples-seed/` before `fly deploy` — they're baked into
`/app/data/samples/` at image build time. Trim long clips down first
(`ffmpeg -i input.mp4 -t 10 -c copy seed.mp4`) so they don't bloat the image.

### Frontend — Vercel

1. Import the GitHub repo as a new project.
2. Set **Root Directory** to `frontend` (Vercel auto-detects Nuxt 3 from there).
3. Add an env var: `NUXT_PUBLIC_API_BASE=https://<fly-app>.fly.dev`.
4. Deploy.

### Tuning detection in production

If pedestrians are getting missed, set Fly secrets to upgrade the model
without redeploying:

```sh
fly secrets set CROSSWALK_YOLO_IMGSZ=1280
fly secrets set CROSSWALK_YOLO_WEIGHTS=yolo11s.pt   # if 1280 alone isn't enough
```

The runtime cost goes up roughly linearly with both knobs; expect ~3–4×
analyses on a `shared-cpu-2x` if you go all-in.

## Notes

- COCO classes are filtered to person, bicycle, car, truck.
- Annotated videos are re-encoded to H.264 + faststart so they play in
  Safari and inline `<video>` tags.
- The job store is in-memory — restarting the backend forgets jobs (but the
  uploaded videos and outputs stay on disk).
