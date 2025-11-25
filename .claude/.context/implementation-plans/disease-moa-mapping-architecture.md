# Disease Area and Mechanism of Action Mapping - Implementation Plan

## Executive Summary

**Capability**: Map competitor drug portfolios by disease area and mechanism of action to identify strategic positioning, competitive intensity, and white space opportunities.

**Strategic Value**: Enables BD teams to visualize competitive landscape, identify acquisition targets, assess partnership opportunities, and make informed portfolio decisions.

**Implementation Complexity**: High (Multi-server data integration, NLP extraction, ontology mapping, graph visualization)

**Estimated Development**: 3-4 weeks for MVP, 2-3 months for production system

---

## Problem Definition

### Business Need

BD teams need to answer strategic questions like:
- **Portfolio Clustering**: "Which companies dominate KRAS inhibitor development?"
- **White Space**: "What MoA-disease combinations lack competitor coverage?"
- **Modality Strategy**: "Is Competitor X focused on antibodies or small molecules?"
- **Multi-indication Plays**: "Which drugs are being tested across multiple diseases?"
- **Competitive Intensity**: "How crowded is the GLP-1 receptor agonist space?"

### Current Gap

Existing competitive intelligence is often:
- **Fragmented**: Trial data separate from approval data, patents disconnected
- **Manual**: Analysts manually scan ClinicalTrials.gov and FDA databases
- **Point-in-time**: Snapshot reports that quickly become outdated
- **Narrative-heavy**: Long text reports without visual strategic maps

### Proposed Solution

Automated system that:
1. **Collects** clinical trial, FDA, patent, and publication data
2. **Extracts** disease areas and mechanisms of action using NLP
3. **Normalizes** entities using OpenTargets (EFO/MONDO for diseases, target validation for MoA)
4. **Maps** portfolios by company → disease → MoA → drug/trial
5. **Visualizes** competitive landscape as matrices, networks, heat maps
6. **Analyzes** strategic positioning, gaps, and opportunities

---

## Data Requirements

### Primary Data Sources (MCP Servers)

| Source | Purpose | Key Fields | Update Frequency |
|--------|---------|------------|------------------|
| **ct_gov_mcp** | Clinical trial pipeline | Sponsor, indication, intervention, phase, status | Real-time |
| **fda_mcp** | Approved drugs | Applicant, indication, mechanism, approval date | Daily |
| **pubmed_mcp** | Scientific rationale | MoA descriptions, disease biology | Weekly |
| **uspto_patents_mcp** | IP landscape | Assignee, claims (MoA details), therapeutic use | Weekly |
| **opentargets_mcp** | Target validation | Target-disease associations, mechanism | Monthly |
| **pubchem_mcp** | Compound properties | Chemical class, pharmacology | As needed |

### Data Extraction Challenges

**Challenge 1: Mechanism of Action Extraction**
- **Problem**: MoA buried in trial descriptions as free text
- **Example**: "A Phase 2 study of ABC-123, a selective KRAS G12C inhibitor, in NSCLC"
- **Solution**: NLP pattern matching + ontology mapping

**Challenge 2: Disease Area Normalization**
- **Problem**: Multiple names for same disease ("T2DM", "Type 2 Diabetes", "NIDDM")
- **Solution**: Use OpenTargets search_diseases API (normalizes to EFO/MONDO IDs, handles synonyms)

**Challenge 3: Company Attribution**
- **Problem**: Lead sponsors, collaborators, licensees, acquired companies
- **Solution**: Company relationship graph + M&A tracking

**Challenge 4: Multi-indication Drugs**
- **Problem**: One drug tested in 5+ diseases (e.g., checkpoint inhibitors)
- **Solution**: Many-to-many mapping (drug ↔ diseases)

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query Interface                      │
│  "Map KRAS inhibitor competitive landscape"                 │
│  "Show Pfizer's oncology portfolio by MoA"                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Query Parser & Parameter Extraction             │
│  - Therapeutic area: "KRAS inhibitors"                      │
│  - Scope: All companies OR specific company                 │
│  - Timeframe: All phases OR Phase 2+                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Data Collection Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ CT.gov   │  │   FDA    │  │  PubMed  │  │  USPTO   │  │
│  │  Trials  │  │  Drugs   │  │   Pubs   │  │ Patents  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Entity Extraction & NLP Layer                   │
│  - MoA Extraction (regex + ML)                              │
│  - Disease Normalization (EFO mapping)                      │
│  - Company Attribution (sponsor → parent company)           │
│  - Drug Name Deduplication (ABC-123 = Drug X)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Ontology Mapping & Normalization                │
│  - Disease → OpenTargets search_diseases (EFO/MONDO IDs)  │
│  - MoA → OpenTargets target validation + pattern matching │
│  - Target-Disease validation → OpenTargets associations   │
│  - Company → Parent entity (M&A tracking)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Portfolio Aggregation Engine                 │
│  - Group by: Company → Disease → MoA → Drugs              │
│  - Count assets per category                               │
│  - Calculate competitive intensity scores                   │
│  - Identify coverage gaps (MoA × Disease matrix)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Visualization & Analysis Layer                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Matrix    │  │  Network   │  │  Heat Map  │           │
│  │   View     │  │   Graph    │  │    View    │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Strategic Insights Generator                    │
│  - Clustering analysis (companies with similar portfolios)  │
│  - White space identification (uncovered MoA × Disease)     │
│  - Competitive intensity scoring (asset count per area)     │
│  - Differentiation opportunities (novel MoA combinations)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Report Generation                         │
│  - Markdown report with visualizations                      │
│  - CSV export for further analysis                          │
│  - JSON API for dashboard integration                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Data Collection Foundation (Week 1-2)

