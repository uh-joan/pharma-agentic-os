#!/usr/bin/env python3
"""
Step 3: Lookup Ticker via SEC EDGAR

Uses SEC EDGAR's official company search API to find stock ticker symbols.
This eliminates the manual 4-6 hour ticker mapping bottleneck.

KEY INNOVATION: Fully automated ticker discovery using SEC EDGAR.

BENEFITS:
- Structured JSON response (not markdown text)
- Official SEC data (high accuracy)
- Already using SEC EDGAR for catalyst tracking (consistency)
- No need for web search or heuristic guessing

PRODUCTION READY: Uses sec_edgar_mcp server.
"""

import sys
import re
import time
from typing import List, Dict, Optional

sys.path.insert(0, ".claude")

from mcp.servers.sec_edgar_mcp import search_companies

# SEC EDGAR Rate Limiting
# Official limit: 10 requests/second
# We use 6-7 req/sec to be safe (same as catalyst tracking)
SEC_RATE_LIMIT_DELAY = 0.15  # 150ms = ~6.7 req/sec


def lookup_ticker_sec_edgar(company_name: str) -> Dict[str, any]:
    """Look up ticker symbol for company using SEC EDGAR.

    Args:
        company_name: Company name from ClinicalTrials.gov

    Returns:
        dict: {
            'company_name': 'AbbVie Inc.',
            'ticker': 'ABBV' or None,
            'exchange': 'NYSE' or None,
            'is_public': True/False,
            'confidence': 'high'/'medium'/'low',
            'reason': 'publicly traded' or 'not public' or 'no data found',
            'search_method': 'sec_edgar',
            'cik': '0001551152' or None
        }
    """
    # Clean company name
    clean_name = company_name.strip()

    try:
        # Query SEC EDGAR company search
        result = search_companies(clean_name)

        # Rate limiting for SEC EDGAR
        time.sleep(SEC_RATE_LIMIT_DELAY)

        # Check if any companies found
        companies = result.get('companies', [])

        if not companies:
            # No companies found
            return {
                'company_name': company_name,
                'ticker': None,
                'exchange': None,
                'is_public': False,  # Not in SEC EDGAR = not public
                'confidence': 'high',
                'reason': 'not public',
                'search_method': 'sec_edgar',
                'cik': None
            }

        # Take first (best) match
        company = companies[0]

        ticker = company.get('ticker', None)
        cik = company.get('cik', None)
        title = company.get('title', '')
        exchange = company.get('exchange', None)

        # Calculate name similarity for confidence
        similarity = calculate_name_similarity(clean_name, title)

        return {
            'company_name': company_name,
            'ticker': ticker if ticker else None,
            'exchange': exchange,
            'is_public': True,
            'confidence': 'high' if similarity > 0.8 else 'medium',
            'reason': 'publicly traded',
            'search_method': 'sec_edgar',
            'cik': cik,
            'sec_title': title,
            'similarity': similarity
        }

    except Exception as e:
        # Search failed
        return {
            'company_name': company_name,
            'ticker': None,
            'exchange': None,
            'is_public': None,  # Unknown
            'confidence': 'low',
            'reason': f'search error: {str(e)}',
            'search_method': 'sec_edgar',
            'cik': None
        }




