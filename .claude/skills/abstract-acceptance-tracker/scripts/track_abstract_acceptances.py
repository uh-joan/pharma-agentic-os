#!/usr/bin/env python3
"""
Abstract Acceptance Tracker

Track conference abstract acceptance announcements by monitoring SEC 8-K filings.
Abstract acceptances are early signals of upcoming clinical data presentations 4-8 weeks before conferences.

Monitors major conferences: ASH, ASCO, ESMO, ADA, CTAD, ACC, AACR
"""

import sys
import re
import time
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from html.parser import HTMLParser

sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_submissions, search_companies


class HTML2Text(HTMLParser):
    """Convert HTML to plain text for SEC filing parsing."""
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ' '.join(self.text)


def download_filing_text(filing: Dict, cik: str) -> str:
    """Download and extract text from SEC EDGAR 8-K filing.

    Args:
        filing: Filing dict with accessionNumber and primaryDocument
        cik: Company CIK number

    Returns:
        str: Plain text content of the filing, or empty string if download fails
    """
    try:
        # Build SEC EDGAR URL
        cik_padded = cik.zfill(10)
        accession = filing.get('accessionNumber', '').replace('-', '')
        primary_doc = filing.get('primaryDocument', '')

        if not accession or not primary_doc:
            return ''

        url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession}/{primary_doc}"

        # SEC requires User-Agent with email
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Research/Analysis pharma-research@example.com'
        })

        # Rate limiting: SEC allows max 10 req/sec
        time.sleep(0.15)  # ~6-7 req/sec to be safe

        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')

        # Convert HTML to text
        parser = HTML2Text()
        parser.feed(html_content)
        text_content = parser.get_text()

        return text_content

    except Exception as e:
        # Silently fail - some filings may not be accessible
        return ''


