from collections.abc import Iterator

import pytest

from lookalike.domain import Domain
from lookalike.inputs import parse_domain_lines


@pytest.mark.parametrize(
    ("lines", "expected_domains", "expected_skipped"),
    [
        pytest.param(
            [],
            (),
            0,
            id="empty-input",
        ),
        pytest.param(
            ["\n", "   \n", "\t\n"],
            (),
            0,
            id="blank-lines-ignored",
        ),
        pytest.param(
            [
                "# comment",
                " # indented comment",
                "\t# tabbed comment",
            ],
            (),
            0,
            id="comment-lines-ignored",
        ),
        pytest.param(
            [
                "paypal.com\n",
                "login.paypal.com\n",
            ],
            (
                Domain(
                    full="paypal.com",
                    subdomains=(),
                    label="paypal",
                    suffix="com",
                ),
                Domain(
                    full="login.paypal.com",
                    subdomains=("login",),
                    label="paypal",
                    suffix="com",
                ),
            ),
            0,
            id="valid-domains",
        ),
        pytest.param(
            [
                "paypal.com\n",
                "invalid\n",
                ".example.com\n",
                "example..com\n",
            ],
            (
                Domain(
                    full="paypal.com",
                    subdomains=(),
                    label="paypal",
                    suffix="com",
                ),
            ),
            3,
            id="invalid-domains-skipped-and-counted",
        ),
        pytest.param(
            [
                " PAYPAL.COM \n",
                "paypal.com\n",
                "PayPal.Com\n",
            ],
            (
                Domain(
                    full="paypal.com",
                    subdomains=(),
                    label="paypal",
                    suffix="com",
                ),
            ),
            0,
            id="duplicates-removed-after-normalisation",
        ),
    ],
)
def test_parse_domain_lines(
    lines: list[str],
    expected_domains: tuple[Domain, ...],
    expected_skipped: int,
) -> None:
    result = parse_domain_lines(lines)

    assert result.domains == expected_domains
    assert result.skipped == expected_skipped


def test_parse_domain_lines_deduplicates_without_reordering() -> None:
    lines = [
        "zebra.com\n",
        "apple.com\n",
        "ZEBRA.COM\n",
        "example.org\n",
        "APPLE.COM\n",
    ]

    result = parse_domain_lines(lines)

    assert result.domains == (
        Domain(
            full="zebra.com",
            subdomains=(),
            label="zebra",
            suffix="com",
        ),
        Domain(
            full="apple.com",
            subdomains=(),
            label="apple",
            suffix="com",
        ),
        Domain(
            full="example.org",
            subdomains=(),
            label="example",
            suffix="org",
        ),
    )
    assert result.skipped == 0


def test_parse_domain_lines_accepts_iterable_lines() -> None:
    def lines() -> Iterator[str]:
        yield "paypal.com\n"
        yield "example.org\n"

    result = parse_domain_lines(lines())

    assert result.domains == (
        Domain(
            full="paypal.com",
            subdomains=(),
            label="paypal",
            suffix="com",
        ),
        Domain(
            full="example.org",
            subdomains=(),
            label="example",
            suffix="org",
        ),
    )
    assert result.skipped == 0
