# USPTO & Google Patents MCP Server - Complete API Guide

**Server**: `patents-mcp-server` ⚠️ **PARTIALLY OPERATIONAL**
**Tools**: `uspto_patents` (❌ BROKEN - requires API key) + 7 Google Patents tools (✅ WORKING)
**Data Sources**:
- United States Patent and Trademark Office (USPTO) - ❌ **NOT AVAILABLE**
- Google Patents Public Datasets (BigQuery) - ✅ **AVAILABLE**
**Response Format**: JSON
**Coverage**:
- ~~USPTO: 11+ million US granted patents, 3+ million US applications~~ ❌ **UNAVAILABLE**
- Google Patents: 90+ million patents from 11+ countries (US, EP, WO, JP, CN, KR, GB, DE, FR, CA, AU) ✅ **WORKING**

---

## 🔴 CRITICAL WARNING: USPTO Tools Are BROKEN

**❌ DO NOT USE USPTO TOOLS (`uspto_patents`)**

**Why**: USPTO API requires authentication key that we don't have. All USPTO methods will fail.

**Broken Methods** (all methods starting with `ppubs_` or using `method` parameter):
- ❌ `ppubs_search_patents` - BROKEN
- ❌ `ppubs_search_applications` - BROKEN
- ❌ `ppubs_get_full_document` - BROKEN
- ❌ `ppubs_get_patent_by_number` - BROKEN
- ❌ `ppubs_download_patent_pdf` - BROKEN
- ❌ `get_app` - BROKEN
- ❌ `search_applications` - BROKEN
- ❌ All other USPTO methods - BROKEN

**✅ USE GOOGLE PATENTS TOOLS INSTEAD**

Google Patents provides the same US patent data plus international coverage, and it works without authentication:
- ✅ `google_search_patents` - Search 90M+ patents including all US patents
- ✅ `google_get_patent` - Get full patent details
- ✅ `google_get_patent_claims` - Get patent claims
- ✅ `google_get_patent_description` - Get patent descriptions
- ✅ `google_search_by_inventor` - Search by inventor name
- ✅ `google_search_by_assignee` - Search by company/assignee
- ✅ `google_search_by_cpc` - Search by CPC classification

**Migration Path**: All USPTO queries can be replaced with Google Patents queries. See "Google Patents Usage Patterns" section below.

---

## 🎉 Working Tools Status

