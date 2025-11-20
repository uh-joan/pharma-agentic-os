---
name: get_aspirin_properties
description: >
  Retrieves comprehensive chemical properties for aspirin from PubChem database.
  Returns molecular weight, formula, SMILES notation, InChI identifiers, and
  structural data. Useful for pharmaceutical chemistry queries, compound validation,
  and drug structure analysis. Trigger keywords: aspirin, acetylsalicylic acid,
  chemical properties, molecular structure, PubChem compound data.
category: drug-discovery
mcp_servers:
  - pubchem_mcp
patterns:
  - json_parsing
  - compound_properties
data_scope:
  total_results: 1
  geographical: Global
  temporal: Current
created: 2025-01-20
last_updated: 2025-01-20
complexity: simple
execution_time: ~1 second
token_efficiency: ~99% reduction vs raw data
---

# get_aspirin_properties

## Purpose
Retrieves comprehensive chemical properties for aspirin (acetylsalicylic acid) from the PubChem database, including molecular identifiers, structural representations, and pharmacological data.

## Usage
Use this skill when you need:
- Molecular weight and formula for aspirin
- SMILES notation for structure representation
- InChI identifiers for database queries
- PubChem CID for cross-referencing
- Chemical structure validation

## Implementation Details
This skill uses the PubChem MCP server to query compound data by name. It extracts key chemical properties and formats them into a human-readable summary.

**Data Source**: PubChem (NIH National Library of Medicine)
**Query Method**: Compound search by name
**Response Format**: JSON dictionary with compound properties

## Example Output
```
Aspirin Chemical Properties:
═══════════════════════════════════════

Basic Information:
  • PubChem CID: 2244
  • IUPAC Name: 2-acetyloxybenzoic acid
  • Molecular Formula: C9H8O4
  • Molecular Weight: 180.16 g/mol

Structure Identifiers:
  • Canonical SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
  • InChI Key: BSYNRYMUTXBXSQ-UHFFFAOYSA-N
```

## Return Value
Returns a dictionary with:
- `success` (bool): Whether the query succeeded
- `properties` (dict): Extracted compound properties
- `raw_data` (dict): Full PubChem response
- `summary` (str): Formatted text summary

## Error Handling
- Gracefully handles missing compound data
- Returns error message if compound not found
- Provides informative failure messages
