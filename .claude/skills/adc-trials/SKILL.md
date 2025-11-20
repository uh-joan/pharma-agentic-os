---
name: get_adc_trials
description: >
  Retrieves all Antibody-Drug Conjugate (ADC) clinical trials from ClinicalTrials.gov
  across all phases and statuses.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
created: 2025-11-19
complexity: medium
---

# get_adc_trials

Retrieves all Antibody-Drug Conjugate (ADC) clinical trials from ClinicalTrials.gov.

**Total Trials**: 363 ADC-related trials (as of 2025-11-19)
**Search Term**: "antibody drug conjugate OR ADC"
**Coverage**: Global, all phases, all statuses