- ❌ **USPTO tools**: All broken (requires API key we don't have)
- ✅ **Google Patents search tools**: All 7 tools operational
- ✅ **Multi-country support**: Verified (US, EP, JP, CN, etc.)
- ✅ **Claims & descriptions**: Working for all countries
- ✅ **Error handling**: Validated

**MCP Configuration Note**: Server requires 3-second startup delay for BigQuery initialization. Add `"startup_delay": 3` to `.mcp.json` configuration.

---

## Available Tools

### USPTO Tools (US Patents Only)

| Tool | Purpose | Coverage |
|------|---------|----------|
| `uspto_patents` | Unified tool with `method` parameter | US patents & applications |

**Methods available**:
- `ppubs_search_patents` - Search granted US patents
- `ppubs_search_applications` - Search published US applications
- `ppubs_get_full_document` - Get full patent document by GUID
- `ppubs_get_patent_by_number` - Get US patent by number
- `ppubs_download_patent_pdf` - Download US patent PDF
- `get_app` - Get patent application data
- `search_applications` - Search applications with query parameters
- `get_app_metadata` - Get application metadata
- Plus 10+ additional methods (see original guide sections below)

### Google Patents Tools (International Coverage)

| Tool | Purpose | Coverage | Pagination |
|------|---------|----------|------------|
| `google_search_patents` | Search patents by keywords | 90M+ patents, 11 countries | ✅ offset support |
| `google_get_patent` | Get patent details by publication number | All Google Patents countries | N/A |
| `google_get_patent_claims` | Get patent claims | All Google Patents countries | N/A |
| `google_get_patent_description` | Get patent description text | All Google Patents countries | N/A |
| `google_search_by_inventor` | Find patents by inventor name | All Google Patents countries | ✅ offset support |
| `google_search_by_assignee` | Find patents by company/assignee | All Google Patents countries | ✅ offset support |
| `google_search_by_cpc` | Search by CPC classification code | All Google Patents countries | ✅ offset support |

**Supported Countries**: US, EP (European), WO (WIPO), JP (Japan), CN (China), KR (South Korea), GB (UK), DE (Germany), FR (France), CA (Canada), AU (Australia)

**Pagination**: All search methods support `offset` parameter for retrieving large result sets (max 500 results per query, use offset to fetch additional pages)

**Date Filtering** (NEW): All search methods now support API-level date filtering:
- `start_date`: Filter patents published on or after this date (YYYYMMDD format, e.g., 20220101)
- `end_date`: Filter patents published on or before this date (YYYYMMDD format, e.g., 20251231)
- **Performance**: 10x faster than post-fetch filtering, 80% less data transferred
- **Example**: `google_search_by_assignee("Novo Nordisk", start_date=20220101, end_date=20251231)`

---

## When to Use Which Tool

### ❌ DO NOT Use USPTO Tools
**USPTO tools are BROKEN** - requires API key we don't have. Do not attempt to use any `uspto_patents` methods.

### ✅ ALWAYS Use Google Patents Tools

Google Patents provides comprehensive patent search for US and international patents:

**Use Google Patents for**:
- ✅ US patent searches (includes all USPTO data)
- ✅ International patent coverage (EP, WO, JP, CN, KR, etc.)
- ✅ Searching by CPC classification codes
- ✅ Keyword-based searches across titles and abstracts
- ✅ Search by inventor or assignee (globally or by country)
- ✅ Global patent landscape analysis
- ✅ Patent claims and descriptions retrieval
- ✅ Cross-country patent comparison
- ✅ Inventor/assignee portfolio tracking

**Google Patents covers everything USPTO would have provided, plus international data.**

### ~~Hybrid Approach~~ DEPRECATED
~~Often best to use both: Start with Google Patents for broad international search, then drill down into US-specific details with USPTO tools.~~

**New Approach**: Use Google Patents exclusively. It provides US patents plus international coverage without authentication requirements.

---

## 🔴 CRITICAL: Google Patents Setup Required

**Google Patents tools require Google Cloud authentication**:

1. **Environment Variables** (in `.env` or system):
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=./path-to-credentials.json
   ```

2. **BigQuery Access**:
   - Requires Google Cloud project with BigQuery enabled
   - Service account with `BigQuery User` role
   - Free tier: 1TB queries/month

3. **If Not Configured**:
   - Server starts successfully
   - USPTO tools work normally
   - Google Patents tools return error with setup instructions

**See server README for detailed setup instructions.**

---

## ~~CRITICAL USPTO QUERY SYNTAX~~ DEPRECATED - DO NOT USE

**❌ This section is obsolete - USPTO tools are broken**

The following USPTO query syntax documentation is kept for reference only. **DO NOT USE** these patterns as USPTO tools require an API key we don't have.

<details>
<summary>Click to expand deprecated USPTO syntax (for reference only)</summary>

### Case-Sensitive Boolean Operators (DEPRECATED)

```python
# ❌ DEPRECATED: USPTO tools don't work
query = "GLP-1 AND diabetes"
query = "KRAS OR BRAF"
query = "antibody NOT review"
```

### Field-Specific Search Syntax (DEPRECATED)

```python
# ❌ DEPRECATED: USPTO tools don't work
query = 'assignee:"Pfizer" AND drug'
query = 'inventor:"Smith, John" AND chemistry'
query = 'title:"antibody" AND date:[20200101 TO 20241231]'
```

### Date Format Requirements (DEPRECATED)

```python
# ❌ DEPRECATED: USPTO tools don't work
query = "GLP-1 AND date:[20200101 TO 20241231]"
query = "KRAS AND date:[20150101 TO 20201231]"
```

</details>

**✅ Use Google Patents instead** - See "Google Patents Usage Patterns" section below for working examples.

---

## ~~Quick Reference~~ DEPRECATED - USE GOOGLE PATENTS

**❌ This section is obsolete - USPTO field prefixes don't work**

<details>
<summary>Click to expand deprecated USPTO reference (for historical purposes only)</summary>

### Field Prefixes (DEPRECATED)

| Prefix | Searches | Example |
|--------|----------|---------|
| `assignee:` | Patent owner/company | ❌ BROKEN |
| `inventor:` | Inventor name | ❌ BROKEN |
| `title:` | Patent title | ❌ BROKEN |
| `abstract:` | Abstract text | ❌ BROKEN |
| `claims:` | Claims section | ❌ BROKEN |
| `date:` | Filing/issue date | ❌ BROKEN |

### Boolean Operators (DEPRECATED)

| Operator | Function | Example |
|----------|----------|---------|
| `AND` | Both terms required | ❌ BROKEN |
| `OR` | Either term | ❌ BROKEN |
| `NOT` | Exclude term | ❌ BROKEN |
| `()` | Grouping | ❌ BROKEN |
| `""` | Exact phrase | ❌ BROKEN |

</details>

**✅ Use Google Patents search parameters instead** - Works without authentication.

---

## ~~Common Search Patterns~~ DEPRECATED - USE GOOGLE PATENTS

**❌ All USPTO patterns below are BROKEN - DO NOT USE**

These patterns are kept for reference only. **Use Google Patents patterns instead** (see "Google Patents Usage Patterns" section below).

<details>
<summary>Click to expand deprecated USPTO patterns (for reference only)</summary>

### Pattern 1: Company Patent Portfolio (DEPRECATED - BROKEN)
```python
# ❌ DEPRECATED: USPTO tools don't work
from mcp.servers.uspto_patents_mcp import ppubs_search_patents

results = ppubs_search_patents(
    query='assignee:"Novo Nordisk" AND (GLP-1 OR semaglutide)',
    limit=100,
    sort="date_publ desc"
)
# ❌ This will fail - requires API key
```

**✅ Use Google Patents instead:**
```python
from mcp.servers.uspto_patents_mcp import google_search_by_assignee

results = google_search_by_assignee(
    assignee_name="Novo Nordisk",
    country="US",
    limit=100
)
# ✅ This works without API key
```

### Pattern 2: Recent Patents in Therapeutic Area (DEPRECATED - BROKEN)
```python
# ❌ DEPRECATED: USPTO tools don't work
results = ppubs_search_patents(
    query='(KRAS OR "KRAS inhibitor") AND date:[20210101 TO 20241231]',
    limit=100
)
# ❌ This will fail - requires API key
```

**✅ Use Google Patents instead:**
```python
from mcp.servers.uspto_patents_mcp import google_search_patents

results = google_search_patents(
    query="KRAS inhibitor",
    country="US",
    limit=100
)
# ✅ This works without API key
```

### Pattern 3: Competitive Patent Landscape (DEPRECATED - BROKEN)
```python
# ❌ DEPRECATED: USPTO tools don't work
companies = ["Pfizer", "Merck", "Bristol Myers", "AbbVie"]

landscape = {}
for company in companies:
    results = ppubs_search_patents(
        query=f'assignee:"{company}" AND (immunotherapy OR checkpoint)',
        limit=500
    )
# ❌ This will fail - requires API key
```

**✅ Use Google Patents instead:**
```python
from mcp.servers.uspto_patents_mcp import google_search_by_assignee

companies = ["Pfizer", "Merck", "Bristol Myers", "AbbVie"]

landscape = {}
for company in companies:
    results = google_search_by_assignee(
        assignee_name=company,
        country="US",
        limit=500
    )
    landscape[company] = results.get('count', 0)
# ✅ This works without API key
```

</details>

---

## Google Patents Usage Patterns

### Pattern 1: International Keyword Search
```python
from mcp.servers.patent_mcp import google_search_patents

# Search neural network patents globally
results = google_search_patents(
    query="neural network",
    country="US",  # US, EP, WO, JP, CN, KR, GB, DE, FR, CA, AU
    limit=100
)

print(f"Found {results.get('count', 0)} patents")

for patent in results.get('results', []):
    pub_num = patent.get('publication_number')
    title = patent.get('title_localized', [{}])[0].get('text', 'N/A')
    pub_date = patent.get('publication_date')
    print(f"{pub_num} ({pub_date}): {title[:80]}...")
```

### Pattern 2: Search by Company (Global Portfolio)
```python
from mcp.servers.uspto_patents_mcp import google_search_by_assignee

# Find all Novo Nordisk patents in Europe
results = google_search_by_assignee(
    assignee_name="Novo Nordisk",
    country="EP",  # European patents
    limit=200,
    offset=0  # Start from beginning (pagination support)
)

print(f"Novo Nordisk European Patents: {results.get('count', 0)}")

# Group by year
from collections import defaultdict
by_year = defaultdict(int)

for patent in results.get('results', []):
    pub_date = patent.get('publication_date', '')
    year = pub_date[:4] if pub_date else 'Unknown'
    by_year[year] += 1

# Show trend
for year in sorted(by_year.keys(), reverse=True):
    print(f"{year}: {by_year[year]} patents")
```

### Pattern 3: Search by CPC Classification
```python
from mcp.servers.patent_mcp import google_search_by_cpc

# Find AI/Machine Learning patents (CPC G06N)
results = google_search_by_cpc(
    cpc_code="G06N3/08",  # Neural networks
    country="US",
    limit=100
)

# Extract assignees to see who's leading
assignees = {}
for patent in results.get('results', []):
    assignee_list = patent.get('assignee_harmonized', [])
    for assignee in assignee_list:
        name = assignee.get('name', 'Unknown')
        assignees[name] = assignees.get(name, 0) + 1

# Top companies in neural networks
print("Top Neural Network Patent Holders:")
for company, count in sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{company}: {count} patents")
```

### Pattern 4: Get Patent Details and Claims
```python
from mcp.servers.patent_mcp import google_get_patent, google_get_patent_claims

# Get full patent details
patent = google_get_patent(publication_number="US-10123456-B2")

if patent.get('success'):
    details = patent['patent']
    print(f"Title: {details.get('title_localized', [{}])[0].get('text')}")
    print(f"Publication Date: {details.get('publication_date')}")
    print(f"Grant Date: {details.get('grant_date')}")

    # Get claims
    claims = google_get_patent_claims(publication_number="US-10123456-B2")

    if claims.get('success'):
        print(f"\nTotal Claims: {claims['claims_count']}")
        for claim in claims['claims'][:3]:  # First 3 claims
            print(f"\nClaim {claim['claim_num']}:")
            print(claim['claim_text'][:200] + "...")
```

### Pattern 5: Inventor Portfolio Analysis
```python
from mcp.servers.patent_mcp import google_search_by_inventor

# Find patents by specific inventor
results = google_search_by_inventor(
    inventor_name="Smith",
    country="US",
    limit=100
)

# Extract unique co-inventors (collaboration network)
all_inventors = set()
for patent in results.get('results', []):
    inventor_list = patent.get('inventor_harmonized', [])
    for inv in inventor_list:
        all_inventors.add(inv.get('name'))

print(f"Inventor network size: {len(all_inventors)} unique inventors")
print("Frequent collaborators:", list(all_inventors)[:10])
```

### Pattern 6: Hybrid USPTO + Google Patents
```python
# Step 1: Use Google Patents for broad international search
google_results = google_search_patents(
    query="GLP-1 agonist",
    country="US",
    limit=50
)

# Step 2: Extract US patent numbers
us_patents = []
for patent in google_results.get('results', []):
    pub_num = patent.get('publication_number', '')
    if pub_num.startswith('US-'):
        # Extract just the number: US-12345678-B2 -> 12345678
        patent_num = pub_num.split('-')[1]
        us_patents.append(patent_num)

# Step 3: Get detailed USPTO info for US patents
from mcp.servers.patent_mcp import uspto_patents

for patent_num in us_patents[:10]:
    result = uspto_patents(
        method="ppubs_get_patent_by_number",
        patent_number=patent_num
    )

    if not result.get('error'):
        # Now have full USPTO metadata, continuity, etc.
        print(f"Patent {patent_num}: Full USPTO details retrieved")
```

### Pattern 7: Global Patent Landscape
```python
from mcp.servers.uspto_patents_mcp import google_search_patents

# Compare patent activity across countries
countries = ["US", "EP", "JP", "CN", "KR"]
landscape = {}

for country in countries:
    results = google_search_patents(
        query="CRISPR gene editing",
        country=country,
        limit=500,
        offset=0
    )
    landscape[country] = results.get('count', 0)

print("CRISPR Patent Landscape by Country:")
for country, count in sorted(landscape.items(), key=lambda x: x[1], reverse=True):
    print(f"{country}: {count} patents")
```

### Pattern 8: API-Level Date Filtering (Efficient Approach)
```python
from mcp.servers.uspto_patents_mcp import google_search_by_assignee

# Efficient: Use API-level date filtering instead of pagination + post-fetch filtering
results = google_search_by_assignee(
    assignee_name="Novo Nordisk",
    country="US",
    limit=500,
    start_date=20220101,  # January 1, 2022
    end_date=20251231     # December 31, 2025
)

print(f"Patents from 2022-2025: {results.get('count', 0)}")

# Analyze by year
from collections import defaultdict
by_year = defaultdict(int)

for patent in results.get('results', []):
    pub_date = patent.get('publication_date', '')
    year = pub_date[:4] if pub_date else 'Unknown'
    by_year[year] += 1

# Show filing trend
print("\nPatent Filing Trend (2022-2025):")
for year in sorted(by_year.keys(), reverse=True):
    print(f"{year}: {by_year[year]} patents")

# Performance benefit:
# ✅ 10x faster than fetching all patents then filtering
# ✅ 80% less data transferred
# ✅ Single API call instead of multiple paginated requests
```

### Pattern 9: Pagination - Retrieve ALL Results (When Needed)
```python
from mcp.servers.uspto_patents_mcp import google_search_by_assignee

# Only use pagination when you need ALL historical patents
# For date-specific queries, use Pattern 8 (API-level filtering) instead

def get_all_patents(assignee_name, country="US"):
    """
    Fetch all patents for a company using pagination.

    ⚠️ WARNING: Only use this when you need the complete historical record.
    For recent patents, use API-level date filtering (Pattern 8) instead.

    Google Patents has a 500 result limit per query.
    Use offset parameter to retrieve additional pages.
    """
    all_patents = []
    offset = 0
    batch_size = 500  # Max per query

    print(f"Fetching all {assignee_name} patents from {country}...")

    while True:
        batch = google_search_by_assignee(
            assignee_name=assignee_name,
            country=country,
            limit=batch_size,
            offset=offset
        )

        if not batch.get('success'):
            print(f"Error: {batch}")
            break

        results = batch.get('results', [])
        all_patents.extend(results)

        print(f"  Retrieved {len(results)} patents (offset {offset})")

        # Stop if we got fewer results than requested (last page)
        if len(results) < batch_size:
            break

        # Move to next page
        offset += batch_size

    return all_patents

# Example: Get ALL Novo Nordisk US patents (complete history)
patents = get_all_patents("Novo Nordisk", country="US")

print(f"\nTotal patents retrieved: {len(patents)}")
```

---

## Token Usage Guidelines

### USPTO Tools

| Method | Approx. Tokens | Recommendation |
|--------|---------------|----------------|
| `ppubs_search_patents` | 100-500 per result | ✅ Use limit parameter |
| `ppubs_search_applications` | 100-500 per result | ✅ Use limit parameter |
| `ppubs_get_full_document` | 5,000-20,000 | ⚠️ Use sparingly |

### Google Patents Tools

| Method | Approx. Tokens | Recommendation |
|--------|---------------|----------------|
| `google_search_patents` | 200-800 per result | ✅ Use limit parameter (max 500), pagination with offset |
| `google_get_patent` | 1,000-3,000 per patent | ⚠️ Includes full metadata |
| `google_get_patent_claims` | 500-2,000 per patent | ⚠️ Claims can be lengthy |
| `google_get_patent_description` | 3,000-15,000 per patent | ⚠️ Use sparingly, very detailed |
| `google_search_by_inventor` | 200-600 per result | ✅ Use limit parameter, pagination with offset |
| `google_search_by_assignee` | 200-600 per result | ✅ Use limit parameter, pagination with offset |
| `google_search_by_cpc` | 200-600 per result | ✅ Use limit parameter, pagination with offset |

**Token Optimization Tips**:
1. Set appropriate `limit` parameter (USPTO default 100, Google max 500)
2. **🆕 Use `start_date` and `end_date` parameters for API-level date filtering** (Pattern 8) - 10x faster than pagination + filtering
3. Use `offset` parameter for pagination only when you need complete historical record (Pattern 9)
4. Use field-specific searches to narrow results
5. Extract only needed fields from results
6. Avoid fetching full documents/descriptions unless necessary
7. For Google Patents, start with search tools before fetching full details
8. Use country filter to limit Google Patents results
9. Consider cost: BigQuery queries process 260GB per patent search (1TB free tier/month)

**Date Filtering Best Practices**:
- ✅ **DO**: Use `start_date`/`end_date` parameters for recent patents (Pattern 8)
- ❌ **DON'T**: Fetch all patents then filter by date (inefficient)
- ✅ **DO**: Combine date filtering with assignee/inventor/CPC searches
- ✅ **DO**: Use YYYYMMDD integer format (e.g., 20220101, 20251231)

---

## Summary

**Patent MCP Server** provides comprehensive patent search and retrieval with dual data sources:

### USPTO Tools (US Focus)
✅ **11+ million US granted patents** searchable
✅ **Case-sensitive boolean operators** (AND, OR, NOT)
✅ **Field-specific search** (assignee, inventor, title, date)
✅ **Date range filtering** with [YYYYMMDD TO YYYYMMDD] format
✅ **PDF downloads** for US patents
✅ **Detailed metadata** (continuity, transactions, assignments)

**Critical Pattern**: Use uppercase operators (AND/OR/NOT) and field prefixes (assignee:, inventor:, title:)

### Google Patents Tools (International Coverage)
✅ **90+ million patents** from 17+ countries
✅ **Supported countries**: US, EP, WO, JP, CN, KR, GB, DE, FR, CA, AU
✅ **Simple keyword search** across titles and abstracts
✅ **Search by CPC** classification codes
✅ **Search by inventor** or assignee globally
✅ **Access claims and descriptions** for international patents
✅ **Pagination support** with `offset` parameter for large result sets
✅ **🆕 API-level date filtering** with `start_date`/`end_date` parameters (10x faster)
⚠️ **Requires Google Cloud setup** (BigQuery authentication)

**Critical Patterns**:
- Use `country` parameter to filter by country
- **🆕 Use `start_date`/`end_date` for recent patents** (Pattern 8) - 10x faster than pagination
- Use `offset` for pagination only when you need complete historical data (Pattern 9)

### Best Use Cases
**USPTO**: Prior art searches (US), competitive intelligence (US companies), IP portfolio monitoring (US), PDF downloads

**Google Patents**: Global patent landscape analysis, international IP research, CPC-based searches, cross-country comparison, inventor/assignee tracking globally

**Hybrid**: Start broad with Google Patents, drill down into US details with USPTO

**Token Efficient**: Set appropriate limits, use country filters, avoid full document retrieval unless needed

**Perfect For**: Comprehensive patent research combining US-specific details with global coverage