def track_abstract_acceptances(
    quarter: str = "Q4",
    year: int = 2025,
    lookback_months: int = 6,
    companies: Optional[List[str]] = None,
    max_companies: int = 50,
    conferences: Optional[List[str]] = None,
    presentation_type: Optional[str] = None
) -> Dict[str, any]:
    """Track conference abstract acceptance announcements from SEC 8-K filings.

    Args:
        quarter: Target quarter (Q1, Q2, Q3, Q4)
        year: Target year
        lookback_months: How far back to search for announcements
        companies: Optional list of company names to search
        max_companies: Maximum number of companies to search (rate limiting)
        conferences: Optional list of conferences to filter (ASH, ASCO, etc.)
        presentation_type: Optional filter for 'oral' or 'poster'

    Returns:
        dict: Contains abstract acceptances found and summary
    """

    # Define quarter date ranges
    quarters = {
        'Q1': ('01-01', '03-31'),
        'Q2': ('04-01', '06-30'),
        'Q3': ('07-01', '09-30'),
        'Q4': ('10-01', '12-31')
    }

    target_start = f"{year}-{quarters[quarter][0]}"
    target_end = f"{year}-{quarters[quarter][1]}"

    # Search window for announcements
    search_start = (datetime.strptime(target_start, '%Y-%m-%d') - timedelta(days=lookback_months*30)).strftime('%Y-%m-%d')

    print(f"Searching 8-K filings from {search_start} to {target_end}")
    print(f"Looking for abstract acceptances with conferences in {quarter} {year}\n")

    # Convert company names to CIKs
    company_ciks = []
    if companies:
        # Limit to max_companies to avoid rate limiting
        companies_to_search = companies[:max_companies]
        print(f"Converting {len(companies_to_search)} company names to CIKs...\n")

        for company_name in companies_to_search:
            try:
                # Search SEC EDGAR for company
                result = search_companies(query=company_name)

                # Extract CIK from result
                if result and 'companies' in result and result['companies']:
                    cik = result['companies'][0].get('cik')
                    if cik:
                        company_ciks.append((company_name, cik))
                        print(f"  ✓ {company_name}: {cik}")
                    else:
                        print(f"  ✗ {company_name}: No CIK found")
                else:
                    print(f"  ✗ {company_name}: No results")
            except Exception as e:
                print(f"  ✗ {company_name}: Error - {str(e)}")
                continue

        print(f"\nFound CIKs for {len(company_ciks)} companies\n")
    else:
        # No companies provided - return empty results
        print("No companies provided")
        return {
            'quarter': f"{quarter} {year}",
            'search_period': f"{search_start} to {target_end}",
            'total_acceptances': 0,
            'acceptances': [],
            'summary': generate_summary([])
        }

    acceptances = []

    # Search each company's 8-K filings
    for company, cik in company_ciks:
        try:
            print(f"Searching {company}...", end=" ")

            # Get all company submissions
            result = get_company_submissions(cik_or_ticker=cik)

            # Manual filter for 8-K filings in date range (filter_filings is broken)
            recent_filings = result.get('recentFilings', [])
            filtered_8ks = []

            for filing in recent_filings:
                if filing.get('form') == '8-K':
                    filing_date = filing.get('filingDate', '')
                    if filing_date and search_start <= filing_date <= target_end:
                        filtered_8ks.append(filing)

            print(f"Found {len(filtered_8ks)} 8-K filings")
            for filing in filtered_8ks:
                    # Extract abstract acceptance info from filing
                    abstract_info = extract_abstract_info(filing, target_start, target_end, cik)
                    if abstract_info:
                        abstract_info['company'] = company
                        abstract_info['cik'] = cik

                        # Apply filters if specified
                        if conferences and abstract_info['conference_name'] not in conferences:
                            continue
                        if presentation_type and abstract_info['presentation_type'].lower() != presentation_type.lower():
                            continue

                        acceptances.append(abstract_info)
            else:
                print("No filings found")
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

    # Remove duplicates and sort by conference date
    acceptances = remove_duplicates(acceptances)
    acceptances.sort(key=lambda x: x.get('conference_start_date', '9999-12-31'))

    return {
        'quarter': f"{quarter} {year}",
        'search_period': f"{search_start} to {target_end}",
        'total_acceptances': len(acceptances),
        'acceptances': acceptances,
        'summary': generate_summary(acceptances)
    }


def extract_abstract_info(filing: dict, target_start: str, target_end: str, cik: str = '') -> Optional[dict]:
    """Extract abstract acceptance information from filing."""
    # Download and extract text from 8-K filing
    filing_text = download_filing_text(filing, cik)

    if not filing_text:
        return None

    # Look for abstract acceptance keywords
    abstract_patterns = [
        r'abstract.*?accept',
        r'accepted.*?present',
        r'oral presentation',
        r'poster presentation',
        r'data.*?presented at'
    ]

    for pattern in abstract_patterns:
        matches = re.finditer(pattern, filing_text, re.IGNORECASE)

        for match in matches:
            # Extract context around the match
            context_start = max(0, match.start() - 500)
            context_end = min(len(filing_text), match.end() + 500)
            context = filing_text[context_start:context_end]

            # Detect conference
            conference_info = detect_conference(context)
            if not conference_info:
                continue

            # Check if conference dates fall in target quarter
            if conference_info['start_date']:
                if not (target_start <= conference_info['start_date'] <= target_end):
                    continue

            # Detect presentation type
            pres_type = detect_presentation_type(context)

            # Extract drug and indication
            drug = extract_drug_name(context)
            indication = extract_indication(context)

            # Extract trial ID
            trial_id = extract_trial_id(context)

            # Get ticker if available
            ticker = extract_ticker(filing_text)

            return {
                'drug': drug,
                'indication': indication,
                'conference': conference_info['name'],
                'conference_name': conference_info['short_name'],
                'conference_dates': conference_info['date_range'],
                'conference_start_date': conference_info['start_date'],
                'presentation_type': pres_type,
                'filing_date': filing.get('filing_date'),
                'trial_id': trial_id,
                'ticker': ticker,
                'filing_url': filing.get('url')
            }

    return None


