from typing import Any, Optional


class ResponseComparator:
    """
    Compare API responses with support for:

    - Dictionary comparison
    - List comparison
    - Missing fields
    - Unexpected fields
    - Value mismatches
    - Type mismatches
    - Ignored paths
    - Numeric tolerance
    """

    def __init__(
        self,
        ignore_paths: Optional[list] = None,
        numeric_tolerance: float = 0.0
    ):
        """
        Initialize the response comparator.

        Args:
            ignore_paths:
                JSON paths to ignore during comparison.

            numeric_tolerance:
                Allowed numeric difference between expected
                and actual values.
        """

        self.ignore_paths = ignore_paths or []

        self.numeric_tolerance = numeric_tolerance


    # --------------------------------------------------
    # PUBLIC COMPARISON METHOD
    # --------------------------------------------------

    def compare(self, expected, actual):

        differences = []

        self._compare_values(
            expected=expected,
            actual=actual,
            path="root",
            differences=differences
        )

        return {
            "match": len(differences) == 0,
            "total_differences": len(differences),
            "differences": differences
        }


    # --------------------------------------------------
    # PATH IGNORE CHECK
    # --------------------------------------------------

    def _is_ignored(self, path):

        for ignored_path in self.ignore_paths:

            if path == ignored_path:
                return True

            if path.startswith(ignored_path + "."):
                return True

            if path.startswith(ignored_path + "["):
                return True

        return False


    # --------------------------------------------------
    # TYPE CHECKING
    # --------------------------------------------------

    def _get_type_name(self, value):

        return type(value).__name__


    # --------------------------------------------------
    # NUMERIC COMPARISON
    # --------------------------------------------------

    def _numbers_match(self, expected, actual):

        return abs(expected - actual) <= self.numeric_tolerance


    # --------------------------------------------------
    # DIFFERENCE CREATION
    # --------------------------------------------------

    def _add_difference(
        self,
        differences,
        difference_type,
        path,
        expected,
        actual
    ):

        differences.append({
            "type": difference_type,
            "path": path,
            "expected": expected,
            "actual": actual,
            "expected_type": self._get_type_name(expected),
            "actual_type": self._get_type_name(actual)
        })


    # --------------------------------------------------
    # MAIN RECURSIVE COMPARISON
    # --------------------------------------------------

    def _compare_values(
        self,
        expected,
        actual,
        path,
        differences
    ):

        # Ignore configured paths
        if self._is_ignored(path):
            return


        # --------------------------------------------------
        # TYPE MISMATCH
        # --------------------------------------------------

        if type(expected) is not type(actual):

            # Allow numeric comparison between integers
            # and floats, excluding booleans.
            if (
                isinstance(expected, (int, float))
                and not isinstance(expected, bool)
                and isinstance(actual, (int, float))
                and not isinstance(actual, bool)
            ):

                if not self._numbers_match(expected, actual):

                    self._add_difference(
                        differences,
                        "value_mismatch",
                        path,
                        expected,
                        actual
                    )

                return


            self._add_difference(
                differences,
                "type_mismatch",
                path,
                expected,
                actual
            )

            return


        # --------------------------------------------------
        # DICTIONARY COMPARISON
        # --------------------------------------------------

        if isinstance(expected, dict):

            expected_keys = set(expected.keys())

            actual_keys = set(actual.keys())


            # Missing fields
            for key in sorted(expected_keys - actual_keys):

                field_path = f"{path}.{key}"

                if self._is_ignored(field_path):
                    continue

                self._add_difference(
                    differences,
                    "missing_field",
                    field_path,
                    expected[key],
                    None
                )


            # Unexpected fields
            for key in sorted(actual_keys - expected_keys):

                field_path = f"{path}.{key}"

                if self._is_ignored(field_path):
                    continue

                self._add_difference(
                    differences,
                    "unexpected_field",
                    field_path,
                    None,
                    actual[key]
                )


            # Compare common fields
            for key in sorted(expected_keys & actual_keys):

                self._compare_values(
                    expected[key],
                    actual[key],
                    path=f"{path}.{key}",
                    differences=differences
                )

            return


        # --------------------------------------------------
        # LIST COMPARISON
        # --------------------------------------------------

        if isinstance(expected, list):

            if len(expected) != len(actual):

                self._add_difference(
                    differences,
                    "list_length_mismatch",
                    path,
                    len(expected),
                    len(actual)
                )


            # Compare common elements
            for index in range(min(len(expected), len(actual))):

                self._compare_values(
                    expected[index],
                    actual[index],
                    path=f"{path}[{index}]",
                    differences=differences
                )

            return


        # --------------------------------------------------
        # NUMERIC COMPARISON
        # --------------------------------------------------

        if (
            isinstance(expected, (int, float))
            and not isinstance(expected, bool)
        ):

            if not self._numbers_match(expected, actual):

                self._add_difference(
                    differences,
                    "value_mismatch",
                    path,
                    expected,
                    actual
                )

            return


        # --------------------------------------------------
        # VALUE COMPARISON
        # --------------------------------------------------

        if expected != actual:

            self._add_difference(
                differences,
                "value_mismatch",
                path,
                expected,
                actual
            )