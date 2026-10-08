from lookalike.detection import Detection
from lookalike.detectors.detector import Detector
from lookalike.detectors.similarity import damerau_levenshtein_distance
from lookalike.domain import Domain


class TyposquatDetector(Detector):
    """Detect registrable labels that differ from a brand by one edit.

    Only the registrable label is compared. Subdomain labels are deliberately
    ignored: they are usually short common words (``beta``, ``mail``, ``docs``),
    so comparing them produces many false positives, e.g. ``beta.example.com``
    against ``meta.com``.

    ``minimum_label_length`` is used to remove unnecessary noise in detections
    i.e. detecting bbq.com to be typosquatting bbc.co.uk
    """

    def __init__(self, minimum_label_length: int = 4) -> None:
        if minimum_label_length < 1:
            raise ValueError("minimum_label_length must be positive")

        self._minimum_label_length = minimum_label_length

    def detect(
        self,
        candidate: Domain,
        brand: Domain,
    ) -> Detection | None:
        """Return a detection when the registrable label is one edit from the brand."""
        if len(brand.label) < self._minimum_label_length:
            return None

        if self._is_typosquat_label(candidate.label, brand.label):
            return Detection(detector="typosquat")

        return None

    @staticmethod
    def _is_typosquat_label(
        candidate_label: str,
        brand_label: str,
    ) -> bool:
        """Return whether a candidate label is one edit from the brand label."""
        return (
            damerau_levenshtein_distance(
                candidate_label,
                brand_label,
            )
            == 1
        )
