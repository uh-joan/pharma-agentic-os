---
name: get_texas_cardiologists
description: >
  Search for cardiologists practicing in Texas using CMS Medicare provider data.
  Returns provider counts by city and organization type. Useful for healthcare
  market analysis, provider network planning, and competitive intelligence in
  cardiovascular care. Trigger keywords: cardiologists, Texas, providers, CMS,
  Medicare, cardiology practice.
category: healthcare
mcp_servers:
  - healthcare_mcp
patterns:
  - provider_search
  - geographical_aggregation
  - organization_analysis
data_scope:
  total_results: 92
  geographical: Texas (US)
  temporal: Current active providers
created: 2025-11-20
last_updated: 2025-11-20
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_texas_cardiologists

## Purpose
Retrieve and analyze cardiologists practicing in Texas using CMS Medicare provider database. Provides geographic distribution and organization type breakdown for healthcare market analysis.

## Usage
Use this skill when you need to:
- Identify cardiologists in Texas for market analysis
- Understand geographic distribution of cardiology practices
- Analyze organization structure (individual vs. group practices)
- Support healthcare network planning
- Conduct competitive intelligence in cardiovascular care

## Implementation Details

### Data Source
- **MCP Server:** `healthcare_mcp`
- **Endpoint:** `search_providers`
- **Filters:** Specialty="Cardiology", State="TX"

### Data Processing
1. Query CMS database for all cardiologists in Texas
2. Aggregate providers by city
3. Categorize by organization type (Individual vs. Group)
4. Sort cities by provider count
5. Generate summary statistics

### Output Format
Returns dictionary with:
- `total_count`: Number of providers found
- `providers`: Full provider list with details
- `cities`: Top 10 cities by provider count
- `organization_types`: Distribution by practice type
- `summary`: Formatted text summary

## Example Output
```
Total Providers: 92

Top 10 Cities:
  • Houston: 28 providers
  • Dallas: 18 providers
  • San Antonio: 12 providers
  ...

Organization Types:
  • Individual: 68 providers
  • Group Practice: 24 providers
```

## Patterns Demonstrated
- **Provider Search:** CMS Medicare database query patterns
- **Geographical Aggregation:** City-level provider counts
- **Organization Analysis:** Practice type categorization

## Notes
- Data reflects currently active Medicare-enrolled providers
- City counts may include multiple locations for same provider
- Organization types based on CMS registration data
