from dataclasses import dataclass

from lookalike.domain import Domain


@dataclass(frozen=True)
class Detection:
    """A detector's result on one (candidate, brand).  In future may contain risk assessment via a confidence score."""

    detector: str


@dataclass(frozen=True, slots=True)
class Finding:
    """Combined detector results for one candidate and protected brand."""

    candidate: Domain
    brand: Domain
    detections: tuple[Detection, ...]
