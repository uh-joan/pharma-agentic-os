# Pharmaceutical Research Intelligence Platform

AI-powered pharmaceutical research system using Claude Code with specialized MCP servers for drug discovery, clinical trials, regulatory data, and competitive intelligence.

## Architecture

Multi-agent system: data gathering + analytical modeling

**Agents:**

*Data Gathering:*
- `pharma-search-specialist`: Query → JSON plan → MCP tools → `data_dump/`

*Epidemiological Analysis:*
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels
- `market-sizing-analyst`: Reads `data_dump/` → TAM/SAM/SOM market sizing synthesis

*Forecasting Pipeline:*
- `patient-flow-modeler`: Reads `data_dump/` → eligibility funnels, treatment sequencing, multi-year patient flows
- `uptake-dynamics-analyst`: Reads `temp/` + `data_dump/` → market share evolution, treated patient projections
- `pricing-strategy-analyst`: Reads `data_dump/` → IRP modeling, tiered pricing, launch sequencing
- `revenue-synthesizer`: Reads `temp/` → revenue forecasts, peak sales, NPV-ready streams

*Competitive Intelligence:*
- `competitive-analyst`: Reads `data_dump/` → competitive landscape mapping, pipeline threats
- `opportunity-identifier`: Reads `temp/` → BD opportunities (partnerships, acquisitions, white space)
- `strategy-synthesizer`: Reads `temp/` → strategic planning, action prioritization, scenario analysis

*Asset Valuation:*
- `pharma-valuation-comparable-analyst`: Reads `data_dump/` → deal benchmarking, licensing precedents, M&A valuation ranges
- `pharma-valuation-npv-modeler`: Reads `data_dump/` → risk-adjusted NPV, DCF analysis, sensitivity scenarios
- `pharma-valuation-structure-optimizer`: Reads `temp/` → upfront/milestone/royalty optimization, risk-sharing frameworks

**Workflow:** Query → pharma-search-specialist (gathers data) → epidemiology-analyst (analyzes) → results

## MCP Servers

The platform integrates 12 specialized MCP servers (see `.mcp.json`):

### Core Pharmaceutical Data
- **ct-gov-mcp**: ClinicalTrials.gov trial data
  - Tool: `mcp__ct-gov-mcp__ct_gov_studies`
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
  - Tool: `mcp__fda-mcp__fda_info`
- **pubmed-mcp**: PubMed biomedical literature
  - Tool: `mcp__pubmed-mcp__pubmed_articles`

### Medical Coding & Standards
- **nlm-codes-mcp**: NLM Clinical Tables (ICD-10, ICD-11, HCPCS, NPI, HPO)
  - Tool: `mcp__nlm-codes-mcp__nlm_ct_codes`
- **who-mcp-server**: WHO Global Health Observatory data
  - Tool: `mcp__who-mcp-server__who-health`

### Chemistry & Biology
- **pubchem-mcp-server**: Compound properties, ADME data
  - Tool: `mcp__pubchem-mcp-server__pubchem`
- **opentargets-mcp-server**: Target validation, gene-drug-disease associations
  - Tool: `mcp__opentargets-mcp-server__opentargets_info`

### Financial & Legal
- **sec-mcp-server**: SEC EDGAR financial filings
  - Tool: `mcp__sec-mcp-server__sec-edgar`
- **patents-mcp-server**: USPTO patent search
  - Tool: `mcp__patents-mcp-server__uspto_patents`
- **financials-mcp-server**: Yahoo Finance stock data + FRED economic indicators
  - Tool: `mcp__financials-mcp-server__financial-intelligence`

### Healthcare Systems
- **healthcare-mcp**: CMS Medicare provider data
  - Tool: `mcp__healthcare-mcp__cms_search_providers`
- **datacommons-mcp**: Population statistics, disease demographics
  - Tools: `mcp__datacommons-mcp__search_indicators`, `mcp__datacommons-mcp__get_observations`

## Quick Start

### 1. Query the System

```bash
# Example queries:
"FDA-approved GLP-1 drugs"
"Clinical trials for Alzheimer's disease in Phase 3"
"Adverse events for atorvastatin"
"Competitive landscape for JAK inhibitors"
```