**Goal**: Reliable data ingestion from MCP servers

**Tasks**:
1. Create skill: `get_therapeutic_area_competitive_data.py`
   - Input: therapeutic_area (e.g., "KRAS inhibitor")
   - Collects: Trials (CT.gov), Drugs (FDA), Patents (USPTO)
   - Output: Raw JSON with all relevant data

2. Data schema definition:
   ```python
   {
     "trials": [
       {
         "nct_id": "NCT12345678",
         "title": "...",
         "sponsor": "Amgen",
         "phase": "Phase 2",
         "status": "Recruiting",
         "conditions": ["Non-Small Cell Lung Cancer"],
         "interventions": ["Sotorasib (KRAS G12C inhibitor)"],
         "description": "..."
       }
     ],
     "drugs": [...],
     "patents": [...]
   }
   ```

3. Pagination and completeness validation
4. Skill verification using closed-loop pattern

**Deliverable**: Verified skill that collects all relevant data sources

### Phase 2: Entity Extraction (Week 2-3)

**Goal**: Extract MoA and disease areas from unstructured text

**Tasks**:
1. **Mechanism of Action Extraction**

   **Approach A: Pattern Matching (MVP)**
   ```python
   import re

   MOA_PATTERNS = [
       r'(\w+)\s+(inhibitor|antagonist|agonist|modulator|blocker)',
       r'anti-(\w+)\s+antibody',
       r'(\w+)\s+receptor\s+(inhibitor|agonist)',
       r'selective\s+(\w+)\s+inhibitor',
       r'(kinase|protease|phosphatase)\s+inhibitor'
   ]

   def extract_moa(text):
       """Extract mechanism of action from trial description."""
       mechanisms = []
       for pattern in MOA_PATTERNS:
           matches = re.findall(pattern, text, re.IGNORECASE)
           mechanisms.extend(matches)
       return mechanisms
   ```

   **Approach B: OpenTargets Validation (Recommended)**
   ```python
   from mcp.servers.opentargets_mcp import search_targets, get_target_disease_associations

   def validate_moa_disease_combination(moa_text, disease_text):
       """Validate MoA-disease combination using OpenTargets evidence."""
       # Extract target from MoA (e.g., "KRAS inhibitor" → "KRAS")
       target_gene = extract_target_from_moa(moa_text)

       # Search for target
       targets = search_targets(query=target_gene, size=1)
       if not targets.get('data'):
           return {'valid': False, 'confidence': 0.0}

       target_id = targets['data'][0]['id']

       # Get disease ID
       diseases = search_diseases(query=disease_text, size=1)
       if not diseases.get('data'):
           return {'valid': False, 'confidence': 0.0}

       disease_id = diseases['data'][0]['id']

       # Check target-disease association
       associations = get_target_disease_associations(
           targetId=target_id,
           diseaseId=disease_id,
           minScore=0.0
       )

       if associations.get('data'):
           assoc = associations['data'][0]
           overall_score = assoc.get('score', 0.0)
           genetic_score = assoc.get('datatypeScores', {}).get('genetic_association', 0.0)

           return {
               'valid': True,
               'confidence': overall_score,
               'genetic_evidence': genetic_score,
               'has_clinical_precedent': assoc.get('datatypeScores', {}).get('known_drug', 0.0) > 0
           }

       return {'valid': False, 'confidence': 0.0}
   ```

   **Approach C: ML-based NER (Future Enhancement)**
   - Train NER model on drug labels for improved MoA extraction
   - Use PubChem/ChEMBL APIs for chemical class classification

2. **Disease Area Normalization**

   ```python
   from mcp.servers.opentargets_mcp import search_diseases, get_disease_details

   def normalize_disease(condition_text):
       """Map disease text to standard ontology using OpenTargets."""
       # OpenTargets handles synonyms and returns EFO/MONDO IDs
       result = search_diseases(
           query=condition_text,
           size=1
       )

       if not result.get('data'):
           return {
               'original': condition_text,
               'normalized': condition_text,
               'disease_id': None,
               'category': 'Unknown'
           }

       disease = result['data'][0]
       disease_id = disease.get('id')  # MONDO_0005148 or EFO_0000305

       # Get additional details (optional - for categorization)
       details = get_disease_details(id=disease_id)
       therapeutic_areas = details.get('therapeuticAreas', [])

       return {
           'original': condition_text,
           'normalized': disease.get('name'),
           'disease_id': disease_id,
           'category': categorize_disease(disease.get('name'), therapeutic_areas),
           'synonyms': details.get('synonyms', [])
       }
   ```

3. **Company Attribution**

   ```python
   COMPANY_HIERARCHY = {
       # Track M&A to attribute trials to current owner
       'Amgen': 'Amgen',
       'Five Prime Therapeutics': 'Amgen',  # Acquired 2021
       'Celgene': 'Bristol Myers Squibb',   # Acquired 2019
       'Array BioPharma': 'Pfizer'          # Acquired 2019
   }

   def attribute_company(sponsor_name):
       """Map sponsor to parent company."""
       return COMPANY_HIERARCHY.get(sponsor_name, sponsor_name)
   ```

**Deliverable**: Entity extraction module with >80% accuracy on test set

### Phase 3: Portfolio Mapping Engine (Week 3-4)

**Goal**: Aggregate data into strategic portfolio view

