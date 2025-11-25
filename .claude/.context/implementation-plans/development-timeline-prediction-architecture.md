# Development Timeline Prediction - Architecture Plan

**Capability**: Development timeline prediction using historical success rates and company patterns
**Agent**: competitive-landscape-analyst
**Created**: 2025-11-24
**Priority**: High-value strategic capability

---

## Executive Summary

Build a predictive system for drug development timelines leveraging:
- **Historical success rates** (phase transition probabilities by indication/company)
- **Statistical models** (Bayesian inference, survival analysis, Monte Carlo simulation)
- **Company-specific patterns** (development velocity, regulatory strategy)
- **Real-time data** from CT.gov, FDA, SEC Edgar

**Target Use Case**: "What's the probability Compound X reaches approval by 2028, given it's in Phase 2 for oncology?"

---

## Data Sources & Available Fields

### ClinicalTrials.gov (ct_gov_mcp)
- ✅ Study start dates (`start`)
- ✅ Primary completion dates (`primComp`)
- ✅ Study completion dates (`studyComp`)
- ✅ First posted dates (`firstPost`)
- ✅ Last update dates (`lastUpdPost`)
- ✅ Phase information (`PHASE1`, `PHASE2`, `PHASE3`)
- ✅ Status (`recruiting`, `completed`, `terminated`, `withdrawn`)
- ✅ Sponsor/company (`lead`)
- ✅ Intervention/drug names
- ✅ Condition/therapeutic area
- ✅ Results posted dates (`resFirstPost`)

**What we can calculate:**
- Phase durations (Phase 2 start → Phase 3 start)
- Success rates (% of Phase 2 trials that reach Phase 3)
- Company velocity (median phase duration by sponsor)
- Indication benchmarks (median duration by therapeutic area)
- Termination rates and reasons

### FDA (fda_mcp)
- ✅ Drug approval dates
- ✅ Submission dates
- ✅ Breakthrough therapy designations (BTD)
- ✅ Fast track designations
- ✅ Priority review status
- ✅ Accelerated approval pathways
- ✅ Indication/therapeutic area

**What we can calculate:**
- Review timelines (submission → approval)
- Regulatory pathway impact (BTD reduces timeline by ~X months)
- Approval success rates by indication

### SEC Edgar (sec_edgar_mcp)
- ✅ Company R&D spending (proxy for development capacity)
- ✅ Company financials (runway, burn rate)

**What we can correlate:**
- R&D spend vs development velocity
- Financial health vs trial success rates

### PubMed (pubmed_mcp)
- ✅ Publication dates
- ✅ Clinical results publications

**What we can use:**
- Publication as signal of phase completion
- Time from trial completion → publication

### OpenTargets (opentargets_mcp)
- ✅ Target-disease associations
- ✅ Genetic evidence scores

**What we can predict:**
- Target validation strength → success probability

---

## Skill Architecture

### Layer 1: Foundation Data Collection Skills

#### 1.1 Historical Phase Transition Analysis
**Skill**: `get_historical_phase_transitions`

**Function**: Extract historical trial data to calculate phase transition probabilities

**Algorithm**:
```python
def get_historical_phase_transitions(therapeutic_area=None, company=None, date_range=None):
    """
    Calculate phase transition probabilities from historical CT.gov data.

    Methodology:
    1. Query completed/terminated trials from CT.gov
    2. Identify phase transitions (match by drug/intervention name)
    3. Calculate transition matrix:
       - P(Phase 2 | Phase 1 success)
       - P(Phase 3 | Phase 2 success)
       - P(Approval | Phase 3 success)
    4. Segment by therapeutic area, company, biomarker use

    Returns:
    {
        'transition_probabilities': {
            'phase1_to_phase2': 0.595,
            'phase2_to_phase3': 0.355,
            'phase3_to_approval': 0.62
        },
        'by_therapeutic_area': {...},
        'by_company': {...},
        'sample_size': 1523
    }
    """
```

**Data Strategy**:
- Use CT.gov `complexQuery` to filter by phase, status, therapeutic area
- Match trials by intervention name across phases (heuristic matching)
- Filter for completed trials with known outcomes (status = `completed` or `terminated`)

**Servers**: `ct_gov_mcp`, `fda_mcp` (for approval confirmation)

**Complexity**: High (requires trial matching across phases)