### 2. System Flow

1. **Classify query** (simple, complex, or exploratory)
2. **Invoke specialist agent** using appropriate template
3. **Receive execution plan** (JSON format)
4. **Execute MCP tool calls** sequentially
5. **Save results** to `data_dump/{YYYY-MM-DD}_{HHMMSS}_{tool}_{term}/`

### 3. Results Structure

Each query creates a timestamped directory in `data_dump/`:

```
data_dump/2025-11-10_183054_fda_baricitinib/
├── query.json         # Original query parameters
├── results.json       # Raw MCP response
├── summary.md         # Human-readable summary
└── metadata.json      # Execution metadata
```

## Query Complexity Classification

### Simple Queries (single database, <5 steps)
- FDA approval status for specific drug
- Clinical trial count for condition
- PubMed articles on topic
- Patent search for compound
- Single entity lookup

### Complex Queries (multi-database, >5 steps)
- Competitive landscape analysis
- Market assessment
- KOL identification
- Safety signal detection
- Pipeline analysis

### Exploratory Queries
- Novel questions without clear workflow
- Ambiguous entities or scope
- "What if" scenarios
- Open-ended research

## Documentation

### Core Documentation
- **`.claude/CLAUDE.md`**: Architecture overview and execution protocols
- **`.claude/agents/pharma-search-specialist.md`**: Agent specification and examples
- **`.mcp.json`**: MCP server configuration

### Tool Guides (`.claude/.context/mcp-tool-guides/`)
- **fda.md**: FDA database queries (drugs, adverse events, recalls)
- **clinicaltrials.md**: ClinicalTrials.gov search patterns
- **pubmed.md**: PubMed literature searches
- **sec-edgar.md**: SEC financial filings
- **datacommons.md**: Population and disease statistics
- **opentargets.md**: Target validation queries
- **pubchem.md**: Chemical compound searches
- **uspto-patents.md**: Patent search strategies

### Strategy Protocols (`.claude/.context/`)
- **performance-optimization.md**: Token efficiency, count-first strategies
- **search-strategy-protocols.md**: 4-phase execution, cognitive directives
- **search-workflows.md**: Proven workflow templates
- **cross-database-integration.md**: Entity linking across sources
- **quality-control.md**: Validation criteria, confidence levels

## Key Features

### Token Optimization
- **Count-first strategy**: Reduces FDA queries from 67K → 400 tokens (99.4% savings)
- **Field selection**: 70-90% token reduction on detail queries
- **Conservative limits**: Max 50-100 records per query
- **Pagination support**: For large datasets

### Data Quality
- **Audit trail**: All queries and results saved
- **Metadata tracking**: Timestamps, parameters, token usage
- **Validation steps**: Quality checks on multi-step workflows
- **Source transparency**: Original MCP responses preserved

### Intelligence Capabilities
- **Multi-database synthesis**: Link entities across FDA, ClinicalTrials.gov, PubMed
- **Competitive analysis**: Pipeline comparison, market positioning
- **Safety monitoring**: Adverse event detection and trending
- **Target validation**: Gene-drug-disease associations

## Example Workflows

### Drug Safety Analysis
1. FDA general search (count-first) → identify products
2. FDA adverse events (aggregated) → safety signals
3. PubMed literature → clinical evidence
4. ClinicalTrials.gov → ongoing trials

### Competitive Landscape
1. ClinicalTrials.gov → pipeline programs by sponsor
2. FDA approvals → marketed products
3. SEC EDGAR → R&D spend, financial health
4. Patents → IP protection timeline

### Target Validation
1. OpenTargets → gene-disease associations
2. PubMed → mechanism literature
3. ClinicalTrials.gov → clinical validation
4. PubChem → tool compounds

### Epidemiological Analysis (using epidemiology-analyst + patient-flow-modeler)
1. Data Commons + WHO + CMS → prevalence data gathering
2. PubMed → severity distribution studies
3. ClinicalTrials.gov → eligibility criteria patterns
4. FDA + CMS → contraindication prevalence
5. Epidemiology-analyst → prevalence model with demographics
6. Patient-flow-modeler → eligibility funnel + multi-year patient flows
7. Output: Treatment-eligible population with 5-10 year projections and sensitivity analysis

