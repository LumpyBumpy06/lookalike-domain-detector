"""Placeholder so the toolchain runs end to end from the first commit.

Keep it or delete it once real tests cover the package. Real tests go in one file
per source module (``test_domain.py`` for ``domain.py`` and so on).
"""

import lookalike


def test_package_has_version() -> None:
    assert lookalike.__version__