---

#### 1.2 Company Development Velocity
**Skill**: `get_company_development_velocity`

**Function**: Calculate company-specific development speed and patterns

**Algorithm**:
```python
def get_company_development_velocity(company_name):
    """
    Calculate median phase durations for a specific company.

    Methodology:
    1. Query all trials by sponsor (lead parameter)
    2. Calculate phase durations:
       - Phase 1: start → primary_completion
       - Phase 2: start → primary_completion
       - Phase 3: start → primary_completion
    3. Calculate percentiles (25th, 50th, 75th)
    4. Identify regulatory strategy:
       - % with Breakthrough Therapy Designation
       - % with Fast Track
       - Geographic preferences (US-first vs global)

    Returns:
    {
        'company': 'Pfizer',
        'phase_durations': {
            'phase1': {'median': 18, 'p25': 12, 'p75': 24},  # months
            'phase2': {'median': 24, 'p25': 18, 'p75': 36},
            'phase3': {'median': 36, 'p25': 24, 'p75': 48}
        },
        'regulatory_patterns': {
            'btd_usage_rate': 0.23,
            'fast_track_rate': 0.45,
            'priority_review_rate': 0.34
        },
        'success_rates': {
            'phase1_to_phase2': 0.65,
            'phase2_to_phase3': 0.42,
            'phase3_to_approval': 0.71
        },
        'sample_size': 127
    }
    """
```

**Data Strategy**:
- CT.gov: Filter by `lead` sponsor, extract date fields
- FDA: Match company drugs to identify regulatory designations
- Calculate durations: `primComp - start` or `studyComp - start`

**Servers**: `ct_gov_mcp`, `fda_mcp`

**Complexity**: Medium (straightforward date math, some matching)

---

#### 1.3 Therapeutic Area Benchmarks
**Skill**: `get_therapeutic_area_timeline_benchmarks`

**Function**: Calculate industry benchmarks for specific indications

**Algorithm**:
```python
def get_therapeutic_area_timeline_benchmarks(therapeutic_area):
    """
    Calculate industry-standard timelines and success rates for an indication.

    Methodology:
    1. Query CT.gov for condition (e.g., "diabetes", "oncology")
    2. Segment by phase
    3. Calculate benchmark statistics:
       - Median duration per phase
       - Success rates (% reaching next phase)
       - Recent trends (2020+ vs 2015-2019)
    4. Incorporate published literature benchmarks

    Returns:
    {
        'therapeutic_area': 'Oncology',
        'benchmarks': {
            'phase1': {'median_months': 18, 'success_rate': 0.48},
            'phase2': {'median_months': 24, 'success_rate': 0.35},
            'phase3': {'median_months': 36, 'success_rate': 0.62}
        },
        'overall_success_rate': 0.051,  # Phase 1 → Approval
        'trend': 'improving',  # vs historical
        'sample_size': 3421,
        'data_quality': 'high',
        'literature_benchmarks': {
            'source': 'Nature Communications 2024',
            'overall_loa': 0.051  # Literature of Approval
        }
    }
    """
```

**Data Strategy**:
- CT.gov: Query by `condition`, segment by `phase`
- Integrate published benchmarks (hardcode from literature)
- Calculate temporal trends (recent vs historical)

**Servers**: `ct_gov_mcp`, `fda_mcp`

**Complexity**: Medium

---

#### 1.4 Regulatory Pathway Impact
**Skill**: `get_regulatory_pathway_impact`

**Function**: Calculate timeline acceleration from regulatory designations

**Algorithm**:
```python
def get_regulatory_pathway_impact():
    """
    Calculate median timeline reduction from regulatory designations.

    Methodology:
    1. FDA data: Identify drugs with BTD, Fast Track, Priority Review
    2. CT.gov: Match to trials, calculate timelines
    3. Compare: Designated vs non-designated
    4. Calculate median difference

    Returns:
    {
        'breakthrough_therapy': {
            'median_reduction_months': 6,
            'approval_rate_lift': 0.12  # 12% higher approval rate
        },
        'fast_track': {
            'median_reduction_months': 3,
            'approval_rate_lift': 0.08
        },
        'priority_review': {
            'median_reduction_months': 2,
            'approval_rate_lift': 0.05
        },
        'accelerated_approval': {
            'median_reduction_months': 4,
            'conditional': True  # May require confirmatory trials
        }
    }
    """
```