**Tasks**:
1. **Data Model**

   ```python
   @dataclass
   class PortfolioMapping:
       """Company portfolio mapped by disease and MoA."""

       company: str
       disease_areas: Dict[str, DiseasePortfolio]

   @dataclass
   class DiseasePortfolio:
       """Portfolio within a disease area."""

       disease_name: str
       disease_category: str  # Oncology, Metabolic, etc.
       mechanisms: Dict[str, MechanismPortfolio]

   @dataclass
   class MechanismPortfolio:
       """Assets targeting a specific mechanism."""

       mechanism: str
       mechanism_class: str  # Kinase inhibitor, mAb, etc.
       assets: List[Asset]

   @dataclass
   class Asset:
       """Individual drug or trial."""

       name: str
       type: str  # "trial" or "approved_drug"
       phase: str
       status: str
       indication: str
       mechanism: str
       company: str
       nct_id: Optional[str]
       approval_date: Optional[str]
   ```

2. **Aggregation Logic**

   ```python
   def build_portfolio_map(raw_data):
       """Aggregate raw data into portfolio structure."""

       portfolio_map = defaultdict(lambda: PortfolioMapping)

       for trial in raw_data['trials']:
           company = attribute_company(trial['sponsor'])
           disease = normalize_disease(trial['conditions'][0])
           mechanism = extract_moa(trial['description'])[0]

           # Create asset
           asset = Asset(
               name=trial['interventions'][0],
               type='trial',
               phase=trial['phase'],
               status=trial['status'],
               indication=disease['normalized'],
               mechanism=mechanism,
               company=company,
               nct_id=trial['nct_id']
           )

           # Add to portfolio map
           portfolio_map[company].disease_areas[disease['normalized']]\
               .mechanisms[mechanism].assets.append(asset)

       return portfolio_map
   ```

3. **Competitive Intensity Scoring**

   ```python
   def calculate_intensity(mechanism_portfolio):
       """Score competitive intensity (0-100)."""

       num_companies = len(set(a.company for a in mechanism_portfolio.assets))
       num_phase3 = sum(1 for a in mechanism_portfolio.assets if a.phase == 'Phase 3')
       num_approved = sum(1 for a in mechanism_portfolio.assets if a.type == 'approved_drug')

       # Scoring formula
       intensity = (
           num_companies * 10 +      # More companies = higher intensity
           num_phase3 * 15 +          # Late-stage trials matter more
           num_approved * 30          # Approved drugs = highest intensity
       )

       return min(intensity, 100)  # Cap at 100
   ```

**Deliverable**: Portfolio mapping engine with intensity scoring

### Phase 4: Visualization & Analysis (Week 4-6)

**Goal**: Generate visual strategic maps and insights

**Tasks**:
1. **Matrix View: Companies × Mechanisms**

   ```python
   def generate_company_moa_matrix(portfolio_map, disease_area=None):
       """Create matrix showing company activity by MoA."""

       companies = sorted(portfolio_map.keys())
       mechanisms = set()

       # Collect all mechanisms
       for company_portfolio in portfolio_map.values():
           for disease_portfolio in company_portfolio.disease_areas.values():
               if disease_area and disease_portfolio.disease_name != disease_area:
                   continue
               mechanisms.update(disease_portfolio.mechanisms.keys())

       mechanisms = sorted(mechanisms)

       # Build matrix
       matrix = []
       for company in companies:
           row = {'company': company}
           for moa in mechanisms:
               count = count_assets(portfolio_map[company], moa, disease_area)
               row[moa] = count
           matrix.append(row)

       return pd.DataFrame(matrix)
   ```

   **Output Example**:
   ```
   Company          | KRAS Inhibitor | EGFR Inhibitor | PD-1 Antibody | ALK Inhibitor
   -----------------|----------------|----------------|---------------|---------------
   Amgen            | 3              | 0              | 1             | 0
   Pfizer           | 0              | 2              | 0             | 1
   Novartis         | 0              | 1              | 0             | 2
   Bristol Myers    | 0              | 0              | 5             | 0
   ```

2. **Heat Map: MoA × Disease Coverage**

   ```python
   def generate_moa_disease_heatmap(portfolio_map):
       """Show which MoA-Disease combinations have activity."""

       diseases = set()
       mechanisms = set()

       # Collect all combinations
       for company_portfolio in portfolio_map.values():
           for disease, disease_portfolio in company_portfolio.disease_areas.items():
               diseases.add(disease)
               mechanisms.update(disease_portfolio.mechanisms.keys())

       # Build heat map data
       heatmap_data = np.zeros((len(mechanisms), len(diseases)))

       for i, moa in enumerate(sorted(mechanisms)):
           for j, disease in enumerate(sorted(diseases)):
               count = count_assets_by_moa_disease(portfolio_map, moa, disease)
               heatmap_data[i][j] = count

       return heatmap_data, sorted(mechanisms), sorted(diseases)
   ```

3. **Network Graph: Company-MoA-Disease Relationships**

   ```python
   def generate_portfolio_network(portfolio_map):
       """Create network graph showing relationships."""

       import networkx as nx

       G = nx.Graph()

       # Add nodes
       for company, portfolio in portfolio_map.items():
           G.add_node(company, type='company')

           for disease, disease_portfolio in portfolio.disease_areas.items():
               G.add_node(disease, type='disease')

               for moa, moa_portfolio in disease_portfolio.mechanisms.items():
                   G.add_node(moa, type='mechanism')

                   # Add edges
                   G.add_edge(company, moa, weight=len(moa_portfolio.assets))
                   G.add_edge(moa, disease, weight=len(moa_portfolio.assets))

       return G
   ```

