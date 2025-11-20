# ClinicalTrials.gov MCP Tool Guide

**MCP Server**: `ct-gov-mcp`
**Tool Name**: `ct_gov_studies`
**Schema Version**: Auto-generated from MCP schema (2025-11-19)

---

## 🔴 CRITICAL: Response Format

**ClinicalTrials.gov returns MARKDOWN, not JSON!**

All other MCP servers return JSON dictionaries, but CT.gov returns a markdown-formatted string that must be parsed with regex.

```python
# ❌ WRONG: Treating response as JSON
result = ct_gov_mcp.search(condition="diabetes")
trials = result['trials']  # ERROR: 'str' object is not subscriptable

# ✅ CORRECT: Parse markdown response
result = ct_gov_mcp.search(condition="diabetes")
nct_ids = re.findall(r'NCT\d{8}', result)  # Extract NCT IDs with regex
```

**See**: `.claude/.context/code-examples/ctgov_markdown_parsing.md` for parsing patterns.

---

## Available Methods

### 1. `search` - Find Clinical Trials
Search for clinical trials using various filters and parameters.

### 2. `suggest` - Get Term Suggestions
Get autocomplete suggestions for search terms from CT.gov dictionaries.

### 3. `get` - Get Detailed Study Information
Retrieve complete information for a specific trial by NCT ID.

---

## Method 1: `search` - Find Clinical Trials

### Required Parameters
- `method`: `"search"` (required)

### Search Term Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `condition` | string | Primary condition/disease | `"Diabetes Mellitus Type 2"`, `"Heart Failure"`, `"Cancer"` |
| `term` | string | Additional search terms | `"Hypertension"`, `"diabetes OR hypertension"` |
| `intervention` | string | Drug/treatment being studied | `"Aspirin"`, `"semaglutide OR liraglutide"` |
| `titles` | string | Search in study titles | `"weight loss"` |
| `outc` | string | Search in outcomes/endpoints | `"mortality"` |
| `id` | string | Study identifiers | `"NCT00841061"`, `"ORG-123"` |

**💡 Pro Tip**: Use `OR` operator to combine multiple terms: `"obesity OR weight loss"`

### Trial Characteristics

#### Phase
```json
{
  "phase": "PHASE2"  // Options: PHASE0, PHASE1, PHASE2, PHASE3, PHASE4, EARLY_PHASE1, NA
}
```

#### Status (Recruitment)
```json
{
  "status": "recruiting"
  // Options: not_yet_recruiting, recruiting, active_not_recruiting, completed,
  //          terminated, enrolling_by_invitation, suspended, withdrawn, unknown
  // Combined: "recruiting OR active_not_recruiting"
}
```

#### Study Type
```json
{
  "studyType": "interventional"
  // Options: interventional, observational, expanded_access,
  //          observational_patient_registry, expanded_access_individual,
  //          expanded_access_intermediate, expanded_access_treatment
  // Combined: "interventional OR observational"
}
```

### Eligibility Criteria

#### Age Groups
```json
{
  "ages": "adult"
  // Options: child, adult, older_adult
  // Combined: "child OR adult"
}
```

#### Custom Age Range
```json
{
  "ageRange": "18y_65y"  // Format: "minAge_maxAge" (e.g., "16y_34y", "65y_85y")
}
```

#### Sex/Gender
```json
{
  "sex": "all"  // Options: all, m, f
}
```

#### Healthy Volunteers
```json
{
  "healthy": "y"  // Include studies accepting healthy volunteers
}
```

### Study Design

#### Allocation
```json
{
  "allocation": "randomized"
  // Options: randomized, nonrandomized, na
  // Combined: "randomized OR nonrandomized"
}
```

#### Masking/Blinding
```json
{
  "masking": "double"
  // Options: none, single, double, triple, quadruple
  // Combined: "single OR double"
}
```

#### Who is Masked
```json
{
  "whoMasked": "participant OR careprovider"
  // Options: participant, careprovider, investigator, outcomesassessor
  // Combined: "participant OR careprovider OR investigator"
}
```