**Data Strategy**:
- FDA: Query designated drugs, extract approval timelines
- CT.gov: Match trials, calculate phase durations
- Statistical comparison (designated vs control)

**Servers**: `fda_mcp`, `ct_gov_mcp`

**Complexity**: Medium-High (requires matching FDA drugs ↔ CT.gov trials)

---

### Layer 2: Statistical Analysis Skills

#### 2.1 Bayesian Success Probability
**Skill**: `calculate_phase_transition_probability`

**Function**: Calculate probability of reaching next phase using Bayesian inference

**Algorithm**:
```python
def calculate_phase_transition_probability(
    current_phase,
    therapeutic_area,
    company=None,
    has_biomarker=False,
    has_btd=False,
    target_validation_score=None
):
    """
    Bayesian calculation of phase transition probability.

    Methodology:
    1. Prior: Industry baseline (from get_therapeutic_area_benchmarks)
    2. Update with company-specific data (if available)
    3. Adjust for factors:
       - Biomarker use: +17.5% (literature: 25.9% vs 8.4%)
       - BTD designation: +12%
       - Target validation score: correlation from OpenTargets
    4. Bayesian update: P(success | evidence)

    Formula:
    P(Phase_n+1 | Phase_n, evidence) =
        P_baseline × Π adjustment_factors × bayesian_update

    Returns:
    {
        'transition_probability': 0.42,  # 42% chance
        'confidence_interval': [0.35, 0.49],  # 90% CI
        'factors': {
            'baseline': 0.355,  # Industry average
            'company_adjustment': 1.18,  # Company 18% better
            'biomarker_boost': 1.175,
            'btd_boost': 1.12
        },
        'methodology': 'bayesian_inference',
        'evidence_strength': 'medium'  # Based on sample size
    }
    """
```

**Dependencies**:
- `get_historical_phase_transitions` (baseline priors)
- `get_company_development_velocity` (company adjustment)
- `get_therapeutic_area_timeline_benchmarks` (indication baseline)

**Servers**: None (pure calculation on collected data)

**Complexity**: Medium (Bayesian math, but straightforward)

---

#### 2.2 Phase Duration Statistics
**Skill**: `calculate_phase_duration_statistics`

**Function**: Statistical analysis of phase durations with confidence intervals

**Algorithm**:
```python
def calculate_phase_duration_statistics(
    phase,
    therapeutic_area,
    company=None
):
    """
    Calculate expected phase duration with statistical confidence.

    Methodology:
    1. Collect historical durations (from CT.gov)
    2. Fit distribution (log-normal is typical for trial durations)
    3. Calculate percentiles (10th, 25th, 50th, 75th, 90th)
    4. Apply adjustments:
       - Company velocity factor
       - Regulatory pathway acceleration
       - Recent trend adjustment (2020+ vs historical)

    Returns:
    {
        'phase': 'PHASE2',
        'expected_duration_months': 24,
        'percentiles': {
            'p10': 12,  # Fastest 10%
            'p25': 18,
            'p50': 24,  # Median
            'p75': 32,
            'p90': 42   # Slowest 10%
        },
        'distribution': 'log-normal',
        'parameters': {'mu': 3.2, 'sigma': 0.5},
        'adjustments_applied': {
            'company_velocity': 0.92,  # 8% faster than average
            'regulatory': 0.85  # 15% faster with BTD
        },
        'confidence': 'high',  # Based on sample size
        'sample_size': 847
    }
    """
```

**Dependencies**:
- `get_therapeutic_area_timeline_benchmarks`
- `get_company_development_velocity`
- `get_regulatory_pathway_impact`

**Servers**: None (calculation only)

**Complexity**: Medium (statistical modeling)

---

#### 2.3 Monte Carlo Timeline Simulation
**Skill**: `simulate_development_timeline`

**Function**: Monte Carlo simulation for probabilistic timeline ranges

