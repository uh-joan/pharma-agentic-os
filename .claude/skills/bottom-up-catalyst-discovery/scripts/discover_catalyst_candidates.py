#!/usr/bin/env python3
"""
Complete Bottom-Up Catalyst Discovery Pipeline

Integrates all 6 steps to discover investable biotech companies with upcoming catalysts:
1. Extract trials with full metadata from ClinicalTrials.gov
2. Filter academic institutions
3. Lookup tickers via SEC EDGAR
4. Enrich with market cap from Yahoo Finance
5. Match companies with trial metadata (NCT ID, drug, indication, completion date)
6. Calculate catalyst confidence and prioritize (HIGH/MEDIUM/LOW)

KEY INNOVATION: Enrichment + prioritization approach (NOT filtering)
- All companies retained, regardless of data availability
- Prioritized by catalyst confidence (PDUFA > trial completion > early stage)
- Ready for future enrichment (abstracts, company events, etc.)

OUTPUT: ~65 investable public biotechs with detailed trial metadata and confidence scoring
"""

import sys
import json
import time
from typing import List, Dict, Optional
from pathlib import Path

sys.path.insert(0, ".claude")

# Import individual step functions from same directory
import importlib.util

# Get current script directory
script_dir = Path(__file__).parent

# Load step1 - Trial metadata extraction
step1_spec = importlib.util.spec_from_file_location("step1", script_dir / "step1_extract_trials_with_metadata.py")
step1_module = importlib.util.module_from_spec(step1_spec)
step1_spec.loader.exec_module(step1_module)
get_trials_by_quarter_with_metadata = step1_module.get_trials_by_quarter_with_metadata

# Load step2
step2_spec = importlib.util.spec_from_file_location("step2", script_dir / "step2_filter_academic.py")
step2_module = importlib.util.module_from_spec(step2_spec)
step2_spec.loader.exec_module(step2_module)
filter_academic_institutions = step2_module.filter_academic_institutions

# Load step3
step3_spec = importlib.util.spec_from_file_location("step3", script_dir / "step3_lookup_ticker.py")
step3_module = importlib.util.module_from_spec(step3_spec)
step3_spec.loader.exec_module(step3_module)
lookup_tickers_batch = step3_module.lookup_tickers_batch

# Load step5
step5_spec = importlib.util.spec_from_file_location("step5", script_dir / "step5_enrich_market_cap.py")
step5_module = importlib.util.module_from_spec(step5_spec)
step5_spec.loader.exec_module(step5_module)
enrich_companies_with_market_cap = step5_module.enrich_companies_with_market_cap

# Load step6
step6_spec = importlib.util.spec_from_file_location("step6", script_dir / "step6_enrich_catalyst_confidence.py")
step6_module = importlib.util.module_from_spec(step6_spec)
step6_spec.loader.exec_module(step6_module)
enrich_catalyst_confidence = step6_module.enrich_catalyst_confidence


