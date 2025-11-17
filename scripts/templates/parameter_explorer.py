"""
Parameter Explorer

Tests parameter combinations to find optimal query settings.
Scores candidates based on result quality metrics.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import json


class ParameterExplorer:
    """
    Test parameter combinations and score results.

    Used for finding optimal search terms, aggregation fields, etc.
    """

    def __init__(
        self,
        mcp_client,
        server: str,
        tool: str,
        base_params: Dict[str, Any]
    ):
        """
        Initialize parameter explorer.

        Args:
            mcp_client: MCPClient instance
            server: MCP server name
            tool: Tool name
            base_params: Base parameters shared across all tests
        """
        self.mcp_client = mcp_client
        self.server = server
        self.tool = tool
        self.base_params = base_params

    def explore(
        self,
        parameter_name: str,
        candidates: List[Any],
        scorer: Callable[[Dict[str, Any]], float],
        limit: int = 5
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Test parameter candidates and find best value.

        Args:
            parameter_name: Name of parameter to explore (e.g., "search_term")
            candidates: List of values to test
            scorer: Function to score results (higher = better)
            limit: Limit for test queries (keep small)

        Returns:
            (best_value, scored_results)

        Example:
            >>> explorer = ParameterExplorer(client, "fda-mcp", "fda_info", {...})
            >>> best, results = explorer.explore(
            ...     "search_term",
            ...     ["GLP-1", "GLP-1 oral", "semaglutide"],
            ...     lambda r: score_oral_formulations(r)
            ... )
        """
        print(f"   Exploring parameter '{parameter_name}' with {len(candidates)} candidates...")

        scored_results = []

        for candidate in candidates:
            # Create test params
            test_params = {
                **self.base_params,
                parameter_name: candidate,
                "limit": limit  # Keep test queries small
            }

            # Execute test query
            try:
                result = self.mcp_client.call_tool(
                    self.server,
                    self.tool,
                    test_params
                )

                # Score result
                score = scorer(result)

                scored_results.append({
                    "candidate": candidate,
                    "score": score,
                    "result": result
                })

                print(f"      {candidate}: {score:.2f}")

            except Exception as e:
                print(f"      {candidate}: ERROR - {str(e)}")
                scored_results.append({
                    "candidate": candidate,
                    "score": 0.0,
                    "error": str(e)
                })

        # Sort by score (descending)
        scored_results.sort(key=lambda x: x["score"], reverse=True)

        # Return best candidate
        best = scored_results[0]["candidate"]
        print(f"   → Best: {best} (score: {scored_results[0]['score']:.2f})")

        return best, scored_results

    def explore_multiple(
        self,
        explorations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Explore multiple parameters sequentially.

        Args:
            explorations: List of exploration configs, each with:
                - parameter_name: Name of parameter
                - candidates: List of values to test
                - scorer: Scoring function

        Returns:
            Dictionary of best values for each parameter

        Example:
            >>> best_params = explorer.explore_multiple([
            ...     {
            ...         "parameter_name": "search_term",
            ...         "candidates": ["GLP-1", "GLP-1 oral"],
            ...         "scorer": score_oral_formulations
            ...     },
            ...     {
            ...         "parameter_name": "count",
            ...         "candidates": ["openfda.brand_name.exact", "openfda.generic_name.exact"],
            ...         "scorer": score_aggregation_quality
            ...     }
            ... ])
        """
        best_params = {}

        for exploration in explorations:
            best, _ = self.explore(
                exploration["parameter_name"],
                exploration["candidates"],
                exploration["scorer"]
            )
            best_params[exploration["parameter_name"]] = best

        return best_params


# Built-in scoring functions
def score_result_count(target: int = 10) -> Callable:
    """
    Score based on result count proximity to target.

    Args:
        target: Ideal number of results

    Returns:
        Scorer function
    """
    def scorer(result: Dict[str, Any]) -> float:
        count = len(result.get("results", []))
        # Penalize both too few and too many results
        deviation = abs(count - target)
        return max(0, 100 - deviation * 5)

    return scorer


def score_token_efficiency(max_tokens: int = 5000) -> Callable:
    """
    Score based on token efficiency.

    Args:
        max_tokens: Maximum acceptable tokens

    Returns:
        Scorer function
    """
    def scorer(result: Dict[str, Any]) -> float:
        # Rough token estimate
        json_str = json.dumps(result)
        estimated_tokens = len(json_str) // 4

        if estimated_tokens > max_tokens:
            return 0.0

        # Higher score for fewer tokens
        return 100 * (1 - estimated_tokens / max_tokens)

    return scorer


def score_field_presence(required_fields: List[str]) -> Callable:
    """
    Score based on presence of required fields in results.

    Args:
        required_fields: List of field paths to check (e.g., "openfda.brand_name")

    Returns:
        Scorer function
    """
    def scorer(result: Dict[str, Any]) -> float:
        results = result.get("results", [])
        if not results:
            return 0.0

        # Check first result for required fields
        first = results[0]
        present = 0

        for field_path in required_fields:
            parts = field_path.split(".")
            value = first
            for part in parts:
                value = value.get(part, {})
                if not value:
                    break
            if value:
                present += 1

        return (present / len(required_fields)) * 100

    return scorer
