from collections.abc import Iterable
from dataclasses import dataclass

from lookalike.domain import Domain, InvalidDomainError, parse_domain


@dataclass(frozen=True)
class InputParseResult:
    """The valid domains found in the given input lines and the number of skipped lines."""

    domains: tuple[Domain, ...]
    skipped: int


def parse_domain_lines(lines: Iterable[str]) -> InputParseResult:
    """Parse input lines into unique, normalised domains.

    Blank lines and comments are ignored. Invalid domain lines are skipped
    and counted. Duplicate domains are removed after normalisation while
    preserving the order of their first occurrence.
    """
    domains: list[Domain] = []
    seen: set[str] = set()
    skipped = 0

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        try:
            domain = parse_domain(line)
        except InvalidDomainError:
            skipped += 1
            continue

        if domain.full in seen:
            continue

        seen.add(domain.full)
        domains.append(domain)

    return InputParseResult(
        domains=tuple(domains),
        skipped=skipped,
    )
