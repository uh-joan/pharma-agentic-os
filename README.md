# Agentic Research Platform

Turn research questions into executable code that queries 12+ specialized data sources—from clinical trials to financial filings to disease statistics.

Built on Anthropic's **code execution with MCP pattern** for 98.7% context reduction. AI agents generate Python code, execute it, and save reusable research functions that grow smarter over time.

**What makes this different:**
- 🤖 **AI agents generate Python code** (not just prompts)
- 📊 **12+ data sources**: Healthcare, Finance, Patents, Public Health
- 🔄 **Reusable skills library** that evolves with use
- ⚡ **98.7% more token-efficient** than direct queries
- 🎯 **End-to-end workflows**: From data collection to strategic analysis

**Quick example:** *"What are the top 10 diabetes drugs by market share?"* → Agent reads FDA & financial data → Generates Python code → Executes → Returns analysis + saves reusable skill for future queries.

**Reference**: [Anthropic Engineering Blog](https://www.anthropic.com/engineering/code-execution-with-mcp) • [Model Context Protocol](https://modelcontextprotocol.io)

---

## Use Cases Across Domains

### 💊 Healthcare & Life Sciences
- **Drug discovery intelligence**: Clinical trials, regulatory approvals, adverse events
- **Competitive landscape analysis**: Clinical + regulatory + market dynamics
- **Target validation**: Genetics, publications, clinical evidence
- **Medical coding workflows**: ICD-10/11, HCPCS, NPI standardization

**Example:** *"Analyze GLP-1 drug landscape"* → 1,808 trials + 21 approved drugs + adverse events + market data → Comprehensive competitive report

### 💰 Financial Research & Investment
- **Biotech due diligence**: Clinical pipelines + SEC filings + patents
- **Market analysis**: Stock performance + clinical outcomes + approval timelines
- **M&A intelligence**: Company financials + pipeline assets + IP portfolios
- **Economic monitoring**: FRED indicators + sector trends + earnings

**Example:** *"Due diligence on biotech M&A deals over $1B"* → SEC filings + trial outcomes + patent landscapes + financial metrics

### 🏥 Public Health & Policy
- **Disease burden analysis**: WHO statistics + population data + healthcare capacity
- **Healthcare system evaluation**: Provider networks + quality metrics + access gaps
- **Epidemiology tracking**: Prevalence trends + demographics + risk factors
- **Resource allocation**: Provider density + disease burden + utilization

**Example:** *"Cardiovascular disease burden in US by state"* → WHO burden data + Data Commons demographics + CMS provider capacity

### 🔬 Academic & IP Research
- **Literature reviews**: PubMed search + citation networks + trend analysis
- **Patent landscape analysis**: USPTO search + prior art + licensing trends
- **Chemical/biological data**: Compound properties + targets + pathways + ADME
- **Innovation tracking**: Patent-to-paper linkage + technology forecasting

**Example:** *"CRISPR patent landscape since 2020"* → USPTO patents + PubMed publications + chemical properties + licensing activity

### 🎯 Cross-Domain Intelligence
- **Multi-source company profiling**: Patents + trials + financials + publications
- **Technology trend analysis**: Patent activity + research papers + clinical trials + market adoption
- **Partnership opportunities**: Asset gaps + complementary capabilities + deal precedents
- **Investment thesis building**: Clinical + regulatory + financial + competitive synthesis

**Example:** *"Complete Alzheimer's disease intelligence"* → Disease burden + clinical trials + approved drugs + genetic targets + market size

---

## Core Architecture

**Pattern**: Code Execution with MCP (Model Context Protocol)

### How It Works

```
User Query
    ↓
Research agent analyzes query
    ↓
Progressive Disclosure:
  - Read relevant MCP tool guide (API docs)
  - Read code example pattern (on-demand)
    ↓
Generate Python code
    ↓
Execute code (Bash tool)
    ↓
Code execution:
  - Query MCP server(s)
  - Process data in-memory
  - Print summary to conversation
    ↓
Agent returns:
  - Summary (500 tokens)
  - Skill code (.py)
  - Documentation (.md)
    ↓
Main agent saves skill:
  - .claude/skills/[skill-name]/SKILL.md
  - .claude/skills/[skill-name]/scripts/[function].py
    ↓
Skill becomes reusable across sessions ✓
```

### Key Benefits

- **98.7% context reduction**: Raw data never enters model context (150k → 2k tokens)
- **Progressive disclosure**: Load only docs/examples needed for current query
- **Skills library**: Build reusable function toolbox across sessions
- **Privacy**: Sensitive data stays in execution environment
- **Natural control flow**: Loops, conditionals, error handling in Python

**Reference**: [Anthropic Engineering Blog - Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

---

## Data Sources (12 MCP Servers)

### Healthcare & Life Sciences
- **ClinicalTrials.gov**: 500K+ clinical trials with study protocols and outcomes
- **FDA**: Drug labels, adverse events, recalls, device registrations (openFDA)
- **PubMed**: 35M+ biomedical literature citations and abstracts
- **Open Targets**: Target validation and gene-drug-disease associations
- **PubChem**: 110M+ chemical compounds with properties and bioactivity

### Medical Standards & Coding
- **NLM Medical Codes**: ICD-10/11 (100K+ codes), HCPCS, NPI, HPO vocabularies
- **WHO Global Health Observatory**: International health statistics and indicators

### Financial & Legal
- **SEC EDGAR**: Public company financial filings and ownership data
- **Financial Markets**: Stock data (Yahoo Finance) + economic indicators (FRED)
- **USPTO Patents**: Patent search, prior art, and intellectual property data

### Healthcare Systems & Population Data
- **CMS Medicare**: Healthcare provider data, procedures, and reimbursement
- **Data Commons**: Population statistics, disease demographics, and trends

**Documentation**: Each data source has detailed API guides in `.claude/.context/mcp-tool-guides/`

---

## Agent System

### Infrastructure Agent (Data Collection Layer)

**pharma-search-specialist** - Creates reusable data collection skills

- **Pattern**: User query → Read docs → Generate Python code → Execute → Return skill
- **Output**: Summary + Python skill + Documentation
- **Location**: `.claude/agents/pharma-search-specialist.md`

**Example Flow**:
```
User: "How many Phase 3 obesity trials are recruiting in the US?"
    ↓
Agent reads: clinicaltrials.md + ctgov_markdown_parsing.md
    ↓
Agent generates Python code with CT.gov markdown parsing
    ↓
Agent executes → "36 trials found"
    ↓
Agent returns: summary + skill code + docs
    ↓
Main agent saves: .claude/skills/us-phase3-obesity-recruiting-trials/
```

### Strategic Agent (Analysis & Synthesis Layer)

**competitive-landscape-analyst** - Competitive intelligence and strategic analysis

- **Pattern**: Metadata-driven data collection → Strategic analysis
- **Input**: Collected data from skills execution
- **Output**: Strategic report with competitive positioning and recommendations
- **Location**: `.claude/agents/competitive-landscape-analyst.md`

**Example Flow**:
```
User: "Analyze KRAS inhibitor competitive landscape"
    ↓
Main agent reads agent metadata → Needs: trials + FDA drugs
    ↓
Main agent checks/creates/executes required skills
    ↓
Main agent invokes analyst with collected data
    ↓
Analyst returns: competitive positioning, market timing, recommendations
    ↓
Report saved: reports/competitive-landscape/YYYY-MM-DD_kras-inhibitor.md
```

---

## Skills Library

The skills library is a **growing collection of reusable data collection functions** that the system builds over time through usage. Each query creates a new skill that can be reused in future sessions.

**How It Works:**
- User asks a question → Agent creates executable Python skill
- Skill saved to `.claude/skills/` with YAML frontmatter + documentation
- Future queries reuse existing skills (via intelligent discovery system)
- Library grows organically with each new query type

**Current Library:** 68 skills across clinical trials, FDA drugs, chemical properties, medical coding, literature search, healthcare providers, financial data, patents, and more.

### Folder Structure

```
.claude/skills/
├── index.json                          # Skills discovery index
├── README.md                           # Skills library documentation
└── [skill-name]/                       # Each skill is self-contained
    ├── SKILL.md                        # YAML frontmatter + documentation
    └── scripts/
        └── [function_name].py          # Executable Python function
```

**Both importable and executable:** Skills can be imported as Python modules or run standalone for testing/validation.

**Discovery System:** 4-level intelligent discovery (index query → health check → semantic matching → strategy decision) ensures optimal skill reuse.

---

## Example Queries

### Healthcare Research
```
"How many Phase 3 obesity trials are currently recruiting?"
"What are the FDA adverse events for SGLT2 inhibitors?"
"Compare GLP-1 receptor agonist efficacy across trials"
"Get Open Targets genetic evidence for Alzheimer's disease"
"Find PubChem properties for approved anticoagulants"
```

### Financial Analysis
```
"Get Abbott's segment revenue breakdown for the last 5 years"
"Analyze biotech M&A deals over $1B since 2020"
"Track Regeneron stock performance vs clinical trial outcomes"
"What are the latest FRED economic indicators for healthcare sector?"
"Compare pharma company R&D spending from SEC filings"
```

### Public Health & Policy
```
"What's the cardiovascular disease burden in sub-Saharan Africa?"
"How many cardiologists are there per capita in Texas?"
"Compare diabetes prevalence trends across OECD countries"
"Get WHO life expectancy data by country for last decade"
"Analyze Medicare provider density by specialty and state"
```

### Academic & IP Research
```
"Find all CRISPR patents filed in 2024"
"Get PubMed publications on checkpoint inhibitor combinations"
"What are the chemical properties of approved anticoagulants?"
"Analyze patent landscape for antibody-drug conjugates"
"Literature review: anti-amyloid antibody publications 2020-2024"
```

### Multi-Domain Intelligence
```
"Analyze Alzheimer's disease: burden + trials + drugs + targets + market"
"Due diligence on Company X: financials + pipeline + patents + publications"
"BRAF inhibitor competitive landscape: trials + approvals + adverse events + market"
"Obesity drug market: trials + FDA drugs + economic burden + provider landscape"
```

---

## Token Efficiency

| Method | Tokens | Efficiency |
|--------|--------|-----------|
| Direct MCP call | 60,000 | ❌ Raw data in context |
| Old Python scripts | 2,000 | ⚠️ Data flows through context |
| **Code execution + MCP** | **500** | ✅ **98.7% reduction** |

**How it works**:
- Data processed in execution environment (Python)
- Only summary enters model context
- Raw API responses never loaded into conversation
- Agent reads only needed documentation (progressive disclosure)

**Measured by Anthropic**: Code execution pattern reduces tokens from 150K → 2K (98.7% reduction).

---

## Progressive Disclosure System

### MCP Tool Guides (API Documentation)
Agent reads these to understand API parameters and response formats:
- `.claude/.context/mcp-tool-guides/clinicaltrials.md`
- `.claude/.context/mcp-tool-guides/fda.md`
- `.claude/.context/mcp-tool-guides/pubmed.md`
- [9 more servers...]

### Code Examples (On-Demand Patterns)
Agent reads ONLY when needed for current query:
- `.claude/.context/code-examples/ctgov_markdown_parsing.md` - CT.gov markdown parsing
- `.claude/.context/code-examples/fda_json_parsing.md` - FDA JSON parsing
- `.claude/.context/code-examples/multi_server_query.md` - Combining servers
- `.claude/.context/code-examples/skills_library_pattern.md` - Skills best practices

**Benefit**: Load 0-2 examples per query instead of all examples always.

### Reference Skills (Pattern Discovery)
Agent discovers and reuses patterns from existing skills:
1. User asks for new data (e.g., "Get ADC trials")
2. Agent checks `.claude/skills/index.json` for similar implementations
3. Agent reads reference skill (e.g., `get_glp1_trials.py`)
4. Agent applies proven patterns (pagination, parsing, error handling)
5. New skill follows same battle-tested structure

**Skills Index** contains:
- Patterns demonstrated by each skill (pagination, markdown_parsing, etc.)
- Best reference skills for each pattern
- Quick discovery without reading all 68 skill files

---

## Quick Start

### 1. Simple Data Query

```bash
# Example queries:
"What GLP-1 drugs are approved for diabetes?"
"How many KRAS inhibitor trials are ongoing?"
"Get Abbott's latest segment financials from SEC"
```

**System Flow**:
1. Research agent invoked
2. Agent reads relevant MCP tool guide + code example
3. Agent generates Python code
4. Code executes via Bash tool
5. Summary displayed, skill saved to `.claude/skills/`

### 2. Strategic Analysis

```bash
# Example:
"Analyze BRAF inhibitor competitive landscape"
```

**System Flow**:
1. Main agent reads competitive-landscape-analyst metadata
2. Main agent identifies required data: trials + FDA drugs
3. Main agent checks/creates/executes skills
4. Main agent invokes strategic agent with collected data
5. Strategic agent returns analysis
6. Report saved to `reports/competitive-landscape/`

### 3. Multi-Domain Research

```bash
# Example:
"Complete Alzheimer's disease intelligence report"
```

**System Flow**:
1. Agent identifies data needs across domains
2. Collects: WHO burden + CT.gov trials + FDA drugs + Open Targets genetics + Data Commons demographics
3. Executes 5+ skills in parallel
4. Synthesizes multi-source intelligence
5. Returns comprehensive report

---

## Directory Structure

```
.claude/
├── CLAUDE.md                           # Architecture documentation
├── .context/                           # Documentation & guides
│   ├── code-examples/                  # Code patterns (7 patterns)
│   ├── mcp-tool-guides/                # MCP server docs (12 servers)
│   ├── templates/                      # Report templates
│   └── implementation-plans/           # Technical design docs
├── agents/                             # Agent definitions (2 agents)
│   ├── pharma-search-specialist.md     # Data collection agent
│   └── competitive-landscape-analyst.md # Strategic analysis agent
├── tools/                              # Platform utilities
│   ├── skill_discovery/                # 4-level discovery system
│   │   ├── index_query.py              # Level 1: Fast index queries
│   │   ├── health_check.py             # Level 2: Health verification
│   │   ├── semantic_matcher.py         # Level 3: Semantic matching
│   │   ├── strategy.py                 # Level 4: Strategy decisions
│   │   └── index_updater.py            # Index maintenance
│   ├── verification/                   # Closed-loop verification
│   │   └── verify_skill.py             # Autonomous skill verification
│   ├── discover_skills.py              # Skill discovery CLI
│   ├── init_skill.py                   # Skill scaffolding
│   ├── package_skill.py                # Structure migration
│   └── parse_skill_metadata.py         # Frontmatter parsing
├── mcp/                                # MCP infrastructure
│   ├── client.py                       # MCP client (JSON-RPC)
│   └── servers/                        # Python function wrappers (12 servers)
└── skills/                             # Skills library (68 skills)
    ├── index.json                      # Skills discovery index
    ├── README.md                       # Skills documentation
    └── [skill-folders]/                # Anthropic folder structure

reports/                                # Strategic analysis reports (version controlled)
├── competitive-landscape/
│   └── YYYY-MM-DD_topic.md
├── clinical-strategy/
└── regulatory-analysis/
```

---

## Design Principles

1. **Code Execution Pattern**: Anthropic's proven pattern for 98.7% token reduction
2. **Progressive Disclosure**: Load only docs/examples needed for current query
3. **Skills Library**: Reusable functions that grow organically with use
4. **In-Memory Processing**: Data processed in execution environment, never in context
5. **Metadata-Driven**: Strategic agents declare data needs via YAML frontmatter
6. **Single Source of Truth**: No duplication across documentation files
7. **Intelligent Discovery**: 4-level system for optimal skill reuse (REUSE > ADAPT > CREATE)

---

## Data Output Strategy

### In-Memory Processing (Default)
- Code processes data in execution environment
- Only summary printed to conversation (500 tokens)
- No files saved
- **98.7% token reduction benefit**

### Skills Persistence (Always)
- All data collection functions saved to `.claude/skills/`
- Folder structure: `skill-name/SKILL.md` + `scripts/function.py`
- YAML frontmatter for intelligent discovery
- Reusable across sessions

### Report Persistence (Strategic Analyses)
- Strategic agent reports saved to `reports/{agent_type}/`
- Version controlled (shows evolution over time)
- YAML frontmatter with metadata
- Templates in `.claude/.context/templates/`

**Rule**: Default to in-memory unless user requests export or runs strategic analysis.

---

## Contributing

### New MCP Servers

1. Add server configuration to `.mcp.json`
2. Create Python wrapper in `.claude/mcp/servers/[server_name]/`
3. Write API documentation in `.claude/.context/mcp-tool-guides/[server].md`
4. Update `.claude/CLAUDE.md` and `README.md`

### New Skills

**Recommended**: Simply ask the research agent to create the skill:

```
"Get [data type] from [source]"
"Find [entity] in [database]"
```

The agent will:
1. Generate working Python code
2. Execute and validate results
3. Save complete skill with documentation
4. Skill is immediately reusable in future queries

**For manual scaffolding** (creates empty templates only):
```bash
python3 .claude/tools/init_skill.py skill_name --server server_name
```

### New Agents

1. Create agent definition in `.claude/agents/[agent-name].md`
2. Use YAML frontmatter for metadata
3. Define data requirements in `data_requirements` section
4. Implement agent logic following existing patterns
5. Update `.claude/CLAUDE.md` and `README.md`

---

## Agent Roadmap

**Current Status:** 2 agents operational
- **pharma-search-specialist**: Infrastructure agent for data collection
- **competitive-landscape-analyst**: Strategic agent for competitive intelligence

**Expansion Strategy:** Multi-vertical approach with specialized agents

### Healthcare & Life Sciences Vertical
**80+ planned agents across drug development lifecycle:**

| Domain | Agent Capabilities |
|--------|-------------------|
| **Discovery & Target ID** | Target identification, validation, druggability, MOA analysis |
| **Drug Discovery** | Medicinal chemistry, HTS, fragment-based screening, DMPK/ADME |
| **Preclinical** | Study design, toxicology, regulatory strategy, timeline optimization |
| **Clinical Development** | Protocol design, clinical operations, biomarker strategy |
| **Regulatory Affairs** | Pathway analysis, precedent analysis, label strategy, AdComm prep |
| **Manufacturing & CMC** | CMC strategy, formulation, manufacturing assessment |
| **Medical Affairs** | KOL strategy, publication planning, medical communications |
| **Market Access** | HTA/cost-effectiveness, pricing, reimbursement optimization |

### Financial Research Vertical
**Potential agents:**
- SEC filing analyzer and sentiment tracker
- Earnings call analyzer with market impact
- Economic indicator monitor (FRED dashboard)
- M&A pattern identifier and deal predictor
- Stock-trial outcome correlation analyzer
- Biotech company comparison engine

### Public Health & Policy Vertical
**Potential agents:**
- Disease surveillance system (WHO + Data Commons)
- Health system capacity analyzer (CMS + providers)
- Intervention impact assessor (burden + outcomes)
- Resource allocation optimizer (providers + demographics)
- Outbreak predictor (epidemiology + trends)
- Policy recommendation engine

### Academic & IP Research Vertical
**Potential agents:**
- Literature synthesizer (PubMed + citations)
- Patent trend analyzer (USPTO + filing patterns)
- Technology forecaster (patents + papers + trials)
- Grant opportunity finder (funding + fit scoring)
- Collaboration matcher (expertise + gaps)
- Innovation scout (cross-domain technology tracking)

### Cross-Domain Strategic Agents
**Multi-source intelligence synthesis:**
- Investment due diligence agent (clinical + financial + regulatory + IP)
- Policy impact assessor (burden + systems + economics + outcomes)
- Innovation scout (patents + papers + trials + markets + adoption)
- Partnership opportunity finder (asset gaps + complementary capabilities)
- Technology transfer agent (academic → commercial readiness)

---

### Request a New Agent

Have a specific research workflow or analysis need? **[Open an issue](https://github.com/uh-joan/pharma-agentic-os/issues/new)** with:
- **Use case**: What problem does this agent solve?
- **Inputs**: What data sources does it need?
- **Outputs**: What analysis or deliverables should it produce?
- **Domain**: Healthcare, Finance, Policy, Research, or Cross-Domain?

We prioritize agents based on:
- Frequency of use across research workflows
- Availability of required MCP data sources
- Community interest and contributions
- Cross-domain applicability

---

## Links

- **Anthropic Code Execution Pattern**: https://www.anthropic.com/engineering/code-execution-with-mcp
- **Model Context Protocol**: https://modelcontextprotocol.io
- **Claude Code**: https://claude.com/claude-code