#### Assignment
```json
{
  "assignment": "parallel"
  // Options: single, parallel, crossover, factorial, sequential
  // Combined: "parallel OR crossover"
}
```

#### Primary Purpose
```json
{
  "purpose": "treatment"
  // Options: treatment, prevention, diagnostic, supportive, screening,
  //          healthservices, basicscience, devicefeasibility, other
  // Combined: "treatment OR prevention"
}
```

#### Observational Model (for observational studies)
```json
{
  "model": "cohort"
  // Options: cohort, casecontrol, caseonly, casecrossover, ecologic, familybased, other, defined
  // Combined: "cohort OR casecontrol"
}
```

#### Time Perspective (for observational studies)
```json
{
  "timePerspective": "prospective"
  // Options: retrospective, prospective, crosssectional, other
  // Combined: "retrospective OR prospective"
}
```

### Intervention Details

#### Intervention Type
```json
{
  "interventionType": "drug"
  // Options: drug, device, biological, procedure, behavioral, genetic,
  //          dietary, radiation, combination, diagnostic, other
  // Combined: "drug OR device"
}
```

### Administrative Filters

#### Location
```json
{
  "location": "Texas"  // Examples: "Houston", "Texas", "United States", "US"
  // Combined: "Texas OR California"
}
```

#### Lead Sponsor
```json
{
  "lead": "Pfizer"  // Company/organization name
  // Combined: "Pfizer OR Merck"
}
```

#### Funder Type
```json
{
  "funderType": "industry"
  // Options: nih, fed, industry, other, indiv, network
  // Combined: "nih OR industry"
}
```

### Data Availability Filters

#### Results Posted
```json
{
  "results": "with"  // Options: with, without, "with without"
}
```

#### Study Documents
```json
{
  "docs": "prot"  // Options: prot (protocol), sap, icf, csr
  // Combined: "prot sap icf"
}
```

#### FDA Violations
```json
{
  "violation": "y"  // Include studies with FDA violations
}
```

### Date Range Filters

All date ranges use format: `"YYYY-MM-DD_YYYY-MM-DD"`

```json
{
  "start": "2020-01-01_2024-12-31",        // Study start date
  "primComp": "2020-01-01_2024-12-31",     // Primary completion date
  "studyComp": "2020-01-01_2024-12-31",    // Study completion date
  "firstPost": "2020-01-01_2024-12-31",    // Study first posted
  "lastUpdPost": "2020-01-01_2024-12-31",  // Last update posted
  "resFirstPost": "2020-01-01_2024-12-31"  // Results first posted
}
```

### Pagination & Results

```json
{
  "pageSize": 100,      // Results per page (default: 10, max: 100)
  "pageToken": "token", // Token from previous response for next page
  "countTotal": true,   // Include total count in response (default: true)
  "sort": "@relevance"  // Sort order
}
```

**Sort Options**:
- `@relevance` - Most relevant first
- `StudyFirstPostDate` - Newest first
- `LastUpdatePostDate` - Recently updated
- `NCTId` - By NCT number
- `StartDate` - By start date
- `PrimaryCompletionDate` - By completion date
- `EnrollmentCount` - By enrollment size

### Advanced: Complex Query Syntax

For maximum precision, use `complexQuery` with CT.gov operators:

```json
{
  "method": "search",
  "complexQuery": "diabetes AND AREA[Phase]PHASE2 AND AREA[OverallStatus]RECRUITING",
  "pageSize": 100
}
```

**Boolean Operators**:
- `AND` - Both conditions must match
- `OR` - Either condition matches
- `NOT` - Exclude matches
- `()` - Grouping

**Context Operators**:
- `AREA[field]value` - Search specific field
- `SEARCH[context](query)` - Nested search
- `RANGE[start, end]` - Date/number ranges (use MAX/MIN for open ranges)
- `MISSING` - Find null values
- `"exact phrase"` - Exact phrase match