def discover_catalyst_candidates(
    quarter: str = "Q4",
    year: int = 2025,
    phases: Optional[List[str]] = None,
    min_market_cap: float = 0,  # No filter - keep all public companies
    max_trials: int = 5000,
    verbose: bool = True
) -> Dict[str, any]:
    """Complete bottom-up discovery pipeline.

    Args:
        quarter: "Q1", "Q2", "Q3", or "Q4"
        year: Year (e.g., 2025)
        phases: List of trial phases (default: ["PHASE2", "PHASE3"])
        min_market_cap: Minimum market cap filter in dollars (default: $0 = no filter)
        max_trials: Maximum trials per phase to query (default: 5000)
        verbose: Print progress (default: True)

    Returns:
        dict: {
            'quarter': 'Q4 2025',
            'pipeline_stats': {
                'step1_trials_extracted': 3783,
                'step1_sponsors_extracted': 1402,
                'step2_companies_filtered': 760,
                'step3_public_companies_identified': 65,
                'step4_market_cap_enriched': 65,
                'step5_trial_metadata_enriched': 65
            },
            'investable_companies': [
                {
                    'company_name': 'AbbVie Inc.',
                    'ticker': 'ABBV',
                    'cik': '0001551152',
                    'market_cap': 300000000000,
                    'market_cap_formatted': '$300.00B',
                    'trial_count': 12,
                    'earliest_catalyst': '2025-10-15',
                    'phase_breakdown': {'PHASE3': 8, 'PHASE2': 4},
                    'trials': [
                        {
                            'nct_id': 'NCT12345678',
                            'title': 'Study of Drug X',
                            'sponsor': 'AbbVie Inc.',
                            'intervention': 'Drug X',
                            'condition': 'Cancer',
                            'phase': 'PHASE3',
                            'completion_date': '2025-10-15',
                            'status': 'RECRUITING',
                            'enrollment': '300'
                        },
                        # ... 11 more trials
                    ]
                },
                # ... 64 more companies
            ],
            'ticker_map': {...},
            'execution_time_minutes': 15.2
        }
    """
    import time
    start_time = time.time()

    if phases is None:
        phases = ["PHASE2", "PHASE3"]

    if verbose:
        print("\n" + "="*70)
        print(f"BOTTOM-UP CATALYST DISCOVERY PIPELINE: {quarter} {year}")
        print("="*70)
        print(f"\nParameters:")
        print(f"  Quarter: {quarter} {year}")
        print(f"  Phases: {phases}")
        print(f"  Min Market Cap: ${min_market_cap / 1_000_000_000:.2f}B")
        print(f"  Max Trials per Phase: {max_trials}")
        print("\n" + "="*70 + "\n")

    # ========================================
    # STEP 1: Extract Trials with Metadata from CT.gov
    # ========================================
    if verbose:
        print("\n📋 STEP 1: Extracting Trials with Metadata from ClinicalTrials.gov")
        print("-" * 70)

    step1_result = get_trials_by_quarter_with_metadata(
        quarter=quarter,
        year=year,
        phases=phases,
        max_trials=max_trials
    )

    sponsors = step1_result['unique_sponsors']
    trials_by_sponsor = step1_result['by_sponsor']  # Keep trial metadata
    all_trials = step1_result['trials']

    if verbose:
        print(f"\n✓ Step 1 Complete:")
        print(f"  Total trials: {step1_result['total_trials']}")
        print(f"  Unique sponsors: {len(sponsors)}")

    # ========================================
    # STEP 2: Filter Academic Institutions
    # ========================================
    if verbose:
        print("\n\n🏛️ STEP 2: Filtering Academic Institutions")
        print("-" * 70)

    step2_result = filter_academic_institutions(sponsors)
    companies = step2_result['companies']

    if verbose:
        print(f"\n  Total input: {step2_result['total_input']}")
        print(f"  Companies found: {step2_result['companies_found']}")
        print(f"  Academic filtered: {step2_result['academic_filtered']}")
        print(f"\n✓ Step 2 Complete: {len(companies)} potential companies")

    # ========================================
    # STEP 3: Lookup Tickers via SEC EDGAR
    # ========================================
    if verbose:
        print("\n\n🔍 STEP 3: Looking Up Stock Tickers via SEC EDGAR")
        print("-" * 70)
        print(f"\n📊 Querying SEC EDGAR for {len(companies)} companies...")
        print("⚠️  Rate limited to ~6.7 req/sec for SEC EDGAR compliance")
        est_time = (len(companies) * 0.15) / 60  # 150ms per company
        print(f"⏱️  Estimated time: ~{est_time:.1f} minutes\n")

    # Lookup tickers for all companies using SEC EDGAR
    ticker_results = lookup_tickers_batch(companies, verbose=verbose)

    # Extract companies with tickers (public companies)
    companies_with_tickers = ticker_results.get('companies_with_tickers', [])

    # Create company name → ticker mapping for later steps
    ticker_map = {
        result['company_name']: {
            'ticker': result['ticker'],
            'cik': result.get('cik'),
            'exchange': result.get('exchange'),
            'confidence': result['confidence']
        }
        for result in companies_with_tickers
    }

    if verbose:
        print(f"\n✓ Step 3 Complete:")
        print(f"  Total companies: {ticker_results['total_companies']}")
        print(f"  Public companies (tickers found): {ticker_results['tickers_found']}")
        print(f"  Private/Non-profit: {ticker_results['not_public']}")
        print(f"  Unknown: {ticker_results['no_data']}")
        print(f"  Success rate: {ticker_results['tickers_found'] / ticker_results['total_companies'] * 100:.1f}%")

    # ========================================
    # STEP 4: Market Cap Enrichment & Filtering
    # ========================================
    if verbose:
        print("\n\n💰 STEP 4: Enriching with Market Cap")
        print("-" * 70)
        print(f"\n📊 Enriching {len(companies_with_tickers)} public companies with market cap...")
        if min_market_cap > 0:
            print(f"   Minimum market cap: ${min_market_cap:,.0f}")
        else:
            print(f"   Minimum market cap: No filter (all companies retained)")
        print("⚠️  Rate limited to ~2 req/sec for Yahoo Finance\n")

    # Build companies list with tickers for enrichment
    companies_to_enrich = [
        {
            'company_name': result['company_name'],
            'ticker': result['ticker'],
            'cik': result.get('cik'),
            'exchange': result.get('exchange')
        }
        for result in companies_with_tickers
    ]

    # Enrich with market cap and filter by threshold
    step4_result = enrich_companies_with_market_cap(
        companies_to_enrich,
        min_market_cap=min_market_cap,
        verbose=verbose
    )

    investable_companies = step4_result['investable_companies']

    if verbose:
        print(f"\n✓ Step 4 Complete:")
        print(f"  Companies queried: {step4_result['total_input']}")
        print(f"  Market cap data found: {step4_result['enriched']}")
        print(f"  No market cap data: {step4_result['errors']}")
        print(f"  Below min threshold: {step4_result['failed_filter']}")
        print(f"  Investable candidates: {len(investable_companies)}")

    # ========================================
    # STEP 5: Enrich Companies with Trial Metadata
    # ========================================
    if verbose:
        print("\n\n📊 STEP 5: Enriching Companies with Trial Details")
        print("-" * 70)

    # Match each investable company with its trials
    for company in investable_companies:
        company_name = company['company_name']

        # Get trials for this company
        company_trials = trials_by_sponsor.get(company_name, [])

        # Add trial metadata to company record
        company['trial_count'] = len(company_trials)
        company['trials'] = company_trials

        # Calculate catalyst summary
        if company_trials:
            # Get earliest completion date
            completion_dates = [t.get('completion_date', '') for t in company_trials if t.get('completion_date')]
            earliest_date = min(completion_dates) if completion_dates else 'Unknown'

            # Count by phase
            phase_counts = {}
            for trial in company_trials:
                phase = trial.get('phase', 'Unknown')
                phase_counts[phase] = phase_counts.get(phase, 0) + 1

            company['earliest_catalyst'] = earliest_date
            company['phase_breakdown'] = phase_counts
        else:
            company['earliest_catalyst'] = 'Unknown'
            company['phase_breakdown'] = {}

    if verbose:
        print(f"\n✓ Step 5 Complete:")
        print(f"  Companies enriched with trial metadata: {len(investable_companies)}")

        # Show trial count distribution
        trial_counts = [c['trial_count'] for c in investable_companies]
        if trial_counts:
            print(f"  Trial count range: {min(trial_counts)}-{max(trial_counts)} per company")
            print(f"  Total catalyst events: {sum(trial_counts)}")

    # ========================================
    # STEP 6: Catalyst Confidence Enrichment & Prioritization
    # ========================================
    if verbose:
        print("\n\n🎯 STEP 6: Catalyst Confidence Enrichment & Prioritization")
        print("-" * 70)

    # Enrich with catalyst confidence and prioritize (NOT filter)
    step6_result = enrich_catalyst_confidence(
        investable_companies,
        quarter=quarter,
        year=year,
        verbose=verbose
    )

    # Get prioritized companies (sorted by confidence)
    prioritized_companies = step6_result['enriched_companies']
    companies_by_tier = step6_result['companies_by_tier']

    if verbose:
        print(f"\n✓ Step 6 Complete:")
        print(f"  HIGH confidence catalysts: {step6_result['high_confidence']} companies")
        print(f"  MEDIUM confidence catalysts: {step6_result['medium_confidence']} companies")
        print(f"  LOW confidence catalysts: {step6_result['low_confidence']} companies")
        print(f"\n  ℹ️  All companies retained, prioritized by catalyst confidence")

    # ========================================
    # FINAL SUMMARY
    # ========================================
    end_time = time.time()
    execution_time_minutes = (end_time - start_time) / 60

    if verbose:
        print("\n\n" + "="*70)
        print("PIPELINE COMPLETE")
        print("="*70)
        print(f"\n📊 Summary Statistics:")
        print(f"  Quarter: {quarter} {year}")
        print(f"  Step 1 - Trials extracted: {step1_result['total_trials']} ({len(sponsors)} sponsors)")
        print(f"  Step 2 - Companies filtered: {len(companies)}")
        print(f"  Step 3 - Public companies identified: {ticker_results['tickers_found']}")
        print(f"  Step 4 - Market cap enriched: {len(investable_companies)}")
        print(f"  Step 5 - Trial metadata enriched: {len(investable_companies)}")
        print(f"  Step 6 - Catalyst confidence enriched: {len(prioritized_companies)}")
        print(f"\n📊 Catalyst Confidence Distribution:")
        print(f"  HIGH:   {step6_result['high_confidence']} companies")
        print(f"  MEDIUM: {step6_result['medium_confidence']} companies")
        print(f"  LOW:    {step6_result['low_confidence']} companies")
        print(f"\n⏱️  Execution time: {execution_time_minutes:.1f} minutes")
        print("\n" + "="*70 + "\n")

    return {
        'quarter': f'{quarter} {year}',
        'pipeline_stats': {
            'step1_trials_extracted': step1_result['total_trials'],
            'step1_sponsors_extracted': len(sponsors),
            'step2_companies_filtered': len(companies),
            'step3_public_companies_identified': ticker_results['tickers_found'],
            'step4_market_cap_enriched': len(investable_companies),
            'step5_trial_metadata_enriched': len(investable_companies),
            'step6_catalyst_confidence_enriched': len(prioritized_companies),
            'high_confidence_catalysts': step6_result['high_confidence'],
            'medium_confidence_catalysts': step6_result['medium_confidence'],
            'low_confidence_catalysts': step6_result['low_confidence']
        },
        'investable_companies': prioritized_companies,  # Sorted by confidence
        'companies_by_tier': companies_by_tier,  # Grouped by confidence
        'ticker_map': ticker_map,
        'execution_time_minutes': execution_time_minutes
    }


