"""Tests for app.py.

Run with either:
    python -m unittest -v test_app
    python -m pytest -v
"""

import io
import random
import unittest
from contextlib import redirect_stderr, redirect_stdout

from app import binary_search, is_sorted, lower_bound, main, upper_bound


class TestIsSorted(unittest.TestCase):
    def test_classifies_sorted_and_unsorted(self):
        self.assertTrue(is_sorted([]))
        self.assertTrue(is_sorted([5]))
        self.assertTrue(is_sorted([1, 2, 2, 3]))
        self.assertFalse(is_sorted([2, 1]))
        self.assertFalse(is_sorted([1, 3, 2]))


class TestBinarySearch(unittest.TestCase):
    def test_finds_every_element(self):
        arr = [-10, -3, 0, 1, 4, 7, 8, 99]
        for expected, value in enumerate(arr):
            self.assertEqual(binary_search(arr, value), expected, f"for {value}")

    def test_missing_values_return_minus_one(self):
        arr = [1, 4, 7, 9]
        for value in (-100, 0, 2, 3, 5, 6, 8, 10, 100):
            self.assertEqual(binary_search(arr, value), -1, f"for {value}")

    def test_empty_and_singleton(self):
        self.assertEqual(binary_search([], 1), -1)
        self.assertEqual(binary_search([1], 1), 0)
        self.assertEqual(binary_search([1], 2), -1)

    def test_boundaries(self):
        arr = list(range(0, 1000, 5))
        self.assertEqual(binary_search(arr, arr[0]), 0)
        self.assertEqual(binary_search(arr, arr[-1]), len(arr) - 1)

    def test_duplicates_return_a_real_index(self):
        arr = [2, 2, 2, 2]
        index = binary_search(arr, 2)
        self.assertGreaterEqual(index, 0)
        self.assertEqual(arr[index], 2)

    def test_ensure_sorted_rejects_unsorted_input(self):
        with self.assertRaises(ValueError):
            binary_search([3, 1, 2], 3, ensure_sorted=True)
        # A valid lookup is still found when the guard is asked for.
        self.assertEqual(binary_search([1, 2, 3], 3, ensure_sorted=True), 2)

    def test_matches_bisect_on_random_inputs(self):
        """Cross-check presence and bounds against the stdlib reference."""
        import bisect

        rng = random.Random(20260926)
        for _ in range(500):
            arr = sorted(rng.randint(-50, 50) for _ in range(rng.randint(0, 40)))
            target = rng.randint(-55, 55)

            left = bisect.bisect_left(arr, target)
            present = left < len(arr) and arr[left] == target

            index = binary_search(arr, target)
            if present:
                self.assertGreaterEqual(index, 0, f"{target} in {arr}")
                self.assertEqual(arr[index], target)
            else:
                self.assertEqual(index, -1, f"{target} in {arr}")

            self.assertEqual(lower_bound(arr, target), left, f"lower_bound {target} in {arr}")
            self.assertEqual(upper_bound(arr, target), bisect.bisect_right(arr, target), f"upper_bound {target} in {arr}")


class TestCli(unittest.TestCase):
    def _run(self, args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(args)
        return code, out.getvalue(), err.getvalue()

    def test_hit_exit_code(self):
        self.assertEqual(main(["1 3 5 7 9", "7"]), 0)

    def test_miss_exit_code(self):
        self.assertEqual(main(["1 3 5 7 9", "4"]), 1)

    def test_accepts_comma_separated_sorted_input(self):
        self.assertEqual(main(["1,3,5,7,9", "5"]), 0)

    def test_unsorted_input_is_rejected_not_sorted(self):
        """Issues #3 and #5: the CLI must honour the sorting precondition."""
        code, _, err = self._run(["9,3,1,7,5", "5"])
        self.assertEqual(code, 2)
        self.assertIn("sorted", err.lower())

    def test_index_refers_to_the_original_input(self):
        """Issue #4: indices must refer to the caller's sequence."""
        code, out, _ = self._run(["5 3 9 1", "3"])
        self.assertEqual(code, 2)
        self.assertNotIn("found at", out)

    def test_index_of_first_element_is_zero(self):
        code, out, _ = self._run(["10 20 30 40", "10"])
        self.assertEqual(code, 0)
        self.assertIn("index 0", out)

    def test_reports_duplicate_range(self):
        code, out, _ = self._run(["1 2 2 2 3", "2"])
        self.assertEqual(code, 0)
        self.assertIn("indices 1..3", out)

    def test_usage_error_on_bad_args(self):
        self.assertEqual(main([]), 2)
        self.assertEqual(main(["1 2 3"]), 2)
        self.assertEqual(main(["1 2 three", "1"]), 2)

    def test_empty_list_is_a_usage_error(self):
        self.assertEqual(main(["", "1"]), 2)


if __name__ == "__main__":
    unittest.main()
