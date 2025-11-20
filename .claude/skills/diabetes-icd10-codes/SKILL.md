---
name: get_diabetes_icd10_codes
description: >
  Search for diabetes-related ICD-10 codes using the NLM Clinical Tables API.
  Returns comprehensive list of diabetes diagnosis codes organized by category
  (Type 1, Type 2, drug-induced, pregnancy-related, etc.). Useful for medical
  coding, billing, research data extraction, and clinical documentation.
  Trigger keywords: ICD-10, diabetes codes, medical coding, diagnosis codes,
  billing codes, Type 1 diabetes, Type 2 diabetes, gestational diabetes.
category: regulatory
mcp_servers:
  - nlm_codes_mcp
patterns:
  - json_parsing
  - categorization
data_scope:
  total_results: 50
  geographical: US (ICD-10-CM)
  temporal: Current coding standards
created: 2025-11-20
last_updated: 2025-11-20
complexity: simple
execution_time: ~1 second
token_efficiency: ~99% reduction vs raw API response
---

# get_diabetes_icd10_codes

## Purpose

Search for diabetes-related ICD-10 codes using the National Library of Medicine's Clinical Tables API. Returns a comprehensive list of diabetes diagnosis codes organized by category for medical coding, billing, and research purposes.

## Usage

Use this skill when you need:
- ICD-10 codes for diabetes diagnoses
- Medical coding for billing/insurance
- Research data extraction using diagnosis codes
- Clinical documentation support
- Understanding diabetes code hierarchy

**Trigger keywords:** ICD-10, diabetes codes, medical coding, diagnosis codes, billing codes

## Implementation Details

**Data Source:** NLM Clinical Tables API (ICD-10-CM codes)

**Code Categories:**
- E08: Diabetes due to underlying condition
- E09: Drug or chemical induced diabetes
- E10: Type 1 diabetes mellitus
- E11: Type 2 diabetes mellitus
- E13: Other specified diabetes mellitus
- O24: Pre-existing diabetes in pregnancy

**Processing:**
1. Query NLM API for "diabetes" term
2. Parse response (format: [count, [codes], [descriptions]])
3. Combine codes with descriptions
4. Group by 3-character prefix
5. Return organized structure

## Return Format

```python
{
    'total_count': int,
    'codes': [
        {'code': str, 'description': str},
        ...
    ],
    'categories': {
        'E10': [code_entries...],
        'E11': [code_entries...],
        ...
    }
}
```

## Example Output

```
Total codes found: 50

Codes by category:

E10 (9 codes):
  E10.0: Type 1 diabetes mellitus with hyperosmolarity
  E10.1: Type 1 diabetes mellitus with ketoacidosis
  ...

E11 (9 codes):
  E11.0: Type 2 diabetes mellitus with hyperosmolarity
  E11.1: Type 2 diabetes mellitus with ketoacidosis
  ...
```

## Limitations

- Returns top 50 matches (configurable with maxList parameter)
- US-specific ICD-10-CM codes (not international ICD-10)
- Requires active internet connection for API access

## Related Skills

- Could extend to other conditions (hypertension, cancer, etc.)
- Could add ICD-11 support when available
- Could integrate with HCPCS code lookups
