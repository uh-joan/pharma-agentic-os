# NLM Codes MCP Server - Complete API Guide

**Server**: `nlm-codes-mcp`
**Tool**: `nlm_ct_codes`
**Data Source**: National Library of Medicine Clinical Tables API
**Response Format**: JSON
**Coverage**: ICD-10-CM, ICD-11, HCPCS, NPI, HPO, LOINC, and more

---

## 🔴 CRITICAL CODING SYSTEMS

### 11 Different Coding Systems

```python
# Medical Diagnosis Codes
method = "icd-10-cm"  # US diagnosis codes (70,000+ codes)
method = "icd-11"     # WHO international codes (17,000+ codes)

# Procedure/Equipment Codes
method = "hcpcs-LII"  # Healthcare procedures, equipment, drugs

# Provider Identifiers
method = "npi-organizations"  # Healthcare organizations
method = "npi-individuals"    # Healthcare providers

# Clinical Vocabularies
method = "hpo-vocabulary"     # Human phenotype ontology
method = "loinc-questions"    # Lab test codes
method = "rx-terms"           # Drug terminology

# Condition Codes
method = "conditions"         # Medical conditions with ICD mappings
```

---

## Quick Reference

### Coding Systems

| System | Coverage | Common Use |
|--------|----------|------------|
| `icd-10-cm` | 70,000+ diagnosis codes | US medical billing, EHR |
| `icd-11` | 17,000+ international codes | WHO global standard |
| `hcpcs-LII` | Procedures, equipment, drugs | Medicare billing |
| `npi-organizations` | Healthcare organizations | Provider lookup |
| `npi-individuals` | Individual providers | Physician search |
| `hpo-vocabulary` | Phenotypic abnormalities | Rare disease research |
| `conditions` | 2,400+ medical conditions | ICD-9/ICD-10 mappings |
| `rx-terms` | Drug name/route pairs | Medication terminology |
| `loinc-questions` | Lab tests & measurements | Clinical observations |
| `ncbi-genes` | Human gene information | Genetic research |
| `major-surgeries-implants` | 280+ surgical procedures | Procedure tracking |

---

## Common Search Patterns

### Pattern 1: ICD-10-CM Diagnosis Code Lookup
```python
from mcp.servers.nlm_codes_mcp import nlm_ct_codes

# Search for hypertension codes
results = nlm_ct_codes(
    method="icd-10-cm",
    terms="hypertension",
    maxList=25
)

print("Hypertension ICD-10-CM Codes:")
for code in results['codes']:
    code_val = code['code']
    description = code['display']
    print(f"{code_val}: {description}")

# Output:
# I10: Essential (primary) hypertension
# I11.0: Hypertensive heart disease with heart failure
# I11.9: Hypertensive heart disease without heart failure
# I12.0: Hypertensive chronic kidney disease with stage 5 CKD
```

### Pattern 2: HCPCS Procedure Code Search
```python
# Find wheelchair equipment codes
results = nlm_ct_codes(
    method="hcpcs-LII",
    terms="wheelchair",
    maxList=50
)

print("Wheelchair HCPCS Codes:")
for code in results['codes']:
    hcpcs_code = code['code']
    description = code['short_desc']
    print(f"{hcpcs_code}: {description}")

# Output:
# E0950: Wheelchair accessory, tray, each
# E1161: Manual adult size wheelchair
# K0001: Standard wheelchair
# K0002: Standard hemi (low seat) wheelchair
```

### Pattern 3: NPI Provider Search
```python
# Find cardiologists in California
results = nlm_ct_codes(
    method="npi-individuals",
    terms="cardiology",
    additionalQuery="addr_practice.state:CA",
    maxList=25
)

print("California Cardiologists:")
for provider in results['results']:
    npi = provider['NPI']
    name = provider['name.full']
    city = provider.get('addr_practice.city', 'Unknown')
    print(f"{name} (NPI: {npi}) - {city}, CA")
```

### Pattern 4: Drug Terminology (RxTerms)
```python
# Search for diabetes medications
results = nlm_ct_codes(
    method="rx-terms",
    terms="metformin",
    maxList=20
)

print("Metformin Formulations:")
for drug in results['drugs']:
    display_name = drug['DISPLAY_NAME']
    strengths = drug.get('STRENGTHS_AND_FORMS', [])

    print(f"\n{display_name}")
    if strengths:
        print(f"  Forms: {', '.join(strengths[:3])}")
```

### Pattern 5: HPO Phenotype Vocabulary
```python
# Search for cardiac phenotypes
results = nlm_ct_codes(
    method="hpo-vocabulary",
    terms="cardiac arrhythmia",
    maxList=15
)

print("Cardiac Arrhythmia Phenotypes:")
for phenotype in results['terms']:
    hpo_id = phenotype['id']
    name = phenotype['name']
    definition = phenotype.get('definition', 'N/A')

    print(f"\n{hpo_id}: {name}")
    if definition != 'N/A':
        print(f"  {definition[:100]}...")
```

### Pattern 6: Medical Conditions with ICD Mappings
```python
# Search for gastroenteritis conditions
results = nlm_ct_codes(
    method="conditions",
    terms="gastroenteritis",
    maxList=20
)

print("Gastroenteritis Conditions:")
for condition in results['conditions']:
    consumer_name = condition['consumer_name']
    primary_name = condition['primary_name']
    icd10_codes = condition.get('icd10cm_codes', [])
    icd9_code = condition.get('term_icd9_code', 'N/A')

    print(f"\n{consumer_name} ({primary_name})")
    if icd10_codes:
        print(f"  ICD-10: {', '.join(icd10_codes[:3])}")
    print(f"  ICD-9: {icd9_code}")
```

---

## Token Usage Guidelines

| Coding System | Approx. Tokens per Result | Recommendation |
|--------------|---------------------------|----------------|
| ICD-10-CM | 50-100 | ✅ Efficient code lookup |
| HCPCS-LII | 80-150 | ✅ Good for procedure search |
| NPI searches | 100-200 | ⚠️ Use maxList parameter |
| HPO vocabulary | 150-300 | ✅ Good for phenotype research |
| Conditions | 100-200 | ✅ Efficient ICD mapping |
| RxTerms | 100-180 | ✅ Good drug terminology |

**Token Optimization Tips**:
1. Always set `maxList` parameter (default can be large)
2. Use `additionalQuery` to filter results server-side
3. Use specific search terms to narrow results
4. Combine with `offset` for pagination
5. Request only needed fields with `displayFields`

---

## Summary

**NLM Codes MCP Server** provides comprehensive clinical coding systems:

✅ **11 coding systems** from diagnosis to procedures to providers
✅ **70,000+ ICD-10-CM codes** for US diagnoses
✅ **17,000+ ICD-11 codes** for international use
✅ **HCPCS codes** for procedures and equipment
✅ **NPI provider lookup** for organizations and individuals
✅ **HPO phenotype vocabulary** for rare disease research
✅ **Drug terminology (RxTerms)** for medication coding
✅ **LOINC codes** for lab tests and measurements

**Critical Pattern**: Choose correct coding system for your use case (ICD vs HCPCS vs NPI vs HPO)

**Token Efficient**: Set maxList parameter, use additionalQuery for filtering, request specific fields

**Perfect For**: Medical coding, EHR integration, provider lookups, clinical research, rare disease phenotyping, drug terminology standardization
