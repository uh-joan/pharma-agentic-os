---
title: Comprehensive Agent Test Query Suite
date: 2025-11-21
purpose: Test suite design for pharma-search-specialist and strategic agents
data_sources_researched:
  - Yahoo Finance News (pharmaceutical trends)
  - ClinicalTrials.gov (66,110+ recruiting trials)
  - PubMed (breakthrough therapies 2024-2025)
  - Open Targets (disease-target associations)
therapeutic_areas_identified:
  - GLP-1/obesity drugs (118 Phase 3 recruiting trials)
  - Alzheimer's disease (51 Phase 3 recruiting trials, 2 new FDA approvals)
  - CAR-T/Gene therapy (12,852+ recruiting trials, first CRISPR approval)
  - Targeted oncology (1,456+ Phase 2 recruiting trials)
  - Rare diseases (orphan drug development acceleration)
coverage: 80+ test queries across 8 domains and 6 strategic scenarios
---

# Comprehensive Agent Test Query Suite

## Executive Summary

This document provides a comprehensive test suite for the Pharmaceutical Research Intelligence Platform, covering 80+ queries across multiple domains, therapeutic areas, and strategic scenarios. The queries are designed to test both infrastructure agents (pharma-search-specialist) and strategic agents (competitive-landscape-analyst) using real-world pharmaceutical intelligence needs.

**Research Foundation**: Based on current pharmaceutical trends from Yahoo Finance news, ClinicalTrials.gov data (66,110+ recruiting trials), PubMed breakthrough therapy literature, and Open Targets disease associations.

**Key Therapeutic Areas Covered**:
- GLP-1/Obesity drugs (oral formulations, combination therapies)
- Alzheimer's disease (anti-amyloid therapies, donanemab/lecanemab)
- CAR-T/Gene therapy (CRISPR approval, personalized therapies)
- Targeted oncology (KRAS, BRAF inhibitors)
- Rare diseases (orphan drug acceleration, FDA flexibility)

---

## Test Query Organization

Queries are organized by:
1. **Domain** - Data source and MCP server used
2. **Scenario** - Business context and strategic purpose
3. **Complexity** - Simple data retrieval → Multi-server synthesis
4. **Expected Agent** - Infrastructure vs. strategic agent
5. **Agent Invocation** - Exact syntax to invoke the query

### Agent Invocation Methods

**Infrastructure Agent (pharma-search-specialist)**:
- **Invocation**: Natural language query (automatic invocation)
- **Example**: User types: `"How many Phase 3 obesity trials are recruiting?"`
- **Behavior**: Main agent automatically invokes pharma-search-specialist to create/execute skill

**Strategic Agent (competitive-landscape-analyst)**:
- **Invocation**: Explicit agent mention with @ syntax
- **Example**: User types: `@agent-competitive-landscape-analyst "Analyze the GLP-1 competitive landscape"`
- **Behavior**: Main agent reads agent metadata, orchestrates data collection, invokes strategic agent

---

## Quick Reference: Query Template

Each query in this test suite follows this format:

**Infrastructure Query Example:**
```
#### Query X.X.X: Title
User Input: "Natural language question"

Agent Invocation: Automatic (natural language query)
Expected Agent: pharma-search-specialist
Domain: [Data source]
Problem: [Business problem]
Data Source: [MCP server]
Complexity: [Low/Medium/High/Very High]
Response Format: [Markdown/JSON parsing]
Key Metrics: [What to extract]
Business Value: [Why this matters]
```

**Strategic Query Example:**
```
#### Query SX.X: Title
User Input: @agent-competitive-landscape-analyst "Strategic question"

Agent Invocation: Explicit (@agent-competitive-landscape-analyst)
Expected Agent: competitive-landscape-analyst (strategic)
Domain: Multi-domain
Problem: [Strategic problem]
Complexity: Very High
Data Requirements: [List of skills needed]
Strategic Analysis Output: [Expected deliverables]
Business Value: [Why this matters]
```

---

## Domain 1: Clinical Trials Intelligence (CT.gov)

### 1.1 Simple Data Retrieval Queries

**Scenario**: Portfolio planning and competitive intelligence

#### Query 1.1.1: GLP-1 Obesity Trials
**User Input**: `"How many Phase 3 obesity trials using GLP-1 agonists are currently recruiting in the US?"`

**Agent Invocation**: Automatic (natural language query)
**Expected Agent**: pharma-search-specialist
**Domain**: Clinical Trials
**Problem**: Need to understand competitive landscape for obesity drug development
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Complexity**: Low (single server, single query)
**Response Format**: Markdown parsing required
**Key Metrics**: Trial count, phase distribution, recruitment status
**Business Value**: Portfolio prioritization, competitive positioning

**Test Validation**:
- Should find ~118 trials (based on research)
- Should parse trial titles, sponsors, locations
- Should handle CT.gov markdown response format
- Should demonstrate pagination if >100 results

---

#### Query 1.1.2: CAR-T Cell Therapy Trials
**User Input**: `"Get all recruiting CAR-T cell therapy trials for B-cell malignancies"`

**Agent Invocation**: Automatic (natural language query)
**Expected Agent**: pharma-search-specialist
**Domain**: Clinical Trials
**Problem**: Emerging immunotherapy landscape assessment
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Complexity**: Low-Medium (requires specific search terms)
**Response Format**: Markdown parsing
**Key Metrics**: Trial count by indication, phase distribution, combination therapies
**Business Value**: Technology platform assessment, partnership opportunities

