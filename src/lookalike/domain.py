from dataclasses import dataclass

# SinglePart ones are already handled e.g. .com, .uk
_MULTIPART_SUFFIXES = frozenset(
    {
        "co.uk",
        "org.uk",
        "ac.uk",
        "com.au",
        "net.au",
        "org.au",
        "co.jp",
    }
)

# Currently supporting only these basic ASCII characters
_VALID_LABEL_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")

MAX_LABEL_LENGTH = 63
MAX_DOMAIN_NAME_LENGTH = 253


class InvalidDomainError(ValueError):
    """Raised when a domain name is invalid."""


@dataclass(frozen=True, slots=True)
class Domain:
    """A parsed, normalised domain, e.g. ``login.paypal.co.uk``.

    ``full`` is the full lowercase name, ``subdomains`` the labels left of the
    registrable label (``("login",)``), ``label`` the registrable label
    (``"paypal"``) and ``suffix`` the public suffix (``"co.uk"``).
    """

    full: str
    subdomains: tuple[str, ...]
    label: str
    suffix: str


def parse_domain(raw: str) -> Domain:
    """Parse ``raw`` into a ``Domain``.

    Raises:
        InvalidDomainError: If the input is empty or is not a valid domain,
            including names with empty or over-long labels, invalid
            characters, or a total length exceeding the supported limit.
    """

    value = raw.strip().lower()

    if value.endswith("."):
        value = value[:-1]

    if not value:
        raise InvalidDomainError("domain is empty")

    if len(value) > MAX_DOMAIN_NAME_LENGTH:
        raise InvalidDomainError("domain name is too long")

    labels = value.split(".")

    if len(labels) <= 1:
        raise InvalidDomainError("domain must contain a suffix")

    for label in labels:
        _validate_label(label)

    suffix_length = _suffix_length(labels)
    registrable_index = len(labels) - suffix_length - 1

    if registrable_index < 0:
        raise InvalidDomainError("domain has no registrable label")

    suffix = ".".join(labels[-suffix_length:])
    label = labels[registrable_index]
    subdomains = tuple(labels[:registrable_index])

    return Domain(
        full=value,
        subdomains=subdomains,
        label=label,
        suffix=suffix,
    )


def _validate_label(label: str) -> None:
    """Validate one ASCII hostname label."""
    if not label:
        raise InvalidDomainError("domain contains an empty label")

    if len(label) > MAX_LABEL_LENGTH:
        raise InvalidDomainError("domain label is too long")

    if label[0] == "-" or label[-1] == "-":
        raise InvalidDomainError("domain labels cannot start or end with a hyphen")

    if not all(character in _VALID_LABEL_CHARACTERS for character in label):
        raise InvalidDomainError("domain label contains invalid characters")


def _suffix_length(labels: list[str]) -> int:
    """Return the number of labels belonging to the supported suffix."""
    if len(labels) >= 2 and ".".join(labels[-2:]) in _MULTIPART_SUFFIXES:
        return 2
    return 1
