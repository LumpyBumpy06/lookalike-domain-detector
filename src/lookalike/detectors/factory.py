from lookalike.detectors.brand_token import BrandTokenDetector
from lookalike.detectors.detector import Detector
from lookalike.detectors.suffix_swap import SuffixSwapDetector
from lookalike.detectors.typo_squat import TyposquatDetector


def default_detectors() -> tuple[Detector, ...]:
    """Build the standard set of lookalike detectors."""
    return (
        BrandTokenDetector(),
        SuffixSwapDetector(),
        TyposquatDetector(),
    )
