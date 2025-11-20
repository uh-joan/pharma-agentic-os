# CMS Healthcare MCP Server - Complete API Guide

**Server**: `healthcare-mcp`
**Tool**: `cms_search_providers`
**Data Source**: Centers for Medicare & Medicaid Services (CMS)
**Response Format**: JSON
**Coverage**: Medicare Part B provider services data

---

## 🔴 CRITICAL DATASET TYPES

### Three Dataset Types with Different Use Cases

```python
# ✅ Dataset Type 1: Geography & Service
# Use for: Regional comparisons, geographic patterns, per-capita rates
dataset_type = "geography_and_service"

# ✅ Dataset Type 2: Provider & Service
# Use for: Individual provider performance, specific procedure tracking
dataset_type = "provider_and_service"

# ✅ Dataset Type 3: Provider
# Use for: Provider demographics, participation patterns, beneficiary characteristics
dataset_type = "provider"
```

---

## Quick Reference

### Dataset Types

| Dataset Type | Best For | Key Fields |
|--------------|----------|------------|
| `geography_and_service` | Regional analysis, market sizing | Geographic code, service counts, beneficiary counts |
| `provider_and_service` | Provider performance, procedure volume | Provider NPI, service codes, total services |
| `provider` | Provider demographics, practice patterns | Provider type, beneficiary demographics, risk scores |

### Common HCPCS Codes

| Code | Service | Category |
|------|---------|----------|
| `99213` | Established patient office visit | Evaluation & Management |
| `99214` | Office visit, moderate complexity | Evaluation & Management |
| `80053` | Comprehensive metabolic panel | Laboratory |
| `93000` | Electrocardiogram | Diagnostic |
| `J1745` | Injection (infliximab) | Drugs |

---

## Common Search Patterns

### Pattern 1: Geographic Service Analysis
```python
from mcp.servers.healthcare_mcp import cms_search_providers

# Compare regions for specific service
results = cms_search_providers(
    dataset_type="geography_and_service",
    geo_level="State",
    hcpcs_code="99213",  # Office visit
    year="2022",
    size=100,
    sort_by="Tot_Srvcs",
    sort_order="desc"
)

print("Top States by Office Visits:")
for record in results['data'][:10]:
    state = record.get('Rndrng_Prvdr_Geo_Desc')
    services = record.get('Tot_Srvcs')
    providers = record.get('Tot_Prvdrs')
    print(f"{state}: {services:,} services by {providers:,} providers")
```

### Pattern 2: Provider Service Volume
```python
# Find top providers for specific procedure
results = cms_search_providers(
    dataset_type="provider_and_service",
    hcpcs_code="J1745",  # Infliximab injection
    provider_type="Rheumatology",
    year="2022",
    size=50,
    sort_by="Tot_Srvcs",
    sort_order="desc"
)

print("Top Rheumatologists - Infliximab Administration:")
for record in results['data'][:20]:
    npi = record.get('Rndrng_NPI')
    name = record.get('Rndrng_Prvdr_Last_Org_Name')
    services = record.get('Tot_Srvcs')
    benes = record.get('Tot_Benes')
    print(f"{name} (NPI: {npi}): {services:,} services, {benes:,} patients")
```

### Pattern 3: Provider Practice Patterns
```python
# Analyze provider demographics and beneficiaries
results = cms_search_providers(
    dataset_type="provider",
    provider_type="Cardiology",
    year="2022",
    size=100,
    sort_by="Tot_Benes",
    sort_order="desc"
)

print("Cardiology Practice Analysis:")
for record in results['data'][:15]:
    name = record.get('Rndrng_Prvdr_Last_Org_Name')
    benes = record.get('Tot_Benes')
    avg_risk = record.get('Bene_Avg_Risk_Scre')
    avg_age = record.get('Bene_Avg_Age')

    print(f"\n{name}:")
    print(f"  Beneficiaries: {benes:,}")
    print(f"  Avg Risk Score: {avg_risk:.2f}")
    print(f"  Avg Age: {avg_age:.1f}")
```

---

## Token Usage Guidelines

| Query Type | Approx. Tokens | Recommendation |
|------------|---------------|----------------|
| Geographic analysis | 100-300 per record | ✅ Use size parameter |
| Provider search | 150-400 per record | ✅ Filter by provider type |
| Service-specific | 100-250 per record | ✅ Use HCPCS code filter |

**Token Optimization Tips**:
1. Always set `size` parameter (default is large)
2. Filter by provider_type to narrow results
3. Use specific HCPCS codes when possible
4. Sort by relevant metric (Tot_Srvcs, Tot_Benes)
5. Use year parameter for most recent data

---

## Summary

**CMS Healthcare MCP Server** provides Medicare provider services data:

✅ **Three dataset types** for different analysis needs
✅ **Geographic analysis** for regional patterns
✅ **Provider-level data** for performance tracking
✅ **HCPCS code filtering** for specific services

**Critical Pattern**: Choose correct dataset_type for your analysis (geography vs provider vs provider_and_service)

**Token Efficient**: Filter by provider_type, HCPCS code, and set appropriate size limits

**Perfect For**: Market analysis, provider network analysis, service utilization patterns, geographic healthcare access
