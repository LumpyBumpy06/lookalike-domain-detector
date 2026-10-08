import pytest

from lookalike.detectors.similarity import damerau_levenshtein_distance


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        pytest.param("", "", 0, id="both-empty"),
        pytest.param("", "a", 1, id="empty-first"),
        pytest.param("a", "", 1, id="empty-second"),
        pytest.param("cat", "cat", 0, id="identical"),
        pytest.param("cat", "cut", 1, id="substitution"),
        pytest.param("cat", "cats", 1, id="insertion"),
        pytest.param("cats", "cat", 1, id="deletion"),
        pytest.param("ab", "ba", 1, id="adjacent-transposition"),
        pytest.param("paypal", "paypa1", 1, id="paypal-substitution"),
    ],
)
def test_damerau_levenshtein_distance(
    first: str,
    second: str,
    expected: int,
) -> None:
    assert damerau_levenshtein_distance(first, second) == expected


@pytest.mark.parametrize(
    ("first", "second"),
    [
        pytest.param("paypal", "paypa1", id="paypal"),
        pytest.param("abc", "cba", id="reversed"),
        pytest.param("", "example", id="empty"),
        pytest.param("cat", "cats", id="different-length"),
    ],
)
def test_damerau_levenshtein_distance_is_symmetric(
    first: str,
    second: str,
) -> None:
    assert damerau_levenshtein_distance(first, second) == damerau_levenshtein_distance(second, first)
