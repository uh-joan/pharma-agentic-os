#!/usr/bin/env python3
"""
Trial Completion Predictor

Predicts likely conference presentations based on ClinicalTrials.gov trial completion dates
and conference timing windows. Uses algorithmic probability scoring.
"""

import sys
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search


def predict_trial_presentations(
    quarter: str = "Q4",
    year: int = 2025,
    min_probability: float = 0.6,
    companies: Optional[List[str]] = None,
    phases: Optional[List[str]] = None
) -> Dict[str, any]:
    """Predict likely conference presentations based on trial completion dates.

    Args:
        quarter: Target quarter (Q1, Q2, Q3, Q4)
        year: Target year
        min_probability: Minimum probability threshold (0.0-1.0)
        companies: Optional list of companies to filter
        phases: Optional list of phases to filter (e.g., ['PHASE2', 'PHASE3'])

    Returns:
        dict: Predictions with probabilities, conference mappings, and summary
    """

    # Conference definitions for each quarter
    conferences = get_conferences_for_quarter(quarter, year)

    if not conferences:
        return {
            'quarter': f'{quarter} {year}',
            'error': f'No major conferences defined for {quarter} {year}',
            'predictions': []
        }

    all_predictions = []

    # Query trials for each conference
    for conf in conferences:
        print(f"\nQuerying trials for {conf['name']}...")
        trials = get_completed_trials_for_conference(
            conf,
            phases or ['PHASE2', 'PHASE3']
        )

        # Calculate probabilities for each trial
        for trial in trials:
            prob = calculate_probability(trial, conf)

            if prob >= min_probability:
                # Parse trial details
                details = parse_trial_info(trial)

                # Apply company filter if specified
                if companies and details['company'] not in companies:
                    continue

                prediction = {
                    'company': details['company'],
                    'drug': details['drug'],
                    'indication': details['indication'],
                    'trial_id': details['nct_id'],
                    'trial_title': details['title'],
                    'trial_phase': details['phase'],
                    'completion_date': details['completion_date'],
                    'conference': conf['name'],
                    'conference_dates': f"{conf['start_date']} to {conf['end_date']}",
                    'presentation_probability': round(prob, 2),
                    'confidence_reason': generate_confidence_reason(trial, conf, prob),
                    'therapeutic_area_match': f"{details['indication']} → {conf['name']}",
                    'months_to_conference': calculate_months_to_conference(
                        details['completion_date'],
                        conf['start_date']
                    )
                }
                all_predictions.append(prediction)

    # Sort by probability (descending)
    all_predictions.sort(key=lambda x: x['presentation_probability'], reverse=True)

    # Generate summary
    summary = generate_summary(all_predictions, conferences)

    return {
        'quarter': f'{quarter} {year}',
        'conferences': [c['name'] for c in conferences],
        'total_predictions': len(all_predictions),
        'predictions': all_predictions,
        'summary': summary
    }


def get_conferences_for_quarter(quarter: str, year: int) -> List[Dict]:
    """Get conference definitions for a given quarter."""

    conference_map = {
        'Q4': {
            2025: [
                {
                    'name': 'ASH 2025',
                    'start_date': '2025-12-07',
                    'end_date': '2025-12-10',
                    'therapeutic_areas': [
                        'Multiple Myeloma', 'Myeloma',
                        'Leukemia', 'Acute Myeloid Leukemia', 'AML', 'ALL', 'CLL', 'CML',
                        'Lymphoma', 'Non-Hodgkin Lymphoma', 'NHL', 'Hodgkin',
                        'Myelodysplastic Syndrome', 'MDS',
                        'Blood Cancer', 'Hematologic', 'Hematological'
                    ],
                    'optimal_completion_start': '2025-05-01',
                    'optimal_completion_end': '2025-09-30',
                    'acceptable_completion_start': '2025-03-01',
                    'acceptable_completion_end': '2025-10-31'
                },
                {
                    'name': 'CTAD 2025',
                    'start_date': '2025-10-29',
                    'end_date': '2025-11-01',
                    'therapeutic_areas': [
                        'Alzheimer', 'Dementia', 'Cognitive Impairment',
                        'Mild Cognitive Impairment', 'MCI',
                        'Neurodegenerative'
                    ],
                    'optimal_completion_start': '2025-03-01',
                    'optimal_completion_end': '2025-07-31',
                    'acceptable_completion_start': '2025-01-01',
                    'acceptable_completion_end': '2025-08-31'
                }
            ]
        }
        # Add more quarters/years as needed
    }

    return conference_map.get(quarter, {}).get(year, [])


