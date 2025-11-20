# PubMed MCP Server - Complete API Documentation

> **Access**: `mcp__pubmed-mcp__pubmed_articles`
> **Database**: Over 35 million biomedical literature citations
> **Response Format**: JSON (structured data)
> **Token Usage**: ~750 tokens per article with full abstract

---

## 🔴 CRITICAL KNOWN LIMITATION

**MCP Result Count Issue**:
- **Problem**: Server may return fewer results than `num_results` requested
- **Validated**: Requested 30 → received only 2 articles; Requested 5 → received 3
- **Root Cause**: Appears to be MCP tool limitation, not query issue
- **Workaround**:
  - ✅ Request conservative numbers (10-20 results)
  - ✅ Expect partial returns and handle gracefully
  - ✅ Don't rely on exact count matching
- **Code Pattern**:
```python
result = search_keywords("diabetes", num_results=20)
actual_count = len(result.get('articles', []))
print(f"Requested 20, received {actual_count}")  # May be less!
```

---

## Table of Contents

1. [When to Use PubMed](#when-to-use)
2. [Quick Reference](#quick-reference)
3. [Methods Overview](#methods-overview)
4. [Method 1: search_keywords](#method-1-search_keywords)
5. [Method 2: search_advanced](#method-2-search_advanced)
6. [Method 3: get_article_metadata](#method-3-get_article_metadata)
7. [Method 4: get_article_pdf](#method-4-get_article_pdf)
8. [Response Format & Parsing](#response-format--parsing)
9. [Search Optimization Strategies](#search-optimization-strategies)
10. [Common Use Cases](#common-use-cases)
11. [Known Quirks & Limitations](#known-quirks--limitations)
12. [Best Practices](#best-practices)
13. [FAQ](#faq)

---

## When to Use

✅ **Use PubMed for**:
- Literature searches for drugs, conditions, mechanisms
- Finding clinical study publications
- Systematic reviews and meta-analyses
- Retrieving article metadata (authors, abstract, journal, MeSH terms)
- Downloading full-text PDFs (when available via PubMed Central)
- Evidence-based research for drug discovery
- Publication trends and author tracking

❌ **Don't use PubMed for**:
- Clinical trial data → Use CT.gov MCP
- Drug approval information → Use FDA MCP
- Target validation → Use Open Targets MCP
- Chemical structures → Use PubChem MCP

---

## Quick Reference

| Method | Purpose | Key Parameters | Returns |
|--------|---------|----------------|---------|
| `search_keywords` | Keyword search | `keywords`, `num_results` | Articles list |
| `search_advanced` | Filtered search | `term`, `author`, `journal`, `start_date`, `end_date` | Articles list |
| `get_article_metadata` | Get article details | `pmid` | Full metadata |
| `get_article_pdf` | Download PDF | `pmid` | PDF data/URL |

---

## Methods Overview

```json
{
  "method": "search_keywords",        // Search with keywords (basic)
  "method": "search_advanced",        // Search with filters (precise)
  "method": "get_article_metadata",   // Get article details by PMID
  "method": "get_article_pdf"         // Download full-text PDF
}
```

**All methods return JSON** (unlike CT.gov which returns markdown).

---

## Method 1: search_keywords

**Purpose**: Basic keyword search with PubMed advanced search syntax support

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"search_keywords"` | Operation type |
| `keywords` | string | ✅ Yes | - | Any text | Search query with keywords, medical terms, drug names, diseases |
| `num_results` | integer | ❌ No | 10 | 1-100 | Maximum results (see limitation warning above) |

### Advanced Search Syntax

PubMed supports rich query syntax within the `keywords` parameter:

#### Basic Search
```json
{
  "method": "search_keywords",
  "keywords": "semaglutide diabetes",  // Implicit AND logic
  "num_results": 10
}
```

#### MeSH Terms (Precise)
```json
{
  "method": "search_keywords",
  "keywords": "\"Diabetes Mellitus, Type 2\"[MeSH] AND \"GLP-1 agonist\"",
  "num_results": 20
}
```

**Why MeSH?** Medical Subject Headings are controlled vocabulary - more precise than free text.

#### Study Type Filters
```json
{
  "method": "search_keywords",
  "keywords": "obesity treatment AND (randomized controlled trial[pt])",
  "num_results": 15
}
```

**Publication types** (`[pt]`):
- `randomized controlled trial[pt]` - RCTs only
- `meta-analysis[pt]` - Meta-analyses
- `review[pt]` - Review articles
- `clinical trial[pt]` - Clinical trials
- `case reports[pt]` - Case reports

#### Date Filters in Keywords
```json
{
  "method": "search_keywords",
  "keywords": "semaglutide AND (\"2023/01/01\"[PDAT] : \"2024/12/31\"[PDAT])",
  "num_results": 10
}
```

**Date format**: `"YYYY/MM/DD"[PDAT]` (Publication Date)

#### Human Studies Only
```json
{
  "method": "search_keywords",
  "keywords": "GLP-1 agonist AND humans[MeSH]",
  "num_results": 10
}
```

#### Exclusions
```json
{
  "method": "search_keywords",
  "keywords": "diabetes treatment NOT review[pt]",
  "num_results": 20
}
```

### Response Structure

```json
{
  "articles": [
    {
      "pmid": "12345678",
      "title": "Article title here",
      "abstract": "Full abstract text...",
      "authors": ["Smith J", "Jones M", "et al."],
      "journal": "N Engl J Med",
      "pub_date": "2024-03-15",
      "doi": "10.1056/NEJMoa...",
      "keywords": ["diabetes", "GLP-1"]
    }
  ],
  "total_count": 15  // May be less than requested!
}
```

### Code Example

```python
from mcp.servers.pubmed_mcp import search_keywords

# Basic search
result = search_keywords(
    keywords="semaglutide obesity",
    num_results=10
)

# Process results (safe handling)
articles = result.get('articles', [])
print(f"Requested 10, received {len(articles)}")  # May be less!

for article in articles:
    pmid = article.get('pmid', 'N/A')
    title = article.get('title', 'No title')
    authors = article.get('authors', [])

    print(f"PMID: {pmid}")
    print(f"Title: {title}")
    print(f"Authors: {', '.join(authors[:3])}")  # First 3 authors
    print()
```

---

## Method 2: search_advanced

**Purpose**: Structured search with field-specific filters

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"search_advanced"` | Operation type |
| `term` | string | ❌ No | - | Any text | General search term for title, abstract, keywords |
| `title` | string | ❌ No | - | Any text | Search specifically in article titles |
| `author` | string | ❌ No | - | Any text | Author name (e.g., "Smith J", "John Smith") |
| `journal` | string | ❌ No | - | Any text | Journal name or abbreviation (e.g., "Nature", "N Engl J Med") |
| `start_date` | string | ❌ No | - | Format: `YYYY/MM/DD` | Start date for publication date range |
| `end_date` | string | ❌ No | - | Format: `YYYY/MM/DD` | End date for publication date range |
| `num_results` | integer | ❌ No | 10 | 1-100 | Maximum results (see limitation warning) |

**Note**: At least one filter parameter (`term`, `title`, `author`, `journal`, or date range) should be provided.

### Common Filter Combinations

#### High-Impact Journal Filter
```json
{
  "method": "search_advanced",
  "term": "semaglutide",
  "journal": "N Engl J Med",
  "num_results": 10
}
```

**Top journals**:
- "N Engl J Med" (New England Journal of Medicine)
- "Nature"
- "Science"
- "Lancet"
- "JAMA"
- "Cell"
- "Diabetes Care"

#### Date Range Filter
```json
{
  "method": "search_advanced",
  "term": "GLP-1 agonist obesity",
  "start_date": "2020/01/01",
  "end_date": "2024/12/31",
  "num_results": 20
}
```

#### Author Search
```json
{
  "method": "search_advanced",
  "author": "Smith J",
  "term": "diabetes",
  "num_results": 15
}
```

**Author name formats**:
- Last name + initial: "Smith J"
- Full name: "John Smith"
- Last name only: "Smith"

#### Combined Filters
```json
{
  "method": "search_advanced",
  "term": "obesity treatment",
  "journal": "Diabetes Care",
  "start_date": "2023/01/01",
  "end_date": "2024/12/31",
  "num_results": 10
}
```

#### Title-Specific Search
```json
{
  "method": "search_advanced",
  "title": "CRISPR gene editing",
  "start_date": "2024/01/01",
  "end_date": "2024/12/31",
  "num_results": 50
}
```

### Response Structure

Same as `search_keywords` (see Method 1).

### Code Example

```python
from mcp.servers.pubmed_mcp import search_advanced

# Recent publications in high-impact journal
result = search_advanced(
    term="GLP-1 agonist",
    journal="N Engl J Med",
    start_date="2023/01/01",
    end_date="2024/12/31",
    num_results=20
)

# Extract publication dates for trend analysis
pub_dates = []
for article in result.get('articles', []):
    pub_date = article.get('pub_date')
    if pub_date:
        pub_dates.append(pub_date)

print(f"Publications by year:")
# Count by year
from collections import Counter
years = [date[:4] for date in pub_dates]
for year, count in Counter(years).items():
    print(f"  {year}: {count} papers")
```

---

## Method 3: get_article_metadata

**Purpose**: Get detailed metadata for a specific PubMed article

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_article_metadata"` | Operation type |
| `pmid` | string OR integer | ✅ Yes | - | PubMed ID | Unique identifier (e.g., "12345678" or 12345678) |

**PMID flexibility**: Can pass as string `"12345678"` or integer `12345678` - both work.

### Response Structure

```json
{
  "pmid": "12345678",
  "title": "Complete article title",
  "abstract": "Full abstract text with background, methods, results, conclusions...",
  "authors": [
    {
      "name": "Smith J",
      "affiliation": "Harvard Medical School",
      "initials": "J"
    },
    {
      "name": "Jones M",
      "affiliation": "Stanford University",
      "initials": "M"
    }
  ],
  "journal": "New England Journal of Medicine",
  "volume": "389",
  "issue": "12",
  "pages": "1234-1245",
  "pub_date": "2024-03-15",
  "doi": "10.1056/NEJMoa...",
  "keywords": {
    "mesh": [
      "Diabetes Mellitus, Type 2",
      "Hypoglycemic Agents",
      "Glucagon-Like Peptide 1"
    ],
    "other": ["GLP-1", "obesity", "weight loss"]
  },
  "citation": "Smith J, Jones M. Title. N Engl J Med. 2024 Mar 15;389(12):1234-45."
}
```

### Code Example

```python
from mcp.servers.pubmed_mcp import get_article_metadata

# Get full metadata for specific article
article = get_article_metadata(pmid="12345678")  # String or int both work

# Extract comprehensive information
title = article.get('title')
abstract = article.get('abstract')
authors = article.get('authors', [])
journal = article.get('journal')
pub_date = article.get('pub_date')
doi = article.get('doi')

print(f"Title: {title}")
print(f"\nJournal: {journal}")
print(f"Published: {pub_date}")
print(f"DOI: {doi}")

# Authors with affiliations
print(f"\nAuthors:")
for author in authors:
    name = author.get('name')
    affiliation = author.get('affiliation', 'N/A')
    print(f"  - {name} ({affiliation})")

# MeSH terms for categorization
mesh_terms = article.get('keywords', {}).get('mesh', [])
print(f"\nMeSH Terms: {', '.join(mesh_terms)}")

# Full abstract
print(f"\nAbstract:\n{abstract}")
```

---

## Method 4: get_article_pdf

**Purpose**: Download full-text PDF for a PubMed article (when available)

### Parameters

| Parameter | Type | Required | Default | Constraint | Description |
|-----------|------|----------|---------|------------|-------------|
| `method` | string | ✅ Yes | - | Must be `"get_article_pdf"` | Operation type |
| `pmid` | string OR integer | ✅ Yes | - | PubMed ID | Unique identifier (e.g., "12345678" or 12345678) |

### PDF Availability

**Not all PubMed articles have freely available PDFs.**

PDF availability depends on:
- ✅ **Publisher open access policies** - Some journals are fully open access
- ✅ **PubMed Central (PMC) availability** - Articles in PMC repository
- ✅ **NIH Public Access** - NIH-funded research (after embargo period)
- ❌ **Journal subscription status** - Paywalled articles not available
- ❌ **Embargo periods** - Recent articles may have delays

### Response Structure

```json
{
  "available": true,
  "pdf_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC.../pdf/",
  "pdf_data": "base64-encoded-pdf-content...",
  "pmid": "12345678",
  "message": "PDF downloaded successfully"
}
```

**If unavailable**:
```json
{
  "available": false,
  "pmid": "12345678",
  "message": "PDF not freely available - check publisher site or institutional access"
}
```

### Code Example

```python
from mcp.servers.pubmed_mcp import get_article_pdf
import base64

# Attempt to download PDF
pdf_result = get_article_pdf(pmid="12345678")

if pdf_result.get('available'):
    print("PDF is available!")

    # Check if URL provided
    pdf_url = pdf_result.get('pdf_url')
    if pdf_url:
        print(f"PDF URL: {pdf_url}")

    # Check if PDF data included (base64-encoded)
    if 'pdf_data' in pdf_result:
        # Decode and save
        pdf_bytes = base64.b64decode(pdf_result['pdf_data'])

        with open('article.pdf', 'wb') as f:
            f.write(pdf_bytes)

        print(f"PDF saved to article.pdf ({len(pdf_bytes)} bytes)")
else:
    print(f"PDF not available: {pdf_result.get('message')}")
    print("Try institutional access or publisher site")
```

---

## Response Format & Parsing

### JSON Structure (All Methods)

Unlike CT.gov (which returns markdown), PubMed returns structured JSON.

**General pattern**:
```python
result = search_keywords(...)

# ✅ CORRECT: Access JSON fields
articles = result.get('articles', [])
for article in articles:
    pmid = article.get('pmid')
    title = article.get('title', 'No title')

# ❌ WRONG: Trying to parse as markdown
nct_ids = re.findall(r'NCT\d{8}', result)  # Wrong server!
```

### Safe Dictionary Access

**Always use `.get()` for optional fields**:

```python
# ✅ CORRECT: Safe access with defaults
authors = article.get('authors', [])
abstract = article.get('abstract', 'No abstract available')
doi = article.get('doi', 'N/A')
mesh_terms = article.get('keywords', {}).get('mesh', [])

# ❌ WRONG: Direct access (may raise KeyError)
authors = article['authors']  # KeyError if missing!
```

### Handling Variable Result Counts

```python
# ✅ CORRECT: Handle partial results
result = search_keywords("diabetes", num_results=50)
articles = result.get('articles', [])

if len(articles) < 50:
    print(f"Warning: Requested 50, received {len(articles)}")
    print("This is a known MCP limitation - proceed with available data")

# Process what you got
for article in articles:
    # ... process article ...
    pass

# ❌ WRONG: Assuming exact count
assert len(articles) == 50  # Will fail due to MCP limitation!
```

---

## Search Optimization Strategies

### 1. Use MeSH Terms for Precision

❌ **Free text** (less precise):
```json
{"keywords": "diabetes type 2 treatment"}
```

✅ **MeSH terms** (more precise):
```json
{"keywords": "\"Diabetes Mellitus, Type 2\"[MeSH] AND therapy[MeSH]"}
```

**Why MeSH?**
- Controlled vocabulary - consistent across articles
- Includes synonyms automatically
- Better precision and recall
- Standard for systematic reviews

**Find MeSH terms**: https://www.ncbi.nlm.nih.gov/mesh

### 2. Filter by Study Type

For **evidence-based research**, filter by publication type:

```python
# RCTs only
keywords="obesity treatment AND (randomized controlled trial[pt])"

# Meta-analyses only
keywords="GLP-1 agonist AND (meta-analysis[pt])"

# Exclude reviews
keywords="diabetes treatment NOT review[pt]"

# Clinical trials only
keywords="semaglutide AND (clinical trial[pt])"
```

### 3. Date Filters for Recent Research

**In keywords** (within search_keywords):
```python
keywords='CRISPR AND ("2024/01/01"[PDAT] : "2024/12/31"[PDAT])'
```

**As parameters** (in search_advanced):
```python
search_advanced(
    term="CRISPR",
    start_date="2024/01/01",
    end_date="2024/12/31"
)
```

### 4. Human Studies Filter

```python
keywords="gene therapy AND humans[MeSH]"
```

Excludes animal studies, in vitro research.

### 5. High-Impact Journals Only

```python
search_advanced(
    term="obesity treatment",
    journal="N Engl J Med OR Lancet OR Nature OR Science OR JAMA"
)
```

### 6. Conservative Result Requests

```python
# ❌ DON'T: Request large counts
num_results=100  # May only get 10-20

# ✅ DO: Request conservative counts
num_results=20   # More realistic expectation
```

---

## Common Use Cases

### Use Case 1: Literature Search for Drug Mechanism

**Goal**: Find recent publications about semaglutide's mechanism of action

```python
from mcp.servers.pubmed_mcp import search_advanced

result = search_advanced(
    term="semaglutide mechanism",
    start_date="2020/01/01",
    end_date="2024/12/31",
    num_results=20
)

# Extract titles and abstracts
for article in result.get('articles', []):
    print(f"Title: {article.get('title')}")
    print(f"Abstract: {article.get('abstract', 'N/A')[:200]}...")
    print()
```

### Use Case 2: Systematic Review - RCTs Only

**Goal**: Find all RCTs for GLP-1 agonists in obesity (for meta-analysis)

```python
from mcp.servers.pubmed_mcp import search_keywords

result = search_keywords(
    keywords='"Glucagon-Like Peptide 1"[MeSH] AND obesity[MeSH] AND (randomized controlled trial[pt]) AND humans[MeSH]',
    num_results=50
)

# Collect PMIDs for PRISMA flowchart
pmids = []
for article in result.get('articles', []):
    pmids.append(article.get('pmid'))

print(f"Found {len(pmids)} RCTs for systematic review")
print(f"PMIDs: {', '.join(pmids)}")
```

### Use Case 3: Author Publication Tracking

**Goal**: Track all publications by specific author in diabetes research

```python
from mcp.servers.pubmed_mcp import search_advanced

result = search_advanced(
    author="Smith J",
    term="diabetes",
    start_date="2020/01/01",
    num_results=30
)

# Group by year
from collections import defaultdict
by_year = defaultdict(list)

for article in result.get('articles', []):
    pub_date = article.get('pub_date', 'Unknown')
    year = pub_date[:4] if pub_date else 'Unknown'
    title = article.get('title')
    by_year[year].append(title)

# Display
for year in sorted(by_year.keys(), reverse=True):
    print(f"\n{year} ({len(by_year[year])} papers):")
    for title in by_year[year]:
        print(f"  - {title}")
```

### Use Case 4: Journal-Specific Research

**Goal**: Get all diabetes papers from NEJM in 2024

```python
from mcp.servers.pubmed_mcp import search_advanced

result = search_advanced(
    term="diabetes",
    journal="N Engl J Med",
    start_date="2024/01/01",
    end_date="2024/12/31",
    num_results=20
)

# Extract key findings from abstracts
for article in result.get('articles', []):
    title = article.get('title')
    abstract = article.get('abstract', '')

    print(f"\nTitle: {title}")

    # Extract conclusion (usually last part of abstract)
    if 'CONCLUSION' in abstract.upper():
        conclusion = abstract.split('CONCLUSION')[-1]
        print(f"Conclusion: {conclusion[:200]}...")
```

### Use Case 5: Citation Management

**Goal**: Get full citation strings for bibliography

```python
from mcp.servers.pubmed_mcp import get_article_metadata

pmids = ["12345678", "87654321", "11111111"]

for pmid in pmids:
    article = get_article_metadata(pmid=pmid)

    # Get formatted citation
    citation = article.get('citation')
    if citation:
        print(citation)
    else:
        # Build citation manually
        authors = article.get('authors', [])
        author_str = ', '.join([a.get('name') for a in authors[:3]])
        if len(authors) > 3:
            author_str += ', et al.'

        title = article.get('title')
        journal = article.get('journal')
        pub_date = article.get('pub_date', '')
        year = pub_date[:4] if pub_date else 'n.d.'

        print(f"{author_str}. {title}. {journal}. {year}.")
```

### Use Case 6: Download Open Access PDFs

**Goal**: Batch download PDFs for all available articles

```python
from mcp.servers.pubmed_mcp import search_keywords, get_article_pdf
import base64
import os

# Search for open access articles
result = search_keywords(
    keywords="diabetes AND free full text[sb]",  # Open access filter
    num_results=10
)

# Create download directory
os.makedirs('pdfs', exist_ok=True)

# Attempt to download each
for article in result.get('articles', []):
    pmid = article.get('pmid')
    title = article.get('title', 'unknown')

    print(f"\nAttempting to download PMID {pmid}...")

    pdf_result = get_article_pdf(pmid=pmid)

    if pdf_result.get('available') and 'pdf_data' in pdf_result:
        # Decode and save
        pdf_bytes = base64.b64decode(pdf_result['pdf_data'])

        # Sanitize filename
        filename = f"pdfs/{pmid}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)

        print(f"  ✓ Downloaded: {filename}")
    else:
        print(f"  ✗ Not available: {pdf_result.get('message')}")
```

---

## Known Quirks & Limitations

### 1. 🔴 MCP Result Count Limitation (CRITICAL)

**Issue**: Server returns fewer results than `num_results` requested

**Evidence**:
- Requested 30 → Received 2
- Requested 5 → Received 3
- Appears to be MCP tool limitation, not PubMed API issue

**Impact**: Cannot rely on exact result counts

**Workaround**:
```python
# ✅ Request conservative numbers
result = search_keywords("diabetes", num_results=20)

# ✅ Handle variable counts
articles = result.get('articles', [])
print(f"Expected 20, got {len(articles)}")  # Be prepared!

# ✅ Don't assume completeness
if len(articles) < num_results:
    print("Partial results - this is expected")
```

### 2. Token Usage (~750 per Article)

**Issue**: Full articles with abstracts use significant tokens

**Impact**: Large result sets can hit context limits

**Workaround**:
```python
# ✅ Request only needed articles
num_results=10  # Conservative

# ✅ Process incrementally
for article in articles:
    # Extract only what you need
    pmid = article.get('pmid')
    title = article.get('title')
    # Skip full abstract if not needed
```

### 3. Date Format Requirement

**Issue**: Dates must be in `YYYY/MM/DD` format

```python
# ✅ CORRECT
start_date="2024/01/01"
keywords='diabetes AND ("2024/01/01"[PDAT] : "2024/12/31"[PDAT])'

# ❌ WRONG
start_date="2024-01-01"  # Wrong separator
start_date="01/01/2024"  # Wrong order
```

### 4. PDF Availability Varies

**Issue**: Most articles don't have freely available PDFs

**Statistics** (approximate):
- ~30% have open access PDFs via PMC
- ~50% paywalled (require subscription)
- ~20% have embargo periods (available later)

**Workaround**:
```python
# ✅ Check availability before processing
pdf_result = get_article_pdf(pmid)
if not pdf_result.get('available'):
    print("Use institutional access or contact authors")
```

### 5. MeSH Term Syntax

**Issue**: MeSH terms require exact formatting

```python
# ✅ CORRECT
keywords='"Diabetes Mellitus, Type 2"[MeSH]'

# ❌ WRONG
keywords='Diabetes Mellitus, Type 2[MeSH]'  # Missing quotes
keywords='"diabetes type 2"[MeSH]'  # Not official MeSH term
```

**Find exact MeSH**: https://www.ncbi.nlm.nih.gov/mesh

### 6. Author Name Variations

**Issue**: Authors may be indexed differently

```python
# Try multiple formats
search_advanced(author="Smith J")  # Initial
search_advanced(author="Smith John")  # Full name
search_advanced(author="Smith")  # Last name only
```

### 7. Journal Name Variations

**Issue**: Journals have abbreviations and full names

```python
# Both work
journal="N Engl J Med"  # Abbreviation
journal="New England Journal of Medicine"  # Full name
```

---

## Best Practices

### ✅ DO

1. **Use MeSH terms for precision**
   ```python
   keywords='"Diabetes Mellitus, Type 2"[MeSH] AND treatment'
   ```

2. **Request conservative result counts**
   ```python
   num_results=10  # Not 100
   ```

3. **Handle variable result counts gracefully**
   ```python
   articles = result.get('articles', [])
   if len(articles) == 0:
       print("No results")
   ```

4. **Use `.get()` for safe dictionary access**
   ```python
   title = article.get('title', 'No title')
   ```

5. **Filter by study type for evidence-based research**
   ```python
   keywords="treatment AND (randomized controlled trial[pt])"
   ```

6. **Use date filters for recent research**
   ```python
   start_date="2023/01/01"
   ```

7. **Check PDF availability before processing**
   ```python
   if pdf_result.get('available'):
       # Process PDF
   ```

### ❌ DON'T

1. **Don't request excessive results**
   ```python
   num_results=100  # Will likely get far fewer
   ```

2. **Don't assume exact result counts**
   ```python
   assert len(articles) == num_results  # Will fail!
   ```

3. **Don't use direct dictionary access**
   ```python
   authors = article['authors']  # KeyError risk!
   ```

4. **Don't mix date formats**
   ```python
   start_date="2024-01-01"  # Wrong! Use 2024/01/01
   ```

5. **Don't expect all PDFs to be available**
   ```python
   pdf = get_article_pdf(pmid)  # May not be available!
   ```

6. **Don't use imprecise free text when MeSH exists**
   ```python
   keywords="diabetes type 2"  # Use MeSH instead
   ```

7. **Don't load unnecessary data into context**
   ```python
   # Skip abstracts if you only need titles/PMIDs
   ```

---

## FAQ

### Q1: How many results can I request?

**A**: Maximum `num_results=100`, but expect fewer due to MCP limitation.

**Recommendation**: Request 10-20 for most queries.

### Q2: Why do I get fewer results than requested?

**A**: Known MCP limitation (validated in testing). Request conservative numbers and handle variable counts gracefully.

### Q3: How do I search for exact phrases?

**A**: Use quotes in keywords:
```python
keywords='"GLP-1 agonist" AND obesity'
```

### Q4: What's the difference between search_keywords and search_advanced?

**A**:
- `search_keywords`: Single string, supports PubMed syntax (MeSH, operators, filters)
- `search_advanced`: Structured parameters (author, journal, dates as separate fields)

**Use search_keywords** when you need complex PubMed syntax.
**Use search_advanced** when you have structured filter criteria.

### Q5: How do I find MeSH terms?

**A**: Use PubMed MeSH browser: https://www.ncbi.nlm.nih.gov/mesh

Or search PubMed and check "MeSH Terms" in article details.

### Q6: Why can't I download some PDFs?

**A**: PDF availability depends on:
- Publisher open access policies
- PubMed Central (PMC) repository
- Embargo periods
- Journal subscription status

**Only ~30% of articles have freely available PDFs.**

### Q7: How do I limit to human studies?

**A**: Add `AND humans[MeSH]` to keywords:
```python
keywords="gene therapy AND humans[MeSH]"
```

### Q8: Can I search multiple journals?

**A**: Yes, in search_advanced with OR:
```python
journal="N Engl J Med OR Lancet OR Nature"
```

### Q9: How do I get only RCTs?

**A**: Use publication type filter:
```python
keywords="treatment AND (randomized controlled trial[pt])"
```

### Q10: What does [pt] mean?

**A**: Publication Type field tag. Other tags:
- `[MeSH]` - MeSH term
- `[PDAT]` - Publication date
- `[AU]` - Author
- `[TA]` - Journal title abbreviation
- `[TI]` - Title
- `[AB]` - Abstract

---

## Summary

**PubMed MCP Server** provides access to 35+ million biomedical citations with:

✅ **Strengths**:
- Massive biomedical literature database
- Rich search syntax (MeSH, operators, filters)
- Structured JSON responses (easy to parse)
- Metadata includes authors, affiliations, MeSH terms
- Some open access PDF downloads

⚠️ **Critical Limitations**:
- **MCP result count issue** (returns fewer than requested)
- ~750 tokens per article (context usage)
- Date format must be YYYY/MM/DD
- PDF availability varies (~30% available)

🎯 **Best Use Cases**:
- Literature reviews for drug discovery
- Finding clinical study publications
- Systematic reviews and meta-analyses
- Author/journal tracking
- Evidence-based research

**Always**: Use MeSH terms, request conservative result counts, handle variable returns gracefully.