**Algorithm**:
```python
def simulate_development_timeline(
    current_phase,
    therapeutic_area,
    company=None,
    has_biomarker=False,
    has_btd=False,
    n_simulations=10000
):
    """
    Monte Carlo simulation for development timeline prediction.

    Methodology:
    1. For each simulation run (10,000 iterations):
       a. Sample phase durations from fitted distributions
       b. Sample success/failure at each phase transition
       c. If failure: terminate, record time-to-failure
       d. If success all phases: record time-to-approval
    2. Aggregate results:
       - Probability of approval
       - Time distribution (if successful)
       - Most likely failure point
    3. Generate scenarios (best/expected/worst case)

    Returns:
    {
        'approval_probability': 0.38,  # 38% reach approval
        'timeline_if_successful': {
            'p10': 36,  # months (best case)
            'p50': 54,  # months (expected)
            'p90': 78   # months (worst case)
        },
        'expected_approval_date': '2028-Q3',
        'confidence_interval_90pct': ['2027-Q4', '2029-Q2'],
        'failure_analysis': {
            'phase2_failure_prob': 0.35,
            'phase3_failure_prob': 0.22,
            'approval_failure_prob': 0.05
        },
        'scenarios': {
            'best_case': {'timeline': 36, 'probability': 0.10},
            'expected': {'timeline': 54, 'probability': 0.50},
            'worst_case': {'timeline': 78, 'probability': 0.10}
        },
        'methodology': 'monte_carlo',
        'n_simulations': 10000
    }
    """
```

**Dependencies**:
- `calculate_phase_transition_probability` (success probabilities)
- `calculate_phase_duration_statistics` (duration distributions)

**Servers**: None (simulation based on collected data)

**Complexity**: High (Monte Carlo simulation, requires numpy/scipy)

---

### Layer 3: Main Orchestrator Skill

#### 3.1 Development Timeline Predictor
**Skill**: `predict_development_timeline`

**Function**: Main orchestrator that combines all sub-skills for comprehensive prediction

**Algorithm**:
```python
def predict_development_timeline(
    drug_name=None,
    current_phase='PHASE2',
    therapeutic_area='Oncology',
    company=None,
    has_biomarker=False,
    has_btd=False,
    target_validation_score=None,
    current_date='2025-11-24'
):
    """
    Comprehensive development timeline prediction.

    Workflow:
    1. Collect foundational data:
       - Historical phase transitions
       - Company velocity patterns
       - Therapeutic area benchmarks
       - Regulatory pathway impacts

    2. Calculate probabilities:
       - Phase transition probabilities (Bayesian)
       - Expected phase durations (statistical)

    3. Run simulation:
       - Monte Carlo timeline simulation (10,000 runs)
       - Generate probabilistic outcomes

    4. Return comprehensive prediction

    Returns:
    {
        'drug': 'Compound-X',
        'current_phase': 'PHASE2',
        'therapeutic_area': 'Oncology',
        'company': 'Pfizer',

        'approval_probability': 0.38,

        'timeline_prediction': {
            'expected_approval_date': '2028-Q3',
            'confidence_90pct': ['2027-Q4', '2029-Q2'],
            'best_case': '2027-Q2',
            'worst_case': '2030-Q1'
        },

        'phase_probabilities': {
            'phase2_to_phase3': 0.42,
            'phase3_to_submission': 0.71,
            'submission_to_approval': 0.92
        },

        'phase_durations_expected': {
            'phase2_remaining': 18,  # months
            'phase3': 30,
            'fda_review': 10
        },

        'risk_factors': [
            'Oncology has low success rate (5.1% overall)',
            'Phase 2→3 transition is critical bottleneck (35% success)'
        ],

        'success_factors': [
            'Company has 18% faster velocity than industry',
            'BTD designation provides 6-month acceleration',
            'Biomarker use increases success rate 17.5%'
        ],

        'comparable_programs': [
            {'drug': 'Similar-Drug-A', 'outcome': 'approved', 'timeline': 56},
            {'drug': 'Similar-Drug-B', 'outcome': 'failed_phase3', 'timeline': 42}
        ],

        'recommendations': [
            'Pursue Breakthrough Therapy Designation (increases probability 12%)',
            'Enroll biomarker-selected population (increases success 17.5%)',
            'Monitor Phase 2→3 transition closely (35% historical success rate)'
        ],

        'methodology': {
            'approach': 'bayesian_monte_carlo',
            'data_sources': ['ct_gov', 'fda', 'literature'],
            'simulations': 10000,
            'confidence_level': 0.90
        },

        'data_quality': {
            'company_sample_size': 127,
            'indication_sample_size': 3421,
            'data_recency': '2020-2024',
            'confidence': 'high'
        }
    }
    """
```

