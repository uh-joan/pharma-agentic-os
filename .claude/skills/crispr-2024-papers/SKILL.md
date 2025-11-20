---
name: get_crispr_2024_papers
description: >
  Search PubMed for CRISPR gene editing research papers published in 2024.
  Returns comprehensive metadata including authors, journal, PMID, and publication date.
  Useful for literature reviews, staying current with CRISPR advances, tracking research trends,
  and identifying key publications in gene editing field.

  Trigger keywords: CRISPR, gene editing, 2024 papers, PubMed literature, recent publications,
  CRISPR research, genome editing papers
category: target-validation
mcp_servers:
  - pubmed_mcp
patterns:
  - json_parsing
  - date_filtering
  - metadata_extraction
data_scope:
  total_results: 100
  geographical: Global
  temporal: 2024 publications only
created: 2025-11-19
last_updated: 2025-11-19
complexity: simple
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw PubMed data
---

# get_crispr_2024_papers

## Purpose
Search PubMed for CRISPR gene editing research papers published in 2024, extracting comprehensive metadata for each publication.

## Usage
Execute to get current CRISPR literature from 2024 with full bibliographic details.

Use cases:
- Literature reviews for CRISPR research
- Tracking recent advances in gene editing
- Identifying key publications and authors
- Journal analysis for publication strategy
- Monitoring research trends

## Implementation Details

### Data Source
- **MCP Server**: `pubmed_mcp`
- **Query**: "CRISPR gene editing" with 2024 date filter
- **Date Range**: 2024/01/01 to 2024/12/31

### Metadata Extracted
For each paper:
- PMID (PubMed ID)
- Title
- Authors (first 3 + et al.)
- Journal name
- Publication date (month + year)

### Return Format
```python
{
    'total_count': int,
    'papers': [
        {
            'pmid': str,
            'title': str,
            'authors': str,
            'journal': str,
            'publication_date': str
        },
        ...
    ],
    'summary': str  # Formatted text with top journals and sample papers
}
```

### Summary Includes
- Total papers found
- Top 5 journals by publication count
- First 5 papers with full metadata

## Example Output

```
CRISPR Gene Editing Papers - 2024

Total Papers Found: 100

Top Journals:
  • International Journal of Molecular Sciences: 6 papers
  • Nature Communications: 6 papers
  • Frontiers in Genome Editing: 5 papers
  • Nucleic Acids Research: 4 papers
  • Molecular Therapy: 4 papers

Sample Papers:

1. [Paper Title]
   Authors: Smith J, Jones A, et al.
   Journal: Nature Communications
   PMID: 38123456
   Date: March 2024
```

## Technical Notes

### Date Filtering
Uses PubMed's PDAT (Publication Date) field with explicit date range:
```python
date_filter = "2024/01/01:2024/12/31[PDAT]"
```

### JSON Parsing
Safely extracts nested fields using `.get()` method:
```python
pmid = medline.get('PMID', {}).get('value', 'N/A')
title = article_data.get('ArticleTitle', 'No title')
```

### Author Handling
- Extracts first 3 authors by name
- Adds "et al." if more than 3 authors
- Handles missing author data gracefully

### Error Handling
- Continues processing if individual article parsing fails
- Returns empty results if no papers found
- Provides fallback values for missing fields

## Limitations
- Returns maximum 100 papers (PubMed default)
- For comprehensive reviews, may need pagination
- Author list truncated to first 3 for readability

## Related Skills
- `get_pubmed_articles` - General PubMed search
- `get_gene_editing_reviews` - Review articles only
- `get_clinical_crispr_papers` - Clinical CRISPR trials
