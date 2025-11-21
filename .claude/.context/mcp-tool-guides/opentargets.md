# Open Targets MCP Server - Complete API Documentation

> **Access**: `mcp__opentargets-mcp-server__opentargets_info`
> **Platform Version**: v25.0.1
> **Response Format**: JSON (structured data)
> **Purpose**: Gene-drug-disease associations, target validation, genetic evidence

---

## 🔴 CRITICAL ID FORMAT REQUIREMENTS

**Gene IDs**: Ensembl gene ID format (NOT gene symbols)
- ✅ CORRECT: `"ENSG00000012048"` (Ensembl ID)
- ❌ WRONG: `"GLP1R"` (gene symbol - use for search only)

**Disease IDs**: MONDO (primary) or EFO format
- ✅ CORRECT: `"MONDO_0005148"` (MONDO format - primary)
- ✅ CORRECT: `"EFO_0000305"` (EFO format - also supported)
- ❌ WRONG: `"diabetes"` (disease name - use for search only)

**Workflow**:
1. Search by symbol/name: `search_targets("GLP1R")` → Get `ENSG00000012048`
2. Use Ensembl ID for associations: `get_target_disease_associations(targetId="ENSG00000012048")`

---

## Table of Contents

1. [When to Use Open Targets](#when-to-use)
2. [Quick Reference](#quick-reference)
3. [Methods Overview](#methods-overview)
4. [Method 1: search_targets](#method-1-search_targets)
5. [Method 2: search_diseases](#method-2-search_diseases)
6. [Method 3: get_target_disease_associations](#method-3-get_target_disease_associations)
7. [Method 4: get_disease_targets_summary](#method-4-get_disease_targets_summary)
8. [Method 5: get_target_details](#method-5-get_target_details)
9. [Method 6: get_disease_details](#method-6-get_disease_details)
10. [Pagination Support](#pagination-support)
11. [Response Format & Parsing](#response-format--parsing)
12. [Evidence Score Interpretation](#evidence-score-interpretation)
13. [Common Use Cases](#common-use-cases)
14. [Known Quirks & Limitations](#known-quirks--limitations)
15. [Best Practices](#best-practices)
16. [FAQ](#faq)

---

## When to Use

✅ **Use Open Targets for**:
- Target validation with genetic evidence
- Drug-target-disease associations
- Safety predictions for therapeutic targets
- Approved drug precedents for mechanisms
- Druggability assessment (tractability scores)
- Evidence-based target prioritization
- Genetic association analysis

❌ **Don't use Open Targets for**:
- Clinical trial data → Use CT.gov MCP
- Drug approval information → Use FDA MCP
- Literature search → Use PubMed MCP
- Chemical structures → Use PubChem MCP

---

## Quick Reference

| Method | Purpose | Key Parameters | ID Format | Returns |
|--------|---------|----------------|-----------|---------|
| `search_targets` | Find genes/targets | `query`, `size` (max: 50K) | Symbol → Ensembl ID | Target list |
| `search_diseases` | Find diseases | `query`, `size` (max: 50K) | Name → MONDO/EFO ID | Disease list |
| `get_target_disease_associations` | Get associations | `targetId`, `diseaseId`, `minScore`, `size` (max: 50K) | Ensembl + MONDO/EFO | Associations |
| `get_disease_targets_summary` | Disease targets | `diseaseId`, `minScore`, `size` (max: 50K) | MONDO/EFO | Target summary |
| `get_target_details` | Target info | `id` | Ensembl ID | Full details |
| `get_disease_details` | Disease info | `id` | MONDO/EFO | Full details |

**Token Usage** (measured):
- Search: 180-250 tokens
- Associations: ~1,350 tokens
- Summaries: ~2,550 tokens
- Details: 160-220 tokens

---

## Methods Overview

```json
{
  "method": "search_targets",                     // Search genes by symbol/name
  "method": "search_diseases",                    // Search diseases by name
  "method": "get_target_disease_associations",    // Get associations with evidence
  "method": "get_disease_targets_summary",        // Overview of targets for disease
  "method": "get_target_details",                 // Comprehensive target info
  "method": "get_disease_details"                 // Comprehensive disease info
}
```

**All methods return JSON** with structured association and evidence data.

---

## Method 1: search_targets

**Purpose**: Search for therapeutic targets by gene symbol or name

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"search_targets"` | Operation type |
| `query` | string | ✅ Yes | - | Any text | Gene symbol, name, or description |
| `size` | integer | ❌ No | 25 | 1-50,000 | Maximum results to return (supports pagination) |

### Search Query Examples

#### Gene Symbol Search (Most Common)
```json
{
  "method": "search_targets",
  "query": "GLP1R",
  "size": 10
}
```

**Common gene symbols**:
- `"GLP1R"` - GLP-1 receptor
- `"DPP4"` - Dipeptidyl peptidase-4
- `"BRCA1"` - Breast cancer 1
- `"KRAS"` - KRAS proto-oncogene
- `"EGFR"` - Epidermal growth factor receptor

#### Gene Name Search
```json
{
  "method": "search_targets",
  "query": "insulin receptor",
  "size": 10
}
```

#### Description Search
```json
{
  "method": "search_targets",
  "query": "protein kinase",
  "size": 20
}
```

### Response Structure

```json
{
  "data": [
    {
      "id": "ENSG00000012048",
      "approvedSymbol": "GLP1R",
      "approvedName": "glucagon like peptide 1 receptor",
      "biotype": "protein_coding",
      "description": "...",
      "chromosome": "6",
      "start": 39,
      "end": 39
    }
  ],
  "total": 1
}
```

**Key fields**:
- `id` - **Ensembl gene ID** (use for associations and details)
- `approvedSymbol` - Official gene symbol
- `approvedName` - Full gene name
- `biotype` - Gene type (usually "protein_coding")

### Code Example

```python
from mcp.servers.opentargets_mcp import search_targets

# Search for GLP-1 receptor
result = search_targets(query="GLP1R", size=5)

# Extract Ensembl IDs for downstream analysis
for target in result.get('data', []):
    ensembl_id = target.get('id')  # CRITICAL: This is needed for associations!
    symbol = target.get('approvedSymbol')
    name = target.get('approvedName')

    print(f"{symbol} ({ensembl_id})")
    print(f"  Name: {name}")
    print()

# Search by description
result = search_targets(query="protein kinase", size=20)
print(f"Found {result.get('total', 0)} protein kinases")
```

---

## Method 2: search_diseases

**Purpose**: Search for diseases by name or synonym

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"search_diseases"` | Operation type |
| `query` | string | ✅ Yes | - | Any text | Disease name, synonym, or description |
| `size` | integer | ❌ No | 25 | 1-50,000 | Maximum results to return (supports pagination) |

### Search Query Examples

#### Disease Name Search
```json
{
  "method": "search_diseases",
  "query": "diabetes",
  "size": 10
}
```

**Common disease queries**:
- `"diabetes"` - Diabetes mellitus
- `"obesity"` - Obesity
- `"Alzheimer"` - Alzheimer's disease
- `"breast cancer"` - Breast neoplasm
- `"rheumatoid arthritis"` - Rheumatoid arthritis

#### Specific Disease Type
```json
{
  "method": "search_diseases",
  "query": "type 2 diabetes",
  "size": 5
}
```

### Response Structure

```json
{
  "data": [
    {
      "id": "MONDO_0005148",
      "name": "type 2 diabetes mellitus",
      "description": "A type of diabetes mellitus...",
      "synonyms": ["diabetes, type 2", "NIDDM", "non-insulin dependent diabetes"]
    }
  ],
  "total": 1
}
```

**Key fields**:
- `id` - **Disease ID** (MONDO or EFO format - use for associations)
- `name` - Disease name
- `description` - Disease description
- `synonyms` - Alternative names (may not be present)

**ID Format Note**: Results may return MONDO IDs (`MONDO_0005148`) or EFO IDs (`EFO_0000305`). Both formats are supported.

### Code Example

```python
from mcp.servers.opentargets_mcp import search_diseases

# Search for diabetes
result = search_diseases(query="diabetes", size=5)

# Extract disease IDs for associations
for disease in result.get('data', []):
    disease_id = disease.get('id')  # CRITICAL: Needed for associations!
    name = disease.get('name')
    description = disease.get('description', 'N/A')

    print(f"{name} ({disease_id})")
    print(f"  {description[:100]}...")
    print()

# Search for cancer types
result = search_diseases(query="breast cancer", size=10)
print(f"Found {result.get('total', 0)} breast cancer types")
```

---

## Method 3: get_target_disease_associations

**Purpose**: Get target-disease associations with genetic evidence scores

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_target_disease_associations"` | Operation type |
| `targetId` | string | ❌ No | - | Ensembl gene ID | Target Ensembl ID (e.g., "ENSG00000012048") |
| `diseaseId` | string | ❌ No | - | MONDO/EFO ID | Disease ID (e.g., "MONDO_0005148", "EFO_0000305") |
| `minScore` | number | ❌ No | 0.0 | 0.0-1.0 | Minimum association score threshold (client-side filter after pagination) |
| `size` | integer | ❌ No | 100 | 1-50,000 | Maximum associations to return (supports automatic pagination in batches of 100) |
| `format` | string | ❌ No | "json" | "json" or "tsv" | Output format |

**Note**: At least one of `targetId` or `diseaseId` should be provided.

### Common Query Patterns

#### All Diseases for a Target (Strong Evidence)
```json
{
  "method": "get_target_disease_associations",
  "targetId": "ENSG00000012048",
  "minScore": 0.5,
  "size": 100
}
```

#### All Targets for a Disease
```json
{
  "method": "get_target_disease_associations",
  "diseaseId": "MONDO_0005148",
  "minScore": 0.3,
  "size": 50
}
```

#### Specific Target-Disease Pair
```json
{
  "method": "get_target_disease_associations",
  "targetId": "ENSG00000012048",
  "diseaseId": "EFO_0000305",
  "minScore": 0.0
}
```

### minScore Thresholds (Evidence Strength)

| Score Range | Classification | Description | Use Case |
|-------------|----------------|-------------|----------|
| **0.5 - 1.0** | **Strong** | High-confidence associations | Primary target selection |
| **0.3 - 0.5** | **Moderate** | Medium-confidence associations | Secondary target list |
| **0.1 - 0.3** | **Weak** | Low-confidence associations | Exploratory analysis |
| **0.0 - 0.1** | **Very Weak** | Minimal evidence | Not recommended |

**Recommendation**: Use `minScore=0.5` for drug discovery target prioritization.

### Response Structure

```json
{
  "data": [
    {
      "targetId": "ENSG00000012048",
      "diseaseId": "EFO_0000305",
      "score": 0.72,
      "datatypeScores": {
        "genetic_association": 0.85,
        "literature": 0.65,
        "somatic_mutation": 0.45,
        "known_drug": 0.90,
        "affected_pathway": 0.50,
        "rna_expression": 0.55,
        "animal_model": 0.40
      }
    }
  ],
  "total": 1
}
```

**Key fields**:
- `targetId` - Ensembl gene ID
- `diseaseId` - Disease ID (MONDO or EFO)
- `score` - Overall association score (0-1)
- `datatypeScores` - Evidence breakdown by type

**Evidence Types**:
- `genetic_association` - GWAS and genetic studies
- `literature` - Text mining from publications
- `somatic_mutation` - Cancer mutation data
- `known_drug` - Approved drug precedents
- `affected_pathway` - Pathway analysis
- `rna_expression` - Gene expression data
- `animal_model` - Animal model evidence

### Code Example

```python
from mcp.servers.opentargets_mcp import get_target_disease_associations

# Get all diseases for GLP1R (strong evidence only)
result = get_target_disease_associations(
    targetId="ENSG00000012048",  # GLP1R
    minScore=0.5,
    size=100
)

# Analyze evidence types
for assoc in result.get('data', []):
    disease_id = assoc.get('diseaseId')
    overall_score = assoc.get('score')
    datatypes = assoc.get('datatypeScores', {})

    print(f"Disease: {disease_id}")
    print(f"Overall Score: {overall_score:.2f}")
    print(f"Evidence breakdown:")
    print(f"  Genetic: {datatypes.get('genetic_association', 0):.2f}")
    print(f"  Literature: {datatypes.get('literature', 0):.2f}")
    print(f"  Known drug: {datatypes.get('known_drug', 0):.2f}")
    print()

# Get specific target-disease association
result = get_target_disease_associations(
    targetId="ENSG00000012048",
    diseaseId="EFO_0000305",
    minScore=0.0  # Get all evidence even if weak
)
```

---

## Method 4: get_disease_targets_summary

**Purpose**: Get overview of all targets associated with a disease

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_disease_targets_summary"` | Operation type |
| `diseaseId` | string | ✅ Yes | - | MONDO/EFO ID | Disease ID (e.g., "MONDO_0005148", "EFO_0000305") |
| `minScore` | number | ❌ No | 0.0 | 0.0-1.0 | Minimum association score threshold (client-side filter after pagination) |
| `size` | integer | ❌ No | 50 | 1-50,000 | Maximum targets to return (supports automatic pagination in batches of 100) |
| `format` | string | ❌ No | "json" | "json" or "tsv" | Output format |

### Query Example

```json
{
  "method": "get_disease_targets_summary",
  "diseaseId": "MONDO_0005148",
  "minScore": 0.5,
  "size": 20
}
```

### Response Structure

Same as `get_target_disease_associations` (see Method 3).

### Code Example

```python
from mcp.servers.opentargets_mcp import get_disease_targets_summary

# Get top targets for type 2 diabetes
result = get_disease_targets_summary(
    diseaseId="MONDO_0005148",  # Type 2 diabetes
    minScore=0.5,
    size=20
)

# Rank targets by evidence score
targets = []
for assoc in result.get('data', []):
    target_id = assoc.get('targetId')
    score = assoc.get('score')
    datatypes = assoc.get('datatypeScores', {})

    targets.append({
        'id': target_id,
        'score': score,
        'genetic': datatypes.get('genetic_association', 0),
        'literature': datatypes.get('literature', 0)
    })

# Sort by overall score
targets.sort(key=lambda x: x['score'], reverse=True)

print("Top 10 targets for type 2 diabetes:")
for i, target in enumerate(targets[:10], 1):
    print(f"{i}. {target['id']}: {target['score']:.2f} (genetic: {target['genetic']:.2f})")
```

---

## Method 5: get_target_details

**Purpose**: Get comprehensive information about a specific target

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_target_details"` | Operation type |
| `id` | string | ✅ Yes | - | Ensembl gene ID | Target Ensembl ID (e.g., "ENSG00000012048") |
| `format` | string | ❌ No | "json" | "json" or "tsv" | Output format |

### Query Example

```json
{
  "method": "get_target_details",
  "id": "ENSG00000012048"
}
```

### Response Structure

```json
{
  "id": "ENSG00000012048",
  "approvedSymbol": "GLP1R",
  "approvedName": "glucagon like peptide 1 receptor",
  "biotype": "protein_coding",
  "chromosome": "6",
  "description": "...",
  "proteinAnnotations": {
    "id": "P43220",
    "functions": ["..."]
  },
  "tractability": {
    "smallmolecule": {
      "top_category": "Clinical Precedence",
      "buckets": [1, 3]
    },
    "antibody": {
      "top_category": "Predicted Tractable - High confidence",
      "buckets": [1, 2]
    }
  },
  "safetyLiabilities": [
    {
      "event": "...",
      "effects": "..."
    }
  ]
}
```

**Key fields (always present)**:
- `id` - Ensembl gene ID
- `approvedSymbol` - Gene symbol
- `approvedName` - Full gene name
- `biotype` - Gene type

**Optional fields** (may not be present):
- `proteinAnnotations` - Protein function data
- `tractability` - Druggability assessment
- `safetyLiabilities` - Known safety issues

### Tractability Categories

**Small Molecule Tractability**:
- `"Clinical Precedence"` - Approved drugs exist
- `"Discovery Precedence"` - Compounds in development
- `"Predicted Tractable - High confidence"` - Likely druggable
- `"Predicted Tractable - Medium to low confidence"` - Possibly druggable
- `"Unknown"` - No druggability data

**Antibody Tractability**:
- `"Clinical Precedence"` - Approved antibodies exist
- `"Predicted Tractable - High confidence"` - Likely targetable
- `"Predicted Tractable - Medium to low confidence"` - Possibly targetable

### Code Example

```python
from mcp.servers.opentargets_mcp import get_target_details

# Get details for GLP1R
details = get_target_details(id="ENSG00000012048")

# Extract key information
symbol = details.get('approvedSymbol')
name = details.get('approvedName')
biotype = details.get('biotype')

print(f"Target: {symbol}")
print(f"Name: {name}")
print(f"Type: {biotype}")

# Check druggability
tractability = details.get('tractability', {})

small_molecule = tractability.get('smallmolecule', {})
sm_category = small_molecule.get('top_category', 'Unknown')
print(f"\nSmall molecule tractability: {sm_category}")

antibody = tractability.get('antibody', {})
ab_category = antibody.get('top_category', 'Unknown')
print(f"Antibody tractability: {ab_category}")

# Check safety
safety = details.get('safetyLiabilities', [])
if safety:
    print(f"\nSafety concerns: {len(safety)} identified")
    for concern in safety:
        event = concern.get('event', 'Unknown')
        print(f"  - {event}")
else:
    print("\nNo known safety liabilities")
```

---

## Method 6: get_disease_details

**Purpose**: Get comprehensive information about a specific disease

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_disease_details"` | Operation type |
| `id` | string | ✅ Yes | - | MONDO/EFO ID | Disease ID (e.g., "MONDO_0005148", "EFO_0000305") |
| `format` | string | ❌ No | "json" | "json" or "tsv" | Output format |

### Query Example

```json
{
  "method": "get_disease_details",
  "id": "MONDO_0005148"
}
```

### Response Structure

```json
{
  "id": "MONDO_0005148",
  "name": "type 2 diabetes mellitus",
  "description": "A type of diabetes mellitus that is characterized by insulin resistance...",
  "synonyms": [
    "diabetes, type 2",
    "NIDDM",
    "non-insulin dependent diabetes mellitus"
  ],
  "therapeuticAreas": [
    "EFO_0000701"
  ]
}
```

**Key fields**:
- `id` - Disease ID (MONDO or EFO format)
- `name` - Disease name
- `description` - Disease description
- `synonyms` - Alternative names (optional)
- `therapeuticAreas` - Disease classification (optional)

### Code Example

```python
from mcp.servers.opentargets_mcp import get_disease_details

# Get details for type 2 diabetes
details = get_disease_details(id="MONDO_0005148")

# Extract information
name = details.get('name')
description = details.get('description')
synonyms = details.get('synonyms', [])

print(f"Disease: {name}")
print(f"\nDescription: {description}")

if synonyms:
    print(f"\nAlso known as:")
    for synonym in synonyms:
        print(f"  - {synonym}")
```

---

## Pagination Support

**Automatic Pagination**: The MCP server automatically handles pagination for large datasets.

### How Pagination Works

When you request a large dataset, the server:
1. Fetches data in **batches of 100 records** from the Open Targets GraphQL API
2. Continues fetching until reaching the requested `size` or total available records
3. Applies `minScore` filtering **after** fetching all pages (client-side)
4. Returns aggregated results with pagination metadata

### Pagination Metadata

All association methods return pagination metadata:

```json
{
  "data": { ... },
  "pagination": {
    "requested": 500,      // Size you requested
    "returned": 500,       // Actual records returned
    "total": 12874,        // Total records available
    "filtered": 500        // Records after minScore filter
  }
}
```

**Key fields**:
- `requested` - The `size` parameter you provided
- `returned` - Actual number of records in response (≤ requested)
- `total` - Total records available in Open Targets (before filtering)
- `filtered` - Records that passed `minScore` threshold (≤ total)

### Large Dataset Examples

#### Example 1: Fetch 1,000 Alzheimer's Targets

```python
from mcp.servers.opentargets_mcp import get_target_disease_associations

# Fetch 1,000 targets (10 pages automatically)
result = get_target_disease_associations(
    diseaseId='MONDO_0004975',  # Alzheimer's disease
    minScore=0.0,
    size=1000
)

pagination = result.get('pagination', {})
rows = result.get('data', {}).get('disease', {}).get('associatedTargets', {}).get('rows', [])

print(f"Requested: {pagination['requested']}")  # 1000
print(f"Returned: {len(rows)}")                 # 1000
print(f"Total available: {pagination['total']}") # 12,874
print(f"Pages fetched: {len(rows) // 100}")     # 10 pages
```

#### Example 2: High-Confidence Filtering from Full Dataset

```python
# Fetch large dataset, then filter by minScore
result = get_target_disease_associations(
    diseaseId='MONDO_0004975',
    minScore=0.5,  # High-confidence only
    size=1000      # Fetch up to 1000, but only high-confidence will be returned
)

pagination = result.get('pagination', {})
rows = result.get('data', {}).get('disease', {}).get('associatedTargets', {}).get('rows', [])

print(f"Total targets in database: {pagination['total']}")  # 12,874
print(f"High-confidence targets (≥0.5): {len(rows)}")       # 75
print(f"All returned scores ≥ 0.5: {all(r['score'] >= 0.5 for r in rows)}")  # True
```

### Performance Considerations

**Pagination Timing**:
- Each page (100 records): ~1-2 seconds
- 500 records (5 pages): ~5-10 seconds
- 1,000 records (10 pages): ~10-20 seconds

**Recommendations**:
- Use `minScore` to reduce dataset size when possible
- Start with smaller `size` values (100-500) for initial exploration
- Request larger datasets (1,000-5,000) only when comprehensive data is needed
- Maximum practical size: 50,000 records (500 pages, ~10-15 minutes)

### Pagination vs. Filtering

**Important**: `minScore` is applied **after** pagination, not during:

```python
# This fetches 1000 records, THEN filters by score
result = get_target_disease_associations(
    diseaseId='MONDO_0004975',
    minScore=0.5,  # Applied after fetching
    size=1000      # Fetches up to 1000 raw records
)

# If only 75 targets have score ≥ 0.5, you get 75 results
# But the server still fetched ~1000 records (10 pages)
```

**Best Practice**: Set `size` based on expected results after filtering:
- For `minScore=0.5`: 75-200 results typical → `size=500` sufficient
- For `minScore=0.3`: 200-1000 results typical → `size=1000` recommended
- For `minScore=0.0`: All records → `size=5000+` may be needed

---

## Response Format & Parsing

### JSON Structure (All Methods)

Open Targets returns structured JSON with consistent patterns.

**General pattern**:
```python
result = search_targets(...)

# ✅ CORRECT: Access JSON fields
data = result.get('data', [])
for item in data:
    item_id = item.get('id')
    # Safe dictionary access with .get()

# ❌ WRONG: Direct access without .get()
item_id = item['id']  # KeyError risk!
```

### Safe Dictionary Access

**Always use `.get()` for optional fields**:

```python
# ✅ CORRECT: Safe access with defaults
tractability = details.get('tractability', {})
small_molecule = tractability.get('smallmolecule', {})
category = small_molecule.get('top_category', 'Unknown')

# ❌ WRONG: Direct access (may raise KeyError)
category = details['tractability']['smallmolecule']['top_category']  # Risky!
```

### Handling ID Format Variations

```python
# Disease IDs can be MONDO or EFO format
disease_id = disease.get('id')

# Both formats work for associations
if disease_id.startswith('MONDO_'):
    print("MONDO format ID")
elif disease_id.startswith('EFO_'):
    print("EFO format ID")

# Use either format in API calls
get_target_disease_associations(diseaseId=disease_id)  # Works for both!
```

---

## Evidence Score Interpretation

### Overall Association Score

| Score Range | Strength | Interpretation | Action |
|-------------|----------|----------------|--------|
| **0.8 - 1.0** | **Very Strong** | Top-tier evidence | High-priority target |
| **0.6 - 0.8** | **Strong** | Robust evidence | Primary target list |
| **0.5 - 0.6** | **Good** | Solid evidence | Strong candidate |
| **0.3 - 0.5** | **Moderate** | Decent evidence | Secondary target list |
| **0.1 - 0.3** | **Weak** | Limited evidence | Exploratory only |
| **0.0 - 0.1** | **Very Weak** | Minimal evidence | Not recommended |

### Evidence Type Priorities (by Data Type)

**For drug discovery** (ranked by importance):

1. **`genetic_association`** - Most predictive of clinical success
2. **`known_drug`** - De-risked by approved drug precedents
3. **`somatic_mutation`** - Oncology targets
4. **`literature`** - Research support
5. **`affected_pathway`** - Mechanism validation
6. **`rna_expression`** - Expression validation
7. **`animal_model`** - Preclinical validation

**Filtering Strategy**:
```python
# Prioritize genetic evidence
for assoc in associations:
    genetic_score = assoc.get('datatypeScores', {}).get('genetic_association', 0)

    if genetic_score >= 0.7:
        print(f"High genetic evidence: {assoc.get('targetId')}")
```

---

## Common Use Cases

### Use Case 1: Target Validation for Drug Discovery

**Goal**: Find and validate targets for type 2 diabetes

```python
from mcp.servers.opentargets_mcp import search_diseases, get_disease_targets_summary, get_target_details

# Step 1: Find disease ID
diseases = search_diseases(query="type 2 diabetes", size=5)
diabetes_id = diseases['data'][0]['id']  # MONDO_0005148

# Step 2: Get top targets
targets = get_disease_targets_summary(
    diseaseId=diabetes_id,
    minScore=0.5,  # Strong evidence only
    size=20
)

# Step 3: Prioritize by genetic evidence
candidates = []
for assoc in targets.get('data', []):
    target_id = assoc.get('targetId')
    score = assoc.get('score')
    genetic = assoc.get('datatypeScores', {}).get('genetic_association', 0)

    if genetic >= 0.6:  # High genetic evidence
        candidates.append((target_id, score, genetic))

candidates.sort(key=lambda x: x[2], reverse=True)  # Sort by genetic score

# Step 4: Get details on top candidates
print("Top 5 genetically validated targets:")
for target_id, overall_score, genetic_score in candidates[:5]:
    details = get_target_details(id=target_id)

    symbol = details.get('approvedSymbol')
    name = details.get('approvedName')

    # Check druggability
    tractability = details.get('tractability', {})
    sm_tractable = tractability.get('smallmolecule', {}).get('top_category', 'Unknown')

    print(f"\n{symbol} ({target_id})")
    print(f"  Name: {name}")
    print(f"  Overall score: {overall_score:.2f}")
    print(f"  Genetic evidence: {genetic_score:.2f}")
    print(f"  Small molecule tractability: {sm_tractable}")
```

### Use Case 2: Competitive Landscape Analysis

**Goal**: Identify targets with approved drug precedents

```python
from mcp.servers.opentargets_mcp import get_disease_targets_summary

# Get all targets for obesity
targets = get_disease_targets_summary(
    diseaseId="EFO_0001073",  # Obesity
    minScore=0.0,  # Get all
    size=100
)

# Filter for targets with known drugs
drugged_targets = []
for assoc in targets.get('data', []):
    datatypes = assoc.get('datatypeScores', {})
    known_drug_score = datatypes.get('known_drug', 0)

    if known_drug_score > 0:  # Has approved drug precedent
        drugged_targets.append({
            'target': assoc.get('targetId'),
            'score': assoc.get('score'),
            'drug_score': known_drug_score
        })

drugged_targets.sort(key=lambda x: x['drug_score'], reverse=True)

print(f"Found {len(drugged_targets)} targets with approved drug precedents:")
for t in drugged_targets[:10]:
    print(f"  {t['target']}: drug score {t['drug_score']:.2f}")
```

### Use Case 3: Safety Assessment

**Goal**: Check safety liabilities for a target

```python
from mcp.servers.opentargets_mcp import search_targets, get_target_details

# Find target
targets = search_targets(query="GLP1R", size=1)
target_id = targets['data'][0]['id']

# Get details including safety
details = get_target_details(id=target_id)

symbol = details.get('approvedSymbol')
safety_liabilities = details.get('safetyLiabilities', [])

print(f"Safety assessment for {symbol}:")

if safety_liabilities:
    print(f"\n{len(safety_liabilities)} safety concerns identified:")
    for concern in safety_liabilities:
        event = concern.get('event', 'Unknown')
        effects = concern.get('effects', 'N/A')
        print(f"\n  Event: {event}")
        print(f"  Effects: {effects}")
else:
    print("\n  No known safety liabilities in Open Targets database")
```

### Use Case 4: Druggability Assessment

**Goal**: Assess tractability for small molecule and antibody approaches

```python
from mcp.servers.opentargets_mcp import search_targets, get_target_details

# Assess multiple targets
target_symbols = ["GLP1R", "DPP4", "SGLT2", "PPARG"]

for symbol in target_symbols:
    # Search
    result = search_targets(query=symbol, size=1)
    if not result.get('data'):
        continue

    target_id = result['data'][0]['id']

    # Get details
    details = get_target_details(id=target_id)

    # Extract tractability
    tractability = details.get('tractability', {})

    sm = tractability.get('smallmolecule', {})
    sm_category = sm.get('top_category', 'Unknown')

    ab = tractability.get('antibody', {})
    ab_category = ab.get('top_category', 'Unknown')

    print(f"\n{symbol}:")
    print(f"  Small molecule: {sm_category}")
    print(f"  Antibody: {ab_category}")

    # Recommendation
    if "Clinical Precedence" in sm_category:
        print(f"  ✅ RECOMMENDED: Small molecule approach (precedent exists)")
    elif "Clinical Precedence" in ab_category:
        print(f"  ✅ RECOMMENDED: Antibody approach (precedent exists)")
    elif "High confidence" in sm_category or "High confidence" in ab_category:
        print(f"  ⚠️  FEASIBLE: Tractable but no precedent")
    else:
        print(f"  ❌ CHALLENGING: Limited tractability")
```

### Use Case 5: Mechanism Exploration

**Goal**: Understand all diseases associated with a target

```python
from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations

# Find target
targets = search_targets(query="BRCA1", size=1)
target_id = targets['data'][0]['id']

# Get all disease associations
associations = get_target_disease_associations(
    targetId=target_id,
    minScore=0.3,  # Moderate+ evidence
    size=50
)

# Group by evidence type
by_evidence = {
    'genetic': [],
    'somatic': [],
    'literature': []
}

for assoc in associations.get('data', []):
    disease_id = assoc.get('diseaseId')
    score = assoc.get('score')
    datatypes = assoc.get('datatypeScores', {})

    # Classify by strongest evidence type
    if datatypes.get('genetic_association', 0) > 0.5:
        by_evidence['genetic'].append((disease_id, score))
    elif datatypes.get('somatic_mutation', 0) > 0.5:
        by_evidence['somatic'].append((disease_id, score))
    elif datatypes.get('literature', 0) > 0.5:
        by_evidence['literature'].append((disease_id, score))

print("BRCA1 disease associations by evidence type:")
print(f"\nGenetic associations: {len(by_evidence['genetic'])}")
for disease_id, score in by_evidence['genetic'][:5]:
    print(f"  {disease_id}: {score:.2f}")

print(f"\nSomatic mutation: {len(by_evidence['somatic'])}")
for disease_id, score in by_evidence['somatic'][:5]:
    print(f"  {disease_id}: {score:.2f}")
```

---

## Known Quirks & Limitations

### 1. ID Format Requirements (CRITICAL)

**Issue**: Must use correct ID formats for API calls

```python
# ✅ CORRECT
targetId="ENSG00000012048"  # Ensembl format
diseaseId="MONDO_0005148"   # MONDO format
diseaseId="EFO_0000305"     # EFO format also works

# ❌ WRONG
targetId="GLP1R"  # Gene symbol not accepted for targetId!
diseaseId="diabetes"  # Disease name not accepted for diseaseId!
```

**Workaround**: Always use search methods first to get IDs.

### 2. minScore Filtering (Post-Pagination)

**Behavior**: `minScore` filtering is applied **after** pagination, not during

**Example**:
```python
# Requests 1000 records, filters by score >= 0.5
result = get_target_disease_associations(
    diseaseId="MONDO_0004975",
    size=1000,
    minScore=0.5
)

# Server fetches 1000 records (10 pages)
# But only returns ~75 that have score >= 0.5
```

**Impact**:
- Returned count may be much less than requested `size`
- Server still fetches full `size` amount (affects performance)

**Best Practice**: Set `size` based on expected filtered results, not raw data size.

### 3. Optional Detail Fields

**Issue**: Detail endpoints may not return all fields

**Fields that may be missing**:
- `tractability` - Druggability data
- `safetyLiabilities` - Safety concerns
- `synonyms` - Disease synonyms
- `therapeuticAreas` - Disease classification

```python
# ✅ CORRECT: Safe access
tractability = details.get('tractability', {})
if tractability:
    # Use tractability data
else:
    print("No tractability data available")

# ❌ WRONG: Assumes field exists
category = details['tractability']['smallmolecule']['top_category']  # KeyError!
```

### 4. Token Usage Variation

**Issue**: Token usage varies significantly by method

**Measured token usage**:
- Search: 180-250 tokens
- Associations: ~1,350 tokens (6x search)
- Summaries: ~2,550 tokens (14x search)
- Details: 160-220 tokens

**Impact**: Summary methods use significantly more context

**Workaround**: Use associations method with filtering instead of summary when possible.

### 5. MONDO vs EFO IDs

**Issue**: Disease IDs may be in MONDO or EFO format

**Both formats work** for API calls, but results may mix formats:
```python
# Search may return MONDO ID
search_diseases("diabetes")  # Returns MONDO_0005148

# But association may show EFO ID
get_target_disease_associations(...)  # Returns EFO_0000305
```

**Workaround**: Accept both formats, use as-is in API calls.

### 6. Evidence Score Granularity

**Issue**: Overall scores are aggregated and may mask specific evidence

**Example**:
- Overall score: 0.50
- Genetic evidence: 0.90
- Literature: 0.10

**Impact**: High overall score doesn't guarantee strong genetic evidence

**Workaround**: Always check `datatypeScores` for evidence breakdown.

---

## Best Practices

### ✅ DO

1. **Use search methods to get IDs first**
   ```python
   # Step 1: Search
   targets = search_targets(query="GLP1R")
   target_id = targets['data'][0]['id']  # ENSG00000012048

   # Step 2: Use ID
   get_target_details(id=target_id)
   ```

2. **Filter by minScore for strong evidence**
   ```python
   minScore=0.5  # Strong associations only
   ```

3. **Check datatypeScores for evidence types**
   ```python
   genetic = assoc.get('datatypeScores', {}).get('genetic_association', 0)
   ```

4. **Use safe dictionary access**
   ```python
   tractability = details.get('tractability', {})
   ```

5. **Prioritize genetic evidence for drug discovery**
   ```python
   if genetic_score >= 0.6:
       # High-priority target
   ```

6. **Check tractability before target selection**
   ```python
   sm_category = tractability.get('smallmolecule', {}).get('top_category')
   if "Clinical Precedence" in sm_category:
       # De-risked target
   ```

### ❌ DON'T

1. **Don't use gene symbols as targetId**
   ```python
   # ❌ WRONG
   get_target_details(id="GLP1R")  # Error!

   # ✅ CORRECT
   get_target_details(id="ENSG00000012048")
   ```

2. **Don't assume all detail fields exist**
   ```python
   # ❌ WRONG
   category = details['tractability']['smallmolecule']  # KeyError risk!

   # ✅ CORRECT
   tractability = details.get('tractability', {})
   ```

3. **Don't rely on exact result counts**
   ```python
   # ❌ WRONG
   assert len(results['data']) == size  # May fail!

   # ✅ CORRECT
   results_count = len(results.get('data', []))  # Accept variable count
   ```

4. **Don't ignore evidence types**
   ```python
   # ❌ WRONG
   if score > 0.5:  # May be driven by literature only

   # ✅ CORRECT
   genetic = datatypes.get('genetic_association', 0)
   if genetic > 0.5:  # Check specific evidence
   ```

5. **Don't skip safety assessment**
   ```python
   # ✅ ALWAYS check safety
   safety = details.get('safetyLiabilities', [])
   ```

---

## FAQ

### Q1: What's the difference between MONDO and EFO IDs?

**A**: Both are disease ontology IDs.
- **MONDO** (Monarch Disease Ontology) - Primary format in Open Targets
- **EFO** (Experimental Factor Ontology) - Alternative format

Both work for API calls. Results may return either format.

### Q2: How do I convert gene symbols to Ensembl IDs?

**A**: Use `search_targets()`:
```python
result = search_targets(query="GLP1R", size=1)
ensembl_id = result['data'][0]['id']  # ENSG00000012048
```

### Q3: What minScore should I use?

**A**: Depends on use case:
- **Drug discovery**: `0.5+` (strong evidence only)
- **Target exploration**: `0.3+` (moderate+ evidence)
- **Comprehensive analysis**: `0.0` (all evidence)

### Q4: What does a 0.7 association score mean?

**A**: Strong association (0.6-0.8 range). This indicates robust evidence supporting the target-disease link. Check `datatypeScores` to see evidence breakdown.

### Q5: How do I prioritize targets by genetic evidence?

**A**: Filter by genetic_association score:
```python
genetic_score = assoc.get('datatypeScores', {}).get('genetic_association', 0)
if genetic_score >= 0.6:
    # High genetic evidence - prioritize
```

### Q6: What does "Clinical Precedence" tractability mean?

**A**: An approved drug already targets this protein/pathway. This de-risks the target significantly.

### Q7: Can I get all associations for a target?

**A**: Yes, with automatic pagination support:
```python
# Get up to 5,000 associations (50 pages)
get_target_disease_associations(
    targetId="ENSG00000012048",
    minScore=0.0,  # All evidence
    size=5000  # Fetches in batches of 100
)

# Or get all 12,874 Alzheimer's targets (if needed)
get_target_disease_associations(
    diseaseId="MONDO_0004975",
    minScore=0.0,
    size=15000  # Fetches all available
)
```

**Note**: Large requests (1,000+) take several seconds as the server fetches multiple pages.

### Q8: What if tractability data is missing?

**A**: Not all targets have tractability assessments. Use `.get()` to handle:
```python
tractability = details.get('tractability', {})
if not tractability:
    print("No tractability data available")
```

### Q9: How do I find drug targets with genetic evidence?

**A**: Use disease targets summary with high minScore:
```python
get_disease_targets_summary(
    diseaseId="MONDO_0005148",
    minScore=0.5,  # Strong evidence
    size=50
)

# Then check genetic evidence
for assoc in results['data']:
    genetic = assoc.get('datatypeScores', {}).get('genetic_association', 0)
```

### Q10: What's the difference between get_target_disease_associations and get_disease_targets_summary?

**A**: Same data, different perspectives:
- `get_target_disease_associations`: All associations (can filter by target OR disease)
- `get_disease_targets_summary`: Disease-centric view (requires diseaseId)

Use `get_target_disease_associations` for flexibility, `get_disease_targets_summary` for disease-specific analysis.

---

## Summary

**Open Targets MCP Server** provides genetic evidence for drug target validation:

✅ **Strengths**:
- Genetic association data (strongest predictor of clinical success)
- Target-disease evidence scores (0-1 scale)
- Druggability assessment (tractability)
- Safety liability prediction
- Approved drug precedents
- Evidence breakdown by type
- **Automatic pagination** (fetch up to 50,000 records)

⚠️ **Critical Requirements**:
- **Must use correct ID formats** (Ensembl for targets, MONDO/EFO for diseases)
- Search first to get IDs, then use for associations
- Check datatypeScores for evidence breakdown
- Use `.get()` for optional fields
- Be mindful of pagination performance for large datasets (1,000+ records)

🎯 **Best Use Cases**:
- Target validation for drug discovery
- Prioritization by genetic evidence
- Druggability assessment
- Safety screening
- Competitive landscape analysis
- **Comprehensive disease target profiling** (up to 12,874 targets for Alzheimer's)

📊 **Pagination Capabilities**:
- Automatic batching: 100 records per page
- Maximum size: 50,000 records (500 pages)
- Metadata tracking: requested/returned/total/filtered counts
- Client-side minScore filtering after pagination
- Performance: ~1-2 seconds per 100 records

**Always**: Search by name/symbol first → Get IDs → Use IDs for associations → Filter by genetic evidence → Check tractability and safety.
