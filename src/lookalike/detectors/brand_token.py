from lookalike.detection import Detection
from lookalike.detectors.detector import Detector
from lookalike.domain import Domain


class BrandTokenDetector(Detector):
    """Detect a protected brand used as a distinct domain token."""

    def detect(
        self,
        candidate: Domain,
        brand: Domain,
    ) -> Detection | None:
        """Return a detection when the brand appears in a suspicious position."""
        if candidate.same_registrable_as(brand):
            return None

        if self._brand_is_token(candidate.label, brand.label):
            return Detection(detector="brand_token")

        if self._brand_appears_in_subdomains(candidate, brand):
            return Detection(detector="brand_token")

        return None

    @staticmethod
    def _brand_is_token(candidate_label: str, brand_label: str) -> bool:
        """Return whether a label contains the brand as a hyphen delimited token."""
        return (
            candidate_label.startswith(f"{brand_label}-")
            or candidate_label.endswith(f"-{brand_label}")
            or f"-{brand_label}-" in candidate_label
        )

    @staticmethod
    def _brand_appears_in_subdomains(
        candidate: Domain,
        brand: Domain,
    ) -> bool:
        """Return whether the brand appears in the candidate's subdomains."""
        if any(BrandTokenDetector._brand_is_subdomain_token(label, brand.label) for label in candidate.subdomains):
            return True

        brand_labels = tuple(brand.full.split("."))
        subdomains = candidate.subdomains
        window_size = len(brand_labels)

        return any(
            subdomains[index : index + window_size] == brand_labels
            for index in range(len(subdomains) - window_size + 1)
        )

    @staticmethod
    def _brand_is_subdomain_token(
        candidate_label: str,
        brand_label: str,
    ) -> bool:
        """Return whether a subdomain label is the brand or contains it as a token."""
        return (
            candidate_label == brand_label
            or candidate_label.startswith(f"{brand_label}-")
            or candidate_label.endswith(f"-{brand_label}")
            or f"-{brand_label}-" in candidate_label
        )