def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two company names.

    Args:
        name1: First company name
        name2: Second company name

    Returns:
        float: Similarity score (0.0 to 1.0)
    """
    # Normalize names
    n1 = name1.upper().strip()
    n2 = name2.upper().strip()

    # Remove common suffixes
    for suffix in ['INC.', 'INC', 'LLC', 'LTD.', 'LTD', 'CORP.', 'CORP',
                   'CORPORATION', 'LIMITED', 'GMBH', 'S.A.', 'PLC', 'THE']:
        n1 = re.sub(rf'\b{suffix}\b', '', n1)
        n2 = re.sub(rf'\b{suffix}\b', '', n2)

    n1 = n1.strip()
    n2 = n2.strip()

    # Exact match
    if n1 == n2:
        return 1.0

    # Check if one contains the other
    if n1 in n2 or n2 in n1:
        return 0.9

    # Word overlap
    words1 = set(n1.split())
    words2 = set(n2.split())

    if not words1 or not words2:
        return 0.0

    overlap = len(words1 & words2)
    union = len(words1 | words2)

    return overlap / union if union > 0 else 0.0


def lookup_ticker_websearch(company_name: str) -> Dict[str, any]:
    """Alias for lookup_ticker_sec_edgar (for backward compatibility)."""
    return lookup_ticker_sec_edgar(company_name)




def lookup_tickers_batch(company_names: List[str], verbose: bool = True) -> Dict[str, any]:
    """Look up ticker symbols for multiple companies.

    Args:
        company_names: List of company names
        verbose: Print progress (default: True)

    Returns:
        dict: {
            'total_companies': 100,
            'tickers_found': 78,
            'not_public': 15,
            'no_data': 7,
            'companies_with_tickers': [{company_name, ticker, exchange, ...}, ...],
            'not_public_companies': ['Mayo Clinic', ...],
            'unknown_companies': ['XYZ Corp', ...]
        }
    """
    results_with_tickers = []
    not_public = []
    unknown = []

    total = len(company_names)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Looking Up Tickers for {total} Companies")
        print(f"{'='*60}\n")

    for i, company_name in enumerate(company_names, 1):
        if verbose:
            print(f"[{i}/{total}] {company_name}...", end=" ")

        result = lookup_ticker_websearch(company_name)

        if result['is_public'] == True and result['ticker']:
            results_with_tickers.append(result)
            if verbose:
                print(f"✓ {result['ticker']} ({result.get('exchange', 'N/A')})")

        elif result['is_public'] == False:
            not_public.append(company_name)
            if verbose:
                print(f"✗ Not public")

        else:
            unknown.append(company_name)
            if verbose:
                print(f"? No data")

    if verbose:
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Total companies: {total}")
        print(f"  Tickers found: {len(results_with_tickers)}")
        print(f"  Not public: {len(not_public)}")
        print(f"  No data: {len(unknown)}")
        print(f"  Success rate: {len(results_with_tickers) / total * 100:.1f}%")
        print(f"{'='*60}\n")

    return {
        'total_companies': total,
        'tickers_found': len(results_with_tickers),
        'not_public': len(not_public),
        'no_data': len(unknown),
        'companies_with_tickers': results_with_tickers,
        'not_public_companies': not_public,
        'unknown_companies': unknown
    }


# Make script executable
if __name__ == "__main__":
    # Test with known companies
    test_companies = [
        "AbbVie Inc.",
        "Amgen Inc",
        "Disc Medicine, Inc.",
        "Arcellx, Inc.",
        "Mayo Clinic",
        "Pfizer",
        "THERABIONIC GmbH",
    ]

    print("="*60)
    print("Testing SEC EDGAR Ticker Lookup")
    print("="*60)
    print("\nTesting with sample companies:\n")
    print("⚠️  Rate limited to ~6.7 req/sec for SEC EDGAR compliance\n")

    results = lookup_tickers_batch(test_companies, verbose=True)

    print("\n\nDetailed Results:")
    print("\n1. Companies with Tickers:")
    for company in results['companies_with_tickers']:
        print(f"   • {company['company_name']}: {company['ticker']} "
              f"({company.get('exchange', 'N/A')}) - Confidence: {company['confidence']}")

    if results['not_public_companies']:
        print("\n2. Not Public:")
        for company in results['not_public_companies']:
            print(f"   • {company}")

    if results['unknown_companies']:
        print("\n3. No Data Found:")
        for company in results['unknown_companies']:
            print(f"   • {company}")

    print("\n" + "="*60)
    print("✓ Ticker lookup test complete")
    print("="*60)