def detect_conference(text: str) -> Optional[dict]:
    """Detect conference name and dates from text."""
    # Conference name patterns
    conference_patterns = {
        'ASH': r'(American Society of Hematology|ASH)\s+(?:Annual\s+Meeting\s+)?20(\d{2})',
        'ASCO': r'(American Society of Clinical Oncology|ASCO)\s+(?:Annual\s+Meeting\s+)?20(\d{2})',
        'ESMO': r'(European Society for Medical Oncology|ESMO)\s+(?:Congress\s+)?20(\d{2})',
        'ADA': r'(American Diabetes Association|ADA)\s+(?:Scientific\s+Sessions\s+)?20(\d{2})',
        'CTAD': r'(Clinical Trials on Alzheimer\'s Disease|CTAD)\s+(?:Conference\s+)?20(\d{2})',
        'ACC': r'(American College of Cardiology|ACC)\s+(?:Annual\s+Scientific\s+Session\s+)?20(\d{2})',
        'AACR': r'(American Association for Cancer Research|AACR)\s+(?:Annual\s+Meeting\s+)?20(\d{2})'
    }

    for short_name, pattern in conference_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            year = match.group(2)
            full_year = f"20{year}"

            # Typical conference dates (rough estimates)
            conference_dates = {
                'ASH': ('12-07', '12-10'),  # Early December
                'ASCO': ('06-02', '06-06'),  # Early June
                'ESMO': ('09-08', '09-12'),  # September
                'ADA': ('06-23', '06-27'),  # Late June
                'CTAD': ('10-29', '11-01'),  # October/November
                'ACC': ('03-16', '03-18'),  # March
                'AACR': ('04-05', '04-10')   # April
            }

            if short_name in conference_dates:
                start, end = conference_dates[short_name]
                date_range = f"{full_year}-{start} to {full_year}-{end}"
                start_date = f"{full_year}-{start}"
            else:
                date_range = f"{full_year}"
                start_date = f"{full_year}-01-01"

            return {
                'name': f"{short_name} {full_year}",
                'short_name': short_name,
                'date_range': date_range,
                'start_date': start_date
            }

    return None


def detect_presentation_type(text: str) -> str:
    """Detect if presentation is oral or poster."""
    text_lower = text.lower()

    # Check for oral presentation
    oral_patterns = [
        r'oral\s+presentation',
        r'oral\s+abstract',
        r'plenary\s+presentation',
        r'late-breaking\s+abstract'
    ]

    for pattern in oral_patterns:
        if re.search(pattern, text_lower):
            return 'Oral'

    # Check for poster
    poster_patterns = [
        r'poster\s+presentation',
        r'poster\s+abstract',
        r'poster\s+session'
    ]

    for pattern in poster_patterns:
        if re.search(pattern, text_lower):
            return 'Poster'

    return 'Unknown'


def extract_drug_name(text: str) -> str:
    """Extract drug name from context."""
    # Look for capitalized drug names or generic names
    drug_pattern = r'\b([A-Z][a-z]+(?:-[A-Z][a-z]+)?(?:mab|tinib|stat)?)\b'
    matches = re.findall(drug_pattern, text)

    # Filter out common words
    stop_words = {'The', 'This', 'These', 'Company', 'Data', 'Results', 'Study', 'Trial'}
    candidates = [m for m in matches if m not in stop_words]

    return candidates[0] if candidates else 'Unknown'