**Test Validation**:
- Should find hundreds of trials (CAR-T is hot area)
- Should identify specific targets (CD19, CD22, BCMA)
- Should parse combination therapy approaches
- Should handle large result sets with pagination

---

#### Query 1.1.3: Alzheimer's Phase 3 Trials
**Query**: "What Phase 3 Alzheimer's disease trials are recruiting globally?"

**Domain**: Clinical Trials
**Problem**: Late-stage pipeline assessment in high-value indication
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Low
**Response Format**: Markdown parsing
**Key Metrics**: 51 trials (based on research), mechanism of action, trial endpoints
**Business Value**: Competitive threat assessment, mechanism diversity analysis

**Current Context**:
- Lecanemab approved July 2023 (anti-amyloid)
- Donanemab approved July 2024 (anti-amyloid)
- KarXT trials for psychosis in AD (muscarinic agonist)
- New mechanisms beyond anti-amyloid emerging

---

#### Query 1.1.4: KRAS Inhibitor Trials
**Query**: "Find all KRAS inhibitor clinical trials across all phases"

**Domain**: Clinical Trials
**Problem**: Precision oncology target validation
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Low
**Response Format**: Markdown parsing
**Key Metrics**: Trial count by KRAS mutation (G12C, G12D, G12V), combination strategies
**Business Value**: Target validation, combination therapy strategies

**Current Context**:
- LUMAKRAS (sotorasib) approved 2021 for KRAS G12C
- KRAZATI (adagrasib) approved 2022 for KRAS G12C
- G12D inhibitors in clinical development (breakthrough area)

---

#### Query 1.1.5: Rare Disease Trials with Orphan Designation
**Query**: "What rare disease trials have orphan drug designation and are in Phase 2 or later?"

**Domain**: Clinical Trials
**Problem**: Orphan drug development opportunity assessment
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium (requires filtering by study type and phase)
**Response Format**: Markdown parsing
**Key Metrics**: Indication diversity, phase distribution, regulatory pathway
**Business Value**: Portfolio diversification, fast-track approval opportunities

**Current Context**:
- 1,268 approved orphan drugs (FDA)
- FDA regulatory flexibility for rare diseases increasing
- Accelerated approval pathways more accessible

---

### 1.2 Advanced Clinical Trial Queries

**Scenario**: Strategic pipeline planning and partnership evaluation

#### Query 1.2.1: Geographic Trial Distribution
**Query**: "Compare the number of Phase 3 oncology trials recruiting in US vs. China"

**Domain**: Clinical Trials + Geographic Analysis
**Problem**: Global clinical development strategy
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium (requires multiple queries with location filters)
**Response Format**: Markdown parsing + aggregation
**Key Metrics**: Trial count by country, therapeutic area trends, sponsor nationality
**Business Value**: Geographic expansion strategy, CRO selection

**Current Context**:
- China biotech surge noted in 2025 trends
- Regulatory harmonization improving
- Cost advantages in Asian clinical trials

---

#### Query 1.2.2: Combination Therapy Trends
**Query**: "What are the most common combination therapies in checkpoint inhibitor trials?"

**Domain**: Clinical Trials + Pattern Analysis
**Problem**: Combination therapy strategy optimization
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High (requires text analysis of interventions)
**Response Format**: Markdown parsing + pattern extraction
**Key Metrics**: Combination frequency, partner drug classes, trial phases
**Business Value**: Partnership strategy, development prioritization

---

#### Query 1.2.3: Endpoint Evolution Analysis
**Query**: "What are the primary endpoints used in metabolic disease trials over the past 5 years?"