4. **Strategic Insights Generator**

   ```python
   def generate_strategic_insights(portfolio_map):
       """Identify strategic patterns and opportunities."""

       insights = {
           'portfolio_clusters': identify_similar_portfolios(portfolio_map),
           'white_spaces': identify_white_spaces(portfolio_map),
           'dominant_players': identify_dominant_players(portfolio_map),
           'emerging_threats': identify_emerging_competitors(portfolio_map),
           'differentiation_opportunities': identify_differentiation(portfolio_map)
       }

       return insights

   def identify_white_spaces(portfolio_map):
       """Find MoA-Disease combinations with low coverage."""

       white_spaces = []

       # Get all possible combinations
       all_moas = get_all_mechanisms(portfolio_map)
       all_diseases = get_all_diseases(portfolio_map)

       for moa in all_moas:
           for disease in all_diseases:
               count = count_assets_by_moa_disease(portfolio_map, moa, disease)

               if count == 0:
                   white_spaces.append({
                       'mechanism': moa,
                       'disease': disease,
                       'opportunity_score': calculate_opportunity_score(moa, disease)
                   })

       return sorted(white_spaces, key=lambda x: x['opportunity_score'], reverse=True)
   ```

**Deliverable**: Visualization module with 4+ view types + strategic insights

### Phase 5: Report Generation & Integration (Week 6-8)

**Goal**: Production-ready reporting system

**Tasks**:
1. **Markdown Report Template**

   ```markdown
   # {Therapeutic Area} Competitive Landscape - Disease & MoA Mapping

   **Date**: {date}
   **Scope**: {scope}
   **Data Sources**: ClinicalTrials.gov ({n} trials), FDA ({n} drugs), USPTO ({n} patents)

   ## Executive Summary

   - **Total Companies**: {n}
   - **Disease Areas**: {n}
   - **Mechanisms of Action**: {n}
   - **Total Assets**: {n} trials, {n} approved drugs
   - **Competitive Intensity**: {score}/100

   ## Portfolio Clustering

   ### Dominant Players
   1. **{Company A}**: {n} assets across {n} mechanisms
      - Primary MoAs: {moa1}, {moa2}, {moa3}
      - Disease focus: {disease1}, {disease2}
      - Strategy: {inferred_strategy}

   2. **{Company B}**: ...

   ### Emerging Competitors
   ...

   ## Mechanism of Action Landscape

   ### Most Crowded MoAs
   1. **{MoA}**: {n} companies, {n} assets
      - Companies: {list}
      - Differentiation strategies: {analysis}

   ### Underexploited MoAs
   ...

   ## Disease Area Analysis

   ### Multi-Indication Strategies
   - **{Drug Name}**: Being tested in {n} indications
     - {Indication 1}: {Phase}
     - {Indication 2}: {Phase}

   ## White Space Analysis

   ### Top Opportunities (MoA × Disease combinations with low coverage)

   1. **{MoA} in {Disease}**
      - Current coverage: {n} assets
      - Opportunity score: {score}/100
      - Rationale: {why this is attractive}

   ## Strategic Recommendations

   1. **Acquisition Targets**: Companies with assets in white space areas
   2. **Partnership Opportunities**: Complement gaps in our portfolio
   3. **Differentiation Strategies**: Novel MoA combinations or patient populations
   4. **Competitive Threats**: Monitor {companies} with overlapping programs

   ## Appendix: Data Tables

   ### Company × MoA Matrix
   {table}

   ### MoA × Disease Heat Map
   {visualization}

   ### Network Graph
   {graph}
   ```

2. **Skill Creation**

   Create final skill: `get_disease_moa_competitive_mapping.py`

   ```python
   def get_disease_moa_competitive_mapping(
       therapeutic_area: str,
       scope: str = 'all',  # 'all' or specific company
       min_phase: str = 'Phase 1',
       include_patents: bool = False,
       output_format: str = 'report'  # 'report', 'json', 'csv'
   ):
       """
       Generate disease-MoA competitive mapping for therapeutic area.

       Args:
           therapeutic_area: Disease/drug class (e.g., "KRAS inhibitor")
           scope: 'all' or company name for focused analysis
           min_phase: Minimum trial phase to include
           include_patents: Include patent landscape analysis
           output_format: 'report' (markdown), 'json', or 'csv'

       Returns:
           Comprehensive portfolio mapping with strategic insights
       """

       # Phase 1: Data collection
       raw_data = collect_data(therapeutic_area, include_patents)

       # Phase 2: Entity extraction
       extracted = extract_entities(raw_data)

       # Phase 3: Portfolio mapping
       portfolio_map = build_portfolio_map(extracted)

       # Phase 4: Visualization & analysis
       visualizations = generate_all_visualizations(portfolio_map)
       insights = generate_strategic_insights(portfolio_map)

       # Phase 5: Report generation
       if output_format == 'report':
           return generate_markdown_report(
               portfolio_map, visualizations, insights
           )
       elif output_format == 'json':
           return portfolio_map.to_dict()
       elif output_format == 'csv':
           return export_to_csv(portfolio_map)
   ```

3. **Integration with competitive-landscape-analyst**

   Update agent metadata:
   ```yaml
   data_requirements:
     always:
       - type: portfolio_mapping
         pattern: get_disease_moa_competitive_mapping
         description: Disease-MoA portfolio mapping across competitors
         sources: [ct_gov_mcp, fda_mcp, uspto_patents_mcp]
   ```

**Deliverable**: Production skill with comprehensive reporting

---

## Data Models & Schemas

### Normalized Data Schema

