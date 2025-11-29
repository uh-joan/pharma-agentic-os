#!/usr/bin/env python3
"""
Step 1: Extract Sponsors from ClinicalTrials.gov

Extracts all lead sponsors from Phase 2/3 trials completing in target quarter.
"""

import sys
import re
from typing import List, Dict, Set, Optional

sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search


def extract_sponsors_from_markdown(markdown_text: str) -> List[str]:
    """Extract lead sponsor names from CT.gov markdown response.

    Args:
        markdown_text: Markdown string from CT.gov search() function

    Returns:
        list: Sponsor names extracted from markdown
    """
    sponsors = []

    # Pattern: **Lead Sponsor:** followed by the sponsor name
    pattern = r'\*\*Lead Sponsor:\*\*\s*([^\n]+)'
    matches = re.findall(pattern, markdown_text)

    for match in matches:
        # Clean the sponsor name
        sponsor = match.strip()
        # Remove trailing markdown formatting
        sponsor = re.sub(r'\s*\*+$', '', sponsor)
        sponsors.append(sponsor)

    return sponsors


def get_quarter_date_range(quarter: str, year: int) -> str:
    """Convert quarter to CT.gov date range format.

    Args:
        quarter: "Q1", "Q2", "Q3", or "Q4"
        year: Year (e.g., 2025)

    Returns:
        str: Date range in CT.gov format "YYYY-MM-DD_YYYY-MM-DD"
    """
    quarter_dates = {
        'Q1': (f"{year}-01-01", f"{year}-03-31"),
        'Q2': (f"{year}-04-01", f"{year}-06-30"),
        'Q3': (f"{year}-07-01", f"{year}-09-30"),
        'Q4': (f"{year}-10-01", f"{year}-12-31")
    }
    start_date, end_date = quarter_dates.get(quarter.upper(), (f"{year}-10-01", f"{year}-12-31"))
    return f"{start_date}_{end_date}"


