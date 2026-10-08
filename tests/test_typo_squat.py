import pytest

from lookalike.detection import Detection
from lookalike.detectors.typo_squat import TyposquatDetector
from lookalike.domain import Domain


@pytest.fixture
def detector() -> TyposquatDetector:
    return TyposquatDetector()


def make_domain(
    label: str,
    suffix: str = "com",
    subdomains: tuple[str, ...] = (),
) -> Domain:
    parts = (*subdomains, f"{label}.{suffix}")
    return Domain(
        full=".".join(parts),
        subdomains=subdomains,
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
    ("subdomain", "brand_label"),
    [
        pytest.param("paypa1", "paypal", id="substitution"),
        pytest.param("paypall", "paypal", id="insertion"),
        pytest.param("paypa", "paypal", id="deletion"),
        pytest.param("payapl", "paypal", id="adjacent-transposition"),
    ],
)
def test_detects_subdomain_one_edit_away(
    detector: TyposquatDetector,
    subdomain: str,
    brand_label: str,
) -> None:
    candidate = make_domain(
        "evil",
        subdomains=(subdomain,),
    )
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
            id="identical-domain",
        ),
        pytest.param(
            make_domain(
                "paypal",
                subdomains=("login",),
            ),
            make_domain("paypal"),
            id="same-brand-in-subdomain",
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
        pytest.param(
            make_domain(
                "evil",
                subdomains=("paypa12",),
            ),
            make_domain("paypal"),
            id="subdomain-distance-greater-than-one",
        ),
    ],
)
def test_does_not_detect_non_typosquat(
    detector: TyposquatDetector,
    candidate: Domain,
    brand: Domain,
) -> None:
    assert detector.detect(candidate, brand) is None


@pytest.mark.parametrize(
    "brand_label",
    [
        pytest.param("bbc", id="three-character-brand"),
        pytest.param("abc", id="three-character-brand"),
    ],
)
def test_ignores_brands_shorter_than_default_minimum(
    detector: TyposquatDetector,
    brand_label: str,
) -> None:
    candidate = make_domain(f"{brand_label[:-1]}x")
    brand = make_domain(brand_label)

    assert detector.detect(candidate, brand) is None


def test_allows_custom_minimum_label_length() -> None:
    detector = TyposquatDetector(minimum_label_length=3)

    candidate = make_domain("bbq")
    brand = make_domain("bbc")

    assert detector.detect(candidate, brand) == Detection(
        detector="typosquat",
    )


def test_rejects_non_positive_minimum_label_length() -> None:
    with pytest.raises(
        ValueError,
        match="minimum_label_length must be positive",
    ):
        TyposquatDetector(minimum_label_length=0)
