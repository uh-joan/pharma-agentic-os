# USPTO Patents MCP Server - Complete API Guide

**Server**: `patents-mcp-server`
**Tool**: `uspto_patents`
**Data Source**: United States Patent and Trademark Office
**Response Format**: JSON
**Coverage**: 11+ million granted patents, 3+ million applications

---

## 🔴 CRITICAL QUERY SYNTAX

### Case-Sensitive Boolean Operators

```python
# ✅ CORRECT: Uppercase operators
query = "GLP-1 AND diabetes"
query = "KRAS OR BRAF"
query = "antibody NOT review"

# ❌ WRONG: Lowercase operators (treated as search terms)
query = "GLP-1 and diabetes"  # Searches for literal "and"
query = "KRAS or BRAF"        # Searches for literal "or"
```

### Field-Specific Search Syntax

```python
# ✅ CORRECT: Field prefixes with colons
query = 'assignee:"Pfizer" AND drug'
query = 'inventor:"Smith, John" AND chemistry'
query = 'title:"antibody" AND date:[20200101 TO 20241231]'

# ❌ WRONG: Without field prefixes
query = "Pfizer drug"  # Searches anywhere, not just assignee
```

### Date Format Requirements

```python
# ✅ CORRECT: [YYYYMMDD TO YYYYMMDD] format
query = "GLP-1 AND date:[20200101 TO 20241231]"
query = "KRAS AND date:[20150101 TO 20201231]"

# ❌ WRONG: Other date formats
query = "GLP-1 AND date:[2020-01-01 TO 2024-12-31]"  # Fails
query = "GLP-1 AND date:2020-2024"                   # Fails
```

---

## Quick Reference

### Field Prefixes

| Prefix | Searches | Example |
|--------|----------|---------|
| `assignee:` | Patent owner/company | `assignee:"Pfizer"` |
| `inventor:` | Inventor name | `inventor:"Smith, John"` |
| `title:` | Patent title | `title:"antibody"` |
| `abstract:` | Abstract text | `abstract:"therapeutic"` |
| `claims:` | Claims section | `claims:"composition"` |
| `date:` | Filing/issue date | `date:[20200101 TO 20241231]` |

### Boolean Operators (CASE-SENSITIVE)

| Operator | Function | Example |
|----------|----------|---------|
| `AND` | Both terms required | `GLP-1 AND diabetes` |
| `OR` | Either term | `KRAS OR BRAF` |
| `NOT` | Exclude term | `antibody NOT review` |
| `()` | Grouping | `(GLP-1 OR semaglutide) AND Novo` |
| `""` | Exact phrase | `"glucagon receptor agonist"` |

---

## Common Search Patterns

### Pattern 1: Company Patent Portfolio
```python
from mcp.servers.uspto_patents_mcp import ppubs_search_patents

# Search all patents by company
results = ppubs_search_patents(
    query='assignee:"Novo Nordisk" AND (GLP-1 OR semaglutide)',
    limit=100,
    sort="date_publ desc"
)

print(f"Found {len(results.get('results', []))} patents")

for patent in results.get('results', []):
    number = patent.get('patentNumber')
    title = patent.get('patentTitle')
    issue_date = patent.get('patentIssueDate')
    print(f"{number} ({issue_date}): {title}")
```

### Pattern 2: Recent Patents in Therapeutic Area
```python
# Search patents in last 3 years
results = ppubs_search_patents(
    query='(KRAS OR "KRAS inhibitor") AND date:[20210101 TO 20241231]',
    limit=100,
    sort="date_publ desc"
)

# Group by assignee
companies = {}
for patent in results.get('results', []):
    assignee = patent.get('assigneeEntityName', 'Unknown')
    companies[assignee] = companies.get(assignee, 0) + 1

# Rank by patent count
ranked = sorted(companies.items(), key=lambda x: x[1], reverse=True)

print("Top Companies - KRAS Patents (2021-2024):")
for company, count in ranked[:10]:
    print(f"{company}: {count} patents")
```

### Pattern 3: Competitive Patent Landscape
```python
# Compare multiple companies in same space
companies = ["Pfizer", "Merck", "Bristol Myers", "AbbVie"]

landscape = {}
for company in companies:
    results = ppubs_search_patents(
        query=f'assignee:"{company}" AND (immunotherapy OR checkpoint)',
        limit=500
    )
    landscape[company] = len(results.get('results', []))

print("Immunotherapy Patent Landscape:")
for company, count in sorted(landscape.items(), key=lambda x: x[1], reverse=True):
    print(f"{company}: {count} patents")
```

---

## Token Usage Guidelines

| Method | Approx. Tokens | Recommendation |
|--------|---------------|----------------|
| `ppubs_search_patents` | 100-500 per result | ✅ Use limit parameter |
| `ppubs_search_applications` | 100-500 per result | ✅ Use limit parameter |
| `ppubs_get_full_document` | 5,000-20,000 | ⚠️ Use sparingly |

**Token Optimization Tips**:
1. Set appropriate `limit` parameter (default 100)
2. Use field-specific searches to narrow results
3. Filter by date range to focus on recent patents
4. Extract only needed fields from results
5. Avoid fetching full documents unless necessary

---

## Summary

**USPTO Patents MCP Server** provides comprehensive patent search and retrieval:

✅ **11+ million granted patents** searchable
✅ **Case-sensitive boolean operators** (AND, OR, NOT)
✅ **Field-specific search** (assignee, inventor, title, date)
✅ **Date range filtering** with [YYYYMMDD TO YYYYMMDD] format

**Critical Pattern**: Use uppercase operators (AND/OR/NOT) and field prefixes (assignee:, inventor:, title:)

**Token Efficient**: Set appropriate limits, use field-specific searches

**Perfect For**: Prior art searches, competitive intelligence, patent landscape analysis, IP portfolio monitoring