# Make script executable
if __name__ == "__main__":
    # Run complete pipeline for Q4 2025
    result = discover_catalyst_candidates(
        quarter="Q4",
        year=2025,
        phases=["PHASE2", "PHASE3"],
        min_market_cap=500_000_000,
        max_trials=5000,
        verbose=True
    )

    # Display tiered results
    print("\n" + "="*70)
    print(f"🎯 {result['quarter'].upper()} CATALYST CANDIDATES")
    print("="*70)
    print(f"\nTotal: {len(result['investable_companies'])} companies")
    print(f"  HIGH confidence:   {result['pipeline_stats']['high_confidence_catalysts']} companies")
    print(f"  MEDIUM confidence: {result['pipeline_stats']['medium_confidence_catalysts']} companies")
    print(f"  LOW confidence:    {result['pipeline_stats']['low_confidence_catalysts']} companies")

    # Display by tier
    companies_by_tier = result['companies_by_tier']

    for tier, tier_name in [('HIGH', 'HIGH CONFIDENCE (Dated Catalysts)'),
                             ('MEDIUM', 'MEDIUM CONFIDENCE (Trial Completions)'),
                             ('LOW', 'LOW CONFIDENCE (Early Stage)')]:

        tier_companies = companies_by_tier.get(tier, [])
        if not tier_companies:
            continue

        print(f"\n\n{'━'*70}")
        print(f"{tier_name} - {len(tier_companies)} companies")
        print(f"{'━'*70}")

        # Show first 5 companies from each tier
        for i, company in enumerate(tier_companies[:5], 1):
            print(f"\n{i}. {company['company_name']} ({company.get('ticker', 'N/A')})")
            if company.get('market_cap_formatted'):
                print(f"   💰 Market Cap: {company['market_cap_formatted']}")

            # Catalyst info
            print(f"   🎯 Catalyst: {company.get('catalyst_type', 'TRIAL_COMPLETION')}")
            print(f"   📅 Date: {company.get('catalyst_date', result['quarter'])}")

            # Trial summary
            trial_count = company.get('trial_count', 0)
            print(f"   📊 Trials: {trial_count} completing in {result['quarter']}")

            if trial_count > 0:
                # Phase breakdown
                phase_breakdown = company.get('phase_breakdown', {})
                if phase_breakdown:
                    phase_summary = ", ".join([f"{count} {phase}" for phase, count in phase_breakdown.items()])
                    print(f"   🧪 Phases: {phase_summary}")

                # Show first trial
                trials = company.get('trials', [])
                if trials:
                    trial = trials[0]
                    print(f"   📋 Example: {trial.get('intervention', 'Drug')} for {trial.get('condition', 'Indication')}")

            # Enrichment notes
            enrichment = company.get('enrichment', {})
            if enrichment.get('pdufa_check_needed'):
                print(f"   ⚠️  PDUFA check recommended")
            if enrichment.get('abstract_check_needed'):
                print(f"   ⚠️  Abstract tracking recommended")

        if len(tier_companies) > 5:
            print(f"\n... and {len(tier_companies) - 5} more {tier} confidence companies")

    print("\n" + "="*70)
    print("✓ Bottom-up catalyst discovery complete!")
    print("="*70)
