from functools import lru_cache

from ultralytics import YOLO


# COCO class IDs we care about for crosswalk analysis.
ALLOWED_CLASS_IDS: tuple[int, ...] = (0, 1, 2, 7)
CLASS_NAMES: dict[int, str] = {
    0: "person",
    1: "bicycle",
    2: "car",
    7: "truck",
}


@lru_cache(maxsize=1)
def load_model(weights: str = "yolo11n.pt") -> YOLO:
    return YOLO(weights)
