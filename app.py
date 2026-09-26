"""Binary search over a sorted sequence.

The module exposes a plain index lookup (:func:`binary_search`) plus
lower/upper bound helpers (:func:`lower_bound`, :func:`upper_bound`) that make
it easy to reason about duplicates and insertion points.

Every function here assumes ``arr`` is sorted in non-decreasing order. That is
the one precondition binary search cannot check for cheaply, so it is verified
once up front in the public helpers behind an ``ensure_sorted`` flag.

The command line interface (:func:`main`) does not reorder the input. It
validates the ordering precondition through ``ensure_sorted=True`` and reports
indices into the sequence exactly as the caller supplied it.
"""

from __future__ import annotations

import sys
from typing import List, Optional, Sequence

__all__ = [
    "binary_search",
    "lower_bound",
    "upper_bound",
    "is_sorted",
    "main",
]


def is_sorted(arr: Sequence) -> bool:
    """Return ``True`` if ``arr`` is sorted in non-decreasing order."""
    return all(a <= b for a, b in zip(arr, arr[1:]))


def _check_sorted(arr: Sequence) -> None:
    """Raise :class:`ValueError` when ``arr`` is not sorted ascending."""
    if not is_sorted(arr):
        raise ValueError(
            "binary search requires a sequence sorted in non-decreasing "
            "order; call sorted(...) on the input first"
        )


def lower_bound(arr: Sequence, target, *, ensure_sorted: bool = False) -> int:
    """Return the index of the first element in ``arr`` that is ``>= target``.

    The result equals ``len(arr)`` when every element is smaller than
    ``target``, which makes this safe to use as an insertion point.
    """
    if ensure_sorted:
        _check_sorted(arr)

    lo, hi = 0, len(arr)
    while lo < hi:
        # Written as `lo + (hi - lo) // 2` rather than `(lo + hi) // 2`.
        # Python integers do not overflow, but the form keeps the invariant
        # obvious and ports cleanly to languages where it matters.
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(arr: Sequence, target, *, ensure_sorted: bool = False) -> int:
    """Return the index of the first element in ``arr`` that is ``> target``."""
    if ensure_sorted:
        _check_sorted(arr)

    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def binary_search(
    arr: Sequence,
    target,
    *,
    ensure_sorted: bool = False,
) -> int:
    """Return the index of ``target`` in ``arr``, or ``-1`` if absent.

    Args:
        arr: Sequence sorted in non-decreasing order.
        target: Value to look for.
        ensure_sorted: Validate the ordering precondition and raise
            :class:`ValueError` instead of silently returning a wrong answer.
            Off by default because the check is ``O(n)`` and would dominate the
            ``O(log n)`` search.

    Returns:
        Any index holding ``target`` (not guaranteed to be the first one), or
        ``-1`` when ``target`` is not present. Use :func:`lower_bound` when the
        leftmost match matters.

    Examples:
        >>> binary_search([1, 3, 5, 7, 9], 7)
        3
        >>> binary_search([1, 3, 5, 7, 9], 4)
        -1
        >>> binary_search([], 1)
        -1
    """
    if ensure_sorted:
        _check_sorted(arr)

    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        value = arr[mid]
        if value == target:
            return mid
        if value < target:
            # Target can only live to the right of mid.
            lo = mid + 1
        else:
            # Target can only live to the left of mid.
            hi = mid - 1
    return -1


def _parse_numbers(raw: str) -> List[int]:
    """Parse ``"1,2,3"`` or ``"1 2 3"`` into a list of ints."""
    parts = raw.replace(",", " ").split()
    if not parts:
        raise ValueError("expected at least one number")
    try:
        return [int(part) for part in parts]
    except ValueError as exc:  # pragma: no cover - exercised via CLI only
        raise ValueError(f"could not parse numbers from {raw!r}") from exc


def main(argv: Optional[List[str]] = None) -> int:
    """Command line entry point: ``python app.py "1 3 5 7 9" 7``.

    The list must already be sorted in non-decreasing order. Ordering is
    validated through the public ``ensure_sorted`` flag rather than by sorting
    the input, so reported indices always refer to the caller's own sequence.
    """
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print(
            'usage: python app.py "<space or comma separated sorted list>" <target>',
            file=sys.stderr,
        )
        return 2

    try:
        arr = _parse_numbers(args[0])
        target = int(args[1])
        index = binary_search(arr, target, ensure_sorted=True)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if index == -1:
        print(f"{target} not found in {arr}")
        return 1

    left = lower_bound(arr, target)
    right = upper_bound(arr, target) - 1
    if left == right:
        print(f"{target} found at index {index}")
    else:
        print(f"{target} found at indices {left}..{right} (e.g. {index})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
