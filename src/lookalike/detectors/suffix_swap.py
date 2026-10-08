from lookalike.detection import Detection
from lookalike.detectors.detector import Detector
from lookalike.domain import Domain


class SuffixSwapDetector(Detector):
    """Detect candidates using the brand label with a different suffix."""

    def detect(
        self,
        candidate: Domain,
        brand: Domain,
    ) -> Detection | None:
        """Return a detection when the labels match but suffixes differ."""
        if candidate.label == brand.label and candidate.suffix != brand.suffix:
            return Detection(detector="suffix_swap")

        return None
