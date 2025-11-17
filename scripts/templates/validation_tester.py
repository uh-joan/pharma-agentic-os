"""
Validation Tester

Runs validation tests on query results.
Evaluates assertions like "should contain X", "should NOT contain Y", etc.
"""

from typing import Any, Callable, Dict, List, Optional
import json


class ValidationTester:
    """
    Run validation tests on MCP query results.

    Supports common pharmaceutical data quality checks:
    - Token efficiency
    - Field presence
    - Content filtering (e.g., oral formulations only)
    - Result count bounds
    """

    def __init__(self, results: List[Dict[str, Any]]):
        """
        Initialize validation tester.

        Args:
            results: Query results to validate
        """
        self.results = results

    def run_tests(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run validation tests.

        Args:
            tests: List of test definitions, each with:
                - name: Test name
                - validator: Validation function (results -> bool)
                - error_message: Message if test fails

        Returns:
            Validation report with passed/failed checks

        Example:
            >>> tester = ValidationTester(results)
            >>> report = tester.run_tests([
            ...     {
            ...         "name": "has_results",
            ...         "validator": lambda r: len(r) > 0,
            ...         "error_message": "No results returned"
            ...     },
            ...     {
            ...         "name": "token_efficient",
            ...         "validator": lambda r: estimate_tokens(r) < 5000,
            ...         "error_message": "Results exceed 5000 tokens"
            ...     }
            ... ])
        """
        checks = []
        all_passed = True

        for test in tests:
            try:
                passed = test["validator"](self.results)
                checks.append({
                    "name": test["name"],
                    "passed": passed,
                    "error_message": None if passed else test.get("error_message")
                })
                if not passed:
                    all_passed = False
            except Exception as e:
                checks.append({
                    "name": test["name"],
                    "passed": False,
                    "error_message": f"Test failed with exception: {str(e)}"
                })
                all_passed = False

        return {
            "passed": all_passed,
            "checks": checks,
            "total": len(tests),
            "passed_count": sum(1 for c in checks if c["passed"])
        }

    def print_report(self, report: Dict[str, Any]):
        """
        Print validation report.

        Args:
            report: Validation report from run_tests()
        """
        print("\n=== Validation Report ===")
        print(f"Total tests: {report['total']}")
        print(f"Passed: {report['passed_count']}")
        print(f"Failed: {report['total'] - report['passed_count']}")

        for check in report["checks"]:
            status = "✅" if check["passed"] else "❌"
            print(f"\n{status} {check['name']}")
            if not check["passed"] and check["error_message"]:
                print(f"   Error: {check['error_message']}")


# Built-in validation functions
def validate_token_limit(max_tokens: int) -> Callable:
    """
    Validate token count is within limit.

    Args:
        max_tokens: Maximum acceptable tokens

    Returns:
        Validator function
    """
    def validator(results: List[Dict[str, Any]]) -> bool:
        json_str = json.dumps(results)
        estimated_tokens = len(json_str) // 4
        return estimated_tokens <= max_tokens

    return validator


def validate_result_count(min_count: int = 1, max_count: Optional[int] = None) -> Callable:
    """
    Validate result count is within bounds.

    Args:
        min_count: Minimum results required
        max_count: Maximum results allowed (None = no limit)

    Returns:
        Validator function
    """
    def validator(results: List[Dict[str, Any]]) -> bool:
        count = len(results)
        if count < min_count:
            return False
        if max_count is not None and count > max_count:
            return False
        return True

    return validator


def validate_field_presence(required_fields: List[str]) -> Callable:
    """
    Validate that required fields are present in results.

    Args:
        required_fields: List of field paths (e.g., "openfda.brand_name")

    Returns:
        Validator function
    """
    def validator(results: List[Dict[str, Any]]) -> bool:
        if not results:
            return False

        # Check all results have required fields
        for result in results:
            for field_path in required_fields:
                parts = field_path.split(".")
                value = result
                for part in parts:
                    value = value.get(part, {})
                    if not value:
                        return False

        return True

    return validator


def validate_content_filter(
    field_path: str,
    include_terms: Optional[List[str]] = None,
    exclude_terms: Optional[List[str]] = None
) -> Callable:
    """
    Validate content filtering (e.g., oral formulations only).

    Args:
        field_path: Path to field to check (e.g., "products.route")
        include_terms: Terms that MUST be present
        exclude_terms: Terms that must NOT be present

    Returns:
        Validator function
    """
    def validator(results: List[Dict[str, Any]]) -> bool:
        if not results:
            return False

        for result in results:
            # Navigate to field
            parts = field_path.split(".")
            value = result
            for part in parts:
                value = value.get(part, {})
                if not value:
                    break

            # Convert to string for comparison
            value_str = str(value).lower()

            # Check include terms
            if include_terms:
                if not any(term.lower() in value_str for term in include_terms):
                    return False

            # Check exclude terms
            if exclude_terms:
                if any(term.lower() in value_str for term in exclude_terms):
                    return False

        return True

    return validator


def validate_field_selection_working(expected_fields: List[str]) -> Callable:
    """
    Validate that field selection worked (only expected fields present).

    Args:
        expected_fields: List of expected top-level fields

    Returns:
        Validator function
    """
    def validator(results: List[Dict[str, Any]]) -> bool:
        if not results:
            return False

        # Check first result
        first = results[0]
        actual_fields = set(first.keys())
        expected_set = set(expected_fields)

        # Allow extra metadata fields
        allowed_extra = {"meta", "id", "type"}
        extra = actual_fields - expected_set - allowed_extra

        # Fail if unexpected fields present
        return len(extra) == 0

    return validator
