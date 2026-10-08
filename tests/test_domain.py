import pytest

from lookalike.domain import Domain, InvalidDomainError, parse_domain

MAX_LABEL_LENGTH = 63
MAX_DOMAIN_NAME_LENGTH = 253


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(
            "paypal.com",
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="simple-domain",
        ),
        pytest.param(
            "login.paypal.com",
            Domain(
                full="login.paypal.com",
                subdomains=("login",),
                label="paypal",
                suffix="com",
            ),
            id="single-subdomain",
        ),
        pytest.param(
            "a.b.example.com",
            Domain(
                full="a.b.example.com",
                subdomains=("a", "b"),
                label="example",
                suffix="com",
            ),
            id="multiple-subdomains",
        ),
        pytest.param(
            "login.paypal.co.uk",
            Domain(
                full="login.paypal.co.uk",
                subdomains=("login",),
                label="paypal",
                suffix="co.uk",
            ),
            id="co-uk-multipart-suffix",
        ),
        pytest.param(
            "example.org.uk",
            Domain(
                full="example.org.uk",
                subdomains=(),
                label="example",
                suffix="org.uk",
            ),
            id="org-uk-multipart-suffix",
        ),
        pytest.param(
            "example.ac.uk",
            Domain(
                full="example.ac.uk",
                subdomains=(),
                label="example",
                suffix="ac.uk",
            ),
            id="ac-uk-multipart-suffix",
        ),
        pytest.param(
            "example.com.au",
            Domain(
                full="example.com.au",
                subdomains=(),
                label="example",
                suffix="com.au",
            ),
            id="com-au-multipart-suffix",
        ),
        pytest.param(
            "example.net.au",
            Domain(
                full="example.net.au",
                subdomains=(),
                label="example",
                suffix="net.au",
            ),
            id="net-au-multipart-suffix",
        ),
        pytest.param(
            "example.org.au",
            Domain(
                full="example.org.au",
                subdomains=(),
                label="example",
                suffix="org.au",
            ),
            id="org-au-multipart-suffix",
        ),
        pytest.param(
            "example.co.jp",
            Domain(
                full="example.co.jp",
                subdomains=(),
                label="example",
                suffix="co.jp",
            ),
            id="co-jp-multipart-suffix",
        ),
        pytest.param(
            "123.example.com",
            Domain(
                full="123.example.com",
                subdomains=("123",),
                label="example",
                suffix="com",
            ),
            id="numeric-subdomain",
        ),
        pytest.param(
            "123.com",
            Domain(
                full="123.com",
                subdomains=(),
                label="123",
                suffix="com",
            ),
            id="numeric-registrable-label",
        ),
        pytest.param(
            "foo-bar.example.com",
            Domain(
                full="foo-bar.example.com",
                subdomains=("foo-bar",),
                label="example",
                suffix="com",
            ),
            id="hyphenated-subdomain",
        ),
        pytest.param(
            "foo-bar.com",
            Domain(
                full="foo-bar.com",
                subdomains=(),
                label="foo-bar",
                suffix="com",
            ),
            id="hyphenated-registrable-label",
        ),
        pytest.param(
            "3foo-bar.example-123.com",
            Domain(
                full="3foo-bar.example-123.com",
                subdomains=("3foo-bar",),
                label="example-123",
                suffix="com",
            ),
            id="valid-digit-and-hyphen-labels",
        ),
    ],
)
def test_parse_domain_returns_expected_parts(
    raw: str,
    expected: Domain,
) -> None:
    assert parse_domain(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(
            " PAYPAL.COM ",
            Domain(
                full="paypal.com",
                subdomains=(),
                label="paypal",
                suffix="com",
            ),
            id="whitespace-and-uppercase",
        ),
        pytest.param(
            "  Login.PAYPAL.Co.Uk  ",
            Domain(
                full="login.paypal.co.uk",
                subdomains=("login",),
                label="paypal",
                suffix="co.uk",
            ),
            id="mixed-case-and-whitespace",
        ),
        pytest.param(
            "example.com.",
            Domain(
                full="example.com",
                subdomains=(),
                label="example",
                suffix="com",
            ),
            id="trailing-root-dot",
        ),
        pytest.param(
            "  EXAMPLE.COM.  ",
            Domain(
                full="example.com",
                subdomains=(),
                label="example",
                suffix="com",
            ),
            id="whitespace-case-and-trailing-root-dot",
        ),
    ],
)
def test_parse_domain_normalises_input(
    raw: str,
    expected: Domain,
) -> None:
    assert parse_domain(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace-only"),
        pytest.param("example", id="no-dot"),
        pytest.param(".", id="root-only"),
    ],
)
def test_parse_domain_rejects_invalid_basic_input(raw: str) -> None:
    with pytest.raises(InvalidDomainError):
        parse_domain(raw)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(".example.com", id="leading-empty-label"),
        pytest.param("example..com", id="empty-middle-label"),
        pytest.param("foo..example.com", id="empty-subdomain-label"),
    ],
)
def test_parse_domain_rejects_empty_labels(raw: str) -> None:
    with pytest.raises(InvalidDomainError):
        parse_domain(raw)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("-example.com", id="leading-hyphen"),
        pytest.param("example-.com", id="trailing-hyphen"),
        pytest.param("foo.-example.com", id="subdomain-leading-hyphen"),
        pytest.param(
            "foo.example-.com",
            id="registrable-label-trailing-hyphen",
        ),
        pytest.param("exa_mple.com", id="underscore"),
        pytest.param("exa%mple.com", id="percent-sign"),
        pytest.param("exa$mple.com", id="dollar-sign"),
        pytest.param("exa/mple.com", id="slash"),
        pytest.param("exa mple.com", id="embedded-space"),
        pytest.param("exämple.com", id="unicode-label"),
    ],
)
def test_parse_domain_rejects_invalid_label_syntax(raw: str) -> None:
    with pytest.raises(InvalidDomainError):
        parse_domain(raw)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(
            "a" * MAX_LABEL_LENGTH + ".com",
            id=f"{MAX_LABEL_LENGTH}-char-registrable-label",
        ),
        pytest.param(
            "a" * MAX_LABEL_LENGTH + ".example.com",
            id=f"{MAX_LABEL_LENGTH}-char-subdomain",
        ),
    ],
)
def test_parse_domain_accepts_labels_of_maximum_length(raw: str) -> None:
    parse_domain(raw)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(
            "a" * (MAX_LABEL_LENGTH + 1) + ".com",
            id=f"{MAX_LABEL_LENGTH + 1}-char-registrable-label",
        ),
        pytest.param(
            "a" * (MAX_LABEL_LENGTH + 1) + ".example.com",
            id=f"{MAX_LABEL_LENGTH + 1}-char-subdomain",
        ),
    ],
)
def test_parse_domain_rejects_labels_longer_than_maximum_length(
    raw: str,
) -> None:
    with pytest.raises(InvalidDomainError):
        parse_domain(raw)


