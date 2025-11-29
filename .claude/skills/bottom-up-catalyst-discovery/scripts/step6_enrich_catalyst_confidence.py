#!/usr/bin/env python3
"""
Step 6: Enrich with Catalyst Confidence Scoring

Instead of filtering companies, this enriches ALL companies with catalyst confidence
and prioritizes based on available data:

- HIGH confidence: PDUFA dates, accepted abstracts, company-announced events
- MEDIUM confidence: Trial completions in target quarter
- LOW confidence: Very early trials or uncertain timing

This ensures we don't miss opportunities due to incomplete data while still
prioritizing actionable catalysts.
"""

import sys
from typing import List, Dict, Optional
from datetime import datetime

sys.path.insert(0, ".claude")


def calculate_catalyst_confidence(company: Dict) -> str:
    """Calculate catalyst confidence level for a company.

    Args:
        company: Company dict with trial metadata

    Returns:
        str: 'HIGH', 'MEDIUM', or 'LOW'
    """
    trials = company.get('trials', [])

    if not trials:
        return 'LOW'

    # Check for enrichment data (PDUFA, abstracts, etc.)
    enrichment = company.get('enrichment', {})

    # HIGH: Has PDUFA date or accepted abstract
    if enrichment.get('pdufa_date') or enrichment.get('abstract_accepted'):
        return 'HIGH'

    # MEDIUM: Has Phase 2/3 trials completing
    phase_breakdown = company.get('phase_breakdown', {})
    has_late_stage = any(
        phase in ['PHASE3', 'Phase3', 'PHASE2', 'Phase2']
        for phase in phase_breakdown.keys()
    )

    if has_late_stage and len(trials) > 0:
        return 'MEDIUM'

    # LOW: Only Phase 1 or very few trials
    return 'LOW'


def enrich_pdufa_data(company: Dict) -> Dict:
    """Enrich company with PDUFA data if available.

    Args:
        company: Company dict

    Returns:
        dict: Updated company dict with PDUFA enrichment

    Note: Currently a placeholder - would connect to FDA PDUFA tracker
    """
    # Placeholder for PDUFA enrichment
    # TODO: Integrate with FDA PDUFA tracker skill when available

    # For now, mark that enrichment is possible
    if 'enrichment' not in company:
        company['enrichment'] = {}

    company['enrichment']['pdufa_check_needed'] = True

    return company


def enrich_abstract_data(company: Dict) -> Dict:
    """Enrich company with conference abstract data if available.

    Args:
        company: Company dict

    Returns:
        dict: Updated company dict with abstract enrichment

    Note: Currently a placeholder - would connect to conference tracker
    """
    # Placeholder for abstract/conference enrichment
    # TODO: Integrate with conference tracker skill when available

    if 'enrichment' not in company:
        company['enrichment'] = {}

    company['enrichment']['abstract_check_needed'] = True

    return company


def determine_catalyst_type(company: Dict) -> str:
    """Determine primary catalyst type for company.

    Args:
        company: Company dict with enrichment

    Returns:
        str: Catalyst type (PDUFA, ABSTRACT, TRIAL_COMPLETION, etc.)
    """
    enrichment = company.get('enrichment', {})

    if enrichment.get('pdufa_date'):
        return 'PDUFA'

    if enrichment.get('abstract_accepted'):
        return 'ABSTRACT_PRESENTATION'

    if enrichment.get('company_announced_events'):
        return 'COMPANY_ANNOUNCED'

    # Default: trial completion
    return 'TRIAL_COMPLETION'