def extract_indication(text: str) -> str:
    """Extract indication from context."""
    indication_keywords = ['for', 'treatment of', 'indicated for', 'in patients with', 'for the treatment of']

    for keyword in indication_keywords:
        if keyword in text.lower():
            idx = text.lower().find(keyword)
            snippet = text[idx:idx+150]
            # Extract until period or comma
            indication = snippet.split('.')[0].split(',')[0].strip()
            # Clean up
            indication = re.sub(r'^\s*for\s+(?:the\s+)?(?:treatment\s+of\s+)?', '', indication, flags=re.IGNORECASE)
            if len(indication) > 10 and len(indication) < 100:
                return indication

    return 'Unknown'


def extract_trial_id(text: str) -> Optional[str]:
    """Extract NCT trial ID from text."""
    nct_pattern = r'NCT\d{8}'
    match = re.search(nct_pattern, text)
    return match.group(0) if match else None


def extract_ticker(text: str) -> Optional[str]:
    """Extract stock ticker from filing text."""
    ticker_pattern = r'NASDAQ:\s*([A-Z]{2,5})|NYSE:\s*([A-Z]{2,5})'
    match = re.search(ticker_pattern, text)
    if match:
        return match.group(1) or match.group(2)
    return None


def remove_duplicates(acceptances: List[dict]) -> List[dict]:
    """Remove duplicate abstract acceptances."""
    seen = set()
    unique = []
    for item in acceptances:
        # Key based on company, conference, and drug
        key = (item['company'], item['conference'], item['drug'])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def generate_summary(acceptances: List[dict]) -> dict:
    """Generate summary statistics."""
    by_conference = {}
    by_presentation_type = {}

    for item in acceptances:
        conf = item['conference_name']
        pres_type = item['presentation_type']

        by_conference[conf] = by_conference.get(conf, 0) + 1
        by_presentation_type[pres_type] = by_presentation_type.get(pres_type, 0) + 1

    total_oral = by_presentation_type.get('Oral', 0)
    total = len(acceptances)
    oral_percentage = round((total_oral / total * 100), 1) if total > 0 else 0

    return {
        'total': total,
        'by_conference': dict(sorted(by_conference.items(), key=lambda x: x[1], reverse=True)),
        'by_presentation_type': by_presentation_type,
        'oral_percentage': oral_percentage
    }


if __name__ == "__main__":
    # Demo with Q4 2025 example
    result = track_abstract_acceptances(quarter="Q4", year=2025, lookback_months=6)

    print(f"\n{'='*80}")
    print(f"Conference Abstract Acceptance Tracker: {result['quarter']}")
    print(f"{'='*80}\n")
    print(f"Total Abstract Acceptances: {result['total_acceptances']}\n")

    if result['acceptances']:
        print("Recent Abstract Acceptances:")
        for i, item in enumerate(result['acceptances'][:5], 1):
            print(f"\n{i}. {item['company']} ({item.get('ticker', 'N/A')})")
            print(f"   Drug: {item['drug']}")
            print(f"   Indication: {item['indication']}")
            print(f"   Conference: {item['conference']}")
            print(f"   Conference Dates: {item['conference_dates']}")
            print(f"   Presentation Type: {item['presentation_type']}")
            if item['trial_id']:
                print(f"   Trial ID: {item['trial_id']}")
            print(f"   Filing Date: {item['filing_date']}")

        print(f"\n{'='*80}")
        print("Summary Statistics:")
        print(f"{'='*80}")
        print(f"\nTotal Acceptances: {result['summary']['total']}")

        if result['summary']['by_conference']:
            print(f"\nBy Conference:")
            for conf, count in result['summary']['by_conference'].items():
                print(f"  {conf}: {count}")

        if result['summary']['by_presentation_type']:
            print(f"\nBy Presentation Type:")
            for ptype, count in result['summary']['by_presentation_type'].items():
                print(f"  {ptype}: {count}")

        print(f"\nOral Presentation Rate: {result['summary']['oral_percentage']}%")
    else:
        print("No abstract acceptances found for this quarter.")
        print("\nNote: SEC EDGAR MCP may need configuration for full 8-K text access")

    print(f"\n{'='*80}")
