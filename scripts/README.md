# MCP Query Code Generation

This directory contains the infrastructure for **code generation** from pharma-search-specialist JSON execution plans.

## Architecture

Instead of Claude Code manually executing MCP queries, it now **generates Python scripts** with:
- Built-in parameter exploration (test different search terms, find optimal settings)
- Automatic validation (quality checks, token efficiency, content filtering)
- Reusable scripts (save, re-run, modify)

## Directory Structure

```
scripts/
├── templates/          # Base classes and utilities (committed to git)
│   ├── __init__.py
│   ├── mcp_client.py          # MCP server communication wrapper
│   ├── base_query.py          # Abstract base class (template method pattern)
│   ├── parameter_explorer.py  # Parameter testing engine
│   └── validation_tester.py   # Result validation framework
├── generated/          # Generated query scripts (gitignored)
│   └── .gitignore
└── utils/              # Code generation utilities (Phase 4)
    └── script_generator.py     # Translates JSON plans to Python code
```

## Workflow

### 1. User Query → JSON Plan

pharma-search-specialist returns JSON execution plan:

```json
{
  "execution_plan": [
    {
      "step": 1,
      "tool": "mcp__fda-mcp__fda_info",
      "method": "lookup_drug",
      "params": {
        "search_term": "GLP-1",
        "search_type": "general",
        "count": "openfda.brand_name.exact",
        "limit": 50
      },
      "exploration": {
        "search_term": {
          "candidates": ["GLP-1", "GLP-1 oral", "semaglutide"],
          "scorer": "score_oral_formulations"
        }
      },
      "validation": [
        {"name": "token_efficient", "max_tokens": 5000},
        {"name": "has_oral_only", "field": "products.route", "include": ["ORAL"]}
      ]
    }
  ]
}
```

### 2. Claude Code → Generated Script

Claude Code translates JSON plan to Python script:

```python
# scripts/generated/glp1_query_20251117_143022.py

from templates.base_query import BaseQuery
from templates.parameter_explorer import ParameterExplorer
from templates.validation_tester import ValidationTester, validate_token_limit

class GLP1Query(BaseQuery):
    def setup(self):
        return {
            "server": "fda-mcp",
            "tool": "mcp__fda-mcp__fda_info",
            "base_params": {
                "method": "lookup_drug",
                "search_type": "general",
                "count": "openfda.brand_name.exact",
                "limit": 50
            }
        }

    def explore_parameters(self):
        explorer = ParameterExplorer(
            self.mcp_client, "fda-mcp", "mcp__fda-mcp__fda_info",
            self.config["base_params"]
        )

        best, _ = explorer.explore(
            "search_term",
            ["GLP-1", "GLP-1 oral", "semaglutide"],
            score_oral_formulations
        )

        return {"search_term": best}

    def execute_queries(self, config):
        result = self.mcp_client.call_tool(
            config["server"], config["tool"],
            {**config["base_params"], **config}
        )
        return [result]

    def validate_results(self, results):
        tester = ValidationTester(results)
        return tester.run_tests([
            {
                "name": "token_efficient",
                "validator": validate_token_limit(5000),
                "error_message": "Results exceed 5000 tokens"
            }
        ])

if __name__ == "__main__":
    query = GLP1Query()
    query.run()
```

### 3. Execute Generated Script

```bash
cd scripts/generated
python glp1_query_20251117_143022.py
```

Output:
```
Starting GLP1Query...
1. Setting up configuration...
2. Explored parameters:
   Exploring parameter 'search_term' with 3 candidates...
      GLP-1: 75.30
      GLP-1 oral: 92.50
      semaglutide: 68.20
   → Best: GLP-1 oral (score: 92.50)
3. Executing queries...
   → Retrieved 1 results
4. Validating results...
   ✅ token_efficient
5. Saving results...
✅ Complete! Results saved to data_dump/2025-11-17_143025_glp1/
```

## Template Components

### mcp_client.py

Wrapper around MCP infrastructure:
- Reads `.mcp.json` configuration
- Spawns MCP server processes
- Handles JSON-RPC communication via stdin/stdout
- Automatic cleanup on exit

```python
from templates.mcp_client import MCPClient

with MCPClient() as client:
    result = client.call_tool(
        "fda-mcp",
        "mcp__fda-mcp__fda_info",
        {"method": "lookup_drug", "search_term": "aspirin", ...}
    )
```

### base_query.py

Abstract base class using template method pattern:
- `setup()` - Initialize configuration
- `explore_parameters()` - Optional parameter testing
- `execute_queries()` - Run MCP queries (required)
- `validate_results()` - Optional quality checks
- `save_results()` - Persist to data_dump/

### parameter_explorer.py

Test parameter combinations to find optimal settings:
- Test multiple candidates (search terms, aggregation fields, etc.)
- Score results using custom scoring functions
- Return best parameter value

Built-in scorers:
- `score_result_count(target=10)` - Prefer results close to target count
- `score_token_efficiency(max_tokens=5000)` - Minimize token usage
- `score_field_presence(required_fields)` - Ensure fields present

### validation_tester.py

Run validation tests on query results:
- Token efficiency checks
- Field presence validation
- Content filtering (e.g., oral formulations only)
- Field selection verification

Built-in validators:
- `validate_token_limit(max_tokens)`
- `validate_result_count(min_count, max_count)`
- `validate_field_presence(required_fields)`
- `validate_content_filter(field_path, include_terms, exclude_terms)`
- `validate_field_selection_working(expected_fields)`

## Benefits

### 1. Parameter Exploration

Automatically test different approaches:
- Search terms: "GLP-1" vs "GLP-1 oral" vs "semaglutide"
- Aggregation fields: "brand_name.exact" vs "generic_name.exact"
- Clinical trial phases: "PHASE3" vs "PHASE2 OR PHASE3"

### 2. Validation Testing

Built-in quality checks:
- Token efficiency (prevent 50k token responses)
- Field selection working correctly
- Content filtering (e.g., oral formulations only)
- Result count bounds

### 3. Reusability

Generated scripts can be:
- Saved for future use
- Modified by users
- Re-run with different parameters
- Shared across team

### 4. Transparency

Code is visible and debuggable:
- See exactly what queries are executed
- Understand parameter exploration logic
- Trace validation failures
- Modify scoring/validation logic

## Next Steps

**Phase 4**: Build script_generator.py
- Parse JSON execution plans
- Generate Python code using Jinja2 templates
- Handle exploration directives
- Include validation tests

**Phase 5**: Domain-specific scorers and validators
- FDA-specific scorers (oral formulations, brand name aggregation)
- Clinical trial scorers (phase selection, sponsor matching)
- PubMed scorers (relevance, recency)

**Phase 6**: End-to-end testing
- Test with real FDA queries
- Validate generated code quality
- Performance benchmarks
- Iteration and refinement