### Competitive Landscape Analysis (using competitive intelligence agents)
1. FDA + ClinicalTrials.gov + SEC + PubMed + OpenTargets → competitive data gathering
2. competitive-analyst → competitive landscape with pipeline threats
3. opportunity-identifier → BD opportunities (partnerships, acquisitions, white space)
4. strategy-synthesizer → strategic plan with positioning and action roadmap
5. Output: Actionable strategic recommendations with scenario planning and decision triggers

## Agents

### Data Gathering

#### pharma-search-specialist
Data gathering coordinator. Input: query → Output: JSON execution plan with MCP tool calls

### Epidemiological Analysis

#### epidemiology-analyst
Prevalence modeling and market sizing. Input: `data_dump/` → Output: Models, segmentation, eligibility funnels

**Capabilities**: Age-standardization, severity segmentation, biomarker stratification, eligibility funnels, sensitivity analysis, CMS real-world evidence integration

#### market-sizing-analyst
TAM/SAM/SOM market sizing synthesis. Input: `data_dump/` → Output: Complete market sizing analysis with executive summary, funnel breakdowns, competitive landscape, timeline projections

**Capabilities**: TAM (total prevalence from Data Commons/WHO/PubMed), SAM (eligibility funnels from CMS/FDA/CT.gov), SOM (competitive analysis from SEC/financials), cross-validation, sensitivity analysis, revenue projections. Covers all 12 MCP servers with no data gaps.

### Forecasting Pipeline

Sequential agents for pharmaceutical forecasting (patient flows → uptake → pricing → revenue):

#### patient-flow-modeler
Treatment-eligible population projections and sequencing. Input: `data_dump/` → Output: Eligibility funnels, multi-year patient flows, sensitivity analysis

**Capabilities**: Eligibility funnel construction (diagnosed → severity-eligible → label-eligible → drug-eligible), treatment line distribution (1L/2L/3L), annual progression modeling, multi-year patient flow projections (5-10 years), scenario analysis (conservative/base/optimistic), tornado sensitivity analysis, treatment sequencing pathways

#### uptake-dynamics-analyst
Market share evolution and adoption dynamics. Input: `temp/patient_flow_*.md` + `data_dump/` → Output: Year-by-year market share evolution, treated patient projections, sensitivity analysis

**Capabilities**: Bass diffusion modeling, S-curve adoption, competitive displacement attribution, launch sequencing impact, treated patient counts (eligible pool × market share), 5-year projections with low/base/high scenarios

#### pricing-strategy-analyst
Global pricing optimization and launch sequencing. Input: `data_dump/` → Output: IRP modeling, tiered pricing strategy, launch sequencing timeline, revenue impact comparison

**Capabilities**: IRP spillover risk modeling, 4-tier pricing framework (premium/competitive/value/access), phased launch sequencing (IRP-free first, IRP-sensitive delayed), cumulative 5-year revenue optimization, sensitivity analysis (±20% price variation)

#### revenue-synthesizer
Pharmaceutical revenue forecasting synthesis. Input: `temp/patient_flow_*.md` + `temp/uptake_dynamics_*.md` + optional `temp/pricing_strategy_*.md` → Output: Multi-year revenue forecast, peak sales, NPV-ready streams

**Capabilities**: Revenue formula (Treated Patients × Annual Cost × Compliance × Net Price %), 5-10 year projections, low/base/high scenarios, tornado sensitivity analysis, risk-adjusted peak sales, geographic breakdown (US/EU5/Japan/RoW), cumulative revenue metrics

### Competitive Intelligence

#### competitive-analyst
Competitive landscape mapping and pipeline threat assessment. Input: `data_dump/` → Output: Competitive analysis with market structure, pipeline threats, differentiation matrix, genetic biomarker intelligence

**Capabilities**: Current market structure (leaders, moats, vulnerabilities), pipeline dynamics (Phase 2/3 segmentation, threat scoring 🔴🟡🟢), differentiation matrix (MOA, efficacy, safety, dosing), genetic biomarker competitive positioning, gaps analysis (white space, crowded segments)

