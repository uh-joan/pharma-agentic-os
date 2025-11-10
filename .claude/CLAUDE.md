# Pharmaceutical Research Intelligence

## Architecture

**Multi-agent pattern**: Data gathering + analytical agents

**Agents**:
- `pharma-search-specialist`: Query → JSON plan → MCP execution → `data_dump/`
- `epidemiology-analyst`: Reads `data_dump/` → prevalence models, segmentation, funnels
- `patient-flow-modeler`: Reads `data_dump/` → eligibility funnels, treatment sequencing, multi-year patient flows
- `uptake-dynamics-analyst`: Reads `temp/` + `data_dump/` → market share evolution, treated patient projections
- `pricing-strategy-analyst`: Reads `data_dump/` → IRP modeling, tiered pricing, launch sequencing
- `revenue-synthesizer`: Reads `temp/` → revenue forecasts, peak sales, NPV-ready streams
- `market-sizing-analyst`: Reads `data_dump/` → TAM/SAM/SOM market sizing synthesis
- `pharma-landscape-competitive-analyst`: Reads `data_dump/` → competitive landscape mapping, pipeline threats
- `pharma-landscape-opportunity-identifier`: Reads `temp/` → BD opportunities (partnerships, acquisitions, white space)
- `pharma-landscape-strategy-synthesizer`: Reads `temp/` → strategic planning, action prioritization, scenario analysis

## MCP Servers (see .mcp.json)

- **ct-gov-mcp**: ClinicalTrials.gov trial data
- **nlm-codes-mcp**: NLM Clinical Tables (ICD-10, ICD-11, HCPCS, NPI, HPO, medical coding)
- **pubmed-mcp**: PubMed biomedical literature
- **fda-mcp**: FDA drug labels, adverse events, recalls, device data
- **who-mcp-server**: WHO Global Health Observatory data
- **sec-mcp-server**: SEC EDGAR financial filings
- **healthcare-mcp**: CMS Medicare provider data
- **financials-mcp-server**: Yahoo Finance, FRED economic data
- **datacommons-mcp**: Population/disease stats
- **patents-mcp-server**: USPTO patent search
- **opentargets-mcp-server**: Target validation, genetics
- **pubchem-mcp-server**: Compound properties, ADME

**Tool specs**: `.claude/.context/mcp-tool-guides/` (clinicaltrials.md, fda.md, pubmed.md, etc.)

## pharma-search-specialist

**Role**: Query analysis → JSON execution plan (no execution)
**Input**: User query
**Output**: JSON with execution_plan array (step, tool, method, params, token_budget)
**Tools**: Read only (reads `.claude/.context/mcp-tool-guides/`)

See `.claude/agents/pharma-search-specialist.md` for plan format and examples.

## Execution Protocol

### 1. Classify Query Complexity

**Simple** (single database, <5 steps):
- FDA approval status for specific drug
- Clinical trial count for condition
- PubMed articles on topic
- Patent search for compound
- Single entity lookup

**Complex** (multi-database, >5 steps):
- Competitive landscape analysis
- Market assessment
- KOL identification
- Safety signal detection
- Pipeline analysis
- Keywords: "competitive", "landscape", "compare", "analyze market", "identify leaders"

**Uncertain/Exploratory**:
- Novel questions without clear workflow
- Ambiguous entities or scope
- "What if" scenarios
- Open-ended research
- Keywords: "explore", "discover", "what are all", "map the space"

### 2. Invoke Specialist

Use the template matching the complexity classification from Step 1.

**For simple queries**:
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read relevant tool guide from .claude/.context/mcp-tool-guides/ (e.g., fda.md, clinicaltrials.md).
Read performance-optimization.md and apply count-first + field selection.
Return ONLY JSON execution plan."
```

**For complex queries** (multi-database, competitive analysis, workflows):
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read search-strategy-protocols.md (4-phase execution).
Read search-workflows.md (find similar workflow template).
Read performance-optimization.md (token efficiency - MANDATORY count-first for FDA).
Read cross-database-integration.md (if linking entities).
Read relevant tool guides (fda.md for FDA queries, clinicaltrials.md for CT.gov, pubmed.md for PubMed).
Return ONLY JSON execution plan."
```

**For uncertain/exploratory queries**:
```
Prompt: "You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Apply 'ultrathink' mode from search-strategy-protocols.md.
Read search-workflows.md for inspiration.
Read quality-control.md for validation criteria.
Read performance-optimization.md (MANDATORY count-first for FDA).
Read relevant tool guides (fda.md, clinicaltrials.md, pubmed.md, etc.).
Design custom workflow. Return ONLY JSON execution plan."
```

### 3. Execute Plan
Parse JSON → execute each step → save to `data_dump/{YYYY-MM-DD}_{HHMMSS}_{tool}_{term}/` → present findings

**After execution**: Save raw MCP results to data_dump/, then optionally invoke analytical agents.

### 4. Invoke Analytical Agents (If Needed)

**epidemiology-analyst** - Prevalence modeling, segmentation, eligibility funnels

Use for: Market sizing, drug-eligible population estimates, patient segmentation

Template:
```
"You are epidemiology-analyst. Read .claude/agents/epidemiology-analyst.md.
Analyze data_dump/[folder]/ and return prevalence model, segmentation, eligibility funnel."
```

**patient-flow-modeler** - Treatment-eligible population projections and sequencing

