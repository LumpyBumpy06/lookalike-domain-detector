from typing import Protocol

from lookalike.detection import Detection
from lookalike.domain import Domain


class Detector(Protocol):
    """Detect whether a candidate domain resembles a protected brand."""

    def detect(
        self,
        candidate: Domain,
        brand: Domain,
    ) -> Detection | None: ...
