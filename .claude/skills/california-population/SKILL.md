---
name: get_california_population
description: >
  Retrieve population statistics for California from Data Commons.
  This skill demonstrates querying demographic data from the Data Commons
  knowledge graph, which provides access to publicly available statistics
  from authoritative sources. Use this when you need California population
  data, demographic trends, or as a reference for querying other geographic
  entities in Data Commons.
category: demographic
mcp_servers:
  - datacommons_mcp
patterns:
  - json_parsing
  - entity_variable_query
data_scope:
  total_results: 1
  geographical: California (US)
  temporal: Latest available (2022)
created: 2025-11-20
last_updated: 2025-11-20
complexity: simple
execution_time: ~1 second
token_efficiency: ~99% reduction vs raw data
---

# get_california_population

## Purpose
Retrieve population statistics for California from the Data Commons knowledge graph.

## Usage
This skill is useful when you need:
- Current California population data
- Reference implementation for Data Commons queries
- Example of geographic entity queries (geoId format)
- Demographic statistics from authoritative sources

## Implementation Details
The skill uses the Data Commons MCP server to query population data:
- **Entity**: `geoId/06` (California FIPS code)
- **Variable**: `Count_Person` (total population)
- **Response format**: JSON with nested data structure

## Data Source
Data Commons aggregates data from sources like:
- US Census Bureau
- CDC
- World Bank
- Other authoritative statistical agencies

## Return Format
```python
{
    'summary': str,  # Human-readable summary
    'data': dict     # Full Data Commons response
}
```

## Example Output
```
California Population Data Retrieved
Source: Data Commons
Population (2022): 39,029,342
```

## Extension Opportunities
This pattern can be adapted for:
- Other US states (change geoId)
- Different variables (GDP, health metrics, etc.)
- Time series data (multiple dates)
- Multiple entities comparison
