import sys
import os

# Add .claude directory to path (works regardless of where script is run from)
script_dir = os.path.dirname(os.path.abspath(__file__))
claude_dir = os.path.abspath(os.path.join(script_dir, '../../..'))
print(f"DEBUG: script_dir = {script_dir}", file=sys.stderr)
print(f"DEBUG: claude_dir = {claude_dir}", file=sys.stderr)
sys.path.insert(0, claude_dir)

from mcp.servers.ct_gov_mcp import search, get_study
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from threading import Lock

def get_trials_by_enrollment_criteria(
    therapeutic_area: str,
    phase: str,
    criteria_type: str = "exclusion",
    search_terms: list = None,
    max_trials: int = None,
    max_workers: int = 10,
    batch_delay: float = 0.1
):
    """Find clinical trials by enrollment eligibility criteria.

    Args:
        therapeutic_area: Disease/condition (e.g., "oncology", "diabetes", "heart failure")
        phase: Clinical trial phase (PHASE1, PHASE2, PHASE3, PHASE4)
        criteria_type: Type of criteria to search ("inclusion", "exclusion", or "both")
        search_terms: List of keywords to find in criteria (e.g., ["pediatric", "children", "age < 18"])
                     If None, returns all eligibility text without filtering
        max_trials: Maximum number of trials to process (default: None = all)
                   Use to limit execution time for large result sets
        max_workers: Number of parallel API calls (default: 10)
                    Higher = faster but more API load
        batch_delay: Delay in seconds between API calls (default: 0.1)
                    Helps avoid rate limiting

    Returns:
        dict: Contains:
            - total_count: Total trials found in search
            - processed_count: Trials actually processed (limited by max_trials)
            - matching_count: Trials with matching criteria
            - match_percentage: Percentage of processed trials matching
            - trials_summary: Formatted summary with statistics
            - matching_trials: List of trial details (NCT ID, title, status, criteria text, matched terms)
    """

    print(f"Phase 1: Searching ClinicalTrials.gov for {phase} {therapeutic_area} trials...")

    # Phase 1: Get all NCT IDs via search
    nct_ids = []
    page_token = None
    max_pages = 10  # Safety limit
    page_count = 0

    while page_count < max_pages:
        try:
            if page_token:
                result = search(
                    term=therapeutic_area,
                    phase=phase,
                    pageSize=1000,
                    pageToken=page_token
                )
            else:
                result = search(
                    term=therapeutic_area,
                    phase=phase,
                    pageSize=1000
                )

            page_count += 1

            if not result or not isinstance(result, str):
                break

            # Extract NCT IDs from markdown response
            page_nct_ids = re.findall(r'### \d+\. (NCT\d{8})', result)
            nct_ids.extend(page_nct_ids)

            print(f"  Page {page_count}: Found {len(page_nct_ids)} trials (total: {len(nct_ids)})")

            # Check for next page
            next_page_match = re.search(r'pageToken: "([^"]+)"', result)
            if next_page_match:
                page_token = next_page_match.group(1)
            else:
                break

        except Exception as e:
            print(f"  Warning: Error fetching page {page_count}: {str(e)}")
            break

    total_found = len(nct_ids)
    print(f"\nPhase 1 Complete: Found {total_found} trials")

    if total_found == 0:
        return {
            'total_count': 0,
            'processed_count': 0,
            'matching_count': 0,
            'match_percentage': 0.0,
            'trials_summary': "No trials found matching search criteria",
            'matching_trials': [],
            'term_frequency': {},
            'status_breakdown': {}
        }

    # Limit processing if requested
    if max_trials and max_trials < total_found:
        nct_ids = nct_ids[:max_trials]
        print(f"Limiting to {max_trials} trials for processing")

    # Phase 2: Fetch detailed trial data in parallel
    print(f"\nPhase 2: Fetching detailed eligibility criteria for {len(nct_ids)} trials...")
    print(f"  Parallel workers: {max_workers}, Batch delay: {batch_delay}s")

    all_trials = []
    processed_count = 0
    failed_count = 0
    progress_lock = Lock()

    def fetch_trial_details(nct_id):
        """Fetch and parse a single trial's eligibility criteria"""
        nonlocal processed_count, failed_count

        try:
            # Add delay to avoid rate limiting
            time.sleep(batch_delay)

            # Get detailed trial information
            study = get_study(nctId=nct_id)

            if not study or not isinstance(study, str):
                with progress_lock:
                    failed_count += 1
                return None

            # Extract basic information
            title_match = re.search(r'\*\*Study Title:\*\* (.*)', study)
            title = title_match.group(1) if title_match else "Unknown"

            status_match = re.search(r'\*\*Status:\*\* (.*)', study)
            status = status_match.group(1) if status_match else "Unknown"

            # Extract eligibility criteria section
            eligibility_match = re.search(
                r'## Eligibility Criteria(.*?)(?=\n##|\Z)',
                study,
                re.DOTALL | re.IGNORECASE
            )

            if not eligibility_match:
                with progress_lock:
                    failed_count += 1
                return None

            eligibility_text = eligibility_match.group(1).strip()

            # Parse inclusion and exclusion sections
            criteria_text = ""
            matched_terms = []

            if criteria_type in ["inclusion", "both"]:
                inclusion_match = re.search(
                    r'(?:Key )?Inclusion Criteria[:\s]*(.*?)(?=(?:Key )?Exclusion Criteria|\Z)',
                    eligibility_text,
                    re.DOTALL | re.IGNORECASE
                )
                if inclusion_match:
                    inclusion_text = inclusion_match.group(1).strip()
                    criteria_text += f"Inclusion: {inclusion_text}\n\n"

                    # Check for matching terms
                    if search_terms:
                        for term in search_terms:
                            if re.search(re.escape(term), inclusion_text, re.IGNORECASE):
                                if term not in matched_terms:
                                    matched_terms.append(term)

            if criteria_type in ["exclusion", "both"]:
                exclusion_match = re.search(
                    r'(?:Key )?Exclusion Criteria[:\s]*(.*?)(?=\Z)',
                    eligibility_text,
                    re.DOTALL | re.IGNORECASE
                )
                if exclusion_match:
                    exclusion_text = exclusion_match.group(1).strip()
                    criteria_text += f"Exclusion: {exclusion_text}"

                    # Check for matching terms
                    if search_terms:
                        for term in search_terms:
                            if re.search(re.escape(term), exclusion_text, re.IGNORECASE):
                                if term not in matched_terms:
                                    matched_terms.append(term)

            # Update progress
            with progress_lock:
                processed_count += 1
                if processed_count % 50 == 0:
                    print(f"  Progress: {processed_count}/{len(nct_ids)} trials processed ({processed_count/len(nct_ids)*100:.1f}%)")

            # Return trial data if matches (or if no filtering)
            if search_terms is None or len(matched_terms) > 0:
                return {
                    'nct_id': nct_id,
                    'title': title,
                    'status': status,
                    'criteria_text': criteria_text,
                    'matched_terms': matched_terms
                }

            return None

        except Exception as e:
            with progress_lock:
                failed_count += 1
            return None

    # Execute parallel fetches
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_nct = {executor.submit(fetch_trial_details, nct_id): nct_id for nct_id in nct_ids}

        for future in as_completed(future_to_nct):
            result = future.result()
            if result:
                all_trials.append(result)

    print(f"\nPhase 2 Complete:")
    print(f"  Processed: {processed_count}/{len(nct_ids)} trials")
    print(f"  Failed: {failed_count} trials")
    print(f"  Matching: {len(all_trials)} trials")

    # Calculate statistics
    matching_count = len(all_trials)
    match_percentage = (matching_count / processed_count * 100) if processed_count > 0 else 0

    # Generate term frequency breakdown
    term_frequency = defaultdict(int)
    if search_terms:
        for trial in all_trials:
            for term in trial['matched_terms']:
                term_frequency[term] += 1

    # Generate status breakdown
    status_counts = defaultdict(int)
    for trial in all_trials:
        status_counts[trial['status']] += 1

    # Generate summary
    summary_lines = [
        f"# Clinical Trials by Enrollment Criteria",
        f"\n**Therapeutic Area**: {therapeutic_area}",
        f"**Phase**: {phase}",
        f"**Criteria Type**: {criteria_type}",
        f"\n## Results Summary",
        f"\n- **Total Trials Found**: {total_found:,}",
        f"- **Trials Processed**: {processed_count:,}",
        f"- **Matching Trials**: {matching_count:,} ({match_percentage:.2f}%)",
        f"- **Failed to Process**: {failed_count:,}",
    ]

    if max_trials and max_trials < total_found:
        summary_lines.append(f"\n⚠️ **Note**: Processing limited to {max_trials:,} trials (out of {total_found:,} found)")

    if search_terms:
        summary_lines.append(f"\n**Search Terms**: {', '.join(search_terms)}")

        if term_frequency:
            summary_lines.append("\n## Term Frequency")
            for term, count in sorted(term_frequency.items(), key=lambda x: x[1], reverse=True):
                summary_lines.append(f"- **{term}**: {count:,} trials ({count/processed_count*100:.1f}%)")

    # Add status breakdown
    if status_counts:
        summary_lines.append("\n## Status Breakdown")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary_lines.append(f"- **{status}**: {count:,} trials")

    # Add sample trials
    if matching_count > 0:
        summary_lines.append("\n## Sample Matching Trials")
        for trial in all_trials[:5]:
            summary_lines.append(f"\n### {trial['nct_id']}: {trial['title'][:80]}...")
            summary_lines.append(f"- **Status**: {trial['status']}")
            if trial['matched_terms']:
                summary_lines.append(f"- **Matched Terms**: {', '.join(trial['matched_terms'])}")
            criteria_preview = trial['criteria_text'][:200].replace('\n', ' ')
            summary_lines.append(f"- **Criteria**: {criteria_preview}...")

    summary_lines.append("\n## Performance")
    summary_lines.append(f"- **API Calls**: {len(nct_ids):,} get_study() calls")
    summary_lines.append(f"- **Parallel Workers**: {max_workers}")
    summary_lines.append(f"- **Batch Delay**: {batch_delay}s per call")

    summary_lines.append("\n## Notes")
    summary_lines.append("- Uses parallel API calls for efficiency (configurable via max_workers)")
    summary_lines.append("- Includes rate limiting to avoid overloading CT.gov API")
    summary_lines.append("- For large datasets (>500 trials), consider using max_trials parameter")
    summary_lines.append("- Eligibility criteria are free-text fields, keyword matching is case-insensitive")
    summary_lines.append("- For regulatory analysis, recommend manual review of matched trials")

    trials_summary = '\n'.join(summary_lines)

    return {
        'total_count': total_found,
        'processed_count': processed_count,
        'matching_count': matching_count,
        'match_percentage': match_percentage,
        'trials_summary': trials_summary,
        'matching_trials': all_trials,
        'term_frequency': dict(term_frequency) if search_terms else {},
        'status_breakdown': dict(status_counts),
        'failed_count': failed_count
    }

if __name__ == "__main__":
    # Test: PREA pediatric exclusion impact for Phase 3 oncology (limited sample)
    print("=" * 80)
    print("TEST: PREA Impact Assessment - Pediatric Exclusions in Phase 3 Oncology")
    print("(Limited to 100 trials for testing)")
    print("=" * 80)

    result = get_trials_by_enrollment_criteria(
        therapeutic_area="oncology",
        phase="PHASE3",
        criteria_type="exclusion",
        search_terms=["pediatric", "children", "age < 18", "under 18", "younger than 18"],
        max_trials=100,  # Limit for testing
        max_workers=10,
        batch_delay=0.1
    )

    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"\nTotal Phase 3 oncology trials found: {result['total_count']:,}")
    print(f"Trials processed: {result['processed_count']:,}")
    print(f"Trials excluding pediatric patients: {result['matching_count']:,} ({result['match_percentage']:.2f}%)")
    print(f"Failed to process: {result['failed_count']:,}")

    if result['term_frequency']:
        print("\nTerm frequency:")
        for term, count in sorted(result['term_frequency'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - '{term}': {count:,} trials")

    print(f"\n{result['trials_summary']}")