def get_trial_sponsors_by_quarter(
    quarter: str = "Q4",
    year: int = 2025,
    phases: Optional[List[str]] = None,
    max_trials: int = 10000
) -> Dict[str, any]:
    """Extract all sponsors from trials completing in specified quarter.

    Args:
        quarter: "Q1", "Q2", "Q3", or "Q4"
        year: Year (e.g., 2025)
        phases: List of phases (default: ["PHASE2", "PHASE3"])
        max_trials: Maximum trials to retrieve per phase (default: 5000)

    Returns:
        dict: {
            'quarter': 'Q4 2025',
            'total_trials': 234,
            'unique_sponsors': 156,
            'sponsors': ['AbbVie Inc.', 'Amgen Inc.', ...],
            'by_phase': {'PHASE2': 89, 'PHASE3': 67}
        }
    """
    if phases is None:
        phases = ["PHASE2", "PHASE3"]

    all_sponsors = []
    trials_by_phase = {}

    # Get date range for quarter
    date_range = get_quarter_date_range(quarter, year)

    print(f"\n{'='*60}")
    print(f"Extracting Sponsors from {quarter} {year} Trials")
    print(f"Completion Date Range: {date_range}")
    print(f"{'='*60}\n")

    # Query each phase separately with pagination
    for phase in phases:
        print(f"Querying {phase} trials completing in {quarter} {year}...")

        try:
            # Build complex query using CT.gov advanced filter syntax
            # Note: Simple primComp parameter doesn't work in MCP, must use complexQuery
            start_date, end_date = date_range.split('_')
            complex_query = f"AREA[Phase]{phase} AND AREA[PrimaryCompletionDate]RANGE[{start_date},{end_date}]"

            phase_sponsors = []
            seen_sponsors = set()  # Track duplicates
            page_token = None
            page_count = 0
            max_pages = max_trials // 1000 + 1  # CT.gov limit is 1000 per page
            previous_token = None

            # Paginate through all results
            while page_count < max_pages:
                # Query CT.gov for trials completing in target quarter
                if page_token:
                    result = search(
                        complexQuery=complex_query,
                        pageSize=1000,
                        pageToken=page_token
                    )
                else:
                    result = search(
                        complexQuery=complex_query,
                        pageSize=1000
                    )

                # Extract sponsors from this page
                page_sponsors = extract_sponsors_from_markdown(result)
                page_count += 1

                # Add all sponsors from this page
                phase_sponsors.extend(page_sponsors)

                # Track new unique sponsors for duplicate detection
                new_sponsors = [s for s in page_sponsors if s not in seen_sponsors]
                seen_sponsors.update(page_sponsors)

                # Stop if we got < 1000 results (partial page = last page)
                if len(page_sponsors) < 1000:
                    print(f"  ✓ Found {len(phase_sponsors)} {phase} trials (across {page_count} pages, partial page)")
                    break

                # Safety: Stop if < 10% new sponsors (heavy duplicates = API exhausted)
                duplicate_ratio = len(new_sponsors) / len(page_sponsors) if page_sponsors else 0
                if duplicate_ratio < 0.05 and page_count > 1:
                    print(f"  ✓ Found {len(seen_sponsors)} unique {phase} sponsors from {len(phase_sponsors)} trials (across {page_count} pages)")
                    break

                # Check for next page token in response
                # Per CT.gov API docs: "If response contains nextPageToken, use its value in pageToken to get next page.
                # The last page will not contain nextPageToken."
                import re

                # Look for nextPageToken in markdown response
                next_token_match = re.search(r'(?:nextPageToken|pageToken)[:\s"]+([A-Za-z0-9_-]+)', result)

                if next_token_match:
                    new_token = next_token_match.group(1)

                    # Continue pagination (token might repeat due to API bug, but keep going)
                    page_token = new_token
                    if new_token != previous_token:
                        print(f"  → Page {page_count}: {len(page_sponsors)} trials ({len(new_sponsors)} new, token changed, fetching more...)")
                    else:
                        print(f"  → Page {page_count}: {len(page_sponsors)} trials ({len(new_sponsors)} new, same token, fetching more...)")
                    previous_token = new_token
                else:
                    # No nextPageToken found
                    # Note: API bug - when pageSize >= 1000, it caps at 1000 and may not return nextPageToken
                    # We already check for partial pages above, so this is likely end
                    print(f"  ✓ Found {len(phase_sponsors)} {phase} trials (across {page_count} pages, no next token)")
                    break

            all_sponsors.extend(phase_sponsors)
            trials_by_phase[phase] = len(phase_sponsors)

        except Exception as e:
            print(f"  ✗ Error querying {phase}: {e}")
            trials_by_phase[phase] = 0

    # Deduplicate sponsors
    unique_sponsors = sorted(list(set(all_sponsors)))

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total trials: {len(all_sponsors)}")
    print(f"  Unique sponsors: {len(unique_sponsors)}")
    print(f"  By phase: {trials_by_phase}")
    print(f"{'='*60}\n")

    return {
        'quarter': f'{quarter} {year}',
        'total_trials': len(all_sponsors),
        'unique_sponsors': len(unique_sponsors),
        'sponsors': unique_sponsors,
        'by_phase': trials_by_phase
    }


# Make script executable
if __name__ == "__main__":
    # Default: Q4 2025
    result = get_trial_sponsors_by_quarter(
        quarter="Q4",
        year=2025,
        phases=["PHASE2", "PHASE3"],
        max_trials=10000
    )

    print(f"\n✓ Extracted {result['unique_sponsors']} unique sponsors from {result['total_trials']} trials")
    print(f"\nFirst 10 sponsors:")
    for i, sponsor in enumerate(result['sponsors'][:10], 1):
        print(f"  {i}. {sponsor}")

    if len(result['sponsors']) > 10:
        print(f"  ... and {len(result['sponsors']) - 10} more")
