"""
Base Query Class - Template Method Pattern

Abstract base class for generated query scripts.
Provides hooks for parameter exploration, query execution, and result validation.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from mcp_client import MCPClient


class BaseQuery(ABC):
    """
    Abstract base class for MCP query scripts.

    Template Method Pattern:
    1. setup() - Initialize configuration
    2. explore_parameters() - Test parameter combinations (optional)
    3. execute_queries() - Run MCP queries
    4. validate_results() - Check result quality
    5. save_results() - Persist to data_dump/

    Subclasses implement abstract methods for specific queries.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize base query.

        Args:
            output_dir: Directory for saving results. Defaults to data_dump/{timestamp}_{query_type}/
        """
        self.output_dir = output_dir or self._create_output_dir()
        self.mcp_client: Optional[MCPClient] = None
        self.results: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def _create_output_dir(self) -> str:
        """Create timestamped output directory."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        query_type = self.__class__.__name__.replace("Query", "").lower()
        output_dir = Path("data_dump") / f"{timestamp}_{query_type}"
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir)

    @abstractmethod
    def setup(self) -> Dict[str, Any]:
        """
        Initialize query configuration.

        Returns:
            Configuration dictionary with server, tool, base params, etc.

        Example:
            >>> def setup(self):
            ...     return {
            ...         "server": "fda-mcp",
            ...         "tool": "mcp__fda-mcp__fda_info",
            ...         "base_params": {
            ...             "method": "lookup_drug",
            ...             "search_type": "general"
            ...         }
            ...     }
        """
        pass

    def explore_parameters(self) -> Optional[Dict[str, Any]]:
        """
        Optionally explore parameter space to find optimal settings.

        Returns:
            Best parameters found, or None to skip exploration

        Example:
            >>> def explore_parameters(self):
            ...     # Test different search terms
            ...     candidates = ["GLP-1", "GLP-1 oral", "semaglutide"]
            ...     best = self._test_candidates(candidates)
            ...     return {"search_term": best}
        """
        return None

    @abstractmethod
    def execute_queries(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute MCP queries.

        Args:
            config: Configuration from setup() + explore_parameters()

        Returns:
            List of query results

        Example:
            >>> def execute_queries(self, config):
            ...     result = self.mcp_client.call_tool(
            ...         config["server"],
            ...         config["tool"],
            ...         config["params"]
            ...     )
            ...     return [result]
        """
        pass

    def validate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optionally validate query results.

        Args:
            results: Query results to validate

        Returns:
            Validation report with passed/failed checks

        Example:
            >>> def validate_results(self, results):
            ...     return {
            ...         "checks": [
            ...             {"name": "has_results", "passed": len(results) > 0},
            ...             {"name": "token_efficient", "passed": estimate_tokens(results) < 5000}
            ...         ]
            ...     }
        """
        return {"checks": [], "passed": True}

    def save_results(self, results: List[Dict[str, Any]], validation: Dict[str, Any]):
        """
        Save results to output directory.

        Args:
            results: Query results
            validation: Validation report
        """
        output_path = Path(self.output_dir)

        # Save results as JSON
        with open(output_path / "results.json", "w") as f:
            json.dump(results, f, indent=2)

        # Save metadata
        self.metadata.update({
            "timestamp": datetime.now().isoformat(),
            "query_type": self.__class__.__name__,
            "result_count": len(results),
            "validation": validation
        })
        with open(output_path / "metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)

        # Save summary
        self._write_summary(output_path / "summary.md", results, validation)

    def _write_summary(self, path: Path, results: List[Dict], validation: Dict):
        """Write human-readable summary."""
        with open(path, "w") as f:
            f.write(f"# Query Results Summary\n\n")
            f.write(f"**Query Type**: {self.__class__.__name__}\n")
            f.write(f"**Timestamp**: {self.metadata['timestamp']}\n")
            f.write(f"**Result Count**: {len(results)}\n\n")

            # Validation status
            f.write("## Validation\n\n")
            if validation.get("passed"):
                f.write("✅ All checks passed\n\n")
            else:
                f.write("❌ Some checks failed\n\n")

            for check in validation.get("checks", []):
                status = "✅" if check.get("passed") else "❌"
                f.write(f"- {status} {check['name']}\n")

    def run(self):
        """
        Execute complete query workflow.

        Steps:
        1. Setup configuration
        2. Explore parameters (optional)
        3. Execute queries
        4. Validate results
        5. Save results
        """
        print(f"Starting {self.__class__.__name__}...")

        # Step 1: Setup
        print("1. Setting up configuration...")
        config = self.setup()

        # Step 2: Parameter exploration (optional)
        explored_params = self.explore_parameters()
        if explored_params:
            print(f"2. Explored parameters: {explored_params}")
            config.update(explored_params)
        else:
            print("2. Skipping parameter exploration")

        # Step 3: Execute queries
        print("3. Executing queries...")
        with MCPClient() as client:
            self.mcp_client = client
            results = self.execute_queries(config)
            self.results = results

        print(f"   → Retrieved {len(results)} results")

        # Step 4: Validate
        print("4. Validating results...")
        validation = self.validate_results(results)

        # Step 5: Save
        print("5. Saving results...")
        self.save_results(results, validation)

        print(f"✅ Complete! Results saved to {self.output_dir}")

        return {
            "output_dir": self.output_dir,
            "result_count": len(results),
            "validation": validation
        }