**Common AREA Fields**:
- `AREA[Phase]PHASE2`
- `AREA[StdAge]ADULT`
- `AREA[OverallStatus]RECRUITING`
- `AREA[ConditionSearch]diabetes`
- `AREA[InterventionName]semaglutide`
- `AREA[LeadSponsorName]Pfizer`
- `AREA[LocationCountry]United States`
- `AREA[DesignAllocation]RANDOMIZED`
- `AREA[DesignMasking]DOUBLE`
- `AREA[StudyType]INTERVENTIONAL`

**Examples**:

```python
# Find Phase 2 diabetes or metabolic syndrome trials
{
  "complexQuery": "(diabetes OR \"metabolic syndrome\") AND AREA[Phase]PHASE2"
}

# Exclude placebo-only trials
{
  "complexQuery": "AREA[InterventionName]aspirin AND NOT placebo"
}

# Boston-area cancer studies
{
  "complexQuery": "cancer AND SEARCH[Location](AREA[LocationCity]Boston AND AREA[LocationState]Massachusetts)"
}

# Recent studies (posted since 2020)
{
  "complexQuery": "diabetes AND AREA[StudyFirstPostDate]RANGE[2020-01-01, MAX]"
}

# Randomized interventional heart attack studies
{
  "complexQuery": "heart attack AND AREA[DesignAllocation]RANDOMIZED AND AREA[StudyType]INTERVENTIONAL"
}
```

**When to use complexQuery?**
- ✅ Need exact field matching (like expert search on clinicaltrials.gov)
- ✅ Complex boolean logic with multiple conditions
- ✅ Date ranges or exclusions
- ❌ Simple single-condition searches (use `condition` parameter instead)

---

## Method 2: `suggest` - Get Term Suggestions

Get autocomplete suggestions from CT.gov dictionaries.

### Required Parameters
```json
{
  "method": "suggest",
  "input": "diab",       // Minimum 2 characters
  "dictionary": "Condition"
}
```

### Dictionaries
- `Condition` - Disease/condition names
- `InterventionName` - Drug/treatment names
- `LeadSponsorName` - Organization names
- `LocationFacility` - Hospital/facility names

### Example
```json
{
  "method": "suggest",
  "input": "semaglu",
  "dictionary": "InterventionName"
}
```

**Returns**: List of matching terms for autocomplete

---

## Method 3: `get` - Get Detailed Study Information

Retrieve complete information for a specific trial.

### Required Parameters
```json
{
  "method": "get",
  "nctId": "NCT00841061"  // Format: NCT + 8 digits
}
```

### Optional Parameters
```json
{
  "format": "json",        // Options: json, csv, json.zip, fhir.json, ris (default: json)
  "markupFormat": "markdown",  // Options: markdown, legacy (default: markdown)
  "fields": ["NCTId", "BriefTitle", "OverallStatus"]  // Specific fields only
}
```

**Field Selection** (reduces token usage):
```json
{
  "method": "get",
  "nctId": "NCT04000165",
  "fields": [
    "NCTId",
    "BriefTitle",
    "OverallStatus",
    "Phase",
    "EnrollmentCount",
    "LeadSponsorName"
  ]
}
```

---

## Response Format & Parsing

### 🔴 CRITICAL: Markdown Response

Unlike other MCP servers (FDA, PubMed, etc.) that return JSON, **CT.gov returns markdown text**.

```python
result = ct_gov_mcp.search(condition="diabetes", pageSize=5)
# result is a STRING, not a dict!

# Parse with regex
import re

# Extract NCT IDs
nct_ids = re.findall(r'NCT\d{8}', result)

# Extract sections
titles = re.findall(r'\*\*Brief Title:\*\* (.*)', result)
statuses = re.findall(r'\*\*Overall Status:\*\* (.*)', result)

# Count results
total_count = len(nct_ids)
```

### Pagination Pattern

```python
# Page 1
result = ct_gov_mcp.search(
    condition="diabetes",
    pageSize=100
)

# Extract nextPageToken from markdown
next_token_match = re.search(r'Next Page Token: ([\w-]+)', result)
if next_token_match:
    next_token = next_token_match.group(1)

    # Page 2
    result2 = ct_gov_mcp.search(
        condition="diabetes",
        pageSize=100,
        pageToken=next_token
    )
```