def get_completed_trials_for_conference(
    conference: Dict,
    phases: List[str]
) -> List[Dict]:
    """Query ClinicalTrials.gov for trials matching conference criteria."""

    all_trials = []

    # Build search terms for therapeutic areas
    search_terms = ' OR '.join(f'"{area}"' for area in conference['therapeutic_areas'])

    # Query with completion date filter
    page_token = None
    phase_filter = ' OR '.join(phases)

    print(f"  Searching: {search_terms[:100]}...")
    print(f"  Completion window: {conference['acceptable_completion_start']} to {conference['acceptable_completion_end']}")

    while True:
        try:
            if page_token:
                result = search(
                    term=search_terms,
                    status="COMPLETED",
                    phase=phase_filter,
                    primComp=f"{conference['acceptable_completion_start']}_{conference['acceptable_completion_end']}",
                    pageSize=1000,
                    pageToken=page_token
                )
            else:
                result = search(
                    term=search_terms,
                    status="COMPLETED",
                    phase=phase_filter,
                    primComp=f"{conference['acceptable_completion_start']}_{conference['acceptable_completion_end']}",
                    pageSize=1000
                )

            # Parse trials from markdown
            trials = parse_trials_from_markdown(result, conference)
            all_trials.extend(trials)

            print(f"  Found {len(trials)} trials (total: {len(all_trials)})")

            # Check for next page
            next_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
            if next_token_match:
                page_token = next_token_match.group(1)
            else:
                break

        except Exception as e:
            print(f"  Warning: Error querying trials: {e}")
            break

    return all_trials


def parse_trials_from_markdown(markdown: str, conference: Dict) -> List[Dict]:
    """Parse trial information from CT.gov markdown response."""

    trials = []

    # Split into individual trial sections
    trial_sections = re.split(r'###\s+\d+\.\s+', markdown)[1:]  # Skip header

    for section in trial_sections:
        try:
            trial = {}

            # Extract NCT ID
            nct_match = re.search(r'(NCT\d{8})', section)
            if not nct_match:
                continue
            trial['nct_id'] = nct_match.group(1)

            # Extract fields
            trial['title'] = extract_field(section, 'Title')
            trial['status'] = extract_field(section, 'Status')
            trial['phase'] = extract_field(section, 'Phase')
            trial['conditions'] = extract_field(section, 'Conditions')
            trial['interventions'] = extract_field(section, 'Interventions')
            trial['sponsor'] = extract_field(section, 'Sponsor')
            trial['completion_date'] = extract_field(section, 'Primary Completion Date')

            # Only include if therapeutic area matches
            if trial['conditions'] and match_therapeutic_area(trial['conditions'], conference):
                trial['matched_conference'] = conference['name']
                trials.append(trial)

        except Exception as e:
            continue

    return trials


def extract_field(section: str, field_name: str) -> str:
    """Extract a field value from markdown section."""
    pattern = rf'\*\*{field_name}:\*\*\s*(.+?)(?:\n|$)'
    match = re.search(pattern, section)
    return match.group(1).strip() if match else ''


def match_therapeutic_area(condition: str, conference: Dict) -> bool:
    """Check if condition matches conference therapeutic areas."""
    condition_lower = condition.lower()
    return any(
        area.lower() in condition_lower
        for area in conference['therapeutic_areas']
    )


def calculate_probability(trial: Dict, conference: Dict) -> float:
    """Calculate presentation probability for a trial."""

    score = 0.0

    # 1. Timing score (50% weight)
    timing_score = calculate_timing_score(
        trial.get('completion_date', ''),
        conference['start_date'],
        conference['optimal_completion_start'],
        conference['optimal_completion_end']
    )
    score += timing_score * 0.5

    # 2. Trial phase (20% weight)
    phase = trial.get('phase', '')
    if 'PHASE3' in phase:
        score += 0.20
    elif 'PHASE2' in phase:
        score += 0.15

    # 3. Therapeutic area match (20% weight)
    if trial.get('matched_conference'):
        score += 0.20

    # 4. Trial status (10% weight)
    if trial.get('status') == 'COMPLETED':
        score += 0.10

    return min(score, 1.0)


def calculate_timing_score(
    completion_date: str,
    conference_date: str,
    optimal_start: str,
    optimal_end: str
) -> float:
    """Calculate timing score based on completion date."""

    if not completion_date:
        return 0.0

    try:
        comp_dt = datetime.strptime(completion_date, '%Y-%m-%d')
        conf_dt = datetime.strptime(conference_date, '%Y-%m-%d')
        opt_start = datetime.strptime(optimal_start, '%Y-%m-%d')
        opt_end = datetime.strptime(optimal_end, '%Y-%m-%d')

        # Check if in optimal window
        if opt_start <= comp_dt <= opt_end:
            return 1.0  # Perfect timing

        # Calculate months before conference
        months_before = (conf_dt - comp_dt).days / 30

        if 3 <= months_before <= 7:
            return 1.0  # Optimal timing
        elif 2 <= months_before < 3 or 7 < months_before <= 9:
            return 0.6  # Acceptable timing
        else:
            return 0.0  # Outside window

    except:
        return 0.0