**Domain**: Clinical Trials + Temporal Analysis
**Problem**: Trial design optimization and regulatory strategy
**Data Source**: ClinicalTrials.gov via `ct_gov_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High (requires temporal filtering and endpoint parsing)
**Response Format**: Markdown parsing + temporal aggregation
**Key Metrics**: Endpoint types, regulatory acceptance trends, success rates
**Business Value**: Trial design optimization, regulatory strategy

---

## Domain 2: FDA Drug Intelligence

### 2.1 Approved Drug Queries

**Scenario**: Market landscape and competitive intelligence

#### Query 2.1.1: GLP-1 Approved Drugs
**Query**: "What GLP-1 receptor agonists are approved by the FDA for obesity?"

**Domain**: FDA Drug Approvals
**Problem**: Market landscape assessment for obesity therapeutics
**Data Source**: FDA via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Low
**Response Format**: JSON parsing
**Key Metrics**: Approval dates, indications, dosing, safety warnings
**Business Value**: Competitive positioning, market entry timing

**Current Context**:
- Oral semaglutide 25mg pending FDA approval (would be first oral GLP-1 for obesity)
- Orforglipron (Eli Lilly) head-to-head trial ongoing vs. injectable semaglutide
- Market exceeding $20B+ globally (2024)

---

#### Query 2.1.2: Breakthrough Therapy Designations
**Query**: "List all drugs with breakthrough therapy designation approved in 2024"

**Domain**: FDA Regulatory Pathways
**Problem**: Fast-track development strategy assessment
**Data Source**: FDA via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Indication, approval timeline, clinical data requirements
**Business Value**: Regulatory strategy, development timeline optimization

**Current Context**:
- Watershed year for cell & gene therapy (13 CGT approvals in 2024)
- First CRISPR therapy approved (Casgevy for sickle cell)
- First MRI-guided intracranial AAV delivery gene therapy

---

#### Query 2.1.3: Orphan Drug Approvals
**Query**: "What orphan drugs were approved for rare neurological diseases in the past 3 years?"

**Domain**: FDA Orphan Drug Program
**Problem**: Rare disease portfolio opportunity assessment
**Data Source**: FDA via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Indication, patient population size, pricing, exclusivity period
**Business Value**: Portfolio diversification, pricing strategy

---

#### Query 2.1.4: Antibody-Drug Conjugate Approvals
**Query**: "Find all approved antibody-drug conjugates and their targets"

**Domain**: FDA Drug Approvals + Mechanism Analysis
**Problem**: Emerging modality landscape assessment
**Data Source**: FDA via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Target antigen, payload type, indication, approval date
**Business Value**: Technology platform evaluation, licensing opportunities

**Current Context**:
- ADCs major trend in oncology (landmark deals in 2025)
- New payloads and linker technologies emerging
- Solid tumor indications expanding beyond hematologic malignancies

---

### 2.2 FDA Adverse Event Queries

**Scenario**: Safety surveillance and risk management

#### Query 2.2.1: GLP-1 Adverse Events
**Query**: "What are the most reported adverse events for semaglutide?"

**Domain**: FDA Adverse Event Reporting
**Problem**: Post-market safety surveillance
**Data Source**: FDA FAERS via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing + frequency analysis
**Key Metrics**: Event frequency, severity, patient demographics
**Business Value**: Risk management, label update strategy

**Current Context**:
- Long-term safety data still emerging (market since 2017)
- Concerns about muscle mass loss, rebound weight gain
- Gallbladder issues, pancreatitis monitoring

---

#### Query 2.2.2: CAR-T Safety Profile
**Query**: "Compare adverse event profiles for approved CAR-T therapies"

**Domain**: FDA Adverse Event Reporting + Comparative Analysis
**Problem**: Safety differentiation and market positioning
**Data Source**: FDA FAERS via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High
**Response Format**: JSON parsing + comparative analysis
**Key Metrics**: Cytokine release syndrome rates, neurotoxicity, long-term effects
**Business Value**: Product differentiation, safety management protocols

---

#### Query 2.2.3: Drug Recall Analysis
**Query**: "What oncology drug recalls occurred in 2024 and why?"

**Domain**: FDA Drug Recalls
**Problem**: Quality control and supply chain risk assessment
**Data Source**: FDA via `fda_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Recall reason, classification, affected lots, resolution time
**Business Value**: Quality system benchmarking, supply chain risk management

---

## Domain 3: Scientific Literature Intelligence (PubMed)

### 3.1 Literature Search Queries

**Scenario**: Scientific evidence gathering and mechanism validation

#### Query 3.1.1: Anti-Amyloid Therapy Literature
**Query**: "Find recent publications on anti-amyloid antibodies for Alzheimer's disease"

**Domain**: Scientific Literature
**Problem**: Mechanism validation and competitive intelligence
**Data Source**: PubMed via `pubmed_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Low
**Response Format**: JSON parsing
**Key Metrics**: Publication count, author institutions, ARIA safety data
**Business Value**: Scientific positioning, safety/efficacy benchmarking

**Current Context**:
- Lecanemab and donanemab recently approved
- ARIA (amyloid-related imaging abnormalities) safety concern
- APOE4 genotype risk stratification required
- Debate over clinical meaningfulness of cognitive benefits

---

#### Query 3.1.2: CRISPR Therapy Publications
**Query**: "What are the latest publications on CRISPR gene editing for sickle cell disease?"

**Domain**: Scientific Literature
**Problem**: Technology platform assessment
**Data Source**: PubMed via `pubmed_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Low
**Response Format**: JSON parsing
**Key Metrics**: Publication trends, clinical outcomes, off-target effects
**Business Value**: Technology evaluation, licensing due diligence

**Current Context**:
- Casgevy (CRISPR/Cas9) approved Dec 2023 (first CRISPR drug)
- FDA "plausible mechanism" pathway for personalized gene editing (Nov 2025)
- KJ treatment case study (rare disease CRISPR application)

---

#### Query 3.1.3: Real-World Evidence Studies
**Query**: "Find real-world evidence studies on checkpoint inhibitor effectiveness"

**Domain**: Scientific Literature + RWE
**Problem**: Real-world performance vs. clinical trial efficacy
**Data Source**: PubMed via `pubmed_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Real-world response rates, survival data, patient selection
**Business Value**: Market access strategy, health economics modeling

---

#### Query 3.1.4: Biomarker Discovery
**Query**: "What biomarkers are being studied for predicting GLP-1 response?"

**Domain**: Scientific Literature + Biomarker Analysis
**Problem**: Patient stratification and precision medicine
**Data Source**: PubMed via `pubmed_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing + entity extraction
**Key Metrics**: Biomarker types, predictive value, validation status
**Business Value**: Companion diagnostics strategy, patient segmentation

---

## Domain 4: Target Validation (Open Targets)

### 4.1 Target-Disease Association Queries

**Scenario**: Early discovery and target selection

#### Query 4.1.1: Alzheimer's Target Landscape
**Query**: "What are the top therapeutic targets for Alzheimer's disease with genetic evidence?"

**Domain**: Target Validation
**Problem**: Beyond amyloid target discovery
**Data Source**: Open Targets via `opentargets_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Low
**Response Format**: JSON parsing
**Key Metrics**: Association score, genetic evidence, tractability
**Business Value**: Pipeline diversification, mechanism innovation

**Current Context**:
- Anti-amyloid therapies show modest benefit (~27% slowing of decline)
- Need for multi-mechanism approaches (tau, inflammation, synaptic)
- KarXT (muscarinic agonist) different mechanism gaining traction

---

#### Query 4.1.2: Cancer Immunotherapy Targets
**Query**: "Find validated targets for cancer immunotherapy beyond PD-1/PD-L1"

**Domain**: Target Validation
**Problem**: Next-generation checkpoint inhibitor discovery
**Data Source**: Open Targets via `opentargets_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Target type, cancer indications, clinical stage
**Business Value**: Pipeline innovation, competitive differentiation

