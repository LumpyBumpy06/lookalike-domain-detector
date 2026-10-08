from lookalike.detection import Detection
from lookalike.detectors.detector import Detector
from lookalike.detectors.similarity import damerau_levenshtein_distance
from lookalike.domain import Domain


class TyposquatDetector(Detector):
    """Detect registrable labels that differ from a brand by one edit."""

    def detect(
        self,
        candidate: Domain,
        brand: Domain,
    ) -> Detection | None:
        """Return a detection when the labels have distance exactly one."""
        distance = damerau_levenshtein_distance(
            candidate.label,
            brand.label,
        )

        if distance != 1:
            return None

        return Detection(detector="typosquat")
