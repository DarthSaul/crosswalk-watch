from dataclasses import dataclass, field

import numpy as np
import supervision as sv

from app.schemas import ZoneDefinition, ZoneStats


@dataclass
class ZoneRuntime:
    definition: ZoneDefinition
    polygon_zone: sv.PolygonZone
    annotator: sv.PolygonZoneAnnotator
    seen_track_ids: set[int] = field(default_factory=set)
    dwell_frames: dict[int, int] = field(default_factory=dict)
    occupancy_series: list[int] = field(default_factory=list)


def build_zone_runtimes(
    definitions: list[ZoneDefinition],
    frame_width: int,
    frame_height: int,
) -> list[ZoneRuntime]:
    runtimes: list[ZoneRuntime] = []
    for zd in definitions:
        polygon = _denormalize(zd.points, frame_width, frame_height)
        pz = sv.PolygonZone(polygon=polygon)
        color = sv.Color.from_hex(zd.color)
        annotator = sv.PolygonZoneAnnotator(
            zone=pz,
            color=color,
            thickness=3,
        )
        runtimes.append(ZoneRuntime(definition=zd, polygon_zone=pz, annotator=annotator))
    return runtimes


def _denormalize(
    points: list[tuple[float, float]], width: int, height: int
) -> np.ndarray:
    return np.array(
        [(round(x * width), round(y * height)) for x, y in points],
        dtype=np.int32,
    )


def update_zone_runtimes(
    runtimes: list[ZoneRuntime], detections: sv.Detections
) -> None:
    for runtime in runtimes:
        in_mask = runtime.polygon_zone.trigger(detections=detections)
        in_zone = detections[in_mask]

        in_track_ids: set[int] = set()
        for tid in in_zone.tracker_id:
            if tid is None:
                continue
            tid_int = int(tid)
            in_track_ids.add(tid_int)
            runtime.seen_track_ids.add(tid_int)
            runtime.dwell_frames[tid_int] = runtime.dwell_frames.get(tid_int, 0) + 1

        runtime.occupancy_series.append(len(in_track_ids))


def annotate_zones(
    frame: np.ndarray, runtimes: list[ZoneRuntime]
) -> np.ndarray:
    out = frame
    for runtime in runtimes:
        out = runtime.annotator.annotate(scene=out)
    return out


def summarize_zones(runtimes: list[ZoneRuntime], fps: float) -> list[ZoneStats]:
    safe_fps = fps if fps > 0 else 30.0
    out: list[ZoneStats] = []
    for runtime in runtimes:
        dwell = runtime.dwell_frames.values()
        avg_dwell_seconds = (sum(dwell) / len(dwell) / safe_fps) if dwell else 0.0
        out.append(
            ZoneStats(
                name=runtime.definition.name,
                color=runtime.definition.color,
                entries=len(runtime.seen_track_ids),
                avg_dwell_seconds=avg_dwell_seconds,
                max_concurrent=max(runtime.occupancy_series, default=0),
                occupancy_series=runtime.occupancy_series,
            )
        )
    return out