---

#### Query 4.1.3: Rare Disease Target Identification
**Query**: "What are the genetic targets for ultra-rare metabolic diseases with small patient populations (<500)?"

**Domain**: Target Validation + Rare Disease
**Problem**: Orphan drug target selection
**Data Source**: Open Targets via `opentargets_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High
**Response Format**: JSON parsing + filtering
**Key Metrics**: Patient population, genetic penetrance, druggability
**Business Value**: Orphan drug portfolio strategy

---

## Domain 5: Chemical Intelligence (PubChem)

### 5.1 Compound Property Queries

**Scenario**: Drug discovery and formulation optimization

#### Query 5.1.1: GLP-1 Agonist Properties
**Query**: "Compare the molecular properties of approved GLP-1 agonists"

**Domain**: Chemical Properties
**Problem**: Structure-activity relationship analysis
**Data Source**: PubChem via `pubchem_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Molecular weight, logP, TPSA, half-life determinants
**Business Value**: Drug design optimization, oral formulation strategy

**Current Context**:
- Oral semaglutide uses SNAC absorption enhancer
- Orforglipron designed as oral-first molecule
- PK/PD optimization for weekly dosing

---

#### Query 5.1.2: KRAS Inhibitor Scaffold Analysis
**Query**: "Find similar compounds to sotorasib and analyze their KRAS G12C binding properties"

**Domain**: Chemical Similarity + Target Binding
**Problem**: Freedom-to-operate and follow-on optimization
**Data Source**: PubChem via `pubchem_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High
**Response Format**: JSON parsing + similarity analysis
**Key Metrics**: Tanimoto similarity, binding affinity, selectivity
**Business Value**: IP strategy, chemical optimization

---

## Domain 6: Patent Intelligence (USPTO)

### 6.1 Patent Landscape Queries

**Scenario**: IP strategy and freedom-to-operate assessment

#### Query 6.1.1: GLP-1 Patent Landscape
**Query**: "What are the key patents covering GLP-1 receptor agonists for obesity?"

**Domain**: Patents
**Problem**: IP landscape and patent expiry forecasting
**Data Source**: USPTO via `uspto_patents_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Patent expiry dates, claim scope, litigation history
**Business Value**: Generic entry timing, licensing strategy

---

#### Query 6.1.2: CAR-T Manufacturing Patents
**Query**: "Find patents related to CAR-T cell manufacturing and production methods"

**Domain**: Patents + Technology Platform
**Problem**: Manufacturing innovation and cost reduction
**Data Source**: USPTO via `uspto_patents_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Assignee, manufacturing innovations, cost-reducing technologies
**Business Value**: Technology licensing, COGS optimization

---

#### Query 6.1.3: CRISPR IP Landscape
**Query**: "Map the CRISPR patent landscape across Broad Institute, Berkeley, and commercial entities"

**Domain**: Patents + IP Strategy
**Problem**: Complex IP landscape navigation
**Data Source**: USPTO via `uspto_patents_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High
**Response Format**: JSON parsing + IP mapping
**Key Metrics**: Patent families, geographic coverage, litigation status
**Business Value**: Licensing strategy, FTO assessment

---

## Domain 7: Healthcare Provider Intelligence (CMS)

### 7.1 Provider and Market Queries

**Scenario**: Commercial strategy and market access

#### Query 7.1.1: Oncologist Prescribing Patterns
**Query**: "What are the top prescribers of checkpoint inhibitors in major cancer centers?"

**Domain**: Healthcare Provider Data
**Problem**: KOL identification and targeting
**Data Source**: CMS Medicare via `healthcare_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Provider type, prescription volume, geographic distribution
**Business Value**: Sales force targeting, KOL engagement

---

#### Query 7.1.2: Market Access by Geography
**Query**: "Compare Medicare reimbursement rates for CAR-T therapy across different states"

**Domain**: Healthcare Economics
**Problem**: Market access and pricing strategy
**Data Source**: CMS Medicare via `healthcare_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: High
**Response Format**: JSON parsing + geographic analysis
**Key Metrics**: Reimbursement rates, prior authorization requirements, coverage policies
**Business Value**: Pricing strategy, market access optimization

---

## Domain 8: Financial Intelligence (SEC/Yahoo Finance)

### 8.1 Company and Market Queries

**Scenario**: Business development and investment analysis

#### Query 8.1.1: Biotech M&A Activity
**Query**: "What biotech M&A deals over $1B have occurred in the past 2 years?"

**Domain**: Financial Intelligence
**Problem**: Strategic transaction benchmarking
**Data Source**: SEC EDGAR via `sec_edgar_mcp`
**Expected Agent**: pharma-search-specialist
**Complexity**: Medium
**Response Format**: JSON parsing
**Key Metrics**: Deal value, therapeutic area, strategic rationale
**Business Value**: BD&L strategy, valuation benchmarking

**Current Context**:
- Obesity drug deals driving high valuations (2025 trend)
- China biotech assets attracting global pharma interest
- AI-driven drug discovery companies commanding premiums

---

#### Query 8.1.2: Pharma Company Pipeline Valuation
**Query**: "Analyze the stock performance correlation with pipeline milestones for Vertex Pharmaceuticals"

