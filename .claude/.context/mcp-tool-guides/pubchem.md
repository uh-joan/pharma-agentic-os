# PubChem MCP Server - Complete API Documentation

> **Access**: `mcp__pubchem-mcp-server__pubchem`
> **Database**: Over 110 million chemical compounds
> **Response Format**: JSON (structured data)
> **Purpose**: Compound properties, structure search, drug-likeness, molecular descriptors

---

## 🔴 CRITICAL: BROKEN METHODS - DO NOT USE

**Two methods are currently UNUSABLE**:

### 1. `get_safety_data` - Returns 21.9 MILLION tokens
- **Problem**: Returns entire safety database (21,900,000 tokens = 876x over MCP limit)
- **Impact**: Query will ALWAYS FAIL with token limit error
- **Status**: Broken - no field selection parameter available
- **Workaround**: See alternatives.py for `get_safety_data_alternative()` (99.998% token reduction)

### 2. `search_similar_compounds` - Returns 400 error
- **Problem**: Returns HTTP 400 Bad Request error
- **Impact**: Method is non-functional
- **Status**: Broken - API endpoint issue
- **Workaround**: See alternatives.py for `search_similar_compounds_alternative()` (uses FastSimilarity API)

**⚠️ DO NOT use these methods until fixed by MCP server maintainers.**

---

## Token Usage Guidelines

**Measured token usage by method**:

| Method | Tokens | Status | Recommendation |
|--------|--------|--------|----------------|
| `search_compounds` | ~200 | ✅ Excellent | Use for initial search |
| `get_compound_properties` | ~150 | ✅ **RECOMMENDED** | Use instead of get_compound_info |
| `get_compound_info` | ~3,000 | ⚠️ High (20x properties) | Avoid unless full details needed |
| `get_compound_synonyms` | ~6,000 | ⚠️ Very high | Use cautiously (popular drugs worst) |
| `get_safety_data` | 21,900,000 | 🔴 **BROKEN** | DO NOT USE |
| `search_similar_compounds` | N/A | 🔴 **BROKEN** | DO NOT USE |

**Best Practice**: Use `get_compound_properties` (150 tokens) instead of `get_compound_info` (3,000 tokens) for 95% token savings.

---

## Table of Contents

