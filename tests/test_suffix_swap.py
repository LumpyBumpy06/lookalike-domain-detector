import pytest

from lookalike.detection import Detection
from lookalike.detectors.suffix_swap import SuffixSwapDetector
from lookalike.domain import Domain


@pytest.fixture
def detector() -> SuffixSwapDetector:
    return SuffixSwapDetector()


@pytest.mark.parametrize(
    ("candidate", "brand"),
    [
        pytest.param(
            Domain(
                full="paypal.net",
                subdomains=(),
                label="paypal",
                suffix="net",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="different-single-label-suffix",
        ),
        pytest.param(
            Domain(
                full="paypal.co.uk",
                subdomains=(),
                label="paypal",
                suffix="co.uk",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="different-multipart-suffix",
        ),
        pytest.param(
            Domain(
                full="login.paypal.net",
                subdomains=("login",),
                label="paypal",
                suffix="net",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="same-label-different-suffix-with-subdomain",
        ),
    ],
)
def test_detects_same_label_with_different_suffix(
    detector: SuffixSwapDetector,
    candidate: Domain,
    brand: Domain,
) -> None:
    assert detector.detect(candidate, brand) == Detection(
        detector="suffix_swap",
    )


@pytest.mark.parametrize(
    ("candidate", "brand"),
    [
        pytest.param(
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="same-label-and-suffix",
        ),
        pytest.param(
            Domain(
                full="login.paypal.com",
                subdomains=("login",),
                label="paypal",
                suffix="com",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="same-label-and-suffix-with-subdomain",
        ),
        pytest.param(
            Domain(
                full="paypa1.com",
                subdomains=(),
                label="paypa1",
                suffix="com",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="different-label",
        ),
        pytest.param(
            Domain(
                full="example.net",
                subdomains=(),
                label="example",
                suffix="net",
            ),
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="different-label-and-suffix",
        ),
    ],
)
def test_does_not_detect_non_suffix_swap(
    detector: SuffixSwapDetector,
    candidate: Domain,
    brand: Domain,
) -> None:
    assert detector.detect(candidate, brand) is None