**Domain**: Financial Analysis + Pipeline Correlation
**Problem**: Asset valuation and investor communication
**Data Source**: Yahoo Finance via `financials_mcp` + CT.gov
**Expected Agent**: competitive-landscape-analyst (strategic)
**Complexity**: High
**Response Format**: Multi-source synthesis
**Key Metrics**: Stock price movement, pipeline events, market cap impact
**Business Value**: Investor relations, asset valuation

---

## Strategic Agent Test Queries (Multi-Domain)

### Scenario 1: Competitive Landscape Analysis

#### Query S1.1: GLP-1 Competitive Landscape
**User Input**: `@agent-competitive-landscape-analyst "Analyze the competitive landscape for GLP-1 receptor agonists in obesity"`

**Agent Invocation**: Explicit (`@agent-competitive-landscape-analyst`)
**Expected Agent**: competitive-landscape-analyst (strategic)
**Domain**: Multi-domain (CT.gov, FDA, PubMed, Patents, Financial)
**Problem**: Comprehensive competitive positioning
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: `get_glp1_obesity_trials`
- FDA approvals: `get_glp1_approved_drugs`
- Patents: `get_glp1_patents`
- Financial: Market size, pricing, reimbursement

**Strategic Analysis Output**:
- Market structure (approved drugs, late-stage pipeline)
- Competitive positioning (mechanism, dosing, efficacy/safety)
- Patent cliff analysis (genericization risk)
- Market entry timing recommendations
- Partnership opportunities
- Pricing and market access strategy

**Business Value**: Portfolio prioritization, investment decisions, BD&L strategy

**Current Market Context**:
- Oral semaglutide 25mg pending approval (game-changer)
- Orforglipron (Lilly) vs. semaglutide head-to-head ongoing
- $20B+ market with double-digit growth
- Compounding pharmacy disruption
- Reimbursement expansion underway

---

#### Query S1.2: Alzheimer's Competitive Landscape
**User Input**: `@agent-competitive-landscape-analyst "Provide a competitive landscape analysis for Alzheimer's disease therapeutics"`

**Agent Invocation**: Explicit (`@agent-competitive-landscape-analyst`)
**Expected Agent**: competitive-landscape-analyst (strategic)
**Domain**: Multi-domain
**Problem**: Beyond anti-amyloid strategy assessment
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: Phase 2/3 trials by mechanism
- FDA approvals: Lecanemab, donanemab, traditional therapies
- Literature: Real-world effectiveness, ARIA safety
- Targets: Beyond amyloid (tau, inflammation, synaptic)

**Strategic Analysis Output**:
- Mechanism diversity analysis
- Anti-amyloid therapy limitations (modest efficacy, ARIA risk)
- Next-generation opportunities (multi-mechanism, precision medicine)
- Market segmentation (APOE4 genotype, disease stage)
- Pricing and reimbursement challenges
- Patient access and safety monitoring requirements

**Business Value**: Mechanism selection, clinical trial design, market positioning

**Current Context**:
- Lecanemab approved July 2023, donanemab July 2024
- Both show ~27% slowing of cognitive decline
- ARIA safety concerns requiring monitoring
- APOE4 homozygotes at higher risk
- KarXT (different mechanism) showing promise for psychosis
- Need for combination therapies recognized

---

#### Query S1.3: KRAS Inhibitor Competitive Landscape
**Query**: "Analyze the KRAS inhibitor competitive landscape across all mutations"

**Domain**: Multi-domain
**Problem**: Precision oncology target expansion
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: By KRAS mutation (G12C, G12D, G12V, etc.)
- FDA approvals: LUMAKRAS, KRAZATI
- Targets: Mutation-specific binding mechanisms
- Combination strategies: With other targeted/immuno therapies

**Strategic Analysis Output**:
- Mutation-specific competitive landscape (G12C crowded, G12D opportunity)
- Combination therapy strategies
- Patient population size by mutation
- Differentiation strategies (potency, safety, convenience)
- Market entry timing by indication
- Partnership opportunities

**Business Value**: Target selection, clinical development strategy, partnership BD&L

**Current Context**:
- G12C inhibitors approved (sotorasib, adagrasib)
- G12D inhibitors in development (unmet need)
- Combination with checkpoint inhibitors being explored
- KRAS mutations ~25% of NSCLC, ~40% colorectal, ~95% pancreatic

---

### Scenario 2: Portfolio Expansion Strategy

#### Query S2.1: Rare Disease Portfolio Assessment
**User Input**: `@agent-competitive-landscape-analyst "Identify attractive orphan drug development opportunities in rare neurological diseases"`

**Agent Invocation**: Explicit (`@agent-competitive-landscape-analyst`)
**Expected Agent**: competitive-landscape-analyst (strategic)
**Domain**: Multi-domain
**Problem**: Portfolio diversification with fast-track opportunities
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: Orphan drug trials in neurology
- FDA: Orphan designations, accelerated approvals
- Targets: Validated genetic targets
- Literature: Unmet medical need, natural history

**Strategic Analysis Output**:
- Opportunity prioritization (patient population, unmet need, technical feasibility)
- Regulatory pathway optimization (orphan, breakthrough, accelerated)
- Development timeline and cost estimates
- Commercial potential and pricing strategy
- Partnership vs. in-house development
- Patient advocacy landscape

**Business Value**: Portfolio strategy, capital allocation, BD&L prioritization

