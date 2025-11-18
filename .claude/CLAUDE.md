# Pharmaceutical Research Intelligence Platform

## Core Execution Principle

**CODE-FIRST ARCHITECTURE**:
- Agents generate **executable Python scripts**, NOT markdown analysis
- Claude Code saves scripts to `scripts/[domain]/` and executes via `python3 script.py`
- Scripts contain MCP queries, business logic, and output formatting
- Results saved to `data_dump/` for raw data, `temp/` for analysis outputs
- Direct MCP calls ONLY for exploration (understanding response structure)

**Why Code-First**:
- ✅ Reproducible (scripts can be re-run)
- ✅ Testable (scripts can be unit tested)
- ✅ Versionable (scripts in git)
- ✅ Composable (scripts import shared functions)
- ✅ Token-efficient (execution happens outside conversation)

## Agent Types

### 1. Planning Agents
**Pattern**: User query → Agent generates JSON plan → Claude Code executes MCP queries → Saves to data_dump/

**Agents**:
- `pharma-search-specialist` - Data gathering queries
- `search-orchestrator` - Multi-phase project orchestration

**Output**: JSON execution plans that Claude Code executes

### 2. Analytical Agents
**Pattern**: Reads existing files (data_dump/, temp/) → Outputs markdown analysis → Claude Code saves to temp/

**Agents**: All `-analyst`, `-modeler`, `-synthesizer`, `-strategist` agents

**Output**: Markdown analysis files

## Script Organization

```
scripts/
├── mcp/                   # MCP query utilities
│   ├── queries/           # Query helper functions
│   ├── client.py          # MCP client wrapper
│   └── servers/           # Server-specific utilities
├── analysis/              # Analysis modules
│   └── modules/           # Shared analysis functions
└── utils/                 # Utilities
    └── fda_query_validator.py
```

## File Persistence

### Raw Data (`data_dump/`)
- **Saved by**: Claude Code after executing MCP queries
- **Contains**: Raw JSON from MCP queries
- **Naming**: `data_dump/YYYY-MM-DD_HHMMSS_[source]_[query]/`
- **Version control**: No (.gitignore)

### Analysis Outputs (`temp/`)
- **Saved by**: Claude Code after analytical agents produce markdown
- **Contains**: Markdown analysis from analytical agents
- **Naming**: `temp/[analysis_type]_YYYY-MM-DD_HHMMSS_[topic].md`
- **Version control**: No (.gitignore)

## Agent Invocation Templates

### For Planning Agents

**pharma-search-specialist**:
```
You are pharma-search-specialist. Read .claude/agents/pharma-search-specialist.md.

Query: '[user query]'

Read relevant tool guide from .claude/.context/mcp-tool-guides/
Return ONLY JSON execution plan.
```

**search-orchestrator**:
```
You are search-orchestrator. Read .claude/agents/search-orchestrator.md.

Analyze project context files and create workflow plan with:
1. mcp_queries: Data gathering tasks
2. specialist_delegations: Analysis tasks
3. synthesis_plan: Final compilation

Return ONLY JSON plan.
```

### For Read-Only Analysts (Legacy)

**Example - epidemiology-analyst**:
```
You are epidemiology-analyst. Read .claude/agents/epidemiology-analyst.md.

Analyze data_dump/[folder]/ and return:
- Prevalence model
- Patient segmentation
- Eligibility funnel

Output: Markdown analysis
```

## MCP Servers

Available MCP servers (see `.mcp.json`):
- `ct-gov-mcp`: ClinicalTrials.gov trial data
- `pubmed-mcp`: PubMed literature
- `fda-mcp`: FDA drug labels, adverse events, recalls
- `nlm-codes-mcp`: ICD-10, ICD-11, HCPCS, NPI coding
- `who-mcp-server`: WHO health statistics
- `sec-mcp-server`: SEC financial filings
- `healthcare-mcp`: CMS Medicare data
- `financials-mcp-server`: Yahoo Finance, FRED economic data
- `datacommons-mcp`: Population/disease statistics
- `patents-mcp-server`: USPTO patent search
- `opentargets-mcp-server`: Target validation, genetics
- `pubchem-mcp-server`: Compound properties, ADME

**Tool guides**: `.claude/.context/mcp-tool-guides/` (clinicaltrials.md, fda.md, etc.)

## FDA Query Optimization

**All FDA queries must include count parameter** to avoid 25k token MCP limit.

Auto-validation via `scripts/utils/fda_query_validator.py`:
- Adds count parameter if missing
- Adds .exact suffix to count fields
- Validates field selection

**See**: `scripts/utils/README.md`

## Token Efficiency

**Critical**: Task tool calls carry full conversation history (~50k tokens).

**Best Practices**:
1. Generate scripts instead of JSON plans (execution happens outside conversation)
2. Keep agent prompts minimal
3. Use count/pagination in MCP queries (max 50-100 records)
4. Scripts handle large data processing efficiently

## Design Principles

1. **Code-First**: Agents generate scripts when reproducibility is needed
2. **Planning-Based**: JSON plans for data gathering queries
3. **Analysis-Based**: Markdown analysis for read-only analytical work
4. **Token-Efficient**: Execution happens outside conversation context where possible
5. **Audit Trail**: Raw data → data_dump/, analysis → temp/

## Current Agents

### Planning Agents
- `pharma-search-specialist`: Data gathering JSON plans
- `search-orchestrator`: Multi-phase project JSON plans

### Analytical Agents
All `-analyst`, `-modeler`, `-synthesizer`, `-strategist` agents:
- epidemiology-analyst
- patient-flow-modeler
- uptake-dynamics-analyst
- pricing-strategy-analyst
- revenue-synthesizer
- market-sizing-analyst
- opportunity-identifier
- strategy-synthesizer
- comparable-analyst
- npv-modeler
- structure-optimizer
- target-identifier
- target-validator
- target-druggability-assessor
- target-hypothesis-synthesizer
- safety-pharmacology-analyst
- genetic-toxicology-analyst
- toxicology-analyst
- toxicologist-regulatory-strategist
- rwe-study-designer
- rwe-outcomes-analyst
- rwe-analytics-strategist
- regulatory-risk-analyst
- regulatory-precedent-analyst
- regulatory-pathway-analyst
- regulatory-label-strategist
- regulatory-adcomm-strategist

**Status**: Read-only markdown analysis pattern