```python
# MoA Taxonomy (simplified - use ChEMBL in production)
MOA_CLASSES = {
    'small_molecule_kinase_inhibitor': [
        'KRAS inhibitor',
        'EGFR inhibitor',
        'ALK inhibitor',
        'BTK inhibitor'
    ],
    'monoclonal_antibody': [
        'PD-1 antibody',
        'PD-L1 antibody',
        'CTLA-4 antibody',
        'HER2 antibody'
    ],
    'gene_therapy': [
        'AAV vector',
        'Lentiviral vector',
        'CRISPR/Cas9'
    ],
    'cell_therapy': [
        'CAR-T',
        'TCR-T',
        'NK cell therapy'
    ]
}

# Disease Taxonomy (simplified - use OpenTargets therapeuticAreas in production)
DISEASE_CATEGORIES = {
    'oncology': [
        'Non-Small Cell Lung Cancer',
        'Colorectal Cancer',
        'Melanoma',
        'Multiple Myeloma'
    ],
    'metabolic': [
        'Type 2 Diabetes',
        'Obesity',
        'NASH'
    ],
    'immunology': [
        'Rheumatoid Arthritis',
        'Psoriasis',
        'Crohn\'s Disease'
    ],
    'neurology': [
        'Alzheimer\'s Disease',
        'Parkinson\'s Disease',
        'Multiple Sclerosis'
    ]
}
```

---

## Algorithms & Methods

### White Space Identification Algorithm

```python
def calculate_opportunity_score(moa, disease, portfolio_map, market_data):
    """
    Score white space opportunity (0-100).

    Factors:
    - Market size (larger = higher score)
    - Unmet need (higher = higher score)
    - Technical feasibility (higher = higher score) - POWERED BY OPENTARGETS
    - Current coverage (lower = higher score)
    """
    from mcp.servers.opentargets_mcp import get_target_disease_associations

    # Market size (from external data)
    market_size_score = normalize_market_size(market_data.get_size(disease))

    # Unmet need (from literature mentions, guideline gaps)
    unmet_need_score = calculate_unmet_need(disease)

    # Technical feasibility using OpenTargets evidence
    feasibility_score = get_opentargets_feasibility(moa, disease)

    # Current coverage (from portfolio map)
    num_assets = count_assets_by_moa_disease(portfolio_map, moa, disease)
    coverage_score = max(0, 100 - num_assets * 20)  # Fewer assets = higher score

    # Weighted combination
    opportunity_score = (
        market_size_score * 0.3 +
        unmet_need_score * 0.3 +
        feasibility_score * 0.2 +
        coverage_score * 0.2
    )

    return opportunity_score


def get_opentargets_feasibility(moa, disease):
    """
    Calculate technical feasibility using OpenTargets evidence (0-100 scale).

    Factors:
    - Overall association score (target-disease link strength)
    - Genetic evidence (strongest predictor of clinical success)
    - Known drug precedent (de-risking factor)
    - Druggability (tractability assessment)
    """
    from mcp.servers.opentargets_mcp import (
        search_targets, search_diseases,
        get_target_disease_associations, get_target_details
    )

    # Extract target from MoA (e.g., "KRAS inhibitor" → "KRAS")
    target_gene = extract_target_from_moa(moa)

    # Get target and disease IDs
    targets = search_targets(query=target_gene, size=1)
    diseases = search_diseases(query=disease, size=1)

    if not targets.get('data') or not diseases.get('data'):
        return 0  # No data = lowest feasibility

    target_id = targets['data'][0]['id']
    disease_id = diseases['data'][0]['id']

    # Get target-disease association
    associations = get_target_disease_associations(
        targetId=target_id,
        diseaseId=disease_id,
        minScore=0.0
    )

    if not associations.get('data'):
        return 20  # No association = low but not zero feasibility

    assoc = associations['data'][0]

    # Evidence components
    overall_score = assoc.get('score', 0.0)  # 0-1
    datatypes = assoc.get('datatypeScores', {})
    genetic_score = datatypes.get('genetic_association', 0.0)  # Most predictive
    known_drug_score = datatypes.get('known_drug', 0.0)  # Precedent

    # Get druggability assessment
    target_details = get_target_details(id=target_id)
    tractability = target_details.get('tractability', {})
    sm_tractable = tractability.get('smallmolecule', {})
    ab_tractable = tractability.get('antibody', {})

    # Druggability scoring
    sm_category = sm_tractable.get('top_category', '')
    ab_category = ab_tractable.get('top_category', '')

    if 'Clinical Precedence' in sm_category or 'Clinical Precedence' in ab_category:
        druggability_score = 1.0  # Approved drug exists
    elif 'High confidence' in sm_category or 'High confidence' in ab_category:
        druggability_score = 0.7  # Highly tractable
    elif 'Medium' in sm_category or 'Medium' in ab_category:
        druggability_score = 0.4  # Moderately tractable
    else:
        druggability_score = 0.2  # Low tractability

    # Weighted combination (0-100 scale)
    feasibility = (
        overall_score * 20 +       # Overall evidence (0-20 points)
        genetic_score * 40 +        # Genetic evidence (0-40 points) - most important
        known_drug_score * 20 +     # Known drug precedent (0-20 points)
        druggability_score * 20     # Druggability (0-20 points)
    )

    return feasibility
```