def test_parse_domain_accepts_domain_at_maximum_length() -> None:
    remaining_label_length = MAX_DOMAIN_NAME_LENGTH - (MAX_LABEL_LENGTH * 3) - 4 - 1
    domain = (
        f"{'a' * MAX_LABEL_LENGTH}.{'b' * MAX_LABEL_LENGTH}.{'c' * MAX_LABEL_LENGTH}.{'d' * remaining_label_length}.x"
    )

    assert len(domain) == MAX_DOMAIN_NAME_LENGTH

    result = parse_domain(domain)

    assert result.full == domain


def test_parse_domain_rejects_domain_over_maximum_length() -> None:
    remaining_label_length = MAX_DOMAIN_NAME_LENGTH - (MAX_LABEL_LENGTH * 3) - 4 - 1
    domain = (
        f"{'a' * MAX_LABEL_LENGTH}."
        f"{'b' * MAX_LABEL_LENGTH}."
        f"{'c' * MAX_LABEL_LENGTH}."
        f"{'d' * (remaining_label_length + 1)}."
        "x"
    )

    assert len(domain) == MAX_DOMAIN_NAME_LENGTH + 1

    with pytest.raises(InvalidDomainError):
        parse_domain(domain)


@pytest.mark.parametrize(
    ("raw", "expected_suffix"),
    [
        pytest.param("example.com", "com", id="com"),
        pytest.param("example.uk", "uk", id="uk"),
        pytest.param("example.co.uk", "co.uk", id="co-uk"),
        pytest.param("example.org.uk", "org.uk", id="org-uk"),
        pytest.param("example.ac.uk", "ac.uk", id="ac-uk"),
        pytest.param("example.com.au", "com.au", id="com-au"),
        pytest.param("example.net.au", "net.au", id="net-au"),
        pytest.param("example.org.au", "org.au", id="org-au"),
        pytest.param("example.co.jp", "co.jp", id="co-jp"),
    ],
)
def test_parse_domain_identifies_supported_suffix(
    raw: str,
    expected_suffix: str,
) -> None:
    assert parse_domain(raw).suffix == expected_suffix


def test_parse_domain_treats_unsupported_public_suffix_as_single_label() -> None:
    result = parse_domain("example.co.nz")

    assert result == Domain(
        full="example.co.nz",
        subdomains=("example",),
        label="co",
        suffix="nz",
    )


def test_parse_domain_rejects_domain_without_registrable_label() -> None:
    with pytest.raises(InvalidDomainError):
        parse_domain("com")


def test_parse_domain_rejects_domain_without_registrable_label_for_multipart_suffix() -> None:
    with pytest.raises(InvalidDomainError):
        parse_domain("co.uk")


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        pytest.param(
            "paypal.com",
            "paypal.com",
            True,
            id="same-domain",
        ),
        pytest.param(
            "paypal.com",
            "login.paypal.com",
            True,
            id="domain-and-subdomain",
        ),
        pytest.param(
            "login.paypal.com",
            "foo.login.paypal.com",
            True,
            id="different-subdomains",
        ),
        pytest.param(
            "paypal.com",
            "paypal.net",
            False,
            id="different-suffix",
        ),
        pytest.param(
            "paypal.com",
            "example.com",
            False,
            id="different-label",
        ),
    ],
)
def test_same_registrable_as(
    first: str,
    second: str,
    expected: bool,
) -> None:
    assert parse_domain(first).same_registrable_as(parse_domain(second)) is expected