**Dependencies** (calls all foundation and analysis skills):
1. `get_historical_phase_transitions`
2. `get_company_development_velocity`
3. `get_therapeutic_area_timeline_benchmarks`
4. `get_regulatory_pathway_impact`
5. `calculate_phase_transition_probability`
6. `calculate_phase_duration_statistics`
7. `simulate_development_timeline`

**Servers**: None directly (orchestrates other skills)

**Complexity**: High (orchestration + integration)

---

## Implementation Priority

### Phase 1: Foundation (Weeks 1-2)
**Priority**: Critical path

1. ✅ **`get_therapeutic_area_timeline_benchmarks`**
   - Simplest to implement (straightforward CT.gov queries)
   - Provides baseline for all other calculations
   - Can hardcode literature benchmarks initially

2. ✅ **`get_company_development_velocity`**
   - Medium complexity, high value
   - Enables company-specific predictions
   - Date math on CT.gov data

3. ⚠️ **`get_historical_phase_transitions`**
   - Hardest foundation skill (requires trial matching)
   - Consider simplification: use literature benchmarks initially
   - Can build matching heuristics iteratively

### Phase 2: Analysis (Week 3)
**Priority**: Core algorithms

4. ✅ **`calculate_phase_duration_statistics`**
   - Statistical modeling, medium complexity
   - Depends on foundation skills

5. ✅ **`calculate_phase_transition_probability`**
   - Bayesian inference, medium complexity
   - Can use simplified priors initially

### Phase 3: Simulation (Week 4)
**Priority**: Advanced capability

6. ✅ **`simulate_development_timeline`**
   - Monte Carlo simulation
   - Requires numpy/scipy
   - High value for probabilistic predictions

### Phase 4: Orchestration (Week 5)
**Priority**: Integration

7. ✅ **`predict_development_timeline`**
   - Main orchestrator
   - Integrates all skills
   - High-level API for competitive-landscape-analyst

### Phase 5: Enhancements (Week 6+)
**Priority**: Optional improvements

8. ⚠️ **`get_regulatory_pathway_impact`** (if time permits)
   - Calculate BTD/Fast Track impact empirically
   - Initially can use literature values

9. 🔮 **Machine Learning Extensions** (future)
   - Train ML models on historical data
   - Feature engineering (target validation, biomarkers, etc.)
   - Gradient boosting for timeline prediction

---

## Statistical Methodologies Detail

### 1. Bayesian Hierarchical Model
**Use**: Phase transition probability calculation

**Hierarchy**:
```
Level 1: Overall industry baseline (published literature)
    ↓
Level 2: Therapeutic area adjustment
    ↓
Level 3: Company-specific adjustment
    ↓
Level 4: Drug-specific factors (biomarker, BTD, etc.)
```

**Formula**:
```
P(success | evidence) = P(success) × Π(adjustment_factors)

Where:
- P(success) = industry baseline (e.g., 0.355 for Phase 2→3)
- adjustment_factors = [company_factor, biomarker_factor, btd_factor, ...]
```

**Implementation**: Simple multiplicative model (can enhance to full Bayesian later)

---

### 2. Survival Analysis (Kaplan-Meier)
**Use**: Phase duration modeling with censored data

**Why**: Many trials are ongoing (censored data) - survival analysis handles this

**Approach**:
```python
from lifelines import KaplanMeierFitter

# Fit survival curve for Phase 2 duration
kmf = KaplanMeierFitter()
kmf.fit(durations, event_observed)  # event = trial completion

median_duration = kmf.median_survival_time_
```

**Application**: Calculate median phase duration accounting for ongoing trials

---

### 3. Monte Carlo Simulation
**Use**: Probabilistic timeline prediction with uncertainty

**Algorithm**:
```python
for i in range(10000):
    success_phase2 = random.random() < p_phase2_success
    if not success_phase2:
        record_failure('phase2', time)
        continue

    duration_phase2 = sample_from_distribution(phase2_dist)

    success_phase3 = random.random() < p_phase3_success
    if not success_phase3:
        record_failure('phase3', time + duration_phase2)
        continue

    duration_phase3 = sample_from_distribution(phase3_dist)
    duration_review = sample_from_distribution(review_dist)

    total_time = duration_phase2 + duration_phase3 + duration_review
    record_success(total_time)
```