#### opportunity-identifier
BD opportunity screening for partnerships, acquisitions, and white space. Input: `temp/competitive_analysis_*.md` → Output: Prioritized BD opportunities with deal economics and timing triggers

**Capabilities**: Partnership screening (<$1B biotech, Phase 1/2, weak commercialization), acquisition screening (<$500M, Phase 2+, undervaluation signals), white space identification (patient populations, geographic gaps, indication expansion), priority tiering (🔴 0-6mo, 🟡 6-12mo, 🟢 12-24mo), deal economics framework

#### strategy-synthesizer
Strategic planning synthesis from competitive intelligence and BD opportunities. Input: `temp/competitive_analysis_*.md` + `temp/bd_opportunities_*.md` → Output: Strategic plan with positioning, action roadmap, scenario planning

**Capabilities**: Strategic positioning frameworks (offensive/defensive/flanking/guerrilla), action prioritization (immediate/near/medium-term horizons), scenario planning (best/base/worst case), decision triggers (go/no-go criteria), risk mitigation strategies (competitive/regulatory/commercial/execution), success metrics and KPIs

### Asset Valuation

Sequential agents for pharmaceutical asset valuation (comparables → NPV → deal structure):

#### pharma-valuation-comparable-analyst
Deal benchmarking and licensing precedent analysis. Input: `data_dump/` → Output: Comparable deal analysis with valuation ranges

**Capabilities**: Three-dimensional matching (indication × stage × structure), stage-appropriate valuation multiples (Phase 1-3, approved), upfront/peak sales benchmarks, total deal/peak sales ratios, milestone structure patterns, royalty rate analysis, 25th/50th/75th percentile ranges

#### pharma-valuation-npv-modeler
Risk-adjusted NPV modeling and DCF analysis. Input: `data_dump/` → Output: NPV analysis with sensitivity scenarios

**Capabilities**: Probability of success (PoS) frameworks by therapeutic area, program-specific adjustments (FDA Breakthrough, orphan drug, novel mechanism), probability-weighted revenue forecasts with patent exclusivity, risk-adjusted development costs, operating cash flow modeling (COGS, SG&A, R&D, tax), phase-appropriate discount rates (10-15%), tornado sensitivity analysis, bull/base/bear scenarios

#### pharma-valuation-structure-optimizer
Deal structure optimization for licensing transactions. Input: `temp/npv_analysis_*.md` + `temp/deal_comparables_*.md` → Output: Upfront/milestone/royalty allocation recommendations

**Capabilities**: NPV-equivalent structure design (seller-favorable/balanced/buyer-favorable), discount rate sensitivity (buyer vs seller WACC), risk allocation analysis (development/regulatory/commercial/timing), milestone allocation (40-50% development, 50-60% commercial), tiered royalty structures (8-20% by sales tier), comparables benchmarking, win-win value creation, dependency validation

## Design Principles

1. **Multi-agent**: Data gathering (pharma-search-specialist) + analytical (epidemiology-analyst, patient-flow-modeler, uptake-dynamics-analyst, pricing-strategy-analyst, revenue-synthesizer, market-sizing-analyst, competitive-analyst, opportunity-identifier, strategy-synthesizer, pharma-valuation-comparable-analyst, pharma-valuation-npv-modeler, pharma-valuation-structure-optimizer)
2. **Separation**: No MCP execution by analytical agents
3. **Token optimization**: Conservative limits, pagination, count-first
4. **Audit trail**: All results → data_dump/, analytical outputs → temp/
5. **Modular**: Easy to add MCP servers and agents

## Contributing

**New MCP Servers:**
1. Add to `.mcp.json`
2. Create tool guide in `.claude/.context/mcp-tool-guides/`
3. Update `.claude/CLAUDE.md`, `README.md`, `.claude/settings.local.json`

**New Agents:**
1. Create in `.claude/agents/` (follow `epidemiology-analyst.md` structure)
2. Use frontmatter, enumerated capability domains, response methodology, example output
3. Update `.claude/CLAUDE.md` and `README.md`