Use for: Eligibility funnels, treatment line distribution, multi-year patient flows, sensitivity analysis

Template:
```
"You are patient-flow-modeler. Read .claude/agents/patient-flow-modeler.md.
Analyze data_dump/[folder]/ and return eligibility funnel with multi-year patient flow projections."
```

**uptake-dynamics-analyst** - Market share evolution and adoption dynamics

Use for: Uptake modeling, competitive displacement, treated patient projections

Template:
```
"You are uptake-dynamics-analyst. Read .claude/agents/uptake-dynamics-analyst.md.
Read temp/patient_flow_*.md and data_dump/[competitive folder]/ and return market share evolution with treated patient projections."
```

**pricing-strategy-analyst** - Global pricing optimization and launch sequencing

Use for: IRP modeling, tiered pricing, launch sequence optimization

Template:
```
"You are pricing-strategy-analyst. Read .claude/agents/pricing-strategy-analyst.md.
Analyze data_dump/[pricing folder]/ and return IRP modeling with tiered pricing strategy and launch sequencing."
```

**revenue-synthesizer** - Pharmaceutical revenue forecasting synthesis

Use for: Revenue projections, peak sales, NPV-ready streams

Template:
```
"You are revenue-synthesizer. Read .claude/agents/revenue-synthesizer.md.
Read temp/patient_flow_*.md, temp/uptake_dynamics_*.md, and optionally temp/pricing_strategy_*.md. Return multi-year revenue forecast with sensitivity analysis."
```

**market-sizing-analyst** - TAM/SAM/SOM market sizing synthesis

Use for: Market sizing, addressable market analysis, revenue potential assessment

Template:
```
"You are market-sizing-analyst. Read .claude/agents/market-sizing-analyst.md.
Analyze data_dump/ and synthesize TAM/SAM/SOM market sizing with competitive landscape."
```

**pharma-landscape-competitive-analyst** - Competitive landscape mapping and pipeline threat assessment

Use for: Market leader analysis, pipeline dynamics, competitive positioning, threat scoring

Template:
```
"You are pharma-landscape-competitive-analyst. Read .claude/agents/pharma-landscape-competitive-analyst.md.
Analyze data_dump/[folder]/ and return competitive landscape analysis with threat assessment."
```

**pharma-landscape-opportunity-identifier** - BD opportunity screening

Use for: Partnership targets, acquisition candidates, white space identification

Template:
```
"You are pharma-landscape-opportunity-identifier. Read .claude/agents/pharma-landscape-opportunity-identifier.md.
Read temp/competitive_analysis_*.md and return BD opportunity screening."
```

**pharma-landscape-strategy-synthesizer** - Strategic planning synthesis

Use for: Market positioning strategy, action prioritization, scenario planning, risk mitigation

Template:
```
"You are pharma-landscape-strategy-synthesizer. Read .claude/agents/pharma-landscape-strategy-synthesizer.md.
Read temp/competitive_analysis_*.md and temp/bd_opportunities_*.md and return strategic plan."
```

### 5. Save Analytical Outputs (If Agents Invoked)

After analytical agent execution, Claude Code saves outputs to `temp/`:
- `temp/epidemiology_analysis_{YYYY-MM-DD}_{HHMMSS}_{condition}.md`
- `temp/patient_flow_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/uptake_dynamics_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/pricing_strategy_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/revenue_forecast_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/market_sizing_{YYYY-MM-DD}_{HHMMSS}_{drug_indication}.md`
- `temp/competitive_analysis_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`
- `temp/bd_opportunities_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`
- `temp/strategic_plan_{YYYY-MM-DD}_{HHMMSS}_{indication}.md`

**Agent Constraint**: Analytical agents are read-only (tools: [Read]). Claude Code orchestrator handles file persistence.

## File Structure

**data_dump/**: Raw MCP results (query.json, results.json, summary.md, metadata.json)
**temp/**: Analytical agent outputs (epidemiology_analysis_*.md, patient_flow_*.md, uptake_dynamics_*.md, pricing_strategy_*.md, revenue_forecast_*.md, market_sizing_*.md, competitive_analysis_*.md, bd_opportunities_*.md, strategic_plan_*.md) - written by Claude Code after agent execution
**.claude/.context/mcp-tool-guides/**: Tool documentation (DO NOT MODIFY)

## Token Efficiency

**Critical**: Task calls carry full conversation history (~50k tokens per call).

**Best Practices**:
1. Keep specialist prompts minimal (use template above)
2. After receiving execution plan, consider clearing context if conversation is long
3. Limit MCP results (max 50-100 records per query)
4. Use count/pagination before fetching large datasets

## Design Principles

1. **Multi-agent**: Data gathering (pharma-search-specialist) + analytical (epidemiology-analyst, patient-flow-modeler, uptake-dynamics-analyst, pricing-strategy-analyst, revenue-synthesizer, market-sizing-analyst, pharma-landscape-competitive-analyst, pharma-landscape-opportunity-identifier, pharma-landscape-strategy-synthesizer)
2. **Separation of concerns**: Gathering vs analysis, no MCP execution by analysts
3. **Read-only analysts**: Analytical agents use only Read tool; Claude Code orchestrator handles file writes to temp/
4. **Token optimization**: Conservative limits, pagination, count strategies
5. **Audit trail**: Raw MCP results → data_dump/, analytical outputs → temp/
6. **Agent constraints**: Read-only tools for analysts, Write reserved for Claude Code orchestrator