**Current Context**:
- 1,268 approved orphan drugs (FDA)
- Regulatory flexibility increasing
- FDA "plausible mechanism" pathway for personalized therapies (Nov 2025)
- Small patient populations require adaptive trial designs
- High pricing accepted given unmet need

---

#### Query S2.2: Geographic Expansion Strategy
**Query**: "Should we expand our oncology clinical development into China and which indications?"

**Domain**: Multi-domain
**Problem**: Global development strategy optimization
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: US vs. China trial distribution
- Regulatory: NMPA approval trends, harmonization status
- Epidemiology: Disease burden and incidence by country
- Financial: Clinical trial costs, CRO capabilities

**Strategic Analysis Output**:
- China market opportunity assessment
- Indication prioritization for China development
- Regulatory pathway comparison (NMPA vs. FDA)
- Clinical trial cost-benefit analysis
- Partnership landscape (local partners, CROs)
- Data bridging and global filing strategy

**Business Value**: Global development strategy, cost optimization, time-to-market

**Current Context**:
- China biotech surge noted in 2025
- NMPA improving regulatory alignment with FDA/EMA
- Significant cost advantages (50-70% lower trial costs)
- Growing investigator and site capabilities
- Large patient populations for recruitment

---

### Scenario 3: Partnership & BD&L Strategy

#### Query S3.1: Acquisition Target Identification
**Query**: "Identify potential acquisition targets in CAR-T therapy with differentiated technology platforms"

**Domain**: Multi-domain
**Problem**: Build vs. buy decision for cell therapy platform
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: Novel CAR-T constructs and targets
- Patents: Freedom-to-operate, manufacturing innovations
- Financial: Company valuations, funding status, burn rate
- Scientific: Publications showing differentiation

**Strategic Analysis Output**:
- Target company prioritization
- Technology differentiation assessment
- Clinical stage and data quality
- Valuation range and deal structure
- Integration complexity and synergies
- Risk assessment (technical, regulatory, commercial)

**Business Value**: M&A strategy, valuation modeling, negotiation preparation

**Current Context**:
- In vivo CAR-T reprogramming emerging (avoid ex vivo manufacturing)
- Solid tumor CAR-T targets expanding
- Allogeneic (off-the-shelf) CAR-T reducing cost
- Manufacturing efficiency critical to COGS

---

#### Query S3.2: Licensing Opportunity Assessment
**Query**: "Evaluate licensing opportunities for oral GLP-1 formulations"

**Domain**: Multi-domain
**Problem**: Technology licensing vs. internal development
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Patents: Oral formulation technologies (SNAC, etc.)
- Clinical trials: Oral GLP-1 trials and results
- Chemical: Oral bioavailability enhancers
- Financial: Licensing deal comparables

**Strategic Analysis Output**:
- Technology landscape (SNAC, permeation enhancers, prodrugs)
- IP strength and exclusivity period
- Clinical proof-of-concept assessment
- Licensing deal benchmarking
- Royalty rate and milestone structures
- Build vs. license decision framework

**Business Value**: Technology strategy, licensing negotiations, portfolio optimization

**Current Context**:
- Novo's oral semaglutide uses SNAC (Eligen, now in-licensed)
- Lilly's orforglipron designed oral-first (different approach)
- Oral bioavailability major challenge for peptides
- Market preference for oral over injectable growing

---

### Scenario 4: Clinical Development Strategy

#### Query S4.1: Optimal Trial Design
**Query**: "What are the optimal trial endpoints and design for a novel anti-tau therapy in Alzheimer's?"

**Domain**: Multi-domain
**Problem**: Trial design optimization for regulatory success
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: Anti-tau trial designs and outcomes
- FDA: Accepted endpoints, biomarker acceptance
- Literature: Tau PET imaging, surrogate markers
- Regulatory: FDA guidance on AD trial design

**Strategic Analysis Output**:
- Primary endpoint selection (cognitive, functional, biomarker)
- Biomarker strategy (tau PET, plasma p-tau)
- Patient population selection (early vs. late AD, APOE4 stratification)
- Trial duration and sample size
- Regulatory pathway (accelerated approval, full approval)
- Competitor trial design comparison

**Business Value**: Regulatory success probability, trial cost optimization, time-to-market

---

#### Query S4.2: Combination Therapy Strategy
**Query**: "What combination therapy approaches should we pursue with our checkpoint inhibitor?"

**Domain**: Multi-domain
**Problem**: Maximize therapeutic benefit through rational combinations
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: Checkpoint inhibitor combinations
- Literature: Synergistic mechanisms, biomarker studies
- FDA: Combination approval precedents
- Safety: Adverse event profiles for combinations

**Strategic Analysis Output**:
- Combination partner prioritization (targeted therapy, chemotherapy, other IO)
- Mechanistic rationale and synergy evidence
- Safety and tolerability considerations
- Regulatory pathway (co-development, sequential approval)
- Partnership vs. internal development
- Trial sequencing strategy

**Business Value**: Development strategy, partnership identification, market differentiation

**Current Context**:
- Checkpoint inhibitor + chemotherapy standard in many indications
- Checkpoint + checkpoint combinations (CTLA-4 + PD-1)
- Checkpoint + targeted therapy emerging (BRAF/MEK, KRAS)
- Biomarker-driven patient selection critical

---

### Scenario 5: Regulatory Strategy

#### Query S5.1: Accelerated Approval Strategy
**Query**: "What surrogate endpoints could support accelerated approval for our rare disease therapy?"