1. [When to Use PubChem](#when-to-use)
2. [Quick Reference](#quick-reference)
3. [Two-Step Workflow Pattern](#two-step-workflow-pattern)
4. [Methods Overview](#methods-overview)
5. [Method 1: search_compounds](#method-1-search_compounds)
6. [Method 2: get_compound_info](#method-2-get_compound_info)
7. [Method 3: search_by_smiles](#method-3-search_by_smiles)
8. [Method 4: get_compound_synonyms](#method-4-get_compound_synonyms)
9. [Method 5: get_compound_properties](#method-5-get_compound_properties)
10. [Method 6-7: Broken Methods](#method-6-7-broken-methods-do-not-use)
11. [Method 8: get_3d_conformers](#method-8-get_3d_conformers)
12. [Method 9: analyze_stereochemistry](#method-9-analyze_stereochemistry)
13. [Method 10: get_assay_info](#method-10-get_assay_info)
14. [Method 11: batch_compound_lookup](#method-11-batch_compound_lookup)
15. [Response Format & Parsing](#response-format--parsing)
16. [Drug-Likeness Analysis](#drug-likeness-analysis)
17. [Common Use Cases](#common-use-cases)
18. [Known Quirks & Limitations](#known-quirks--limitations)
19. [Best Practices](#best-practices)
20. [FAQ](#faq)

---

## When to Use

✅ **Use PubChem for**:
- Compound property lookups (MW, logP, TPSA)
- Structure searches (SMILES, InChI, CAS)
- Drug-likeness predictions (Lipinski's Rule of 5)
- Molecular descriptor calculations
- Chemical structure analysis
- Stereochemistry and chirality analysis
- Bioassay data lookup
- Batch compound processing

❌ **Don't use PubChem for**:
- Clinical trials → Use CT.gov MCP
- Drug approvals → Use FDA MCP
- Target validation → Use Open Targets MCP
- Literature search → Use PubMed MCP

---

## Quick Reference

| Method | Purpose | Key Parameters | Returns | Tokens |
|--------|---------|----------------|---------|--------|
| `search_compounds` | Find compounds | `query`, `search_type`, `max_records` | CID list | ~200 |
| `get_compound_properties` | Get properties | `cid`, `properties` | MW/logP/TPSA | ~150 ✅ |
| `get_compound_info` | Full details | `cid` | Complete data | ~3,000 ⚠️ |
| `get_compound_synonyms` | Get names | `cid` | All synonyms | ~6,000 ⚠️ |
| `search_by_smiles` | Structure match | `smiles`, `threshold` | Similar CIDs | Variable |
| `get_3d_conformers` | 3D structure | `cid`, `conformer_type` | Coordinates | Variable |
| `analyze_stereochemistry` | Chirality | `cid` | Stereocenter data | ~200 |
| `get_assay_info` | Assay details | `aid` | Assay metadata | Variable |
| `batch_compound_lookup` | Bulk processing | `cids`, `operation` | Batch results | Variable |

---

## Two-Step Workflow Pattern

**PubChem requires a two-step process for most queries**:

### Step 1: Search by Name → Get CID
```python
# Search for compound
result = search_compounds(query="aspirin", max_records=1)

# Extract CID (PubChem Compound ID)
cid = result['data'][0]['CID']  # e.g., "2244"
```

### Step 2: Use CID → Get Properties
```python
# Get molecular properties using CID
props = get_compound_properties(cid="2244")

# Extract properties
mw = props.get('MolecularWeight')  # 180.16
logp = props.get('XLogP')  # 1.2
tpsa = props.get('TPSA')  # 63.6
```

**Why two steps?**
- CID is the primary identifier for all PubChem data
- Name searches can have multiple matches
- CID ensures you get the exact compound

---

## Methods Overview

```json
{
  "method": "search_compounds",           // Search by name/CAS/formula
  "method": "get_compound_info",          // Full compound details (⚠️ 3k tokens)
  "method": "search_by_smiles",           // Exact SMILES match
  "method": "get_compound_synonyms",      // All names (⚠️ 6k tokens)
  "method": "get_compound_properties",    // MW/logP/TPSA (✅ 150 tokens - RECOMMENDED)
  "method": "search_similar_compounds",   // 🔴 BROKEN - DO NOT USE
  "method": "get_3d_conformers",          // 3D coordinates
  "method": "analyze_stereochemistry",    // Chirality analysis
  "method": "get_assay_info",             // Bioassay metadata
  "method": "get_safety_data",            // 🔴 BROKEN - DO NOT USE
  "method": "batch_compound_lookup"       // Bulk operations
}
```

---

## Method 1: search_compounds

**Purpose**: Search for compounds by name, CAS number, formula, or structure

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"search_compounds"` | Operation type |
| `query` | string | ✅ Yes | - | Any text | Search query |
| `search_type` | string | ❌ No | "name" | See enum below | Type of search |
| `max_records` | integer | ❌ No | 100 | 1-10000 | Maximum results |

**search_type values**:
- `"name"` - Compound name or CAS number (default)
- `"smiles"` - SMILES structure notation
- `"inchi"` - InChI identifier
- `"formula"` - Molecular formula
- `"cid"` - PubChem Compound ID
- `"sdf"` - Structure-Data File format

### Search Query Examples

#### By Name (Most Common)
```json
{
  "method": "search_compounds",
  "query": "aspirin",
  "max_records": 10
}
```

#### By CAS Number
```json
{
  "method": "search_compounds",
  "query": "50-78-2",
  "search_type": "name",
  "max_records": 5
}
```

#### By Molecular Formula
```json
{
  "method": "search_compounds",
  "query": "C9H8O4",
  "search_type": "formula",
  "max_records": 20
}
```

#### By SMILES
```json
{
  "method": "search_compounds",
  "query": "CC(=O)Oc1ccccc1C(=O)O",
  "search_type": "smiles",
  "max_records": 5
}
```

### Response Structure

```json
{
  "data": [
    {
      "CID": 2244,
      "MolecularFormula": "C9H8O4",
      "MolecularWeight": 180.16,
      "IUPACName": "2-acetyloxybenzoic acid",
      "Title": "Aspirin"
    }
  ],
  "total": 1
}
```

**Key fields**:
- `CID` - **PubChem Compound ID** (use for all subsequent queries)
- `MolecularFormula` - Chemical formula
- `MolecularWeight` - Molecular weight (Da)
- `IUPACName` - IUPAC systematic name
- `Title` - Common name

### Code Example

```python
from mcp.servers.pubchem_mcp import search_compounds

# Search by name
result = search_compounds(query="semaglutide", max_records=5)

# Extract CIDs for further analysis
for compound in result.get('data', []):
    cid = compound.get('CID')
    formula = compound.get('MolecularFormula')
    mw = compound.get('MolecularWeight')
    title = compound.get('Title', 'N/A')

    print(f"CID {cid}: {title}")
    print(f"  Formula: {formula}, MW: {mw}")
    print()

# Search by CAS number
aspirin = search_compounds(query="50-78-2", max_records=1)
cid = aspirin['data'][0]['CID']  # 2244
print(f"Aspirin CID: {cid}")
```

---

## Method 2: get_compound_info

**Purpose**: Get comprehensive compound details

⚠️ **WARNING: High token usage (~3,000 tokens)**
- Use `get_compound_properties` instead for 95% token savings
- Only use when full details required

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_compound_info"` | Operation type |
| `cid` | string OR integer | ✅ Yes | - | PubChem CID | Compound ID |

### Response Structure

```json
{
  "CID": 2244,
  "MolecularFormula": "C9H8O4",
  "MolecularWeight": 180.16,
  "CanonicalSMILES": "CC(=O)Oc1ccccc1C(=O)O",
  "InChI": "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)",
  "IUPACName": "2-acetyloxybenzoic acid",
  "Title": "Aspirin",
  "Description": "Aspirin is a salicylate...",
  "XLogP": 1.2,
  "TPSA": 63.6,
  "Complexity": 212
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import get_compound_info

# ⚠️ WARNING: Returns ~3,000 tokens
compound = get_compound_info(cid="2244")

# Extract comprehensive data
cid = compound.get('CID')
formula = compound.get('MolecularFormula')
mw = compound.get('MolecularWeight')
smiles = compound.get('CanonicalSMILES')
inchi = compound.get('InChI')
iupac = compound.get('IUPACName')
description = compound.get('Description')

print(f"CID: {cid}")
print(f"Formula: {formula}")
print(f"MW: {mw}")
print(f"SMILES: {smiles}")
print(f"InChI: {inchi}")
print(f"IUPAC: {iupac}")
print(f"\nDescription: {description}")
```

**Recommendation**: Use `get_compound_properties` instead (see Method 5) for 95% token savings.

---

## Method 3: search_by_smiles

**Purpose**: Find exact SMILES structure match

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"search_by_smiles"` | Operation type |
| `smiles` | string | ✅ Yes | - | SMILES notation | Query structure |
| `threshold` | integer | ❌ No | 90 | 0-100 | Similarity threshold |

### Query Example

```json
{
  "method": "search_by_smiles",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "threshold": 85
}
```

**Common SMILES examples**:
- Aspirin: `"CC(=O)Oc1ccccc1C(=O)O"`
- Caffeine: `"CN1C=NC2=C1C(=O)N(C(=O)N2C)C"`
- Ibuprofen: `"CC(C)Cc1ccc(cc1)C(C)C(=O)O"`

### Response Structure

```json
{
  "data": [
    {
      "CID": 2244,
      "Similarity": 100.0
    },
    {
      "CID": 2157,
      "Similarity": 87.3
    }
  ]
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import search_by_smiles

# Find compounds with similar structure to aspirin
results = search_by_smiles(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    threshold=85
)

# Analyze similarity distribution
for compound in results.get('data', []):
    cid = compound.get('CID')
    similarity = compound.get('Similarity', 0)
    print(f"CID {cid}: {similarity:.1f}% similar")
```

---

## Method 4: get_compound_synonyms

**Purpose**: Get all names and synonyms for a compound

⚠️ **WARNING: High token usage (~6,000 tokens for popular drugs)**
- Use cautiously - popular drugs have hundreds of synonyms
- Consider limiting to first N synonyms if full list not needed

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_compound_synonyms"` | Operation type |
| `cid` | string OR integer | ✅ Yes | - | PubChem CID | Compound ID |

### Response Structure

```json
{
  "Synonyms": [
    "Aspirin",
    "Acetylsalicylic acid",
    "2-Acetoxybenzoic acid",
    "ASA",
    "Acylpyrin",
    "... (hundreds more for popular drugs)"
  ]
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import get_compound_synonyms

# ⚠️ WARNING: Returns ~6,000 tokens for popular drugs
synonyms = get_compound_synonyms(cid="2244")  # Aspirin

# Extract names
names = synonyms.get('Synonyms', [])
print(f"Found {len(names)} names for aspirin:")

# Show first 10 only
for name in names[:10]:
    print(f"  - {name}")

if len(names) > 10:
    print(f"  ... and {len(names) - 10} more")
```

---

## Method 5: get_compound_properties

**Purpose**: Get molecular properties for drug-likeness analysis

✅ **RECOMMENDED**: Use this instead of `get_compound_info`
- **Token usage**: ~150 tokens (vs 3,000 for get_compound_info)
- **95% token savings**
- Perfect for drug-likeness calculations

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_compound_properties"` | Operation type |
| `cid` | string OR integer | ✅ Yes | - | PubChem CID | Compound ID |
| `properties` | array | ❌ No | Common props | Property names | Specific properties to retrieve |

**Common properties** (returned by default):
- `MolecularWeight` - Molecular weight (Da)
- `XLogP` - Lipophilicity (partition coefficient)
- `TPSA` - Topological polar surface area (Ų)
- `HBondDonorCount` - Hydrogen bond donors
- `HBondAcceptorCount` - Hydrogen bond acceptors
- `RotatableBondCount` - Rotatable bonds
- `Complexity` - Structural complexity score

### Query Example

```json
{
  "method": "get_compound_properties",
  "cid": "2244",
  "properties": ["MolecularWeight", "XLogP", "TPSA", "HBondDonorCount", "HBondAcceptorCount"]
}
```

### Response Structure

```json
{
  "MolecularWeight": 180.16,
  "XLogP": 1.2,
  "TPSA": 63.6,
  "HBondDonorCount": 1,
  "HBondAcceptorCount": 4,
  "RotatableBondCount": 3,
  "Complexity": 212.05
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import get_compound_properties

# ✅ RECOMMENDED: Only ~150 tokens
props = get_compound_properties(cid="2244")  # Aspirin

# Extract drug-likeness properties
mw = props.get('MolecularWeight')
logp = props.get('XLogP')
tpsa = props.get('TPSA')
hbd = props.get('HBondDonorCount')
hba = props.get('HBondAcceptorCount')

print(f"Molecular Weight: {mw} Da")
print(f"LogP: {logp}")
print(f"TPSA: {tpsa} Ų")
print(f"H-bond donors: {hbd}")
print(f"H-bond acceptors: {hba}")

# Check Lipinski's Rule of 5
lipinski_pass = (
    mw <= 500 and
    logp <= 5 and
    hbd <= 5 and
    hba <= 10
)
print(f"\nLipinski compliant: {lipinski_pass}")
```

---

## Method 6-7: Broken Methods - DO NOT USE

### Method 6: search_similar_compounds - 🔴 BROKEN

**Problem**: Returns HTTP 400 Bad Request error
**Status**: Non-functional
**DO NOT USE**

```python
# ❌ DO NOT USE - Will return 400 error
# search_similar_compounds(smiles="...", threshold=90)
```

**Workaround**: See `.claude/mcp/servers/pubchem_mcp/alternatives.py` for `search_similar_compounds_alternative()`

### Method 7: get_safety_data - 🔴 BROKEN

**Problem**: Returns 21.9 MILLION tokens (876x over MCP 25k limit)
**Status**: Unusable - query will always fail
**DO NOT USE**

```python
# ❌ DO NOT USE - Will exceed token limit
# get_safety_data(cid="2244")
```

**Workaround**: See `.claude/mcp/servers/pubchem_mcp/alternatives.py` for `get_safety_data_alternative()` (99.998% token reduction)

---

## Method 8: get_3d_conformers

**Purpose**: Get 3D structural conformer data

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_3d_conformers"` | Operation type |
| `cid` | string OR integer | ✅ Yes | - | PubChem CID | Compound ID |
| `conformer_type` | string | ❌ No | "3d" | "3d" or "2d" | Conformer type |

### Query Example

```json
{
  "method": "get_3d_conformers",
  "cid": "2244",
  "conformer_type": "3d"
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import get_3d_conformers

# Get 3D conformers for aspirin
conformers = get_3d_conformers(cid="2244")

# Extract coordinate data
coords_3d = conformers.get('Conformers', [])
print(f"Found {len(coords_3d)} 3D conformers")

# Process first conformer
if coords_3d:
    conformer = coords_3d[0]
    atoms = conformer.get('Atoms', [])
    print(f"First conformer has {len(atoms)} atoms")
```

---

## Method 9: analyze_stereochemistry

**Purpose**: Analyze stereochemistry and chirality

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"analyze_stereochemistry"` | Operation type |
| `cid` | string OR integer | ✅ Yes | - | PubChem CID | Compound ID |

### Query Example

```json
{
  "method": "analyze_stereochemistry",
  "cid": "2244"
}
```

### Response Structure

```json
{
  "StereocentersCount": 2,
  "DefinedStereocenters": 2,
  "UndefinedStereocenters": 0,
  "ChiralCenters": [...]
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import analyze_stereochemistry

# Analyze chirality for compound
stereo = analyze_stereochemistry(cid="2244")

stereocenters = stereo.get('StereocentersCount', 0)
defined = stereo.get('DefinedStereocenters', 0)
undefined = stereo.get('UndefinedStereocenters', 0)

print(f"Total stereocenters: {stereocenters}")
print(f"Defined: {defined}")
print(f"Undefined: {undefined}")

if undefined > 0:
    print("⚠️ Warning: Undefined stereocenters present")
```

---

## Method 10: get_assay_info

**Purpose**: Get bioassay metadata and details

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_assay_info"` | Operation type |
| `aid` | integer | ✅ Yes | - | PubChem AID | Assay ID |
| `target` | string | ❌ No | - | Any text | Target name filter |
| `activity_type` | string | ❌ No | - | Any text | Activity type (IC50, EC50, Ki) |
| `activity_outcome` | string | ❌ No | "all" | See enum | Filter by outcome |
| `source` | string | ❌ No | - | Any text | Data source (ChEMBL, NCGC) |

**activity_outcome values**:
- `"active"` - Active compounds only
- `"inactive"` - Inactive compounds only
- `"inconclusive"` - Inconclusive results
- `"all"` - All outcomes (default)

### Query Example

```json
{
  "method": "get_assay_info",
  "aid": 1234,
  "activity_outcome": "active"
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import get_assay_info

# Get assay details
assay = get_assay_info(aid=1234, activity_outcome="active")

# Extract assay metadata
name = assay.get('AssayName')
target = assay.get('Target')
description = assay.get('Description')

print(f"Assay: {name}")
print(f"Target: {target}")
print(f"Description: {description}")
```

---

## Method 11: batch_compound_lookup

**Purpose**: Bulk processing of multiple compounds (up to 200)

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"batch_compound_lookup"` | Operation type |
| `cids` | array | ✅ Yes | - | Max 200 CIDs | Array of PubChem CIDs |
| `operation` | string | ❌ No | "property" | See enum | Batch operation type |

**operation values**:
- `"property"` - Get properties for all compounds (default)
- `"synonyms"` - Get synonyms for all compounds
- `"classification"` - Get classifications
- `"description"` - Get descriptions

### Query Example

```json
{
  "method": "batch_compound_lookup",
  "cids": [2244, 3672, 2157],
  "operation": "property"
}
```

### Code Example

```python
from mcp.servers.pubchem_mcp import batch_compound_lookup

# Get properties for multiple compounds
cids = [2244, 3672, 2157]  # Aspirin, Caffeine, Salicylic acid

results = batch_compound_lookup(
    cids=cids,
    operation="property"
)

# Process batch results
for compound in results.get('data', []):
    cid = compound.get('CID')
    mw = compound.get('MolecularWeight')
    logp = compound.get('XLogP')

    print(f"CID {cid}: MW={mw}, LogP={logp}")
```

---

## Response Format & Parsing

### JSON Structure (All Methods)

PubChem returns structured JSON with consistent patterns.

**General pattern**:
```python
result = search_compounds(...)

# ✅ CORRECT: Access JSON fields safely
data = result.get('data', [])
for compound in data:
    cid = compound.get('CID')
    mw = compound.get('MolecularWeight', 0)

# ❌ WRONG: Direct access without .get()
cid = compound['CID']  # KeyError risk!
```

### Safe Dictionary Access

**Always use `.get()` for optional fields**:

```python
# ✅ CORRECT: Safe access with defaults
props = get_compound_properties(cid="2244")
mw = props.get('MolecularWeight', 0)
logp = props.get('XLogP', 0)
tpsa = props.get('TPSA', 0)

# ❌ WRONG: Direct access
mw = props['MolecularWeight']  # KeyError if missing!
```

---

## Drug-Likeness Analysis

### Lipinski's Rule of 5

**Criteria for oral bioavailability**:
- Molecular Weight ≤ 500 Da
- LogP ≤ 5
- H-bond donors ≤ 5
- H-bond acceptors ≤ 10

```python
from mcp.servers.pubchem_mcp import search_compounds, get_compound_properties

# Step 1: Search for compound
result = search_compounds(query="semaglutide", max_records=1)
cid = result['data'][0]['CID']

# Step 2: Get properties
props = get_compound_properties(cid=cid)

# Step 3: Check Lipinski's Rule of 5
mw = props.get('MolecularWeight', 0)
logp = props.get('XLogP', 0)
hbd = props.get('HBondDonorCount', 0)
hba = props.get('HBondAcceptorCount', 0)

lipinski_pass = (
    mw <= 500 and
    logp <= 5 and
    hbd <= 5 and
    hba <= 10
)

print(f"Lipinski's Rule of 5: {'PASS' if lipinski_pass else 'FAIL'}")
print(f"  MW: {mw} Da ({'✓' if mw <= 500 else '✗'})")
print(f"  LogP: {logp} ({'✓' if logp <= 5 else '✗'})")
print(f"  H-bond donors: {hbd} ({'✓' if hbd <= 5 else '✗'})")
print(f"  H-bond acceptors: {hba} ({'✓' if hba <= 10 else '✗'})")
```

### Veber's Rules (Oral Bioavailability)

**Additional criteria**:
- Rotatable bonds ≤ 10
- TPSA ≤ 140 Ų

```python
rot_bonds = props.get('RotatableBondCount', 0)
tpsa = props.get('TPSA', 0)

veber_pass = (
    rot_bonds <= 10 and
    tpsa <= 140
)

print(f"\nVeber's Rules: {'PASS' if veber_pass else 'FAIL'}")
print(f"  Rotatable bonds: {rot_bonds} ({'✓' if rot_bonds <= 10 else '✗'})")
print(f"  TPSA: {tpsa} Ų ({'✓' if tpsa <= 140 else '✗'})")
```

---

## Common Use Cases

### Use Case 1: Compound Property Lookup

**Goal**: Get molecular properties for drug-likeness analysis

```python
from mcp.servers.pubchem_mcp import search_compounds, get_compound_properties

# Search by name
result = search_compounds(query="ibuprofen", max_records=1)
cid = result['data'][0]['CID']

# Get properties (✅ Only ~150 tokens)
props = get_compound_properties(cid=cid)

# Extract key properties
print(f"Ibuprofen (CID {cid}):")
print(f"  MW: {props.get('MolecularWeight')} Da")
print(f"  LogP: {props.get('XLogP')}")
print(f"  TPSA: {props.get('TPSA')} Ų")
print(f"  Complexity: {props.get('Complexity')}")
```

### Use Case 2: Batch Drug-Likeness Screening

**Goal**: Screen multiple compounds for drug-likeness

```python
from mcp.servers.pubchem_mcp import search_compounds, batch_compound_lookup

# Search for multiple compounds
compounds = ["aspirin", "caffeine", "ibuprofen", "paracetamol"]
cids = []

for name in compounds:
    result = search_compounds(query=name, max_records=1)
    if result.get('data'):
        cids.append(result['data'][0]['CID'])

# Batch get properties
batch_results = batch_compound_lookup(cids=cids, operation="property")

# Screen for Lipinski compliance
print("Drug-Likeness Screening:")
for compound in batch_results.get('data', []):
    cid = compound.get('CID')
    mw = compound.get('MolecularWeight', 0)
    logp = compound.get('XLogP', 0)
    hbd = compound.get('HBondDonorCount', 0)
    hba = compound.get('HBondAcceptorCount', 0)

    lipinski = (mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10)

    print(f"\nCID {cid}: {'✓ PASS' if lipinski else '✗ FAIL'}")
    print(f"  MW={mw}, LogP={logp}, HBD={hbd}, HBA={hba}")
```

### Use Case 3: Structure Search

**Goal**: Find compounds with similar structures

```python
from mcp.servers.pubchem_mcp import search_compounds, search_by_smiles

# Get SMILES for query compound
result = search_compounds(query="aspirin", max_records=1)
cid = result['data'][0]['CID']

# Get compound info to extract SMILES
compound = get_compound_info(cid=cid)
smiles = compound.get('CanonicalSMILES')

print(f"Query SMILES: {smiles}")

# Find similar structures (⚠️ Method is broken - use alternatives.py)
# similar = search_by_smiles(smiles=smiles, threshold=85)
```

### Use Case 4: CAS Number Lookup

**Goal**: Convert CAS numbers to PubChem CIDs

```python
from mcp.servers.pubchem_mcp import search_compounds

# CAS numbers for common drugs
cas_numbers = {
    "50-78-2": "Aspirin",
    "58-08-2": "Caffeine",
    "15687-27-1": "Ibuprofen"
}

print("CAS Number → PubChem CID Mapping:")
for cas, expected_name in cas_numbers.items():
    result = search_compounds(query=cas, max_records=1)

    if result.get('data'):
        cid = result['data'][0]['CID']
        title = result['data'][0].get('Title', 'Unknown')
        print(f"  {cas} ({expected_name}): CID {cid} - {title}")
```

### Use Case 5: Stereochemistry Analysis

**Goal**: Analyze chiral centers for enantiomers

```python
from mcp.servers.pubchem_mcp import search_compounds, analyze_stereochemistry

# Search for chiral drug
result = search_compounds(query="ibuprofen", max_records=1)
cid = result['data'][0]['CID']

# Analyze stereochemistry
stereo = analyze_stereochemistry(cid=cid)

stereocenters = stereo.get('StereocentersCount', 0)
defined = stereo.get('DefinedStereocenters', 0)
undefined = stereo.get('UndefinedStereocenters', 0)

print(f"Ibuprofen Stereochemistry Analysis:")
print(f"  Total stereocenters: {stereocenters}")
print(f"  Defined: {defined}")
print(f"  Undefined: {undefined}")

if stereocenters > 0:
    print(f"\n⚠️ Chiral compound - enantiomers may have different activity")
```

---

## Known Quirks & Limitations

### 1. 🔴 Broken Methods (CRITICAL)

**Issue**: Two methods are completely unusable

**`get_safety_data`**:
- Returns 21.9M tokens (876x over limit)
- Query always fails
- Workaround: Use alternatives.py

**`search_similar_compounds`**:
- Returns HTTP 400 error
- Non-functional
- Workaround: Use alternatives.py

### 2. Token Usage Variation

**Issue**: Methods vary significantly in token usage

```python
# ✅ Efficient
get_compound_properties(cid)  # ~150 tokens

# ⚠️ High usage
get_compound_info(cid)  # ~3,000 tokens (20x more!)
get_compound_synonyms(cid)  # ~6,000 tokens (40x more!)
```

**Recommendation**: Always use `get_compound_properties` for molecular data.

### 3. Two-Step Workflow Required

**Issue**: Must search by name first, then query by CID

```python
# ❌ WRONG: Can't query properties directly by name
# props = get_compound_properties(query="aspirin")  # Error!

# ✅ CORRECT: Two-step process
result = search_compounds(query="aspirin", max_records=1)
cid = result['data'][0]['CID']
props = get_compound_properties(cid=cid)
```

### 4. CID Format Flexibility

**Issue**: CID can be string or integer

```python
# Both work
get_compound_properties(cid="2244")  # String
get_compound_properties(cid=2244)    # Integer
```

**Recommendation**: Use string format for consistency.

### 5. Synonyms for Popular Drugs

**Issue**: Popular drugs have hundreds of synonyms (high token usage)

```python
# Aspirin: ~200 synonyms (~6k tokens)
# Ibuprofen: ~300 synonyms (~8k tokens)
# Caffeine: ~400 synonyms (~10k tokens)
```

**Workaround**: Limit to first N synonyms if full list not needed.

### 6. max_records Upper Limit

**Issue**: Maximum 10,000 results per search

```python
# ✅ Valid
search_compounds(query="...", max_records=10000)

# ❌ Invalid (exceeds limit)
# search_compounds(query="...", max_records=20000)  # Error!
```

**Recommendation**: Use 5-10 for most queries to minimize tokens.

---

## Best Practices

### ✅ DO

1. **Use get_compound_properties instead of get_compound_info**
   ```python
   # ✅ RECOMMENDED (150 tokens)
   props = get_compound_properties(cid="2244")

   # ❌ AVOID (3,000 tokens)
   # info = get_compound_info(cid="2244")
   ```

2. **Follow two-step workflow**
   ```python
   # Step 1: Name → CID
   result = search_compounds(query="aspirin")
   cid = result['data'][0]['CID']

   # Step 2: CID → Properties
   props = get_compound_properties(cid=cid)
   ```

3. **Limit max_records for searches**
   ```python
   search_compounds(query="...", max_records=5)  # Not 100
   ```

4. **Use safe dictionary access**
   ```python
   mw = props.get('MolecularWeight', 0)
   ```

5. **Check Lipinski's Rule of 5 for drug-likeness**
   ```python
   lipinski_pass = (mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10)
   ```

### ❌ DON'T

1. **Don't use broken methods**
   ```python
   # ❌ DO NOT USE
   # get_safety_data(cid="2244")  # 21.9M tokens!
   # search_similar_compounds(...)  # Returns 400 error!
   ```

2. **Don't use get_compound_info for molecular properties**
   ```python
   # ❌ WRONG (3,000 tokens)
   # info = get_compound_info(cid="2244")

   # ✅ CORRECT (150 tokens)
   props = get_compound_properties(cid="2244")
   ```

3. **Don't request excessive synonyms**
   ```python
   # ❌ AVOID for popular drugs (6k+ tokens)
   # synonyms = get_compound_synonyms(cid="2244")
   ```

4. **Don't use direct dictionary access**
   ```python
   # ❌ WRONG
   mw = props['MolecularWeight']  # KeyError risk!

   # ✅ CORRECT
   mw = props.get('MolecularWeight', 0)
   ```

5. **Don't exceed batch limit**
   ```python
   # ❌ WRONG (exceeds 200 limit)
   # batch_compound_lookup(cids=list(range(300)))

   # ✅ CORRECT (within limit)
   batch_compound_lookup(cids=cids[:200])
   ```

---

## FAQ

### Q1: How do I get molecular weight and logP for a compound?

**A**: Use two-step workflow with `get_compound_properties`:
```python
# Step 1: Name → CID
result = search_compounds(query="aspirin", max_records=1)
cid = result['data'][0]['CID']

# Step 2: CID → Properties
props = get_compound_properties(cid=cid)
mw = props.get('MolecularWeight')
logp = props.get('XLogP')
```

### Q2: Why should I avoid get_compound_info?

**A**: Token usage:
- `get_compound_info`: ~3,000 tokens
- `get_compound_properties`: ~150 tokens (20x less!)

Use properties for 95% token savings.

### Q3: How do I check if a compound is drug-like?

**A**: Use Lipinski's Rule of 5:
```python
props = get_compound_properties(cid=cid)
mw = props.get('MolecularWeight', 0)
logp = props.get('XLogP', 0)
hbd = props.get('HBondDonorCount', 0)
hba = props.get('HBondAcceptorCount', 0)

lipinski = (mw <= 500 and logp <= 5 and hbd <= 5 and hba <= 10)
```

### Q4: Can I search by CAS number?

**A**: Yes, use `search_compounds` with `search_type="name"`:
```python
result = search_compounds(query="50-78-2", search_type="name")
```

### Q5: What's the difference between CID and CAS?

**A**:
- **CID** - PubChem Compound ID (PubChem's internal ID)
- **CAS** - CAS Registry Number (unique chemical identifier)

Both identify compounds but CID is used for PubChem queries.

### Q6: Can I search by molecular formula?

**A**: Yes:
```python
result = search_compounds(query="C9H8O4", search_type="formula")
```

### Q7: How do I get SMILES for a compound?

**A**: Use `get_compound_info` (⚠️ high tokens) or search:
```python
info = get_compound_info(cid="2244")
smiles = info.get('CanonicalSMILES')
```

### Q8: Why do broken methods exist if they don't work?

**A**: MCP server implementation issues. Use alternatives.py workarounds until fixed.

### Q9: Can I batch process compounds?

**A**: Yes, up to 200 compounds:
```python
batch_compound_lookup(cids=[2244, 3672, 2157], operation="property")
```

### Q10: How do I find stereoisomers?

**A**: Use `analyze_stereochemistry`:
```python
stereo = analyze_stereochemistry(cid="2244")
stereocenters = stereo.get('StereocentersCount', 0)
```

---

## Summary

**PubChem MCP Server** provides access to 110+ million compounds:

✅ **Strengths**:
- Comprehensive molecular property data
- Structure search capabilities
- Drug-likeness prediction (Lipinski, Veber)
- Batch processing (up to 200 compounds)
- Stereochemistry analysis
- CAS number lookup

⚠️ **Critical Limitations**:
- **Two methods BROKEN** (get_safety_data, search_similar_compounds)
- Two-step workflow required (name → CID → properties)
- High token usage for get_compound_info (~3k) and get_compound_synonyms (~6k)

🎯 **Best Use Cases**:
- Molecular property lookup
- Drug-likeness screening
- Structure-based searches
- Batch compound analysis
- Lipinski/Veber compliance checking

**Always**:
- Use `get_compound_properties` (not `get_compound_info`) - 95% token savings
- Follow two-step workflow (search → get CID → query properties)
- Avoid broken methods (use alternatives.py)
- Limit max_records to 5-10 for searches