def enrich_catalyst_confidence(
    companies: List[Dict],
    quarter: str = "Q4",
    year: int = 2025,
    verbose: bool = True
) -> Dict[str, any]:
    """Enrich all companies with catalyst confidence and prioritize.

    Args:
        companies: List of investable companies with trial metadata
        quarter: Quarter string (e.g., "Q4", "Q1")
        year: Year (e.g., 2025)
        verbose: Print progress

    Returns:
        dict: {
            'total_companies': 65,
            'high_confidence': 12,
            'medium_confidence': 48,
            'low_confidence': 5,
            'companies_by_tier': {
                'HIGH': [...],
                'MEDIUM': [...],
                'LOW': [...]
            },
            'enriched_companies': [all companies sorted by confidence]
        }
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"Enriching Catalyst Confidence")
        print(f"{'='*60}\n")
        print(f"Processing {len(companies)} companies...")

    enriched_companies = []

    for i, company in enumerate(companies, 1):
        # Step 1: Enrich with PDUFA data (if available)
        company = enrich_pdufa_data(company)

        # Step 2: Enrich with abstract/conference data (if available)
        company = enrich_abstract_data(company)

        # Step 3: Calculate confidence level
        company['catalyst_confidence'] = calculate_catalyst_confidence(company)

        # Step 4: Determine catalyst type
        company['catalyst_type'] = determine_catalyst_type(company)

        # Step 5: Format catalyst date
        if company.get('earliest_catalyst') and company['earliest_catalyst'] != 'Unknown':
            company['catalyst_date'] = company['earliest_catalyst']
        else:
            # Use quarter range as fallback
            # Map quarter to month range
            quarter_months = {
                'Q1': 'Jan-Mar',
                'Q2': 'Apr-Jun',
                'Q3': 'Jul-Sep',
                'Q4': 'Oct-Dec'
            }
            months = quarter_months.get(quarter.upper(), 'TBD')
            company['catalyst_date'] = f'{quarter} {year} ({months})'

        enriched_companies.append(company)

        if verbose and i % 10 == 0:
            print(f"  Processed {i}/{len(companies)} companies...")

    # Sort by confidence (HIGH → MEDIUM → LOW) then by trial count
    confidence_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    enriched_companies.sort(
        key=lambda c: (
            confidence_order[c['catalyst_confidence']],
            -c.get('trial_count', 0)  # More trials = higher priority within tier
        )
    )

    # Group by tier
    companies_by_tier = {
        'HIGH': [c for c in enriched_companies if c['catalyst_confidence'] == 'HIGH'],
        'MEDIUM': [c for c in enriched_companies if c['catalyst_confidence'] == 'MEDIUM'],
        'LOW': [c for c in enriched_companies if c['catalyst_confidence'] == 'LOW']
    }

    if verbose:
        print(f"\n✓ Enrichment Complete:")
        print(f"  HIGH confidence: {len(companies_by_tier['HIGH'])} companies")
        print(f"  MEDIUM confidence: {len(companies_by_tier['MEDIUM'])} companies")
        print(f"  LOW confidence: {len(companies_by_tier['LOW'])} companies")

    return {
        'total_companies': len(companies),
        'high_confidence': len(companies_by_tier['HIGH']),
        'medium_confidence': len(companies_by_tier['MEDIUM']),
        'low_confidence': len(companies_by_tier['LOW']),
        'companies_by_tier': companies_by_tier,
        'enriched_companies': enriched_companies
    }


# Make script executable for testing
if __name__ == "__main__":
    # Test with sample data
    sample_companies = [
        {
            'company_name': 'Test Pharma Inc.',
            'ticker': 'TEST',
            'market_cap': 1000000000,
            'trial_count': 3,
            'phase_breakdown': {'PHASE3': 2, 'PHASE2': 1},
            'earliest_catalyst': '2025-11-15',
            'trials': [
                {'nct_id': 'NCT123', 'phase': 'PHASE3'},
                {'nct_id': 'NCT456', 'phase': 'PHASE3'},
                {'nct_id': 'NCT789', 'phase': 'PHASE2'}
            ]
        },
        {
            'company_name': 'BioTech Co.',
            'ticker': 'BIO',
            'market_cap': 500000000,
            'trial_count': 1,
            'phase_breakdown': {'PHASE1': 1},
            'earliest_catalyst': 'Unknown',
            'trials': [
                {'nct_id': 'NCT999', 'phase': 'PHASE1'}
            ]
        }
    ]

    result = enrich_catalyst_confidence(sample_companies, verbose=True)

    print(f"\n\nResults by Tier:")
    print("="*60)
    for tier in ['HIGH', 'MEDIUM', 'LOW']:
        companies = result['companies_by_tier'][tier]
        if companies:
            print(f"\n{tier} Confidence ({len(companies)} companies):")
            for company in companies:
                print(f"  • {company['company_name']} ({company['ticker']})")
                print(f"    Catalyst type: {company['catalyst_type']}")
                print(f"    Trials: {company['trial_count']}")