**Output**: Distribution of possible timelines, approval probability

---

### 4. Regression Analysis (Future Enhancement)
**Use**: Predict timeline based on multiple features

**Features**:
- Target validation score (OpenTargets)
- Company R&D spend (SEC Edgar)
- Prior approval history
- Therapeutic area
- Endpoint complexity (mortality vs surrogate)
- Geographic strategy (US-only vs global)

**Models**:
- Random Forest (feature importance analysis)
- Gradient Boosting (highest accuracy)
- Cox Proportional Hazards (time-to-event with covariates)

---

## Literature Benchmarks (To Hardcode)

### Overall Success Rates (Phase I → Approval)
```python
LITERATURE_BENCHMARKS = {
    'overall': 0.096,  # 9.6% (Biostatistics 2019)
    'oncology': 0.051,  # 5.1% (Nature Comms 2024)
    'hematology': 0.261,  # 26.1% (Biostatistics 2019)
    'infectious_disease': 0.196,
    'ophthalmology': 0.187,
    'cardiovascular': 0.132,
    'metabolic': 0.115
}
```

### Phase Transition Probabilities
```python
PHASE_TRANSITIONS = {
    'phase1_to_phase2': 0.595,
    'phase2_to_phase3': 0.355,
    'phase3_to_submission': 0.620,
    'submission_to_approval': 0.904
}
```

### Regulatory Pathway Impact (Literature)
```python
REGULATORY_IMPACT = {
    'breakthrough_therapy': {
        'timeline_reduction_months': 6,
        'approval_rate_lift': 0.12
    },
    'fast_track': {
        'timeline_reduction_months': 3,
        'approval_rate_lift': 0.08
    },
    'biomarker_selection': {
        'approval_rate_boost': 0.175  # 25.9% vs 8.4% = 17.5% lift
    }
}
```

**Sources**:
- Biostatistics (2019): Thomas, Wong et al.
- Nature Communications (2024): Dynamic clinical trial success rates
- BIO Industry Report (2024): Clinical development success rates

---

## Technical Considerations

### Libraries Required
```python
# Statistical analysis
import numpy as np
import scipy.stats as stats
from scipy.stats import lognorm

# Survival analysis (optional, for advanced features)
# from lifelines import KaplanMeierFitter

# Date handling
from datetime import datetime, timedelta
import re
```

### Data Quality Challenges

