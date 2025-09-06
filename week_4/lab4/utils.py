"""Lab4 utils: diff normalization and comparison."""
from typing import List


def normalize_diff_lines(diff_text: str) -> List[str]:
    """Normalize a unified diff/text by:
    - splitting into lines
    - removing diff metadata lines (---, +++, @@)
    - stripping leading/trailing whitespace on each line
    - removing blank lines

    Returns the list of normalized lines in order.
    """
    if diff_text is None:
        return []
    lines = []
    for raw in diff_text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith('---') or s.startswith('+++') or s.startswith('@@'):
            continue
        lines.append(s)
    return lines


def diffs_equal_sequence(diff_a: str, diff_b: str) -> bool:
    """Compare two diffs for exact equality after normalization (order matters)."""
    a = normalize_diff_lines(diff_a)
    b = normalize_diff_lines(diff_b)
    return a == b


def diffs_equal_set(diff_a: str, diff_b: str) -> bool:
    """Compare two diffs ignoring order of lines."""
    a = normalize_diff_lines(diff_a)
    b = normalize_diff_lines(diff_b)
    return set(a) == set(b)
