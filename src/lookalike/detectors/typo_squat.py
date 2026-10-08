from lookalike.detection import Detection
from lookalike.detectors.detector import Detector
from lookalike.detectors.similarity import damerau_levenshtein_distance
from lookalike.domain import Domain


class TyposquatDetector(Detector):
    """Detect registrable labels that differ from a brand by one edit.

    ``minimum_label _length`` is used to remove unecessary noise in detections 
    i.e. detecting bbq.com to be typosquatting bbc.co.uk
    """

    def __init__(self, minimum_label_length: int = 3) -> None:
        if minimum_label_length < 1:
            raise ValueError("minimum_label_length must be positive")

        self._minimum_label_length = minimum_label_length

    def detect(
        self,
        candidate: Domain,
        brand: Domain,
    ) -> Detection | None:
        """Return a detection when the labels have distance exactly one."""
        if len(brand.label) < self._minimum_label_length:
            return None

        distance = damerau_levenshtein_distance(
            candidate.label,
            brand.label,
        )

        if distance != 1:
            return None

        return Detection(detector="typosquat")