def calculate_months_to_conference(completion_date: str, conference_date: str) -> int:
    """Calculate months between completion and conference."""
    try:
        comp_dt = datetime.strptime(completion_date, '%Y-%m-%d')
        conf_dt = datetime.strptime(conference_date, '%Y-%m-%d')
        return int((conf_dt - comp_dt).days / 30)
    except:
        return 0


def parse_trial_info(trial: Dict) -> Dict:
    """Parse and extract key trial information."""

    # Extract company from sponsor
    sponsor = trial.get('sponsor', '')
    company = sponsor.split(',')[0].strip() if sponsor else 'Unknown'

    # Extract drug from interventions
    interventions = trial.get('interventions', '')
    drug = interventions.split(',')[0].strip() if interventions else 'Unknown'

    # Clean up drug name (remove "Drug:" prefix if present)
    if drug.startswith('Drug:'):
        drug = drug[5:].strip()

    return {
        'company': company,
        'drug': drug,
        'indication': trial.get('conditions', ''),
        'nct_id': trial.get('nct_id', ''),
        'title': trial.get('title', ''),
        'phase': trial.get('phase', ''),
        'completion_date': trial.get('completion_date', '')
    }


def generate_confidence_reason(trial: Dict, conference: Dict, probability: float) -> str:
    """Generate human-readable confidence reason."""

    reasons = []

    # Timing
    completion_date = trial.get('completion_date', '')
    if completion_date:
        months = calculate_months_to_conference(completion_date, conference['start_date'])
        if 3 <= months <= 7:
            reasons.append(f'Optimal timing ({months} months)')
        elif months > 0:
            reasons.append(f'Acceptable timing ({months} months)')

    # Phase
    phase = trial.get('phase', '')
    if 'PHASE3' in phase:
        reasons.append('Phase 3')
    elif 'PHASE2' in phase:
        reasons.append('Phase 2')

    # Therapeutic area
    if trial.get('matched_conference'):
        reasons.append('Primary TA match')

    return ', '.join(reasons) if reasons else 'Based on available data'


def generate_summary(predictions: List[Dict], conferences: List[Dict]) -> Dict:
    """Generate summary statistics."""

    by_conference = defaultdict(int)
    by_phase = defaultdict(int)
    high_prob = 0
    medium_prob = 0

    for pred in predictions:
        by_conference[pred['conference']] += 1
        by_phase[pred['trial_phase']] += 1

        if pred['presentation_probability'] >= 0.75:
            high_prob += 1
        elif pred['presentation_probability'] >= 0.60:
            medium_prob += 1

    return {
        'total': len(predictions),
        'by_conference': dict(by_conference),
        'by_phase': dict(by_phase),
        'high_probability': high_prob,
        'medium_probability': medium_prob
    }


if __name__ == "__main__":
    print("Trial Completion Predictor - Q4 2025 Demo\n")
    print("=" * 80)

    result = predict_trial_presentations(
        quarter="Q4",
        year=2025,
        min_probability=0.6
    )

    print(f"\nQuarter: {result['quarter']}")
    print(f"Conferences: {', '.join(result['conferences'])}")
    print(f"Total Predictions: {result['total_predictions']}")

    if result['total_predictions'] > 0:
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)

        summary = result['summary']
        print(f"\nTotal Predictions: {summary['total']}")
        print(f"High Probability (≥75%): {summary['high_probability']}")
        print(f"Medium Probability (60-74%): {summary['medium_probability']}")

        print("\nBy Conference:")
        for conf, count in summary['by_conference'].items():
            print(f"  {conf}: {count}")

        print("\nBy Phase:")
        for phase, count in summary['by_phase'].items():
            print(f"  {phase}: {count}")

        print("\n" + "=" * 80)
        print("TOP 10 PREDICTIONS")
        print("=" * 80)

        for i, pred in enumerate(result['predictions'][:10], 1):
            print(f"\n{i}. {pred['company']} - {pred['drug']}")
            print(f"   Trial: {pred['trial_id']} ({pred['trial_phase']})")
            print(f"   Indication: {pred['indication']}")
            print(f"   Conference: {pred['conference']} ({pred['conference_dates']})")
            print(f"   Completion: {pred['completion_date']} ({pred['months_to_conference']} months before)")
            print(f"   Probability: {pred['presentation_probability']:.0%}")
            print(f"   Reason: {pred['confidence_reason']}")
    else:
        print("\nNo predictions found matching criteria.")

    print(f"\n{'='*80}")
