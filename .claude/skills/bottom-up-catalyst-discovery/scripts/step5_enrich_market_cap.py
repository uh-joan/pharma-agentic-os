#!/usr/bin/env python3
"""
Step 5: Enrich with Market Cap from Yahoo Finance

Gets market capitalization data from Yahoo Finance for validated public companies.
Filters to investable companies (typically > $500M market cap).
"""

import sys
import re
from typing import List, Dict, Optional

sys.path.insert(0, ".claude")
from mcp.servers.financials_mcp import financial_intelligence


def extract_market_cap_from_markdown(markdown_text: str) -> Optional[float]:
    """Extract market cap value from Yahoo Finance markdown response.

    Args:
        markdown_text: Markdown string from financial_intelligence()

    Returns:
        float: Market cap in dollars, or None if not found
    """
    # Pattern: **Market Cap:** 123.45B USD
    # Handles B (billions), M (millions), T (trillions)

    # Try Market Cap first
    pattern = r'\*\*Market Cap:\*\*\s+([0-9,.]+)\s*([BMT])\s+USD'
    match = re.search(pattern, markdown_text, re.IGNORECASE)

    # If Market Cap not found or is N/A, try Enterprise Value as fallback
    if not match:
        # Market cap not found, try enterprise value
        pattern = r'\*\*Enterprise Value:\*\*\s+([0-9,.]+)\s*([BMT])\s+USD'
        match = re.search(pattern, markdown_text, re.IGNORECASE)

    if not match:
        return None

    value_str = match.group(1).replace(',', '')
    multiplier = match.group(2).upper()

    try:
        value = float(value_str)

        # Convert to dollars
        if multiplier == 'T':
            return value * 1_000_000_000_000
        elif multiplier == 'B':
            return value * 1_000_000_000
        elif multiplier == 'M':
            return value * 1_000_000
        else:
            return value

    except ValueError:
        return None


