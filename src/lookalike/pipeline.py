from collections.abc import Iterable

from lookalike.detection import Detection, Finding
from lookalike.detectors.detector import Detector
from lookalike.domain import Domain


def run_pipeline(
    candidates: Iterable[Domain],
    brands: Iterable[Domain],
    detectors: Iterable[Detector],
) -> tuple[Finding, ...]:
    """Run every detector against every eligible candidate and brand pair."""
    candidate_domains = tuple(candidates)
    brand_domains = tuple(brands)
    detector_list = tuple(detectors)

    findings: list[Finding] = []

    for candidate in candidate_domains:
        for brand in brand_domains:
            if candidate.same_registrable_as(brand):
                continue

            detections: list[Detection] = []

            for detector in detector_list:
                detection = detector.detect(candidate, brand)

                if detection is not None:
                    detections.append(detection)

            if detections:
                findings.append(
                    Finding(
                        candidate=candidate,
                        brand=brand,
                        detections=tuple(detections),
                    )
                )

    findings.sort(
        key=lambda finding: (
            finding.candidate.full,
            finding.brand.full,
        )
    )

    return tuple(findings)
