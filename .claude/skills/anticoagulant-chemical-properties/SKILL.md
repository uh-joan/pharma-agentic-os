---
name: get_anticoagulant_chemical_properties
description: >
  Multi-server integration combining FDA approved anticoagulant drugs with PubChem
  chemical properties. Demonstrates cross-server data enrichment by querying FDA
  for drug labels then enriching with molecular properties from PubChem. Returns
  comprehensive drug intelligence including molecular formulas, weights, SMILES,
  InChI, LogP, TPSA, and 20+ chemical descriptors. Use for complete chemical
  characterization of FDA approved anticoagulants or as reference pattern for
  FDA + PubChem integration. Keywords: anticoagulant, blood thinner, chemical
  properties, molecular weight, SMILES, InChI, drug properties.
category: drug-discovery
mcp_servers:
  - fda_mcp
  - pubchem_mcp
patterns:
  - multi_server_query
  - json_parsing
  - data_enrichment
  - deduplication
data_scope:
  total_results: 66
  geographical: US
  temporal: All time
created: 2025-11-20
last_updated: 2025-11-20
complexity: medium
execution_time: ~30 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_anticoagulant_chemical_properties

## Purpose
Multi-server integration combining FDA drug approval data with PubChem chemical properties for comprehensive anticoagulant drug intelligence.

## Integration Flow
1. FDA Query: Search FDA drug labels for "anticoagulant"
2. Name Extraction: Extract unique brand/generic names
3. PubChem Lookup: Query PubChem for each drug
4. Data Enrichment: Combine FDA + PubChem properties
5. Property Extraction: 28 chemical descriptors per drug

## Chemical Properties Retrieved
- PubChem CID, Molecular formula/weight
- SMILES, InChI, IUPAC name
- XLogP (lipophilicity), TPSA (polar surface area)
- H-bond donors/acceptors, Rotatable bonds
- Molecular complexity, Stereochemistry

## Token Efficiency
- Raw data: ~650,000 tokens
- Summary: ~500 tokens
- **Reduction**: 99.9%
