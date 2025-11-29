#!/usr/bin/env python3
"""
PDUFA Date Tracker

Track PDUFA (FDA approval decision) dates by searching SEC EDGAR 8-K filings.
PDUFA dates are exact FDA decision deadlines announced when FDA accepts NDAs/BLAs.
"""

import sys
import re
import time
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
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


def track_pdufa_dates(
    quarter: str = "Q4",
    year: int = 2025,
    lookback_months: int = 12,
    companies: Optional[List[str]] = None,
    max_companies: int = 50
) -> Dict[str, any]:
    """Track PDUFA dates by searching SEC EDGAR 8-K filings.

    Returns:
        dict: Contains quarter, total_pdufa_dates, pdufa_dates list, and summary
    """
    # Define quarter date ranges
    quarter_ranges = {
        "Q1": (f"{year}-01-01", f"{year}-03-31"),
        "Q2": (f"{year}-04-01", f"{year}-06-30"),
        "Q3": (f"{year}-07-01", f"{year}-09-30"),
        "Q4": (f"{year}-10-01", f"{year}-12-31")
    }

    if quarter not in quarter_ranges:
        raise ValueError(f"Invalid quarter: {quarter}")

    target_start, target_end = quarter_ranges[quarter]

    # Calculate filing search date range
    try:
        from dateutil.relativedelta import relativedelta
        target_end_dt = datetime.strptime(target_end, "%Y-%m-%d")
        search_start_dt = target_end_dt - relativedelta(months=lookback_months)
        search_start = search_start_dt.strftime("%Y-%m-%d")
    except ImportError:
        search_start = f"{year-1}-{target_end[5:]}"

    print(f"Searching 8-K filings from {search_start} to {target_end}")
    print(f"Looking for PDUFA dates in {quarter} {year}")

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
            'total_pdufa_dates': 0,
            'pdufa_dates': [],
            'summary': generate_summary([], quarter, year)
        }

    all_pdufa_dates = []

    for company_name, cik in company_ciks:
        try:
            print(f"Searching {company_name} (CIK {cik})...")

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

            filings = filtered_8ks
            print(f"  Found {len(filings)} 8-K filings")

            for filing in filings:
                    pdufa_info = extract_pdufa_info(filing, target_start, target_end, cik)
                    if pdufa_info:
                        if not companies or any(c.lower() in pdufa_info['company'].lower()
                                              for c in companies):
                            if not any(p['pdufa_date'] == pdufa_info['pdufa_date'] and
                                     p['cik'] == pdufa_info['cik']
                                     for p in all_pdufa_dates):
                                all_pdufa_dates.append(pdufa_info)
        except Exception as e:
            print(f"  Error: {str(e)}")
            continue

    all_pdufa_dates.sort(key=lambda x: x['pdufa_date'])
    summary = generate_summary(all_pdufa_dates, quarter, year)

    return {
        'quarter': f"{quarter} {year}",
        'search_period': f"{search_start} to {target_end}",
        'total_pdufa_dates': len(all_pdufa_dates),
        'pdufa_dates': all_pdufa_dates,
        'summary': summary
    }


def extract_pdufa_info(filing: Dict, target_start: str, target_end: str, cik: str = '') -> Optional[Dict]:
    """Extract PDUFA info from filing."""
    # Download and extract text from 8-K filing
    filing_text = download_filing_text(filing, cik)

    if not filing_text:
        return None

    company = filing.get('company_name', filing.get('companyName', 'Unknown'))
    filing_date = filing.get('filing_date', filing.get('filingDate', ''))
    filing_url = filing.get('url', filing.get('link', ''))

    # PDUFA date patterns
    date_patterns = [
        r'PDUFA\s+date\s+of\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'target\s+action\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'FDA\s+action\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
    ]

    pdufa_date = None
    for pattern in date_patterns:
        match = re.search(pattern, filing_text, re.IGNORECASE)
        if match:
            pdufa_date = parse_date(match.group(1))
            if pdufa_date:
                break

    if not pdufa_date or not (target_start <= pdufa_date <= target_end):
        return None

    # Extract drug and indication
    drug_pattern = r'(?:for|regarding)\s+([A-Z][a-z]+(?:-[A-Z][a-z]+)?)'
    drug_match = re.search(drug_pattern, filing_text)
    drug_name = drug_match.group(1) if drug_match else "Unknown"

    indication = "Unknown"
    review_type = "Priority Review" if re.search(r'priority\s+review', filing_text, re.IGNORECASE) else "Standard Review"

    ticker_match = re.search(r'\(([A-Z]{2,5})\)', company)
    ticker = ticker_match.group(1) if ticker_match else None

    return {
        'company': company,
        'ticker': ticker,
        'drug': drug_name,
        'indication': indication,
        'pdufa_date': pdufa_date,
        'filing_date': filing_date,
        'review_type': review_type,
        'cik': cik,
        'filing_url': filing_url
    }


def parse_date(date_str: str) -> Optional[str]:
    """Parse date to YYYY-MM-DD."""
    formats = [
        "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y",
        "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y", "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def generate_summary(pdufa_dates: List[Dict], quarter: str, year: int) -> Dict:
    """Generate summary statistics."""
    if not pdufa_dates:
        return {'total': 0, 'by_review_type': {}, 'by_month': {}, 'companies': [], 'priority_review_percentage': 0}

    by_review_type = defaultdict(int)
    by_month = defaultdict(int)

    for pdufa in pdufa_dates:
        by_review_type[pdufa['review_type']] += 1
        by_month[pdufa['pdufa_date'][:7]] += 1

    companies = sorted(set(p['company'] for p in pdufa_dates))
    priority_pct = round(by_review_type.get('Priority Review', 0) / len(pdufa_dates) * 100, 1)

    return {
        'total': len(pdufa_dates),
        'by_review_type': dict(by_review_type),
        'by_month': dict(sorted(by_month.items())),
        'companies': companies,
        'priority_review_percentage': priority_pct
    }


if __name__ == "__main__":
    import json

    result = track_pdufa_dates(quarter="Q4", year=2025, lookback_months=12)

    print(f"\n{'='*80}")
    print(f"PDUFA Tracker: {result['quarter']}")
    print(f"{'='*80}\n")
    print(f"Total PDUFA Dates: {result['total_pdufa_dates']}\n")

    if result['summary']['total'] > 0:
        print("Summary:")
        print(f"  Priority: {result['summary']['by_review_type'].get('Priority Review', 0)}")
        print(f"  Standard: {result['summary']['by_review_type'].get('Standard Review', 0)}")

        print("\nBy Month:")
        for month, count in result['summary']['by_month'].items():
            print(f"  {month}: {count}")

        print(f"\nCompanies ({len(result['summary']['companies'])}): {', '.join(result['summary']['companies'][:5])}")

        print(f"\n{'='*80}")
        for i, pdufa in enumerate(result['pdufa_dates'][:3], 1):
            print(f"{i}. {pdufa['company']} - {pdufa['drug']}")
            print(f"   PDUFA: {pdufa['pdufa_date']} ({pdufa['review_type']})")
    else:
        print("No PDUFA dates found.")
        print("\nNote: MCP server may need configuration for full text access")

    print(f"\n{'='*80}")
    print(json.dumps({'quarter': result['quarter'], 'total': result['total_pdufa_dates'],
                     'summary': result['summary']}, indent=2))
