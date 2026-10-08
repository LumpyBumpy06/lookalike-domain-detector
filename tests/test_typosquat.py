import pytest

from lookalike.detection import Detection
from lookalike.detectors.typosquat import TyposquatDetector
from lookalike.domain import Domain


@pytest.fixture
def detector() -> TyposquatDetector:
    return TyposquatDetector()


def make_domain(label: str, suffix: str = "com") -> Domain:
    return Domain(
        full=f"{label}.{suffix}",
        subdomains=(),
        label=label,
        suffix=suffix,
    )


@pytest.mark.parametrize(
    ("candidate_label", "brand_label"),
    [
        pytest.param("paypa1", "paypal", id="substitution"),
        pytest.param("paypall", "paypal", id="insertion"),
        pytest.param("paypa", "paypal", id="deletion"),
        pytest.param("payapl", "paypal", id="adjacent-transposition"),
    ],
)
def test_detects_label_one_edit_away(
    detector: TyposquatDetector,
    candidate_label: str,
    brand_label: str,
) -> None:
    candidate = make_domain(candidate_label)
    brand = make_domain(brand_label)

    assert detector.detect(candidate, brand) == Detection(
        detector="typosquat",
    )


@pytest.mark.parametrize(
    ("candidate", "brand"),
    [
        pytest.param(
            make_domain("paypal"),
            make_domain("paypal"),
            id="identical-label",
        ),
        pytest.param(
            Domain(
                full="login.paypal.com",
                subdomains=("login",),
                label="paypal",
                suffix="com",
            ),
            make_domain("paypal"),
            id="same-label-in-subdomain",
        ),
        pytest.param(
            make_domain("paypal", suffix="net"),
            make_domain("paypal"),
            id="different-suffix",
        ),
        pytest.param(
            make_domain("paypa12"),
            make_domain("paypal"),
            id="distance-greater-than-one",
        ),
    ],
)
def test_does_not_detect_non_typosquat(
    detector: TyposquatDetector,
    candidate: Domain,
    brand: Domain,
) -> None:
    assert detector.detect(candidate, brand) is None