### Portfolio Similarity Clustering

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def identify_similar_portfolios(portfolio_map):
    """Cluster companies by portfolio similarity."""

    companies = list(portfolio_map.keys())

    # Create feature vectors (Company × MoA-Disease combinations)
    all_combinations = get_all_moa_disease_combinations(portfolio_map)

    feature_matrix = np.zeros((len(companies), len(all_combinations)))

    for i, company in enumerate(companies):
        for j, (moa, disease) in enumerate(all_combinations):
            count = count_assets(portfolio_map[company], moa, disease)
            feature_matrix[i][j] = count

    # Calculate similarity
    similarity_matrix = cosine_similarity(feature_matrix)

    # Find clusters (companies with >70% similarity)
    clusters = []
    for i, company_i in enumerate(companies):
        cluster = [company_i]
        for j, company_j in enumerate(companies):
            if i != j and similarity_matrix[i][j] > 0.7:
                cluster.append(company_j)

        if len(cluster) > 1:
            clusters.append(cluster)

    return clusters
```

---

## Example Outputs

### Example 1: KRAS Inhibitor Landscape

```markdown
# KRAS Inhibitor Competitive Landscape - Disease & MoA Mapping

**Date**: 2025-11-24
**Scope**: All companies
**Data Sources**: ClinicalTrials.gov (363 trials), FDA (2 drugs)

## Executive Summary

- **Total Companies**: 8
- **Disease Areas**: 12 (NSCLC, CRC, pancreatic cancer, etc.)
- **Mechanisms of Action**: 4 (G12C inhibitor, G12D inhibitor, pan-KRAS, SOS1 inhibitor)
- **Total Assets**: 23 trials, 2 approved drugs
- **Competitive Intensity**: 78/100 (HIGH)

## Portfolio Clustering

### Dominant Players

1. **Amgen**: 5 assets (3 approved/late-stage, 2 early-stage)
   - Primary MoA: KRAS G12C inhibitor (Sotorasib - approved)
   - Disease focus: NSCLC (primary), CRC (secondary)
   - Strategy: First-mover advantage in G12C, expanding indications

2. **Mirati Therapeutics**: 3 assets
   - Primary MoA: KRAS G12C inhibitor (Adagrasib - approved)
   - Disease focus: NSCLC, CRC
   - Strategy: Fast-follower, differentiation via CNS penetration

3. **Revolution Medicines**: 4 assets (all early-stage)
   - Primary MoAs: KRAS G12C, KRAS G12D, pan-KRAS, SOS1
   - Strategy: Multi-pronged approach across KRAS variants

## Mechanism of Action Landscape

### Most Crowded MoAs

1. **KRAS G12C Inhibitor**: 6 companies, 12 assets
   - Companies: Amgen, Mirati, Eli Lilly, Roche, Johnson & Johnson, Revolution Medicines
   - Competitive intensity: 95/100 (EXTREME)
   - Differentiation strategies:
     - CNS penetration (Mirati)
     - Combination therapies (Amgen + chemotherapy)
     - Novel patient populations (earlier lines)

### Underexploited MoAs

1. **KRAS G12D Inhibitor**: 2 companies, 3 assets
   - Companies: Revolution Medicines, Mirati
   - Competitive intensity: 35/100 (LOW-MODERATE)
   - Opportunity: G12D more prevalent in pancreatic cancer than G12C

## White Space Analysis

### Top Opportunities

1. **Pan-KRAS Inhibitor in Pancreatic Cancer**
   - Current coverage: 1 Phase 1 trial
   - Opportunity score: 87/100
   - Rationale: High unmet need (5-year survival <10%), limited targeted options

2. **KRAS G12D Inhibitor in Colorectal Cancer**
   - Current coverage: 1 Phase 1 trial
   - Opportunity score: 82/100
   - Rationale: G12D prevalent in CRC, only G12C inhibitors approved

## Strategic Recommendations

1. **Acquisition Targets**:
   - Revolution Medicines (broadest KRAS portfolio, early-stage valuations)
   - Companies with SOS1 inhibitors (upstream KRAS regulation)

2. **Partnership Opportunities**:
   - Combination trials with checkpoint inhibitors (synergistic with KRAS)
   - Biomarker development partnerships (identify responsive populations)

3. **Differentiation Strategies**:
   - Focus on G12D or pan-KRAS (less crowded than G12C)
   - Target pancreatic cancer (highest unmet need)
   - Develop oral formulations with CNS penetration

4. **Competitive Threats**:
   - Monitor Revolution Medicines Phase 2 data (multi-variant approach)
   - Watch for Amgen/Mirati expansion into earlier treatment lines
```

### Example 2: Company-Focused Analysis (Pfizer Oncology)

```markdown
# Pfizer Oncology Portfolio - Disease & MoA Mapping

## Portfolio Overview

**Total Assets**: 47 oncology programs
- 12 approved drugs
- 35 clinical trials (8 Phase 3, 12 Phase 2, 15 Phase 1)

## Disease Area Distribution

1. **Breast Cancer**: 12 assets (CDK4/6i, HER2-ADC, etc.)
2. **Non-Small Cell Lung Cancer**: 9 assets (ALK inhibitor, TKI)
3. **Hematologic Malignancies**: 8 assets (BTK inhibitor, JAK inhibitor)
4. **Prostate Cancer**: 6 assets (AR inhibitor, PARP inhibitor)
5. **Other solid tumors**: 12 assets

## Mechanism of Action Portfolio

### Small Molecule Kinase Inhibitors (18 assets)
- ALK inhibitor (Lorlatinib - approved)
- CDK4/6 inhibitor (Palbociclib - approved)
- BTK inhibitor (multiple programs)
- JAK inhibitor (ruxolitinib - approved)

### Antibody-Drug Conjugates (4 assets)
- HER2-ADC (collaboration with Seagen)
- TROP2-ADC (early development)

