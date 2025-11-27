import sys
import os

# Add project root to path so we can import from .claude.skills
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up: scripts/ -> skill/ -> skills/ -> .claude/ -> project_root
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

# Now we can import using dotted paths from project root
import importlib.util

# Import FDA device approvals skill
fda_spec = importlib.util.spec_from_file_location(
    "get_company_fda_device_approvals",
    os.path.join(project_root, ".claude", "skills", "company-fda-device-approvals", "scripts", "get_company_fda_device_approvals.py")
)
fda_module = importlib.util.module_from_spec(fda_spec)
fda_spec.loader.exec_module(fda_module)
get_company_fda_device_approvals = fda_module.get_company_fda_device_approvals

# Import clinical trials portfolio skill
trials_spec = importlib.util.spec_from_file_location(
    "get_company_clinical_trials_portfolio",
    os.path.join(project_root, ".claude", "skills", "company-clinical-trials-portfolio", "scripts", "get_company_clinical_trials_portfolio.py")
)
trials_module = importlib.util.module_from_spec(trials_spec)
trials_spec.loader.exec_module(trials_module)
get_company_clinical_trials_portfolio = trials_module.get_company_clinical_trials_portfolio
from difflib import SequenceMatcher
from datetime import datetime

def analyze_company_product_launch_timeline(
    company_name,
    focus_area=None,
    start_year=2020,
    end_year=None
):
    """Correlate FDA device approvals with clinical trials to analyze product launch timelines.

    Args:
        company_name (str): Company name (e.g., "Boston Scientific", "Medtronic")
        focus_area (str, optional): Therapeutic area filter (e.g., "cardiovascular")
        start_year (int): Analysis start year (default: 2020)
        end_year (int, optional): Analysis end year (default: current year)

    Returns:
        dict: Contains FDA approvals, clinical trials, correlated products, statistics, and summary
    """
    if end_year is None:
        end_year = datetime.now().year

    print(f"\n{'='*80}")
    print(f"Product Launch Timeline Analysis: {company_name}")
    if focus_area:
        print(f"Focus Area: {focus_area}")
    print(f"Time Period: {start_year}-{end_year}")
    print(f"{'='*80}\n")

    # Step 1: Get FDA device approvals
    print("Step 1: Collecting FDA device approvals...")
    fda_result = get_company_fda_device_approvals(
        company_name=company_name,
        start_year=start_year,
        end_year=end_year
    )
    print(f"  ✓ Found {fda_result['total_approvals']} FDA approvals")

    # Step 2: Get clinical trials portfolio
    print("\nStep 2: Collecting clinical trials portfolio...")
    trials_result = get_company_clinical_trials_portfolio(
        sponsor_name=company_name,
        condition=focus_area,
        start_year=start_year
    )
    print(f"  ✓ Found {trials_result['total_trials']} clinical trials")

    # Step 3: Correlate FDA approvals with trials using fuzzy matching
    print("\nStep 3: Correlating FDA approvals with clinical trials...")
    correlated_products = []

    for approval in fda_result['approvals']:
        device_name = approval['device_name'].lower()

        # Find matching trials using fuzzy string matching
        matching_trials = []
        for trial in trials_result['trials']:
            trial_title = trial['title'].lower()
            trial_interventions = ' '.join(trial['interventions']).lower()

            # Calculate similarity score
            title_score = SequenceMatcher(None, device_name, trial_title).ratio()
            intervention_score = max(
                [SequenceMatcher(None, device_name, intervention.lower()).ratio()
                 for intervention in trial['interventions']] + [0]
            )

            # Match if either score exceeds threshold
            if title_score > 0.4 or intervention_score > 0.6:
                matching_trials.append({
                    'nct_id': trial['nct_id'],
                    'title': trial['title'],
                    'status': trial['status'],
                    'phase': trial['phase'],
                    'posted_date': trial['posted_date'],
                    'enrollment': trial['enrollment'],
                    'match_score': max(title_score, intervention_score)
                })

        if matching_trials:
            # Calculate trial-to-approval timeline
            approval_year = None
            try:
                approval_year = int(approval['approval_date'][:4])
            except:
                pass

            earliest_trial_year = None
            for trial in matching_trials:
                try:
                    trial_year = int(trial['posted_date'].split()[-1])
                    if earliest_trial_year is None or trial_year < earliest_trial_year:
                        earliest_trial_year = trial_year
                except:
                    pass

            timeline_years = None
            if approval_year and earliest_trial_year:
                timeline_years = approval_year - earliest_trial_year

            correlated_products.append({
                'device_name': approval['device_name'],
                'approval_type': approval['approval_type'],
                'approval_date': approval['approval_date'],
                'device_class': approval['device_class'],
                'medical_specialty': approval['medical_specialty'],
                'matching_trials': len(matching_trials),
                'trial_details': matching_trials,
                'timeline_years': timeline_years,
                'k_number': approval.get('k_number'),
                'pma_number': approval.get('pma_number')
            })

    print(f"  ✓ Correlated {len(correlated_products)} products with supporting trials")

    # Step 4: Calculate strategic insights
    print("\nStep 4: Calculating strategic insights...")

    # Average trial-to-approval time
    timeline_values = [p['timeline_years'] for p in correlated_products if p['timeline_years'] is not None]
    avg_timeline = sum(timeline_values) / len(timeline_values) if timeline_values else None

    # Approval pathway distribution
    pathway_distribution = {
        'PMA': sum(1 for p in correlated_products if p['approval_type'] == 'PMA'),
        '510k': sum(1 for p in correlated_products if p['approval_type'] == '510k'),
        'registration': sum(1 for p in correlated_products if p['approval_type'] == 'registration')
    }

    # Active pipeline (recruiting/active trials)
    active_statuses = ['RECRUITING', 'ACTIVE_NOT_RECRUITING', 'ENROLLING_BY_INVITATION']
    active_pipeline = sum(1 for t in trials_result['trials']
                         if t['status'] in active_statuses)

    # Generate summary
    summary_lines = [
        f"\n{'='*80}",
        f"Product Launch Timeline Analysis: {company_name}",
        f"{'='*80}",
        f"\nData Summary:",
        f"  • Total FDA Approvals: {fda_result['total_approvals']}",
        f"  • Total Clinical Trials: {trials_result['total_trials']}",
        f"  • Products with Supporting Trials: {len(correlated_products)}",
        ""
    ]

    if avg_timeline:
        summary_lines.append(f"Strategic Insights:")
        summary_lines.append(f"  • Average Trial-to-Approval Time: {avg_timeline:.1f} years")

    if pathway_distribution:
        summary_lines.append(f"\nApproval Pathway Distribution:")
        if pathway_distribution['PMA'] > 0:
            summary_lines.append(f"  • PMA (Class III): {pathway_distribution['PMA']} products")
        if pathway_distribution['510k'] > 0:
            summary_lines.append(f"  • 510(k) (Class I/II): {pathway_distribution['510k']} products")
        if pathway_distribution['registration'] > 0:
            summary_lines.append(f"  • Registrations: {pathway_distribution['registration']} products")

    summary_lines.append(f"\nActive Pipeline:")
    summary_lines.append(f"  • Recruiting/Active Trials: {active_pipeline}")

    # Top correlated products
    if correlated_products:
        top_products = sorted(correlated_products,
                            key=lambda x: x['matching_trials'],
                            reverse=True)[:5]
        summary_lines.append(f"\nTop Products by Trial Support:")
        for i, product in enumerate(top_products, 1):
            summary_lines.append(
                f"  {i}. {product['device_name']} ({product['matching_trials']} trials)"
            )

    summary_lines.append(f"\n{'='*80}\n")
    summary = "\n".join(summary_lines)

    return {
        'company': company_name,
        'focus_area': focus_area,
        'time_period': f"{start_year}-{end_year}",
        'fda_approvals': fda_result,
        'clinical_trials': trials_result,
        'correlated_products': correlated_products,
        'statistics': {
            'total_approvals': fda_result['total_approvals'],
            'total_trials': trials_result['total_trials'],
            'correlated_products': len(correlated_products),
            'avg_timeline_years': avg_timeline,
            'pathway_distribution': pathway_distribution,
            'active_pipeline': active_pipeline
        },
        'summary': summary
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze company product launch timeline by correlating FDA approvals with clinical trials'
    )
    parser.add_argument('company', help='Company name (e.g., "Boston Scientific", "Medtronic")')
    parser.add_argument('--focus-area', help='Therapeutic area filter (e.g., "cardiovascular", "neurology")')
    parser.add_argument('--start-year', type=int, default=2020, help='Filter approvals/trials after this year (default: 2020)')
    parser.add_argument('--end-year', type=int, help='Filter approvals/trials before this year')

    args = parser.parse_args()

    result = analyze_company_product_launch_timeline(
        company_name=args.company,
        focus_area=args.focus_area,
        start_year=args.start_year,
        end_year=args.end_year
    )

    print(result['summary'])

    # Show sample correlated products
    if result['correlated_products']:
        print("\nSample Correlated Products:")
        for product in result['correlated_products'][:3]:
            print(f"\n  {product['device_name']}")
            print(f"  Approval: {product['approval_type']} ({product['approval_date']})")
            print(f"  Supporting Trials: {product['matching_trials']}")
            if product['timeline_years']:
                print(f"  Trial-to-Approval: {product['timeline_years']} years")