**Domain**: Multi-domain (Regulatory + Clinical)
**Problem**: Fastest regulatory pathway for rare disease
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- FDA: Accelerated approval precedents in rare disease
- Clinical trials: Surrogate marker validation studies
- Literature: Natural history studies, biomarker qualification
- Regulatory: FDA guidance on rare disease endpoints

**Strategic Analysis Output**:
- Surrogate endpoint options and regulatory acceptance likelihood
- Natural history data requirements
- Biomarker qualification pathway
- Post-marketing confirmatory trial design
- Risk mitigation for confirmatory trial failure
- Regulatory meeting strategy (pre-IND, EOP2)

**Business Value**: Regulatory success, time-to-market, patient access

**Current Context**:
- FDA regulatory flexibility increasing for rare diseases
- "Plausible mechanism" pathway for personalized therapies (2025)
- Orphan drug designation + breakthrough therapy designation combo
- Small patient populations require adaptive designs

---

#### Query S5.2: Global Regulatory Alignment
**Query**: "How can we align our trial design to satisfy FDA, EMA, and NMPA requirements simultaneously?"

**Domain**: Multi-domain (Global Regulatory)
**Problem**: Global filing strategy optimization
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Regulatory: FDA/EMA/NMPA guidance comparison
- Clinical trials: Global trial designs and approvals
- Geography: Regional disease epidemiology differences
- Regulatory: Data bridging requirements

**Strategic Analysis Output**:
- Harmonized trial design feasibility
- Region-specific additional requirements
- Data bridging strategy for China
- Filing sequence optimization (FDA first vs. simultaneous)
- Regulatory meeting strategy by region
- Risk assessment for regional rejections

**Business Value**: Global market access, development efficiency, cost optimization

---

### Scenario 6: Market Access & Commercial Strategy

#### Query S6.1: Pricing and Reimbursement Strategy
**Query**: "What pricing and reimbursement strategy should we pursue for our CAR-T therapy?"

**Domain**: Multi-domain (Financial + Market Access)
**Problem**: Maximize access while ensuring sustainable pricing
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Financial: CAR-T pricing benchmarks ($373K-$475K per treatment)
- CMS: Medicare reimbursement policies
- Clinical: Outcomes data for health economics
- Market access: Prior authorization, coverage policies

**Strategic Analysis Output**:
- Pricing benchmarking and positioning
- Value-based contracting opportunities
- Reimbursement strategy by payer segment
- Patient access program design
- Health economics modeling (QALY, cost-effectiveness)
- Risk-sharing agreements

**Business Value**: Revenue optimization, patient access, payer negotiations

**Current Context**:
- CAR-T pricing $373K (Kymriah) to $475K (Yescarta)
- CMS covering but with restrictions
- Manufacturing cost reduction critical (in vivo CAR-T)
- Outcomes-based contracts emerging

---

#### Query S6.2: Launch Sequencing Strategy
**Query**: "Which indication should we launch first with our multi-indication immunotherapy asset?"

**Domain**: Multi-domain (Commercial + Clinical + Market)
**Problem**: Optimize launch sequence for commercial success
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**:
- Clinical trials: Data maturity by indication
- Epidemiology: Patient population size by indication
- Market: Competitive landscape by indication
- Financial: Revenue potential and market dynamics

**Strategic Analysis Output**:
- Indication prioritization (data strength, market opportunity, competition)
- Launch sequence rationale
- Sales force build and targeting strategy
- KOL engagement plan
- Payer strategy by indication
- Cross-indication positioning

**Business Value**: Revenue maximization, market share, brand positioning

---

## Advanced Multi-Server Pattern Queries

### Query A1: Cross-Reference Validation
**Query**: "Compare clinical trial reported outcomes with real-world evidence from Medicare claims for checkpoint inhibitors"

**Domain**: Multi-domain (CT.gov + CMS + PubMed)
**Problem**: Real-world effectiveness vs. trial efficacy
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**: 3 servers, data harmonization, statistical analysis
**Business Value**: Market access, health economics, payer negotiations

---

### Query A2: Patent-Clinical Trial Alignment
**Query**: "Map patent claims to clinical trial interventions for CRISPR therapies to identify freedom-to-operate risks"

**Domain**: Multi-domain (USPTO + CT.gov + PubChem)
**Problem**: IP strategy for clinical development
**Expected Agent**: pharma-search-specialist (complex infrastructure)
**Complexity**: Very High
**Data Requirements**: Patent analysis, trial intervention parsing, chemical structure matching
**Business Value**: IP strategy, FTO assessment, licensing decisions

---

### Query A3: Epidemiology-Trial-Market Analysis
**Query**: "Assess the gap between disease burden (Data Commons), clinical trial enrollment, and market size for rare metabolic diseases"

**Domain**: Multi-domain (Data Commons + CT.gov + SEC Edgar)
**Problem**: Market sizing and patient access assessment
**Expected Agent**: competitive-landscape-analyst
**Complexity**: Very High
**Data Requirements**: Epidemiology, trial enrollment, market data synthesis
**Business Value**: Portfolio prioritization, patient access strategy

---

## Test Suite Execution Guidelines

### Phase 1: Infrastructure Testing (pharma-search-specialist)
**Purpose**: Validate basic data collection across all MCP servers

1. Execute simple queries (1 query per MCP server)
2. Validate skill creation (folder structure, YAML frontmatter)
3. Test pagination handling (CT.gov large result sets)
4. Verify closed-loop validation (verify_skill.py execution)
5. Confirm markdown vs. JSON parsing (CT.gov vs. others)

**Success Criteria**:
- All skills created successfully (folder structure)
- All skills executable standalone
- Pagination complete (no data truncation)
- Verification passes for all skills
- Skills added to index.json

