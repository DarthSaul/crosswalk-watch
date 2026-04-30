import os
from pathlib import Path

import cv2
import pytest

from app.pipeline.processor import process_video
from app.schemas import ZoneDefinition


SAMPLE_ENV_VAR = "CROSSWALK_SAMPLE_PATH"


def _find_sample() -> Path | None:
    env = os.environ.get(SAMPLE_ENV_VAR)
    if env:
        p = Path(env)
        if p.is_file():
            return p

    here = Path.cwd().resolve()
    for parent in [here, *here.parents]:
        for candidate in (parent / "data" / "samples", parent / "samples"):
            if candidate.is_dir():
                for f in sorted(candidate.glob("*.mp4")):
                    return f
    return None


def _trim_clip(src: Path, dst: Path, seconds: float) -> int:
    cap = cv2.VideoCapture(str(src))
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        target = int(round(fps * seconds))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(dst), fourcc, fps, (width, height))
        try:
            written = 0
            while written < target:
                ok, frame = cap.read()
                if not ok:
                    break
                writer.write(frame)
                written += 1
            return written
        finally:
            writer.release()
    finally:
        cap.release()


def test_pipeline_smoke(tmp_path: Path) -> None:
    sample = _find_sample()
    if sample is None:
        pytest.skip("no sample video available in data/samples or ../samples")

    clip = tmp_path / "clip.mp4"
    written = _trim_clip(sample, clip, seconds=5.0)
    assert written > 0, "failed to trim sample clip"

    output = tmp_path / "out.mp4"
    progress: list[float] = []

    zones = [
        ZoneDefinition(
            name="center",
            color="#ff6b6b",
            points=[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)],
        )
    ]
    stats = process_video(
        clip,
        output,
        zones=zones,
        progress_callback=progress.append,
    )

    assert output.exists(), "annotated output mp4 was not written"
    assert output.stat().st_size > 1024, "annotated output is suspiciously small"
    assert stats.processed_frames == written
    assert stats.total_frames == written
    assert progress, "progress callback never fired"
    assert progress[-1] == 1.0, f"final progress was {progress[-1]}, not 1.0"

    assert len(stats.zones) == 1
    zone_stat = stats.zones[0]
    assert zone_stat.name == "center"
    assert zone_stat.color == "#ff6b6b"
    assert len(zone_stat.occupancy_series) == written
    assert zone_stat.entries >= 0
    assert zone_stat.max_concurrent >= 0
    peak = max(zone_stat.occupancy_series) if zone_stat.occupancy_series else 0
    assert zone_stat.max_concurrent == peak
