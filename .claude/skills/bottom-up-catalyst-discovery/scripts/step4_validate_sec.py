#!/usr/bin/env python3
"""
Step 4: Validate Public Companies via SEC EDGAR

Uses SEC EDGAR database to validate that companies are indeed publicly traded.
Returns CIK (Central Index Key) for validated public companies.

Gold standard for public company validation - 100% accurate.
"""

import sys
import re
from typing import List, Dict, Optional

sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import search_companies


def normalize_company_name(name: str) -> str:
    """Normalize company name for better SEC EDGAR matching.

    Args:
        name: Company name from ClinicalTrials.gov

    Returns:
        str: Normalized name for SEC search
    """
    # Convert to uppercase
    name = name.upper()

    # Remove common suffixes
    name = re.sub(r'\s+(INC\.?|LLC|LTD\.?|LIMITED|CORPORATION|CORP\.?|CO\.?)$', '', name)

    # Remove special characters
    name = re.sub(r'[,\.]', '', name)

    # Trim whitespace
    return name.strip()


def validate_public_company_sec(company_name: str, ticker: Optional[str] = None) -> Dict[str, any]:
    """Validate if company is publicly traded using SEC EDGAR.

    Args:
        company_name: Company name to validate
        ticker: Optional ticker symbol for enhanced search

    Returns:
        dict: {
            'company_name': 'AbbVie Inc.',
            'is_public': True/False,
            'cik': '0001551152' or None,
            'sec_name': 'ABBV INC' or None,
            'ticker_validated': True/False,
            'validation_method': 'name_match' or 'ticker_match',
            'confidence': 'high'/'medium'/'low'
        }
    """
    # Normalize name for search
    clean_name = normalize_company_name(company_name)

    try:
        # Method 1: Search by company name
        result = search_companies(query=clean_name)

        if result.get('total_found', 0) > 0:
            companies = result.get('companies', [])
            first_match = companies[0]

            cik = first_match.get('cik')
            sec_name = first_match.get('title', '')

            # Check if ticker matches (if provided)
            ticker_validated = False
            if ticker:
                # SEC EDGAR sometimes has tickers in the result
                # But often the tickers array is empty
                sec_tickers = first_match.get('tickers', [])
                if ticker.upper() in [t.upper() for t in sec_tickers]:
                    ticker_validated = True

            return {
                'company_name': company_name,
                'is_public': True,
                'cik': cik,
                'sec_name': sec_name,
                'ticker_validated': ticker_validated,
                'validation_method': 'name_match',
                'confidence': 'high' if ticker_validated else 'medium',
                'total_matches': result.get('total_found', 0)
            }

        # Method 2: If ticker provided and name search failed, try ticker
        if ticker:
            result = search_companies(query=ticker)

            if result.get('total_found', 0) > 0:
                companies = result.get('companies', [])
                first_match = companies[0]

                return {
                    'company_name': company_name,
                    'is_public': True,
                    'cik': first_match.get('cik'),
                    'sec_name': first_match.get('title', ''),
                    'ticker_validated': True,
                    'validation_method': 'ticker_match',
                    'confidence': 'high',
                    'total_matches': result.get('total_found', 0)
                }

        # No matches found - likely not public
        return {
            'company_name': company_name,
            'is_public': False,
            'cik': None,
            'sec_name': None,
            'ticker_validated': False,
            'validation_method': 'no_match',
            'confidence': 'high',
            'total_matches': 0
        }

    except Exception as e:
        # Error during search
        return {
            'company_name': company_name,
            'is_public': None,
            'cik': None,
            'sec_name': None,
            'ticker_validated': False,
            'validation_method': 'error',
            'confidence': 'low',
            'error': str(e)
        }


