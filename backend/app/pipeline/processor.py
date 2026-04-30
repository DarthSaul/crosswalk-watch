import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

import supervision as sv

from app.pipeline.annotators import annotate_frame, make_annotators
from app.pipeline.detector import ALLOWED_CLASS_IDS, CLASS_NAMES, load_model
from app.pipeline.tracker import make_tracker
from app.pipeline.zones import (
    annotate_zones,
    build_zone_runtimes,
    summarize_zones,
    update_zone_runtimes,
)
from app.schemas import ProcessingStats, ZoneDefinition


ProgressCallback = Callable[[float], None]


class PipelineError(Exception):
    pass


def process_video(
    video_path: Path,
    output_path: Path,
    zones: list[ZoneDefinition] | None = None,
    progress_callback: ProgressCallback | None = None,
    progress_throttle_frames: int = 15,
) -> ProcessingStats:
    if not video_path.exists():
        raise PipelineError(f"video not found: {video_path}")

    model = load_model()
    tracker = make_tracker()
    annotators = make_annotators()

    video_info = sv.VideoInfo.from_video_path(str(video_path))
    total = video_info.total_frames or 0
    width, height = video_info.resolution_wh
    fps = float(video_info.fps or 30.0)

    zone_runtimes = build_zone_runtimes(zones or [], width, height)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = output_path.with_suffix(".raw.mp4")

    seen_tracks: set[int] = set()
    started = time.monotonic()
    processed = 0

    try:
        with sv.VideoSink(target_path=str(raw_path), video_info=video_info) as sink:
            for frame in sv.get_video_frames_generator(source_path=str(video_path)):
                results = model(
                    frame,
                    classes=list(ALLOWED_CLASS_IDS),
                    verbose=False,
                )[0]
                detections = sv.Detections.from_ultralytics(results)
                detections = tracker.update_with_detections(detections)

                update_zone_runtimes(zone_runtimes, detections)

                labels = _build_labels(detections)
                for tid in detections.tracker_id:
                    if tid is not None:
                        seen_tracks.add(int(tid))

                annotated = annotate_frame(frame, detections, labels, annotators)
                annotated = annotate_zones(annotated, zone_runtimes)
                sink.write_frame(annotated)
                processed += 1

                if (
                    progress_callback
                    and total > 0
                    and processed % progress_throttle_frames == 0
                ):
                    progress_callback(min(processed / total, 0.99))

        _transcode_to_web_mp4(raw_path, output_path)
    finally:
        raw_path.unlink(missing_ok=True)

    if progress_callback:
        progress_callback(1.0)

    return ProcessingStats(
        total_frames=total,
        processed_frames=processed,
        unique_tracks=len(seen_tracks),
        duration_seconds=time.monotonic() - started,
        fps=fps,
        zones=summarize_zones(zone_runtimes, fps),
    )


def _build_labels(detections: sv.Detections) -> list[str]:
    out: list[str] = []
    for tid, cid in zip(detections.tracker_id, detections.class_id):
        name = CLASS_NAMES.get(int(cid), "obj") if cid is not None else "obj"
        prefix = f"#{int(tid)} " if tid is not None else ""
        out.append(f"{prefix}{name}")
    return out


def _transcode_to_web_mp4(src: Path, dst: Path) -> None:
    if shutil.which("ffmpeg") is None:
        src.replace(dst)
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-an",
        str(dst),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise PipelineError(
            f"ffmpeg transcode failed (exit {result.returncode}): {result.stderr.strip()}"
        )