def get_market_cap_yahoo(ticker: str) -> Dict[str, any]:
    """Get market cap for ticker from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., "ABBV")

    Returns:
        dict: {
            'ticker': 'ABBV',
            'market_cap': 345000000000.0 or None,
            'market_cap_formatted': '$345.00B',
            'success': True/False,
            'error': None or error message
        }
    """
    try:
        # Get stock summary from Yahoo Finance
        result = financial_intelligence(
            method='stock_summary',
            symbol=ticker
        )

        # Extract market cap from markdown text
        markdown_text = result.get('text', '')
        market_cap = extract_market_cap_from_markdown(markdown_text)

        if market_cap:
            # Format for display
            if market_cap >= 1_000_000_000_000:
                formatted = f"${market_cap / 1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                formatted = f"${market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                formatted = f"${market_cap / 1_000_000:.2f}M"
            else:
                formatted = f"${market_cap:,.2f}"

            return {
                'ticker': ticker,
                'market_cap': market_cap,
                'market_cap_formatted': formatted,
                'success': True,
                'error': None
            }
        else:
            return {
                'ticker': ticker,
                'market_cap': None,
                'market_cap_formatted': None,
                'success': False,
                'error': 'Market cap not found in response'
            }

    except Exception as e:
        return {
            'ticker': ticker,
            'market_cap': None,
            'market_cap_formatted': None,
            'success': False,
            'error': str(e)
        }


def enrich_companies_with_market_cap(
    companies: List[Dict[str, any]],
    min_market_cap: float = 500_000_000,
    verbose: bool = True
) -> Dict[str, any]:
    """Enrich companies with market cap data and filter by size.

    Args:
        companies: List of dicts with 'ticker' field
        min_market_cap: Minimum market cap filter (default: $500M)
        verbose: Print progress (default: True)

    Returns:
        dict: {
            'total_input': 100,
            'enriched': 92,
            'errors': 8,
            'passed_filter': 78,
            'failed_filter': 14,
            'investable_companies': [{ticker, market_cap, ...}, ...],
            'too_small_companies': [{ticker, market_cap, ...}, ...],
            'error_companies': ['XYZ', ...]
        }
    """
    enriched = []
    errors = []

    total = len(companies)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Enriching {total} Companies with Market Cap Data")
        print(f"Minimum Market Cap Filter: ${min_market_cap / 1_000_000_000:.2f}B")
        print(f"{'='*60}\n")

    for i, company_data in enumerate(companies, 1):
        ticker = company_data.get('ticker')
        company_name = company_data.get('company_name', 'Unknown')

        if not ticker:
            errors.append(company_name)
            if verbose:
                print(f"[{i}/{total}] {company_name}: ✗ No ticker")
            continue

        if verbose:
            print(f"[{i}/{total}] {ticker} ({company_name})...", end=" ")

        result = get_market_cap_yahoo(ticker)

        if result['success']:
            # Merge market cap data with company data
            enriched_company = {
                **company_data,
                'market_cap': result['market_cap'],
                'market_cap_formatted': result['market_cap_formatted']
            }
            enriched.append(enriched_company)

            if verbose:
                print(f"✓ {result['market_cap_formatted']}")
        else:
            errors.append(ticker)
            if verbose:
                print(f"✗ {result['error']}")

    # Filter by market cap
    investable = [c for c in enriched if c['market_cap'] >= min_market_cap]
    too_small = [c for c in enriched if c['market_cap'] < min_market_cap]

    if verbose:
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Total input: {total}")
        print(f"  Enriched: {len(enriched)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Passed filter (≥ ${min_market_cap / 1_000_000_000:.2f}B): {len(investable)}")
        print(f"  Failed filter (< ${min_market_cap / 1_000_000_000:.2f}B): {len(too_small)}")
        print(f"  Success rate: {len(enriched) / total * 100:.1f}%")
        print(f"{'='*60}\n")

    return {
        'total_input': total,
        'enriched': len(enriched),
        'errors': len(errors),
        'passed_filter': len(investable),
        'failed_filter': len(too_small),
        'investable_companies': investable,
        'too_small_companies': too_small,
        'error_companies': errors
    }


# Make script executable
if __name__ == "__main__":
    # Test with validated companies
    test_companies = [
        {'company_name': 'AbbVie Inc.', 'ticker': 'ABBV', 'cik': '0001551152'},
        {'company_name': 'Amgen Inc', 'ticker': 'AMGN', 'cik': '0000318154'},
        {'company_name': 'Disc Medicine, Inc.', 'ticker': 'IRON', 'cik': '0001816736'},
        {'company_name': 'Arcellx, Inc.', 'ticker': 'ACLX', 'cik': '0001786205'},
        {'company_name': 'Pfizer', 'ticker': 'PFE', 'cik': '0000078003'},
    ]

    print("="*60)
    print("Testing Market Cap Enrichment via Yahoo Finance")
    print("="*60)
    print("\nEnriching sample companies:\n")

    results = enrich_companies_with_market_cap(
        test_companies,
        min_market_cap=500_000_000,  # $500M minimum
        verbose=True
    )

    print("\n\nDetailed Results:")

    print("\n1. Investable Companies (≥ $500M):")
    for company in results['investable_companies']:
        print(f"   • {company['ticker']}: {company['company_name']}")
        print(f"     Market Cap: {company['market_cap_formatted']}")
        print(f"     CIK: {company['cik']}")

    if results['too_small_companies']:
        print("\n2. Too Small (< $500M):")
        for company in results['too_small_companies']:
            print(f"   • {company['ticker']}: {company['company_name']}")
            print(f"     Market Cap: {company['market_cap_formatted']}")

    if results['error_companies']:
        print("\n3. Enrichment Errors:")
        for company in results['error_companies']:
            print(f"   • {company}")

    print("\n" + "="*60)
    print("✓ Market cap enrichment test complete")
    print("="*60)
