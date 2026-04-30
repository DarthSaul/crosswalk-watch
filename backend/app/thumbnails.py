from pathlib import Path

import cv2


class ThumbnailError(Exception):
    pass


def extract_thumbnail(video_path: Path, out_path: Path, at_seconds: float) -> None:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ThumbnailError(f"could not open video: {video_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        target_idx = round(at_seconds * fps)
        if frame_count > 0:
            target_idx = max(0, min(target_idx, frame_count - 1))
        else:
            target_idx = max(0, target_idx)

        cap.set(cv2.CAP_PROP_POS_FRAMES, float(target_idx))
        ok, frame = cap.read()
        if not ok or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0.0)
            ok, frame = cap.read()
        if not ok or frame is None:
            raise ThumbnailError(f"could not read any frame from {video_path}")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 85]):
            raise ThumbnailError(f"failed to write thumbnail to {out_path}")
    finally:
        cap.release()
