import pytest

from lookalike.detection import Detection
from lookalike.detectors.brand_token import BrandTokenDetector
from lookalike.domain import Domain, parse_domain


@pytest.fixture
def detector() -> BrandTokenDetector:
    return BrandTokenDetector()


@pytest.fixture
def paypal() -> Domain:
    return parse_domain("paypal.com")


@pytest.mark.parametrize(
    "candidate",
    [
        pytest.param(
            "paypal-secure.com",
            id="token-at-start",
        ),
        pytest.param(
            "secure-paypal.com",
            id="token-at-end",
        ),
        pytest.param(
            "secure-paypal-login.com",
            id="token-in-middle",
        ),
    ],
)
def test_detects_brand_as_hyphen_separated_token(
    detector: BrandTokenDetector,
    paypal: Domain,
    candidate: str,
) -> None:
    assert detector.detect(
        parse_domain(candidate),
        paypal,
    ) == Detection(detector="brand_token")


def test_detects_hyphenated_brand_as_token(
    detector: BrandTokenDetector,
) -> None:
    brand = parse_domain("pay-pal.com")
    candidate = parse_domain("secure-pay-pal-login.com")

    assert detector.detect(candidate, brand) == Detection(
        detector="brand_token",
    )


@pytest.mark.parametrize(
    "candidate",
    [
        pytest.param(
            "paypal.evil.com",
            id="brand-as-subdomain",
        ),
        pytest.param(
            "login-paypal.evil.com",
            id="hyphenated-brand-as-subdomain",
        ),
        pytest.param(
            "paypal-secure-login.evil.com",
            id="brand-token-in-subdomain",
        ),
        pytest.param(
            "foo.paypal.evil.com",
            id="brand-subdomain-with-prefix",
        ),
    ],
)
def test_detects_brand_token_in_subdomain(
    detector: BrandTokenDetector,
    paypal: Domain,
    candidate: str,
) -> None:
    assert detector.detect(
        parse_domain(candidate),
        paypal,
    ) == Detection(detector="brand_token")


@pytest.mark.parametrize(
    "candidate",
    [
        pytest.param(
            "paypal.com.account-verify.net",
            id="brand-domain-as-subdomain-sequence",
        ),
        pytest.param(
            "foo.paypal.com.account-verify.net",
            id="brand-domain-with-prefix",
        ),
    ],
)
def test_detects_brand_domain_in_subdomain_sequence(
    detector: BrandTokenDetector,
    paypal: Domain,
    candidate: str,
) -> None:
    assert detector.detect(
        parse_domain(candidate),
        paypal,
    ) == Detection(detector="brand_token")


@pytest.mark.parametrize(
    "candidate",
    [
        pytest.param(
            "paypalsecure.com",
            id="brand-is-not-a-whole-token",
        ),
        pytest.param(
            "securepay-pal.com",
            id="brand-is-not-a-whole-token",
        ),
        pytest.param(
            "paypa1.evil.com",
            id="typosquat-is-not-brand-token",
        ),
        pytest.param(
            "paypal.com",
            id="brand-domain-itself",
        ),
        pytest.param(
            "login.paypal.com",
            id="same-registrable-domain",
        ),
        pytest.param(
            "paypal.net",
            id="different-suffix",
        ),
        pytest.param(
            "notpaypal.com.evil.net",
            id="brand-domain-is-not-a-label-sequence",
        ),
        pytest.param(
            "paypall.com.account-verify.net",
            id="similar-domain-not-brand-domain",
        ),
    ],
)
def test_does_not_detect_non_brand_token(
    detector: BrandTokenDetector,
    paypal: Domain,
    candidate: str,
) -> None:
    assert detector.detect(
        parse_domain(candidate),
        paypal,
    ) is None
