from dataclasses import dataclass

import numpy as np
import supervision as sv


@dataclass
class AnnotatorStack:
    box: sv.BoxAnnotator
    label: sv.LabelAnnotator
    trace: sv.TraceAnnotator


def make_annotators() -> AnnotatorStack:
    return AnnotatorStack(
        box=sv.BoxAnnotator(thickness=2),
        label=sv.LabelAnnotator(text_scale=0.5, text_thickness=1),
        trace=sv.TraceAnnotator(thickness=2, trace_length=30),
    )


def annotate_frame(
    frame: np.ndarray,
    detections: sv.Detections,
    labels: list[str],
    stack: AnnotatorStack,
) -> np.ndarray:
    out = stack.trace.annotate(scene=frame.copy(), detections=detections)
    out = stack.box.annotate(scene=out, detections=detections)
    out = stack.label.annotate(scene=out, detections=detections, labels=labels)
    return out
