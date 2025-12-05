---
name: get_us_cardiometabolic_disease_prevalence
description: >
  Search US epidemiological data for cardiovascular and metabolic comorbidities
  (NASH/MASH, HFpEF, CKD) using Data Commons. Attempts to find prevalence data
  but may return mortality or incidence data when direct prevalence is unavailable.
  Useful for identifying data gaps in competitive landscape reports and determining
  when alternative sources (medical literature, disease registries) are needed for
  specific prevalence claims. Trigger keywords: "disease prevalence", "US population",
  "cardiometabolic", "NASH", "MASH", "HFpEF", "CKD", "fatty liver", "heart failure",
  "kidney disease", "epidemiology data".
category: population-health
mcp_servers:
  - datacommons_mcp
patterns:
  - search_with_fallback
  - data_validation
  - availability_checking
data_scope:
  total_results: 3 diseases queried
  geographical: United States
  temporal: Latest available year per disease
  data_types: prevalence, mortality, incidence
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~10 seconds
token_efficiency: ~99% reduction vs raw data
data_availability_note: >
  Data Commons has limited prevalence data for specific disease subtypes.
  The skill identifies when prevalence data is unavailable and recommends
  alternative sources (literature, registries, CDC reports).
---

# get_us_cardiometabolic_disease_prevalence

## Purpose

Search US epidemiological data for cardiovascular and metabolic comorbidities to validate or identify gaps in prevalence claims made in competitive landscape reports.

Specifically targets:
- **NASH/MASH**: Non-alcoholic steatohepatitis / Metabolic dysfunction-associated steatohepatitis
- **HFpEF**: Heart failure with preserved ejection fraction
- **CKD**: Chronic kidney disease

## Use Case

Created to validate three uncited prevalence claims in the GLP-1 competitive landscape report:
1. NASH/MASH prevalence: "3-5% US population" (line 289)
2. HFpEF prevalence: "3-5M US patients" (line 788)
3. CKD prevalence: "15% US adults" (line 860)

The skill searches Data Commons for US prevalence data and clearly indicates when direct prevalence data is not available, recommending alternative sources for citation.

## Data Availability

**Key Finding**: Data Commons has limited prevalence data for specific disease subtypes. The skill:
- Searches comprehensively across multiple query terms
- Prioritizes prevalence data over mortality/incidence
- Returns best available data with clear type labeling
- Identifies when alternative sources are needed

Common outcome: Mortality data available, but direct prevalence requires medical literature or disease registries.

## Usage

### Direct Execution
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/us-cardiometabolic-disease-prevalence/scripts/get_us_cardiometabolic_disease_prevalence.py
```

### Import and Use
```python
from .claude.skills.us_cardiometabolic_disease_prevalence.scripts.get_us_cardiometabolic_disease_prevalence import get_us_cardiometabolic_disease_prevalence

result = get_us_cardiometabolic_disease_prevalence()
print(result['summary']['details'])
```

## Alternative Data Sources

When prevalence data is not available in Data Commons, consider:

- **NASH/MASH**: American Association for the Study of Liver Diseases (AASLD), European Association for the Study of the Liver (EASL)
- **HFpEF**: American Heart Association (AHA), American College of Cardiology (ACC) heart failure reports
- **CKD**: National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), United States Renal Data System (USRDS)
