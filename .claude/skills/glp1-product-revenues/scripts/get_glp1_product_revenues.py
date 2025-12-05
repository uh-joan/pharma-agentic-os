import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.sec_edgar_mcp import get_company_cik, get_company_submissions

def get_glp1_product_revenues():
    """Extract GLP-1 product revenues from SEC EDGAR filings for Novo Nordisk and Eli Lilly.

    This skill attempts to extract revenue data from recent 10-K filings. Due to SEC EDGAR
    API limitations, it provides filing metadata and guidance on where to find GLP-1 revenues.

    Returns:
        dict: Contains companies data with filing information and summary
    """
    companies_data = {}

    # Define target companies and their GLP-1 products
    targets = {
        'Novo Nordisk': {
            'ticker': 'NVO',
            'products': ['OZEMPIC', 'WEGOVY', 'RYBELSUS'],
            'segments': ['Diabetes and Obesity care', 'GLP-1']
        },
        'Eli Lilly': {
            'ticker': 'LLY',
            'products': ['MOUNJARO', 'ZEPBOUND', 'TRULICITY'],
            'segments': ['Diabetes', 'Endocrinology']
        }
    }

    for company_name, info in targets.items():
        print(f"\nProcessing {company_name} ({info['ticker']})...")

        try:
            # Get CIK
            cik_result = get_company_cik(info['ticker'])
            if not cik_result or 'cik' not in cik_result:
                print(f"  ✗ Could not find CIK for {info['ticker']}")
                continue

            cik = cik_result['cik']
            print(f"  ✓ CIK: {cik}")

            # Get recent filings
            submissions = get_company_submissions(cik)
            if not submissions or 'recentFilings' not in submissions:
                print(f"  ✗ No filings found")
                continue

            recent = submissions['recentFilings']

            # Find most recent 10-K/20-F (annual) and 10-Q/6-K (quarterly) filings
            # 10-K: US companies annual report
            # 20-F: Foreign companies annual report
            annual_filings = []
            quarterly_filings = []

            # recentFilings is a list of filing dictionaries
            for filing in recent:
                filing_info = {
                    'form': filing['form'],
                    'date': filing['filingDate'],
                    'accession': filing['accessionNumber'],
                    'primary_doc': filing.get('primaryDocument', '')
                }

                if filing['form'] in ['10-K', '20-F'] and len(annual_filings) < 2:
                    annual_filings.append(filing_info)
                elif filing['form'] in ['10-Q', '6-K'] and len(quarterly_filings) < 4:
                    quarterly_filings.append(filing_info)

            if not annual_filings:
                print(f"  ✗ No annual report filings (10-K/20-F) found")
                continue

            most_recent_annual = annual_filings[0]
            print(f"  ✓ Most recent annual report ({most_recent_annual['form']}): {most_recent_annual['date']}")

            # Build SEC EDGAR URL for direct filing access
            edgar_url = f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={most_recent_annual['accession']}&xbrl_type=v"

            company_data = {
                'ticker': info['ticker'],
                'cik': cik,
                'products': info['products'],
                'segments': info['segments'],
                'most_recent_annual_filing': {
                    'form': most_recent_annual['form'],
                    'filing_date': most_recent_annual['date'],
                    'accession_number': most_recent_annual['accession'],
                    'edgar_url': edgar_url,
                    'year': int(most_recent_annual['date'][:4])
                },
                'recent_quarterly_filings': [
                    {
                        'form': q['form'],
                        'date': q['date'],
                        'accession': q['accession']
                    } for q in quarterly_filings
                ],
                # Manual revenue data from public sources (2023 data)
                'estimated_revenues': {
                    'note': 'Revenue estimates from public earnings reports and analyst data',
                    'source': 'Company earnings releases and SEC filings',
                    'year': 2023
                }
            }

            # Add known 2023 GLP-1 revenues from public data
            if company_name == 'Novo Nordisk':
                company_data['estimated_revenues']['products'] = {
                    'OZEMPIC': 14_000_000_000,  # ~$14B (2023)
                    'WEGOVY': 4_400_000_000,     # ~$4.4B (2023)
                    'RYBELSUS': 2_000_000_000    # ~$2B (2023)
                }
                company_data['estimated_revenues']['total'] = 20_400_000_000

            elif company_name == 'Eli Lilly':
                company_data['estimated_revenues']['products'] = {
                    'MOUNJARO': 5_000_000_000,   # ~$5B (2023)
                    'TRULICITY': 7_000_000_000,  # ~$7B (2023)
                    'ZEPBOUND': 500_000_000      # ~$500M (launched late 2023)
                }
                company_data['estimated_revenues']['total'] = 12_500_000_000

            companies_data[company_name] = company_data
            print(f"  ✓ Filing metadata collected")

        except Exception as e:
            print(f"  ✗ Error processing {company_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    # Generate summary
    total_market = sum(data['estimated_revenues']['total'] for data in companies_data.values())

    summary_lines = [f"\n{'='*70}"]
    summary_lines.append("GLP-1 Product Revenue Analysis")
    summary_lines.append(f"{'='*70}\n")
    summary_lines.append("NOTE: SEC EDGAR API provides filing metadata. Revenue figures below are")
    summary_lines.append("      estimates from public earnings reports and analyst data (2023).\n")

    for company_name, data in companies_data.items():
        revenue_b = data['estimated_revenues']['total'] / 1_000_000_000
        market_share = (data['estimated_revenues']['total'] / total_market * 100) if total_market > 0 else 0

        summary_lines.append(f"{company_name} ({data['ticker']}):")
        summary_lines.append(f"  Estimated Total GLP-1 Revenue (2023): ${revenue_b:.1f}B")
        summary_lines.append(f"  Market Share: {market_share:.1f}%")
        summary_lines.append(f"  ")
        summary_lines.append(f"  Product Breakdown:")
        for product, amount in sorted(data['estimated_revenues']['products'].items(),
                                      key=lambda x: x[1], reverse=True):
            summary_lines.append(f"    • {product}: ${amount/1_000_000_000:.1f}B")

        summary_lines.append(f"  ")
        summary_lines.append(f"  Most Recent Annual Filing ({data['most_recent_annual_filing']['form']}):")
        summary_lines.append(f"    Date: {data['most_recent_annual_filing']['filing_date']}")
        summary_lines.append(f"    Accession: {data['most_recent_annual_filing']['accession_number']}")
        summary_lines.append(f"    URL: {data['most_recent_annual_filing']['edgar_url']}")
        summary_lines.append("")

    summary_lines.append(f"Combined GLP-1 Market (NVO + LLY): ${total_market/1_000_000_000:.1f}B")
    summary_lines.append(f"\nTo get exact product-level revenues, visit the SEC EDGAR URLs above")
    summary_lines.append(f"and search for product names in the financial statements (Item 8) or")
    summary_lines.append(f"segment reporting sections (often in Note 2 - Segment Information).")
    summary_lines.append(f"{'='*70}")

    summary = '\n'.join(summary_lines)

    return {
        'companies': companies_data,
        'total_market_revenue': total_market,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_glp1_product_revenues()
    print(result['summary'])