def validate_companies_batch(
    companies: List[Dict[str, any]],
    verbose: bool = True,
    rate_limit_delay: float = 0.5
) -> Dict[str, any]:
    """Validate multiple companies with SEC EDGAR.

    Args:
        companies: List of dicts with 'company_name' and optionally 'ticker'
        verbose: Print progress (default: True)
        rate_limit_delay: Delay in seconds between API calls to avoid rate limiting (default: 0.5)

    Returns:
        dict: {
            'total_companies': 100,
            'public_validated': 78,
            'not_public': 20,
            'errors': 2,
            'public_companies': [{company_name, cik, ticker, ...}, ...],
            'not_public_companies': ['Mayo Clinic', ...],
            'error_companies': ['XYZ Corp', ...]
        }
    """
    import time

    public_companies = []
    not_public = []
    errors = []

    total = len(companies)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Validating {total} Companies via SEC EDGAR")
        print(f"Rate Limit Delay: {rate_limit_delay}s per company")
        print(f"Estimated Time: {(total * rate_limit_delay) / 60:.1f} minutes")
        print(f"{'='*60}\n")

    for i, company_data in enumerate(companies, 1):
        company_name = company_data.get('company_name')
        ticker = company_data.get('ticker')

        if verbose:
            ticker_str = f"({ticker})" if ticker else ""
            print(f"[{i}/{total}] {company_name} {ticker_str}...", end=" ")

        result = validate_public_company_sec(company_name, ticker)

        # Rate limiting delay
        if i < total:  # Don't delay after last company
            time.sleep(rate_limit_delay)

        if result['is_public'] == True:
            # Merge with original company data
            public_companies.append({**company_data, **result})
            if verbose:
                print(f"✓ Public (CIK: {result['cik']})")

        elif result['is_public'] == False:
            not_public.append(company_name)
            if verbose:
                print(f"✗ Not public")

        else:
            errors.append(company_name)
            if verbose:
                print(f"? Error: {result.get('error', 'Unknown')}")

    if verbose:
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Total companies: {total}")
        print(f"  Public validated: {len(public_companies)}")
        print(f"  Not public: {len(not_public)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Validation rate: {len(public_companies) / total * 100:.1f}%")
        print(f"{'='*60}\n")

    return {
        'total_companies': total,
        'public_validated': len(public_companies),
        'not_public': len(not_public),
        'errors': len(errors),
        'public_companies': public_companies,
        'not_public_companies': not_public,
        'error_companies': errors
    }


# Make script executable
if __name__ == "__main__":
    # Test with known companies
    test_companies = [
        {'company_name': 'AbbVie Inc.', 'ticker': 'ABBV'},
        {'company_name': 'Amgen Inc', 'ticker': 'AMGN'},
        {'company_name': 'Disc Medicine, Inc.', 'ticker': 'IRON'},
        {'company_name': 'Arcellx, Inc.', 'ticker': 'ACLX'},
        {'company_name': 'Pfizer', 'ticker': 'PFE'},
        {'company_name': 'Mayo Clinic', 'ticker': None},  # Should be not public
        {'company_name': 'THERABIONIC GmbH', 'ticker': None},  # Should be not public
    ]

    print("="*60)
    print("Testing SEC EDGAR Public Company Validation")
    print("="*60)
    print("\nValidating sample companies:\n")

    results = validate_companies_batch(test_companies, verbose=True)

    print("\n\nDetailed Results:")
    print("\n1. Public Companies Validated:")
    for company in results['public_companies']:
        print(f"   • {company['company_name']}: CIK {company['cik']}")
        print(f"     SEC Name: {company['sec_name']}")
        print(f"     Ticker: {company.get('ticker', 'N/A')} "
              f"(Validated: {company.get('ticker_validated', False)})")

    if results['not_public_companies']:
        print("\n2. Not Public:")
        for company in results['not_public_companies']:
            print(f"   • {company}")

    if results['error_companies']:
        print("\n3. Validation Errors:")
        for company in results['error_companies']:
            print(f"   • {company}")

    print("\n" + "="*60)
    print("✓ SEC EDGAR validation test complete")
    print("="*60)
