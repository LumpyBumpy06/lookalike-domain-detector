def damerau_levenshtein_distance(first: str, second: str) -> int:
    """Return the Damerau-Levenshtein distance between two strings.

    The distance is the minimum number of single-character insertions,
    deletions, substitutions, or adjacent transpositions needed to transform
    one string into the other.
    """
    if first == second:
        return 0

    if not first:
        return len(second)

    if not second:
        return len(first)

    rows = len(first)
    columns = len(second)
    infinity = rows + columns

    distance = [[0] * (columns + 2) for _ in range(rows + 2)]

    distance[0][0] = infinity

    for row in range(rows + 1):
        distance[row + 1][0] = infinity
        distance[row + 1][1] = row

    for column in range(columns + 1):
        distance[0][column + 1] = infinity
        distance[1][column + 1] = column

    last_row: dict[str, int] = {}

    for row in range(1, rows + 1):
        last_matching_column = 0

        for column in range(1, columns + 1):
            matching_row = last_row.get(second[column - 1], 0)
            matching_column = last_matching_column

            cost = 1

            if first[row - 1] == second[column - 1]:
                cost = 0
                last_matching_column = column

            distance[row + 1][column + 1] = min(
                distance[row][column] + cost,
                distance[row + 1][column] + 1,
                distance[row][column + 1] + 1,
                (
                    distance[matching_row][matching_column]
                    + (row - matching_row - 1)
                    + 1
                    + (column - matching_column - 1)
                ),
            )

        last_row[first[row - 1]] = row

    return distance[rows + 1][columns + 1]