### Checkpoint Inhibitors (3 assets)
- PD-L1 antibody (Avelumab - approved, co-developed with Merck KGaA)

## Strategic Positioning

**Strengths**:
- Dominant in CDK4/6 inhibitors (Ibrance = blockbuster)
- Strong ALK inhibitor franchise (Lorlatinib best-in-class)
- Diverse modality portfolio (kinases + ADCs + immunotherapy)

**Gaps**:
- Limited KRAS inhibitor presence (competitive disadvantage vs Amgen/Mirati)
- Weak in CAR-T (competitors: Novartis, Gilead, BMS)
- Underweighted in PD-1/PD-L1 (vs BMS, Merck, Roche)

**White Space Opportunities**:
- KRAS G12D inhibitor (could acquire Revolution Medicines)
- BiTE platform (vs Amgen's Blincyto success)
- EGFR-MET bispecific (vs Roche's Amivantamab)
```

---

## Success Metrics

### Technical Metrics

- **Data Coverage**: >90% of relevant trials/drugs captured
- **Entity Extraction Accuracy**: >80% for MoA, >90% for disease
- **Processing Speed**: Full landscape analysis in <5 minutes
- **Freshness**: Data updated daily (FDA) and weekly (trials)

### Business Metrics

- **Adoption**: BD team uses for >50% of competitive assessments
- **Decision Impact**: Informs >20% of M&A/partnership decisions
- **Time Savings**: 80% reduction vs manual analysis (40 hours → 8 hours)
- **Insight Quality**: >70% of white space recommendations validated by experts

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **MoA extraction errors** | High - wrong strategic conclusions | Manual validation sample (10%), expert review of novel MoAs |
| **Company attribution errors** (M&A) | Medium - misattribute assets | Maintain M&A database, quarterly updates |
| **Disease normalization failures** | Medium - miss portfolio clusters | Use multiple ontologies (EFO + ICD-10), fuzzy matching |
| **Data staleness** | Medium - miss recent developments | Daily FDA updates, weekly trial registry scraping |
| **Incomplete data** (pre-clinical programs) | Low - miss early threats | Supplement with patent analysis, conference monitoring |

---

## Dependencies & Prerequisites

### Technical Dependencies

- **MCP Servers**: ct_gov_mcp, fda_mcp, pubmed_mcp, uspto_patents_mcp, opentargets_mcp
- **Python Libraries**: pandas, numpy, networkx, scikit-learn, regex
- **Ontologies**: EFO (disease), ChEMBL (mechanism), MeSH (literature)
- **Data Sources**: M&A database, market size estimates

### Knowledge Dependencies

- Disease area taxonomies
- Mechanism of action classifications
- Company organizational structures
- Therapeutic area treatment paradigms

---

## Future Enhancements

### Phase 2 (Months 3-6)

1. **Real-time Monitoring Dashboard**
   - Web interface with live updates
   - Alerts for new competitive developments
   - Interactive visualizations (D3.js, Plotly)

2. **ML-based MoA Extraction**
   - Train NER model on drug labels
   - Fine-tune on PubMed abstracts
   - >95% extraction accuracy

3. **Predictive Analytics**
   - Clinical success probability by MoA-Disease
   - Time-to-market prediction
   - Competitive threat scoring

### Phase 3 (Months 6-12)

1. **Multi-Modal Integration**
   - Financial data (R&D spending by program)
   - Conference presentations (ASH, ASCO, etc.)
   - Social media monitoring (clinical trial results)

2. **Automated Strategic Recommendations**
   - AI-generated acquisition target lists
   - Partnership matching (complement portfolio gaps)
   - Differentiation strategy suggestions

3. **Global Expansion**
   - China trial registries (ChiCTR)
   - European registries (EU-CTR)
   - Japanese registries (JAPIC)

---

## Why OpenTargets Over Direct Ontologies?

### OpenTargets Advantages

**1. Disease Normalization (Replaces EFO/MONDO Direct Access)**

Traditional approach (direct EFO):
```python
# Manual ontology lookup - requires downloading and parsing EFO OWL files
# Complex SPARQL queries or OWL parsing
# No synonym handling without additional work
```

OpenTargets approach:
```python
# Simple API call with built-in synonym matching
diseases = search_diseases(query="type 2 diabetes", size=1)
disease_id = diseases['data'][0]['id']  # MONDO_0005148
synonyms = diseases['data'][0].get('synonyms', [])  # ['T2DM', 'NIDDM', ...]
```

**Benefits**:
- ✅ Built-in synonym matching ("T2DM" → "Type 2 Diabetes Mellitus")
- ✅ Returns both MONDO and EFO IDs
- ✅ Includes disease descriptions and therapeutic area classification
- ✅ No need to download/maintain ontology files
- ✅ Simple JSON API (no OWL/SPARQL complexity)

**2. Mechanism of Action Validation (Supplements ChEMBL)**

Traditional approach:
```python
# Pattern matching only - no validation of MoA-disease relevance
# ChEMBL provides mechanism classes but not target-disease associations
```

OpenTargets approach:
```python
# Validate MoA-disease combination with genetic evidence
associations = get_target_disease_associations(
    targetId="ENSG00000012048",  # KRAS
    diseaseId="MONDO_0005061"     # NSCLC
)
genetic_score = associations['data'][0]['datatypeScores']['genetic_association']

# Know if this is a REAL opportunity (0.8 genetic score) or fishing expedition (0.1 score)
```

**Benefits**:
- ✅ Genetic evidence scores (strongest predictor of clinical success per Nelson et al. 2015)
- ✅ Known drug precedent detection (de-risking factor)
- ✅ Druggability assessment (tractability scores)
- ✅ Validates biological plausibility of MoA-disease combinations

**3. White Space Opportunity Scoring (Evidence-Based)**

Traditional approach:
```python
# Feasibility = guess based on literature or expert opinion
# No quantitative scoring
```

OpenTargets approach:
```python
# Quantitative feasibility scoring based on:
feasibility = (
    overall_association_score * 20 +  # Target-disease link strength
    genetic_evidence_score * 40 +      # GWAS/genetic validation (most predictive)
    known_drug_score * 20 +            # Approved drug precedent
    druggability_score * 20            # Tractability (small molecule/antibody)
)

# Example: KRAS G12C in NSCLC
# - Genetic: 0.85 → 34 points (strong genetic evidence)
# - Known drug: 0.90 → 18 points (Sotorasib/Adagrasib approved)
# - Druggability: 1.0 → 20 points (Clinical precedence)
# - Overall: 0.72 → 14 points
# TOTAL: 86/100 → HIGH feasibility white space
```

**Benefits**:
- ✅ Evidence-based scoring (not opinion-based)
- ✅ Genetic evidence prioritization (2x higher likelihood of approval per King 2019)
- ✅ De-risking via known drug precedent
- ✅ Quantitative comparison across opportunities

**4. No Need for MeSH**

MeSH (Medical Subject Headings) is primarily for PubMed indexing. For portfolio mapping:
- **Not needed**: Disease normalization handled by OpenTargets (EFO/MONDO)
- **Not needed**: MoA extraction from trial text doesn't require MeSH
- **Optional**: Could use for PubMed literature analysis, but not core to portfolio mapping

### Technical Comparison

| Feature | Direct EFO/ChEMBL | OpenTargets API |
|---------|-------------------|-----------------|
| **Disease normalization** | Requires OWL parsing | Simple JSON API |
| **Synonym matching** | Manual implementation | Built-in |
| **Target-disease validation** | Not available | Genetic evidence scores |
| **Druggability** | Not in EFO/ChEMBL | Tractability scores |
| **Clinical precedent** | Manual lookup | Known drug evidence type |
| **Integration complexity** | High (ontology files, parsers) | Low (REST API) |
| **Maintenance** | Must track ontology versions | API handles versioning |
| **Evidence quality** | N/A | Scored 0-1 with breakdowns |

### Data Quality Benefits

**Example: "Type 2 Diabetes" Normalization**

Direct EFO approach:
```python
# Multiple possible matches:
# - EFO:0000305 (obsolete?)
# - EFO:0001360 (current?)
# - MONDO:0005148 (new standard?)
# Manual disambiguation required
```

OpenTargets approach:
```python
diseases = search_diseases(query="type 2 diabetes", size=1)
# Returns:
{
  'id': 'MONDO_0005148',  # Current standard
  'name': 'type 2 diabetes mellitus',
  'synonyms': ['T2DM', 'NIDDM', 'diabetes type 2', ...],
  'therapeuticAreas': ['EFO_0000701']  # Metabolic disease
}
# Automatically handles obsolete terms and current standards
```

### Implementation Simplification

**Lines of code comparison**:

Direct EFO/ChEMBL:
- Disease normalization: ~200 lines (OWL parsing, synonym matching, disambiguation)
- MoA validation: ~100 lines (pattern matching, no validation possible)
- Total: ~300 lines + external ontology files

OpenTargets:
- Disease normalization: ~20 lines (API call + error handling)
- MoA validation: ~50 lines (API calls with evidence scoring)
- Total: ~70 lines, no external files

**Maintenance burden**:
- Direct: Update ontology files quarterly, track version compatibility
- OpenTargets: API versioning handled server-side, backward compatible

### Conclusion: OpenTargets as Primary Ontology Layer

**Use OpenTargets for:**
- ✅ Disease normalization (replaces EFO/MONDO direct access)
- ✅ MoA-disease validation (supplements pattern matching)
- ✅ Opportunity scoring (genetic evidence, druggability)
- ✅ White space risk assessment

**Optional supplements:**
- ChEMBL: For comprehensive chemical mechanism classification (if needed beyond target-based MoA)
- PubChem: For compound property analysis
- MeSH: Skip for portfolio mapping (not needed)

**Net result**: 75% less code, higher quality scoring, evidence-based validation, and simplified maintenance.

---

## Conclusion

This implementation plan delivers a comprehensive **Disease-MoA Competitive Mapping** system that transforms fragmented pharmaceutical data into actionable strategic intelligence.

**Key Innovations**:
- ✅ **Automated entity extraction** (MoA, diseases from unstructured text)
- ✅ **OpenTargets-powered normalization** (EFO/MONDO disease IDs, target validation, genetic evidence)
- ✅ **Evidence-based feasibility scoring** (genetic evidence, druggability, clinical precedent)
- ✅ **Multi-dimensional visualization** (matrices, networks, heat maps)
- ✅ **Strategic insights generation** (white space, clustering, threats)
- ✅ **Integration with existing platform** (skills library, MCP servers, agents)

**Expected Impact**:
- 80% faster competitive landscape analysis
- Higher-quality M&A/partnership decisions
- Proactive identification of competitive threats
- Data-driven portfolio strategy optimization

**Timeline**: 3-4 weeks MVP, 2-3 months production system

**Next Steps**:
1. Validate approach with BD team stakeholders
2. Create Phase 1 skill (data collection)
3. Test entity extraction accuracy on sample data
4. Iterate on visualization preferences
5. Deploy MVP and gather feedback