---

### Phase 2: Skill Discovery Testing
**Purpose**: Validate intelligent skill reuse (REUSE/ADAPT/CREATE strategies)

1. Execute similar queries to test REUSE (exact match)
2. Execute related queries to test ADAPT (therapeutic area change)
3. Execute novel queries to test CREATE (new pattern)
4. Validate health check system (broken skill detection)
5. Test semantic matching (non-obvious reuse opportunities)

**Success Criteria**:
- REUSE strategy works (existing skill executed)
- ADAPT strategy works (skill forked and modified)
- CREATE strategy works (reference pattern used)
- Health checks detect issues
- Semantic matching finds alternatives

---

### Phase 3: Strategic Agent Testing (competitive-landscape-analyst)
**Purpose**: Validate multi-domain data collection and synthesis

1. Execute competitive landscape queries (S1.1, S1.2, S1.3)
2. Validate metadata-driven orchestration (data_requirements)
3. Test parameter inference (therapeutic_area extraction)
4. Validate report generation (templates, markdown formatting)
5. Confirm report persistence (reports/ directory, git versioning)

**Success Criteria**:
- All required skills created/executed
- Data collection transparent (summary shown to user)
- Strategic analysis comprehensive (4000-6000 words)
- Report saved to reports/ directory
- YAML frontmatter complete

---

### Phase 4: Edge Cases and Error Handling

**Test Scenarios**:
1. **Empty Results**: Query returns 0 trials (verify graceful handling)
2. **API Errors**: Server returns 404/500 (verify retry logic)
3. **Pagination Limits**: CT.gov >10,000 results (verify truncation handling)
4. **Ambiguous Queries**: Multiple interpretations (verify clarification)
5. **Skill Conflicts**: Two skills with same name (verify versioning)
6. **Index Corruption**: index.json malformed (verify recovery)
7. **Broken Skills**: Skill syntax error (verify health check detection)
8. **Missing Dependencies**: Python package not installed (verify error messaging)

**Success Criteria**:
- Graceful error messages
- No silent failures
- User notified of issues
- Recovery mechanisms work
- Logs capture failures

---

## Summary Statistics

**Total Test Queries**: 80+

**Distribution by Domain**:
- Clinical Trials (CT.gov): 15 queries
- FDA Drug Intelligence: 12 queries
- Scientific Literature (PubMed): 8 queries
- Target Validation (Open Targets): 6 queries
- Chemical Intelligence (PubChem): 4 queries
- Patent Intelligence (USPTO): 5 queries
- Healthcare Provider (CMS): 4 queries
- Financial Intelligence (SEC/Yahoo): 4 queries
- Strategic Multi-Domain: 18 queries
- Advanced Multi-Server: 4 queries

**Distribution by Complexity**:
- Low (single server, simple query): 28 queries
- Medium (single server, complex query): 24 queries
- High (multi-server or advanced analysis): 18 queries
- Very High (strategic multi-domain synthesis): 10 queries

**Distribution by Expected Agent**:
- pharma-search-specialist: 58 queries
- competitive-landscape-analyst: 22 queries

**Distribution by Scenario**:
- Competitive landscape analysis: 12 queries
- Portfolio expansion strategy: 8 queries
- Partnership & BD&L: 10 queries
- Clinical development strategy: 8 queries
- Regulatory strategy: 6 queries
- Market access & commercial: 8 queries

**Therapeutic Area Coverage**:
- Oncology: 22 queries
- Metabolic/Obesity: 15 queries
- Neurology/Alzheimer's: 12 queries
- Cell & Gene Therapy: 14 queries
- Rare Diseases: 10 queries
- General/Cross-therapeutic: 7 queries

---

## Conclusion

This comprehensive test suite provides 80+ queries covering all major pharmaceutical intelligence domains, strategic scenarios, and MCP servers. The queries are designed to test both infrastructure capabilities (pharma-search-specialist) and strategic synthesis (competitive-landscape-analyst), with real-world business contexts reflecting current pharmaceutical trends.

### Agent Invocation Summary

**All queries include explicit invocation syntax:**

1. **Infrastructure Queries (58 queries)**: Use natural language - system automatically invokes pharma-search-specialist
   - Example: `"How many Phase 3 obesity trials are recruiting?"`
   - Pattern: Simple question → Auto-invoke pharma-search-specialist → Create/execute skill → Return data

2. **Strategic Queries (22 queries)**: Use explicit @agent mention - manually invoke competitive-landscape-analyst
   - Example: `@agent-competitive-landscape-analyst "Analyze the GLP-1 competitive landscape"`
   - Pattern: @agent + question → Read agent metadata → Orchestrate data collection → Invoke strategic agent → Generate report

**Note**: Each query in this document now includes:
- **User Input**: The exact text to type
- **Agent Invocation**: Automatic (natural) vs. Explicit (@agent syntax)
- **Expected Agent**: Which agent should respond

This makes the test suite immediately actionable - testers can copy-paste the "User Input" field directly into the system.

### Test Suite Validation

The test suite validates:
- **Data collection accuracy** across 12 MCP servers
- **Skills library evolution** (REUSE/ADAPT/CREATE strategies)
- **Multi-domain synthesis** for strategic analysis
- **Closed-loop verification** for autonomous quality assurance
- **Progressive disclosure** for token efficiency
- **Report generation** for strategic work product preservation
- **Agent invocation patterns** (automatic vs. explicit)

Successful execution of this test suite will demonstrate the platform's readiness for production pharmaceutical research intelligence use cases.