**See**: `.claude/.context/code-examples/ctgov_markdown_parsing.md` for complete patterns.

---

## Common Use Cases

### 1. Find Recruiting Trials by Condition
```json
{
  "method": "search",
  "condition": "Diabetes Mellitus Type 2",
  "status": "recruiting",
  "pageSize": 50
}
```

### 2. Phase 3 Trials by Company
```json
{
  "method": "search",
  "intervention": "semaglutide",
  "phase": "PHASE3",
  "lead": "Novo Nordisk",
  "pageSize": 50
}
```

### 3. Recent Trials (Posted in 2024)
```json
{
  "method": "search",
  "condition": "obesity",
  "firstPost": "2024-01-01_2024-12-31",
  "pageSize": 100
}
```

### 4. US-Based Adult Trials
```json
{
  "method": "search",
  "condition": "heart failure",
  "location": "United States",
  "ages": "adult",
  "pageSize": 50
}
```

### 5. Completed Trials with Results
```json
{
  "method": "search",
  "condition": "cancer",
  "status": "completed",
  "results": "with",
  "pageSize": 100
}
```

### 6. Industry-Sponsored Drug Trials
```json
{
  "method": "search",
  "intervention": "monoclonal antibody",
  "interventionType": "biological",
  "funderType": "industry",
  "pageSize": 50
}
```

---

## Best Practices

### ✅ DO

1. **Use specific status values** (case-sensitive):
   - ✅ `"recruiting"`
   - ❌ `"Recruiting"` or `"RECRUITING"`

2. **Use correct phase format**:
   - ✅ `"PHASE2"`, `"PHASE3"`
   - ❌ `"Phase 2"`, `"Phase 3"`

3. **Parse markdown responses** with regex:
   ```python
   nct_ids = re.findall(r'NCT\d{8}', result)
   ```

4. **Limit fields when possible**:
   ```json
   {"fields": ["NCTId", "BriefTitle", "OverallStatus"]}
   ```

5. **Use pagination for large result sets**:
   ```json
   {"pageSize": 100, "pageToken": "..."}
   ```

6. **Combine filters with OR**:
   ```json
   {"intervention": "semaglutide OR liraglutide"}
   ```

### ❌ DON'T

1. **Don't treat response as JSON**:
   ```python
   # ❌ WRONG
   trials = result['trials']  # Error: string has no key 'trials'

   # ✅ CORRECT
   nct_ids = re.findall(r'NCT\d{8}', result)
   ```

2. **Don't use incorrect status casing**:
   ```json
   // ❌ WRONG
   {"status": "RECRUITING"}

   // ✅ CORRECT
   {"status": "recruiting"}
   ```

3. **Don't forget pagination** for large datasets:
   ```python
   # ❌ WRONG: Only gets first 10 results
   result = search(condition="diabetes")

   # ✅ CORRECT: Gets up to 100 results
   result = search(condition="diabetes", pageSize=100)
   ```

4. **Don't use simplified parameters when complexQuery is needed**:
   ```json
   // ❌ LESS PRECISE
   {"condition": "diabetes", "status": "recruiting"}

   // ✅ MORE PRECISE
   {"complexQuery": "AREA[ConditionSearch]diabetes AND AREA[OverallStatus]RECRUITING"}
   ```

---

## Known Quirks & Limitations

### 1. Markdown Response Format
- **Only CT.gov returns markdown** - all other MCPs return JSON
- Must use regex parsing, not JSON methods
- Pattern: `.claude/.context/code-examples/ctgov_markdown_parsing.md`

### 2. Case-Sensitive Parameters
- Status values are lowercase: `"recruiting"` not `"RECRUITING"`
- Phase values are uppercase: `"PHASE2"` not `"phase2"`
- Inconsistent with web interface (which accepts any case)

### 3. Pagination Token Extraction
- `nextPageToken` must be extracted from markdown response
- Look for pattern: `Next Page Token: [token]`
- Empty when no more pages

### 4. Field Name Differences
- MCP uses camelCase: `nctId`, `pageSize`
- Web API uses PascalCase: `NCTId`, `PageSize`
- Schema enforces MCP format