1. **Trial Matching Across Phases**
   - **Problem**: Same drug may have different names in Phase 1 vs Phase 2
   - **Solution**: Fuzzy matching on intervention names, sponsor matching
   - **Fallback**: Use aggregated statistics (don't match individual trials)

2. **Censored Data (Ongoing Trials)**
   - **Problem**: Many trials are still ongoing
   - **Solution**: Survival analysis methods OR filter to completed only
   - **Impact**: May bias toward faster timelines if using completed only

3. **Company Name Variations**
   - **Problem**: "Pfizer Inc" vs "Pfizer" vs "Wyeth" (acquired)
   - **Solution**: Company name normalization, parent company mapping

4. **Therapeutic Area Classification**
   - **Problem**: "NSCLC" vs "Non-Small Cell Lung Cancer" vs "Oncology"
   - **Solution**: Multi-level hierarchy (specific → general)

### Performance Optimization

1. **Caching Strategy**
   - Cache historical benchmark data (changes slowly)
   - Cache company velocity (update monthly)
   - Don't cache current trial status (changes frequently)

2. **Query Optimization**
   - Use CT.gov `complexQuery` for single-query filtering
   - Use `pageSize=100` for pagination efficiency
   - Filter by date range to limit data volume

3. **Computation Strategy**
   - Pre-compute benchmarks (one-time setup)
   - Monte Carlo: 10,000 simulations (~1-2 seconds)
   - Parallelize if needed (but likely fast enough single-threaded)

---

## Integration with competitive-landscape-analyst

### Agent Metadata Addition
Add to `.claude/agents/competitive-landscape-analyst.md`:

```yaml
capabilities:
  - ...existing capabilities...
  - timeline_prediction:
      description: "Predict development timelines using historical success rates"
      triggers: ["timeline", "when will", "approval date", "probability"]
      skills_required:
        - predict_development_timeline

data_requirements:
  contextual:
    - type: timeline_prediction
      pattern: predict_development_timeline
      trigger: keywords("timeline", "when", "approval date", "probability of success")
```

### Usage Example
```
User: "When will Pfizer's KRAS inhibitor likely get approved?"

Main Agent:
1. Infers: therapeutic_area = "Oncology", company = "Pfizer", current_phase = (query CT.gov)
2. Checks/creates: predict_development_timeline skill
3. Executes: predict_development_timeline(
     therapeutic_area="Oncology",
     company="Pfizer",
     current_phase="PHASE2",
     has_biomarker=True
   )
4. Returns: "Based on historical data, Pfizer's KRAS inhibitor has a 38% probability
            of approval, with expected approval in Q3 2028 (90% CI: Q4 2027 - Q2 2029)"
```

---

## Success Metrics

**Validation Approach**:
1. **Historical backtesting**:
   - Take trials from 2015-2018
   - Predict their approval dates/probabilities
   - Compare to actual outcomes (2018-2024)
   - Calculate prediction error (MAE, RMSE)

2. **Benchmark against literature**:
   - Our calculated success rates should match published benchmarks
   - Phase transition probabilities: ±5% of literature values
   - Phase durations: ±3 months of literature medians

3. **Uncertainty calibration**:
   - 90% confidence intervals should contain actual outcome 90% of time
   - Check for over/under-confidence

**Target Accuracy**:
- Timeline prediction: ±6 months (median absolute error)
- Success probability: ±10% (e.g., predict 40%, actual 35-45%)
- Phase transition: ±5% of literature benchmarks

---

## Future Enhancements (Post-MVP)

1. **Machine Learning Models**
   - Train gradient boosting on features: target validation, biomarkers, endpoints
   - Feature importance: which factors most predict success?
   - Automated feature engineering

2. **Real-World Evidence Integration**
   - Publication velocity as signal (PubMed)
   - Patent activity as early signal (USPTO)
   - Conference presentation patterns

3. **Competitive Intelligence**
   - Compare multiple programs side-by-side
   - "Which program will reach market first?"
   - Portfolio prioritization

4. **Dynamic Updates**
   - Continuous learning from new trial results
   - Automatic benchmark updates (quarterly)
   - Alert on significant deviations from predictions

5. **Economic Modeling**
   - NPV calculation (probability × market size × timeline)
   - Cost-to-approval estimation
   - Portfolio optimization

---

## Risk Assessment

**High Risk Areas**:
1. ❌ **Trial matching across phases**: Hard to match Phase 1 → Phase 2 → Phase 3
   - **Mitigation**: Use aggregated statistics initially, don't match individual trials

2. ⚠️ **Data quality**: CT.gov data may be incomplete or inconsistent
   - **Mitigation**: Use literature benchmarks as fallback, validate against known outcomes

3. ⚠️ **Small sample sizes**: Some company/indication combinations have <10 trials
   - **Mitigation**: Fall back to broader categories, report confidence level

**Medium Risk Areas**:
4. ⚠️ **Changing landscape**: Recent success rates different from historical (AI impact)
   - **Mitigation**: Weight recent data more heavily (2020+)

5. ⚠️ **Regulatory changes**: FDA policies evolve
   - **Mitigation**: Track temporal trends, flag when using older data

**Low Risk Areas**:
6. ✅ **Computational complexity**: Monte Carlo may be slow
   - **Mitigation**: 10K simulations run in <2 seconds, acceptable

7. ✅ **Library dependencies**: Minimal (numpy/scipy standard)
   - **Mitigation**: Use only standard scientific Python stack

---

## Next Steps

1. ✅ **Approve this architecture plan**
2. ⚠️ **Start with Phase 1 implementation**:
   - Create `get_therapeutic_area_timeline_benchmarks` (simplest)
   - Validate CT.gov data quality
   - Hardcode literature benchmarks
3. ⚠️ **Build foundation incrementally**:
   - Add company velocity analysis
   - Create statistical models
4. ⚠️ **Test and validate**:
   - Backtest on historical trials
   - Compare to literature benchmarks
5. ⚠️ **Integrate with competitive-landscape-analyst**

---

**Architecture Sign-off**: Ready for implementation 🚀
