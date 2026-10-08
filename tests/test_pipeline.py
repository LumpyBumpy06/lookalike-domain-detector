from collections.abc import Iterable
from unittest.mock import Mock, call

import pytest

from lookalike.detection import Detection, Finding
from lookalike.detectors.detector import Detector
from lookalike.domain import Domain, parse_domain
from lookalike.pipeline import run_pipeline


def make_detector(detection: Detection | None = None) -> Mock:
    detector = Mock(spec=Detector)
    detector.detect.return_value = detection
    return detector


@pytest.fixture
def paypal() -> Domain:
    return parse_domain("paypal.com")


@pytest.fixture
def example() -> Domain:
    return parse_domain("example.org")


def test_pipeline_calls_every_detector_for_every_candidate_brand_pair(
    paypal: Domain,
    example: Domain,
) -> None:
    candidates = (
        parse_domain("paypa1.com"),
        parse_domain("example.net"),
    )
    brands = (paypal, example)

    first = make_detector()
    second = make_detector()
    detectors = (first, second)

    run_pipeline(candidates, brands, detectors)

    expected_pairs = [
        (candidates[0], brands[0]),
        (candidates[0], brands[1]),
        (candidates[1], brands[0]),
        (candidates[1], brands[1]),
    ]

    expected_calls = [call(candidate, brand) for candidate, brand in expected_pairs]

    for detector in detectors:
        assert detector.detect.call_args_list == expected_calls


@pytest.mark.parametrize(
    "candidate",
    [
        pytest.param("paypal.com", id="brand-domain"),
        pytest.param("login.paypal.com", id="brand-subdomain"),
        pytest.param("a.b.paypal.com", id="nested-brand-subdomain"),
    ],
)
def test_pipeline_does_not_call_detectors_for_brand_domain_or_subdomain(
    paypal: Domain,
    candidate: str,
) -> None:
    candidate_domain = parse_domain(candidate)
    detector = make_detector()

    findings = run_pipeline(
        candidates=(candidate_domain,),
        brands=(paypal,),
        detectors=(detector,),
    )

    detector.detect.assert_not_called()
    assert findings == ()


def test_pipeline_checks_brand_subdomain_against_other_brands(
    paypal: Domain,
    example: Domain,
) -> None:
    candidate = parse_domain("login.paypal.com")
    detector = make_detector(
        Detection(detector="test"),
    )

    findings = run_pipeline(
        candidates=(candidate,),
        brands=(paypal, example),
        detectors=(detector,),
    )

    detector.detect.assert_called_once_with(candidate, example)

    assert findings == (
        Finding(
            candidate=candidate,
            brand=example,
            detections=(Detection(detector="test"),),
        ),
    )


def test_pipeline_merges_multiple_detector_results_into_one_finding(
    paypal: Domain,
) -> None:
    candidate = parse_domain("paypal-secure.com")

    first = make_detector(
        Detection(detector="brand-token"),
    )
    second = make_detector(
        Detection(detector="another"),
    )

    findings = run_pipeline(
        candidates=(candidate,),
        brands=(paypal,),
        detectors=(first, second),
    )

    assert findings == (
        Finding(
            candidate=candidate,
            brand=paypal,
            detections=(
                Detection(detector="brand-token"),
                Detection(detector="another"),
            ),
        ),
    )


def test_pipeline_does_not_create_finding_when_no_detector_fires(
    paypal: Domain,
) -> None:
    candidate = parse_domain("example.net")
    detector = make_detector()

    findings = run_pipeline(
        candidates=(candidate,),
        brands=(paypal,),
        detectors=(detector,),
    )

    detector.detect.assert_called_once_with(candidate, paypal)
    assert findings == ()


def test_pipeline_preserves_detector_order_in_finding(
    paypal: Domain,
) -> None:
    candidate = parse_domain("paypal-secure.com")

    first = make_detector(Detection(detector="first"))
    second = make_detector(Detection(detector="second"))
    third = make_detector(Detection(detector="third"))

    findings = run_pipeline(
        candidates=(candidate,),
        brands=(paypal,),
        detectors=(first, second, third),
    )

    assert findings[0].detections == (
        Detection(detector="first"),
        Detection(detector="second"),
        Detection(detector="third"),
    )


def test_pipeline_returns_findings_in_deterministic_order() -> None:
    candidates = (
        parse_domain("zebra-paypal.com"),
        parse_domain("paypal-secure.com"),
        parse_domain("paypa1.com"),
    )
    brands = (
        parse_domain("paypal.com"),
        parse_domain("example.com"),
    )

    detector = make_detector(
        Detection(detector="test"),
    )

    findings = run_pipeline(
        candidates=candidates,
        brands=brands,
        detectors=(detector,),
    )

    assert [(finding.candidate.full, finding.brand.full) for finding in findings] == [
        ("paypa1.com", "example.com"),
        ("paypa1.com", "paypal.com"),
        ("paypal-secure.com", "example.com"),
        ("paypal-secure.com", "paypal.com"),
        ("zebra-paypal.com", "example.com"),
        ("zebra-paypal.com", "paypal.com"),
    ]


def test_pipeline_accepts_iterables() -> None:
    candidate = parse_domain("paypa1.com")
    brand = parse_domain("paypal.com")
    detector = make_detector(
        Detection(detector="test"),
    )

    candidates: Iterable[Domain] = (domain for domain in (candidate,))
    brands: Iterable[Domain] = (domain for domain in (brand,))
    detectors: Iterable[Detector] = (item for item in (detector,))

    findings = run_pipeline(candidates, brands, detectors)

    assert findings == (
        Finding(
            candidate=candidate,
            brand=brand,
            detections=(Detection(detector="test"),),
        ),
    )