### 5. Date Format Variations
- Search parameters: `"YYYY-MM-DD_YYYY-MM-DD"` (underscore separator)
- Complex queries: `RANGE[YYYY-MM-DD, YYYY-MM-DD]` (comma separator)

### 6. Maximum Page Size
- Hard limit: 100 results per page
- For >100 results, must use pagination
- Set `pageSize=100` for efficiency

### 7. OR Operator in Simple Parameters
- Works in `condition`, `intervention`, `term`, etc.
- Example: `"condition": "diabetes OR obesity"`
- Alternative: Use `complexQuery` for complex boolean logic

---

## Performance Optimization

### Token Reduction Strategies

1. **Limit fields** (90% token reduction):
   ```json
   {"fields": ["NCTId", "BriefTitle"]}  // ~500 tokens vs ~5000
   ```

2. **Filter precisely** (reduce result count):
   ```json
   {"condition": "rare disease", "status": "recruiting"}  // 5 results
   ```
   vs
   ```json
   {"condition": "cancer"}  // 50,000+ results
   ```

3. **Use complexQuery** (more precise matching):
   ```json
   {"complexQuery": "AREA[ConditionSearch](\"Diabetes Mellitus, Type 2\"[MeSH])"}
   ```

4. **Pagination** (process in chunks):
   ```python
   # Process 100 at a time instead of 10,000 at once
   for page in range(100):
       result = search(pageSize=100, pageToken=token)
       # Process this page
       token = extract_next_token(result)
   ```

---

## Schema Examples (from MCP)

The MCP server provides these built-in examples:

1. **Basic diabetes search**:
   ```json
   {"method": "search", "condition": "diabetes", "pageSize": 5}
   ```

2. **Term suggestions**:
   ```json
   {"method": "suggest", "input": "diab", "dictionary": "Condition"}
   ```

3. **Get specific study**:
   ```json
   {"method": "get", "nctId": "NCT00841061"}
   ```

4. **Complex Phase 2 search**:
   ```json
   {
     "method": "search",
     "complexQuery": "(diabetes OR \"metabolic syndrome\") AND AREA[Phase]PHASE2",
     "pageSize": 10
   }
   ```

5. **Exclude placebo**:
   ```json
   {
     "method": "search",
     "complexQuery": "AREA[InterventionName]aspirin AND NOT placebo",
     "pageSize": 15
   }
   ```

6. **Location-specific**:
   ```json
   {
     "method": "search",
     "complexQuery": "cancer AND SEARCH[Location](AREA[LocationCity]Boston AND AREA[LocationState]Massachusetts)",
     "pageSize": 20
   }
   ```

7. **Date range (recent trials)**:
   ```json
   {
     "method": "search",
     "complexQuery": "diabetes AND AREA[StudyFirstPostDate]RANGE[2020-01-01, MAX]",
     "pageSize": 25
   }
   ```

---

## Quick Reference

| Task | Parameter | Example Value |
|------|-----------|---------------|
| Find by disease | `condition` | `"Diabetes Mellitus Type 2"` |
| Find by drug | `intervention` | `"semaglutide"` |
| Filter by phase | `phase` | `"PHASE2"`, `"PHASE3"` |
| Filter by status | `status` | `"recruiting"`, `"completed"` |
| Filter by location | `location` | `"Texas"`, `"United States"` |
| Filter by sponsor | `lead` | `"Pfizer"`, `"Novo Nordisk"` |
| Results per page | `pageSize` | `100` (max) |
| Next page | `pageToken` | Extract from markdown response |
| Specific trial | `nctId` | `"NCT00841061"` |
| Advanced search | `complexQuery` | AREA[] syntax |

---

## Related Resources

- **Markdown Parsing Pattern**: `.claude/.context/code-examples/ctgov_markdown_parsing.md`
- **Pagination Pattern**: `.claude/.context/code-examples/ctgov_pagination_pattern.md`
- **Skills Library**: Check existing CT.gov skills for proven patterns
- **Official API Docs**: https://clinicaltrials.gov/data-api/api

---

**Last Updated**: Auto-generated from MCP schema - 2025-11-19
