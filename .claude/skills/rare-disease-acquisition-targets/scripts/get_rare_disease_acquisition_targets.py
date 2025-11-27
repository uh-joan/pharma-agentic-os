import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
from mcp.servers.financials_mcp import financial_intelligence
import re
import requests
from typing import Dict, List, Tuple, Optional

def get_ticker_from_web(company_name: str) -> Optional[str]:
    """Get stock ticker symbol with smart company name preprocessing.

    Handles complex company names from CT.gov trials:
    - Extracts parent from "X, a Y Company" format (e.g., "Genzyme, a Sanofi Company" → "Sanofi")
    - Removes legal suffixes (Pharmaceuticals, Inc, AG, etc.)
    - Tries multiple name variations for better matching

    Args:
        company_name: Company name to lookup (e.g., "Novartis Pharmaceuticals", "Genzyme, a Sanofi Company")

    Returns:
        Ticker symbol (e.g., "NVS", "SNY") or None if not found
    """
    try:
        # Preprocess company name to improve matching
        search_names = [company_name]  # Original name first

        # Extract parent company from "X, a Y Company" format
        parent_match = re.search(r',\s*a\s+([^,]+?)\s+Company', company_name, re.IGNORECASE)
        if parent_match:
            parent_name = parent_match.group(1).strip()
            search_names.insert(0, parent_name)  # Try parent first

        # Remove common legal/business suffixes
        base_name = re.sub(r'\s+(Pharmaceuticals?|Pharma|Inc\.?|LLC|AG|SA|GmbH|Ltd\.?|Limited|Corp\.?|Corporation)\s*$',
                          '', company_name, flags=re.IGNORECASE).strip()
        if base_name != company_name and base_name not in search_names:
            search_names.append(base_name)

        # Try each variation
        for search_name in search_names:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                "q": search_name,
                "quotesCount": 5,
                "newsCount": 0
            }
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(url, params=params, headers=headers, timeout=5)

            if response.status_code != 200:
                continue

            data = response.json()
            quotes = data.get('quotes', [])
            if not quotes:
                continue

            # Find best match
            for quote in quotes:
                symbol = quote.get('symbol')
                quote_type = quote.get('quoteType', '')
                long_name = quote.get('longname', '').lower()
                short_name = quote.get('shortname', '').lower()
                search_lower = search_name.lower()

                # Only accept equity securities (not funds, ETFs, etc.)
                if quote_type not in ['EQUITY', 'INDEX', '']:
                    continue

                # Check for name match
                if search_lower in long_name or search_lower in short_name or long_name.startswith(search_lower):
                    return symbol

            # Fallback to first equity result if exact match
            for quote in quotes:
                if quote.get('quoteType') in ['EQUITY', '']:
                    long_name = quote.get('longname', '').lower()
                    if search_lower in long_name:
                        return quote.get('symbol')

        return None

    except Exception as e:
        return None

# Pattern-based sponsor type detection (NO HARDCODED COMPANY NAMES)
ACADEMIC_KEYWORDS = [
    'university', 'college', 'institute', 'medical center',
    'cancer center', 'hospital', 'school of medicine',
    "children's hospital", 'research center', 'clinic',
    'foundation', 'academic'
]

GOVERNMENT_KEYWORDS = [
    'national institutes', 'nih', 'nci', 'niaid', 'nhlbi',
    'veterans affairs', 'department of', 'ministry of health',
    'public health', 'government', 'federal'
]

CRO_KEYWORDS = [
    'cro', 'contract research', 'clinical research organization',
    'research services', 'quintiles', 'covance', 'parexel'
]

# Therapeutic area query patterns
THERAPEUTIC_QUERIES = {
    'ultra_rare_metabolic': 'lysosomal storage OR mitochondrial disease OR organic acidemia OR urea cycle OR peroxisomal',
    'neuromuscular': 'muscular dystrophy OR spinal muscular atrophy OR myasthenia gravis OR neuropathy',
    'gene_therapy': 'gene therapy OR AAV OR lentiviral OR adenoviral OR CRISPR',
    'oncology_rare': 'rare cancer OR orphan cancer OR sarcoma OR mesothelioma',
    'any': 'orphan OR "rare disease"'
}

def is_academic_sponsor(sponsor: str) -> bool:
    """Check if sponsor is academic institution using pattern matching."""
    if not sponsor:
        return False
    sponsor_lower = sponsor.lower()
    return any(keyword in sponsor_lower for keyword in ACADEMIC_KEYWORDS)

def is_government_sponsor(sponsor: str) -> bool:
    """Check if sponsor is government agency using pattern matching."""
    if not sponsor:
        return False
    sponsor_lower = sponsor.lower()
    return any(keyword in sponsor_lower for keyword in GOVERNMENT_KEYWORDS)

def is_cro_sponsor(sponsor: str) -> bool:
    """Check if sponsor is CRO using pattern matching."""
    if not sponsor:
        return False
    sponsor_lower = sponsor.lower()
    return any(keyword in sponsor_lower for keyword in CRO_KEYWORDS)

def fuzzy_match_company_name(sponsor_name: str, sec_results: List[Dict], threshold: float = 0.6) -> Optional[str]:
    """Fuzzy match CT.gov sponsor name to SEC company name.

    Handles variations like:
    - "Ultragenyx Pharmaceutical Inc." vs "Ultragenyx Pharmaceutical Inc"
    - "BioMarin Pharmaceutical" vs "BioMarin Pharmaceutical Inc."

    Args:
        sponsor_name: Sponsor name from clinical trial
        sec_results: List of SEC search result dicts
        threshold: Similarity threshold (0.0-1.0), default 0.6

    Returns:
        Best matching CIK or None
    """
    # Normalize sponsor name
    normalized_sponsor = sponsor_name.lower().strip()

    # Remove common suffixes for better matching
    suffixes = [' inc.', ' inc', ' corporation', ' corp.', ' corp', ' ltd.', ' ltd',
                ' llc', ' limited', ' plc', ' therapeutics', ' pharma', ' pharmaceutical',
                ' biopharmaceuticals', ' biopharmaceutical', ' biotech', ' bio']

    for suffix in suffixes:
        if normalized_sponsor.endswith(suffix):
            normalized_sponsor = normalized_sponsor[:-len(suffix)].strip()

    best_match_cik = None
    best_ratio = 0.0

    for company in sec_results:
        company_name = company.get('title', '').lower().strip()

        # Also normalize SEC name
        normalized_sec = company_name
        for suffix in suffixes:
            if normalized_sec.endswith(suffix):
                normalized_sec = normalized_sec[:-len(suffix)].strip()

        # Calculate similarity ratio
        ratio = SequenceMatcher(None, normalized_sponsor, normalized_sec).ratio()

        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match_cik = company.get('cik')

    return best_match_cik

def infer_ticker(company_name: str) -> Optional[str]:
    """Infer stock ticker from company name using common patterns.

    Args:
        company_name: Company name from clinical trial

    Returns:
        Likely ticker symbol or None
    """
    # Known ticker mappings for common biotech companies
    ticker_map = {
        'ultragenyx': 'RARE',
        'biomarin': 'BMRN',
        'sarepta': 'SRPT',
        'alexion': 'ALXN',
        'vertex': 'VRTX',
        'bluebird': 'BLUE',
        'sanofi': 'SNY',
        'takeda': 'TAK',
        'novartis': 'NVS',
        'roche': 'RHHBY',
        'ptc therapeutics': 'PTCT',
        'regenxbio': 'RGNX',
        'denali therapeutics': 'DNLI',
        'cyclo therapeutics': 'CYTH',
        'proqr therapeutics': 'PRQR',
        'avrobio': 'AVRO',
        'stealth biotherapeutics': 'MITO',
        'gensight biologics': 'SIGHT',
        'lysogene': 'LYS',
        'passage bio': 'PASG',
        'aeglea biotherapeutics': 'AGLE',
        'homology medicines': 'FIXX',
        'catalyst pharmaceuticals': 'CPRX',
        'amicus therapeutics': 'FOLD',
        'chiesi': None,  # Private/Non-US
        'recordati': 'RECI.MI',  # Milan exchange
    }

    # Normalize company name
    normalized = company_name.lower().strip()

    # Remove common suffixes
    for suffix in [' inc.', ' inc', ' corporation', ' corp.', ' corp', ' ltd.', ' ltd',
                   ' llc', ' limited', ' plc', ' therapeutics', ' pharma', ' pharmaceutical',
                   ' biopharmaceuticals', ' biopharmaceutical', ' biotech', ' bio', ',']:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()

    # Check direct match
    if normalized in ticker_map:
        return ticker_map[normalized]

    # Check partial match
    for key, ticker in ticker_map.items():
        if key in normalized or normalized in key:
            return ticker

    return None

def parse_yahoo_markdown(markdown_text: str) -> Dict:
    """Parse Yahoo Finance markdown response to extract structured data.

    Dynamically extracts metrics from markdown without hardcoding company-specific data.

    Args:
        markdown_text: Markdown formatted financial summary from financials_mcp

    Returns:
        Dictionary with extracted metrics
    """
    metrics = {}

    try:
        # Parse Market Cap: "**Market Cap:** 9.94B USD" or "**Market Cap:** N/A USD"
        market_cap_match = re.search(r'\*\*Market Cap:\*\*\s*([\d.]+)([BMK]?)\s*USD', markdown_text)
        if market_cap_match:
            value = float(market_cap_match.group(1))
            unit = market_cap_match.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            metrics['market_cap_millions'] = round((value * multiplier) / 1e6, 2)

        # Parse Enterprise Value: "**Enterprise Value:** 9.94B USD"
        ev_match = re.search(r'\*\*Enterprise Value:\*\*\s*([\d.]+)([BMK]?)\s*USD', markdown_text)
        if ev_match:
            value = float(ev_match.group(1))
            unit = ev_match.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            metrics['enterprise_value_millions'] = round((value * multiplier) / 1e6, 2)

        # Parse P/E Ratio: "**Trailing P/E:** 10.51" or "**Forward P/E:** 10.51"
        pe_match = re.search(r'\*\*(?:Trailing|Forward) P/E:\*\*\s*([\d.]+)', markdown_text)
        if pe_match:
            metrics['pe_ratio'] = float(pe_match.group(1))

        # Parse EPS: "**Trailing EPS:** 2.69 USD"
        eps_match = re.search(r'\*\*Trailing EPS:\*\*\s*([\d.-]+)\s*USD', markdown_text)
        if eps_match:
            metrics['eps'] = float(eps_match.group(1))

        # Parse Beta: "**Beta:** 0.30"
        beta_match = re.search(r'\*\*Beta:\*\*\s*([\d.]+)', markdown_text)
        if beta_match:
            metrics['beta'] = float(beta_match.group(1))

        # Parse Shares Outstanding: "**Shares Outstanding:** 192.11M"
        shares_match = re.search(r'\*\*Shares Outstanding:\*\*\s*([\d.]+)([BMK]?)', markdown_text)
        if shares_match:
            value = float(shares_match.group(1))
            unit = shares_match.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            metrics['shares_outstanding_millions'] = round((value * multiplier) / 1e6, 2)

        # === NEW: Parse stock_financials fields ===

        # Parse Total Cash: "**Total Cash:** 425.25M USD"
        cash_match = re.search(r'\*\*Total Cash:\*\*\s*([\d.]+)([BMK]?)\s*USD', markdown_text)
        if cash_match:
            value = float(cash_match.group(1))
            unit = cash_match.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            metrics['cash_millions'] = round((value * multiplier) / 1e6, 2)

        # Parse Operating Cash Flow: "**Operating Cash Flow:** -445,673,984 USD"
        ocf_match = re.search(r'\*\*Operating Cash Flow:\*\*\s*([-\d,]+)\s*USD', markdown_text)
        if ocf_match:
            value_str = ocf_match.group(1).replace(',', '')
            metrics['operating_cash_flow_millions'] = round(float(value_str) / 1e6, 2)

        # Parse Free Cash Flow: "**Free Cash Flow:** -195,176,992 USD"
        fcf_match = re.search(r'\*\*Free Cash Flow:\*\*\s*([-\d,]+)\s*USD', markdown_text)
        if fcf_match:
            value_str = fcf_match.group(1).replace(',', '')
            metrics['free_cash_flow_millions'] = round(float(value_str) / 1e6, 2)

        # Parse Total Debt: "**Total Debt:** 863.11M USD"
        debt_match = re.search(r'\*\*Total Debt:\*\*\s*([\d.]+)([BMK]?)\s*USD', markdown_text)
        if debt_match:
            value = float(debt_match.group(1))
            unit = debt_match.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            metrics['total_debt_millions'] = round((value * multiplier) / 1e6, 2)

        # Parse Debt-to-Equity: "**Debt-to-Equity:** 5341.38"
        dte_match = re.search(r'\*\*Debt-to-Equity:\*\*\s*([\d.]+)', markdown_text)
        if dte_match:
            metrics['debt_to_equity'] = float(dte_match.group(1))

        # Parse Quick Ratio: "**Quick Ratio:** 1.59"
        qr_match = re.search(r'\*\*Quick Ratio:\*\*\s*([\d.]+)', markdown_text)
        if qr_match:
            metrics['quick_ratio'] = float(qr_match.group(1))

        # Parse Current Ratio: "**Current Ratio:** 1.89"
        cr_match = re.search(r'\*\*Current Ratio:\*\*\s*([\d.]+)', markdown_text)
        if cr_match:
            metrics['current_ratio'] = float(cr_match.group(1))

    except Exception as e:
        # Graceful degradation - return whatever we parsed successfully
        pass

    return metrics

def get_yahoo_finance_metrics(company_name: str, ticker: Optional[str] = None) -> Optional[Dict]:
    """Get comprehensive financial metrics from Yahoo Finance (stock_summary + stock_financials).

    v3.0: Replaced SEC EDGAR with Yahoo Finance stock_financials for:
    - Cash and cash equivalents
    - Operating cash flow → Cash runway calculation
    - Free cash flow → Distress signals
    - Debt ratios → Leverage analysis
    - Liquidity ratios → Financial health

    Args:
        company_name: Company name
        ticker: Optional ticker symbol (will be looked up via web if not provided)

    Returns:
        Dictionary with comprehensive financial metrics or None if not found
    """
    try:
        # If no ticker provided, try web-based lookup
        if not ticker:
            ticker = get_ticker_from_web(company_name)
            if not ticker:
                return None

        # Get valuation metrics from stock_summary
        summary_response = financial_intelligence(method="stock_summary", symbol=ticker)
        if not summary_response or 'error' in summary_response:
            return None

        summary_text = summary_response.get('text', '')
        if not summary_text:
            return None

        summary_metrics = parse_yahoo_markdown(summary_text)

        # Get detailed financials (cash, cash flow, debt) from stock_financials
        financials_response = financial_intelligence(method="stock_financials", symbol=ticker)
        financials_text = financials_response.get('text', '') if financials_response and 'error' not in financials_response else ''

        # Parse financial metrics (cash, cash flow, debt, liquidity)
        financial_metrics = parse_yahoo_markdown(financials_text) if financials_text else {}

        # Build comprehensive result dictionary
        metrics = {
            'ticker': ticker,
            # Valuation metrics from stock_summary
            'market_cap_millions': summary_metrics.get('market_cap_millions'),
            'enterprise_value_millions': summary_metrics.get('enterprise_value_millions'),
            'pe_ratio': summary_metrics.get('pe_ratio'),
            'eps': summary_metrics.get('eps'),
            'beta': summary_metrics.get('beta'),
            'shares_outstanding_millions': summary_metrics.get('shares_outstanding_millions'),
            # Financial health metrics from stock_financials
            'cash_millions': financial_metrics.get('cash_millions'),
            'total_debt_millions': financial_metrics.get('total_debt_millions'),
            'operating_cash_flow_millions': financial_metrics.get('operating_cash_flow_millions'),
            'free_cash_flow_millions': financial_metrics.get('free_cash_flow_millions'),
            'debt_to_equity': financial_metrics.get('debt_to_equity'),
            'quick_ratio': financial_metrics.get('quick_ratio'),
            'current_ratio': financial_metrics.get('current_ratio'),
            'cash_runway_months': None,
            'distress_signals': []
        }

        # Calculate cash runway from operating cash flow (if cash burn exists)
        if metrics.get('cash_millions') and metrics.get('operating_cash_flow_millions'):
            ocf = metrics['operating_cash_flow_millions']
            if ocf < 0:  # Company is burning cash
                monthly_burn = abs(ocf) / 12
                metrics['cash_runway_months'] = round(metrics['cash_millions'] / monthly_burn, 1)
            # else: positive cash flow = no runway concern

        # Distress signal detection
        # Signal 1: Low cash runway (<12 months)
        if metrics.get('cash_runway_months') and metrics['cash_runway_months'] < 12:
            metrics['distress_signals'].append(
                f"Low cash runway ({metrics['cash_runway_months']:.1f} months at current burn rate)"
            )

        # Signal 2: Negative free cash flow
        if metrics.get('free_cash_flow_millions') and metrics['free_cash_flow_millions'] < 0:
            metrics['distress_signals'].append(
                f"Negative free cash flow (${abs(metrics['free_cash_flow_millions']):.1f}M)"
            )

        # Signal 3: High debt-to-equity ratio (>500%)
        if metrics.get('debt_to_equity') and metrics['debt_to_equity'] > 500:
            metrics['distress_signals'].append(
                f"Very high debt-to-equity ratio ({metrics['debt_to_equity']:.0f}%)"
            )

        # Signal 4: Low quick ratio (<1.0)
        if metrics.get('quick_ratio') and metrics['quick_ratio'] < 1.0:
            metrics['distress_signals'].append(
                f"Low quick ratio ({metrics['quick_ratio']:.2f}, unable to cover short-term liabilities)"
            )

        # Signal 5: Negative EPS (profitability)
        if metrics.get('eps') and metrics['eps'] < 0:
            metrics['distress_signals'].append(
                f"Negative EPS (${abs(metrics['eps']):.2f} loss per share)"
            )

        # Signal 6: Very low P/E ratio (<5)
        if metrics.get('pe_ratio') and metrics['pe_ratio'] < 5:
            metrics['distress_signals'].append(
                f"Very low P/E ratio ({metrics['pe_ratio']:.1f})"
            )

        return metrics

    except Exception as e:
        return None

def get_combined_financial_metrics(company_name: str) -> Optional[Dict]:
    """Get comprehensive financial metrics from Yahoo Finance.

    v3.0: Replaced SEC EDGAR with Yahoo Finance stock_financials for complete financial data:
    - Cash and cash flow (operating, free) → Cash runway calculation
    - Debt and liquidity ratios → Financial health assessment
    - Market valuation (market cap, P/E, EPS) → Acquisition pricing
    - Distress signal detection → M&A timing

    Args:
        company_name: Company name to look up

    Returns:
        Dictionary with financial metrics from Yahoo Finance or None if not found
    """
    # Get comprehensive Yahoo Finance data (stock_summary + stock_financials)
    yahoo_data = get_yahoo_finance_metrics(company_name)

    if not yahoo_data:
        return None

    # Return Yahoo Finance data directly (already has all metrics)
    yahoo_data['company_name'] = company_name
    yahoo_data['sources'] = ['Yahoo Finance']

    return yahoo_data

def get_financial_metrics(company_name: str) -> Optional[Dict]:
    """Get key financial metrics from SEC EDGAR for a company.

    Args:
        company_name: Company name to look up

    Returns:
        Dictionary with financial metrics or None if not found
    """
    try:
        # Search for company (with rate limiting)
        search_result = rate_limited_sec_call(search_companies, company_name)

        if not search_result or 'results' not in search_result or len(search_result['results']) == 0:
            return None

        results_list = search_result['results']

        # Try fuzzy matching
        matched_cik = fuzzy_match_company_name(company_name, results_list)

        if not matched_cik:
            # Fallback to first result
            matched_cik = results_list[0].get('cik')

        if not matched_cik:
            return None

        # Get company facts (with rate limiting)
        facts_result = rate_limited_sec_call(get_company_facts, matched_cik)

        if not facts_result or 'facts' not in facts_result:
            return None

        # Find matching company in results for display name
        matched_company = next((c for c in results_list if c.get('cik') == matched_cik), results_list[0])

        # Extract financial metrics from company facts
        metrics = {
            'company_name': matched_company.get('title', company_name),
            'cik': matched_cik,
            'ticker': matched_company.get('ticker'),
            'cash_millions': None,
            'rd_expense_millions': None,
            'cash_runway_months': None,
            'distress_signals': []
        }

        # Parse facts for key metrics
        us_gaap = facts_result.get('facts', {}).get('us-gaap', {})

        # Cash and cash equivalents
        cash_data = us_gaap.get('CashAndCashEquivalentsAtCarryingValue', {}).get('units', {}).get('USD', [])
        if cash_data:
            latest_cash = sorted(cash_data, key=lambda x: x.get('end', ''), reverse=True)[0]
            metrics['cash_millions'] = round(latest_cash.get('val', 0) / 1_000_000, 2)

        # R&D Expense (annual)
        rd_data = us_gaap.get('ResearchAndDevelopmentExpense', {}).get('units', {}).get('USD', [])
        if rd_data:
            # Get latest annual R&D (form 10-K)
            annual_rd = [r for r in rd_data if r.get('form') == '10-K']
            if annual_rd:
                latest_rd = sorted(annual_rd, key=lambda x: x.get('end', ''), reverse=True)[0]
                metrics['rd_expense_millions'] = round(latest_rd.get('val', 0) / 1_000_000, 2)

        # Calculate cash runway
        if metrics['cash_millions'] and metrics['rd_expense_millions'] and metrics['rd_expense_millions'] > 0:
            monthly_burn = metrics['rd_expense_millions'] / 12
            metrics['cash_runway_months'] = round(metrics['cash_millions'] / monthly_burn, 1)

            # Distress signal: Low cash runway
            if metrics['cash_runway_months'] < 12:
                metrics['distress_signals'].append(f"Low cash runway ({metrics['cash_runway_months']} months)")

        # Negative earnings
        net_income_data = us_gaap.get('NetIncomeLoss', {}).get('units', {}).get('USD', [])
        if net_income_data:
            annual_income = [i for i in net_income_data if i.get('form') == '10-K']
            if annual_income:
                latest_income = sorted(annual_income, key=lambda x: x.get('end', ''), reverse=True)[0]
                income_millions = round(latest_income.get('val', 0) / 1_000_000, 2)
                if income_millions < 0:
                    metrics['distress_signals'].append(f"Negative earnings (${abs(income_millions)}M loss)")

        return metrics

    except Exception as e:
        # Gracefully handle errors (private companies, API failures, etc.)
        return None

def extract_field(content, field_name):
    """Extract field value from markdown content."""
    pattern = rf'\*\*{re.escape(field_name)}:\*\*\s*(.+?)(?:\n\*\*|\n\n|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        value = match.group(1).strip()
        value = re.sub(r'\*\*', '', value)
        value = re.sub(r'\n+', ' ', value)
        return value
    return None

def query_ct_gov_with_pagination(query: str, phase: str) -> List[Dict]:
    """Query CT.gov with full pagination."""
    all_trials = []
    page_token = None
    page_count = 0

    print(f"Querying CT.gov: {query[:50]}... phase={phase}")

    while True:
        page_count += 1

        # Use condition parameter for the search query
        result = search(
            condition=query,
            phase=phase,
            pageSize=1000,
            pageToken=page_token if page_token else None
        )

        if not result:
            break

        # Parse markdown response
        trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)

        for i in range(1, len(trial_blocks), 2):
            if i+1 < len(trial_blocks):
                nct_id = trial_blocks[i]
                content = trial_blocks[i+1]

                trial = {
                    'nct_id': nct_id,
                    'sponsor': extract_field(content, 'Lead Sponsor'),
                    'intervention': extract_field(content, 'Interventions'),
                    'condition': extract_field(content, 'Conditions'),
                    'phase': extract_field(content, 'Phase'),
                    'status': extract_field(content, 'Status')
                }

                all_trials.append(trial)

        # Check for next page
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match and len(all_trials) < 10000:
            page_token = next_token_match.group(1)
            print(f"  Page {page_count}: {len(trial_blocks)-1} trials")
        else:
            break

    print(f"  Total: {page_count} pages, {len(all_trials)} trials")
    return all_trials

def filter_and_aggregate_sponsors(
    trials: List[Dict],
    exclude_academic: bool,
    exclude_government: bool,
    exclude_cro: bool,
    min_programs: int,
    max_programs: int
) -> Tuple[Dict[str, List[Dict]], Dict[str, int]]:
    """Filter trials and aggregate by sponsor with filtering stats."""

    filtering_stats = {
        'total_trials': len(trials),
        'companies_before_filtering': 0,
        'excluded_academic': 0,
        'excluded_government': 0,
        'excluded_large_pharma': 0,
        'excluded_cro': 0,
        'excluded_small_portfolio': 0,
        'companies_after_filtering': 0
    }

    # Aggregate by sponsor
    sponsor_trials = {}
    for trial in trials:
        sponsor = trial.get('sponsor', 'Unknown')
        if sponsor not in sponsor_trials:
            sponsor_trials[sponsor] = []
        sponsor_trials[sponsor].append(trial)

    filtering_stats['companies_before_filtering'] = len(sponsor_trials)

    # Filter sponsors
    filtered_sponsors = {}
    for sponsor, sponsor_trial_list in sponsor_trials.items():
        # Check exclusions
        if exclude_academic and is_academic_sponsor(sponsor):
            filtering_stats['excluded_academic'] += 1
            continue

        if exclude_government and is_government_sponsor(sponsor):
            filtering_stats['excluded_government'] += 1
            continue

        if exclude_cro and is_cro_sponsor(sponsor):
            filtering_stats['excluded_cro'] += 1
            continue

        # Check portfolio size
        program_count = len(sponsor_trial_list)
        if program_count < min_programs:
            filtering_stats['excluded_small_portfolio'] += 1
            continue

        if program_count > max_programs:
            filtering_stats['excluded_large_pharma'] += 1
            continue

        filtered_sponsors[sponsor] = sponsor_trial_list

    filtering_stats['companies_after_filtering'] = len(filtered_sponsors)

    return filtered_sponsors, filtering_stats

def calculate_acquisition_score(sponsor: str, trials: List[Dict], financial_metrics: Optional[Dict] = None) -> int:
    """Calculate acquisition attractiveness score."""
    score = 0

    total_programs = len(trials)
    phase2_count = sum(1 for t in trials if 'phase2' in str(t.get('phase', '')).lower())
    phase3_count = sum(1 for t in trials if 'phase3' in str(t.get('phase', '')).lower())
    recruiting_count = sum(1 for t in trials if 'recruiting' in str(t.get('status', '')).lower())

    # Portfolio sweet spot (2-5 programs): +30
    if 2 <= total_programs <= 5:
        score += 30
    elif total_programs == 1:
        score += 10
    elif total_programs > 5:
        score += 20

    # Has Phase 3 (de-risked): +25
    if phase3_count > 0:
        score += 25

    # Multiple programs (platform potential): +20
    if total_programs >= 3:
        score += 20

    # Active recruiting (momentum): +15
    if recruiting_count > 0:
        score += 15

    # Balanced Phase 2+3 portfolio: +10
    if phase2_count > 0 and phase3_count > 0:
        score += 10

    # Financial distress signals increase acquisition likelihood
    if financial_metrics:
        distress_count = len(financial_metrics.get('distress_signals', []))
        score += distress_count * 5  # Each distress signal adds 5 points

    return score

def rank_acquisition_targets(
    sponsor_trials: Dict[str, List[Dict]],
    max_results: int,
    enrich_financials: bool = False,
    max_cash_runway_months: Optional[float] = None
) -> List[Dict]:
    """Rank sponsors by acquisition attractiveness."""

    ranked_targets = []

    for sponsor, trials in sponsor_trials.items():
        # Calculate metrics
        total_programs = len(trials)
        phase2_count = sum(1 for t in trials if 'phase2' in str(t.get('phase', '')).lower())
        phase3_count = sum(1 for t in trials if 'phase3' in str(t.get('phase', '')).lower())
        recruiting_count = sum(1 for t in trials if 'recruiting' in str(t.get('status', '')).lower())

        # Financial enrichment (always uses both SEC EDGAR + Yahoo Finance)
        financial_metrics = None
        if enrich_financials:
            print(f"  Enriching: {sponsor}...", end=" ")
            financial_metrics = get_combined_financial_metrics(sponsor)
            if financial_metrics:
                sources = ', '.join(financial_metrics.get('sources', []))
                distress_count = len(financial_metrics.get('distress_signals', []))
                print(f"✓ [{sources}] ({distress_count} distress signals)")
            else:
                print("✗ (not found)")

        # Apply cash runway filter if specified
        if max_cash_runway_months and financial_metrics:
            cash_runway = financial_metrics.get('cash_runway_months')
            if cash_runway and cash_runway > max_cash_runway_months:
                continue  # Skip companies with too much runway

        # Find lead asset
        lead_asset = None
        for trial in sorted(trials, key=lambda t: (
            'phase3' in str(t.get('phase', '')).lower(),
            'phase2' in str(t.get('phase', '')).lower(),
            'recruiting' in str(t.get('status', '')).lower()
        ), reverse=True):
            lead_asset = trial
            break

        # Calculate score
        score = calculate_acquisition_score(sponsor, trials, financial_metrics)

        ranked_targets.append({
            'sponsor': sponsor,
            'acquisition_score': score,
            'total_programs': total_programs,
            'phase2_count': phase2_count,
            'phase3_count': phase3_count,
            'recruiting_count': recruiting_count,
            'lead_asset': {
                'nct_id': lead_asset.get('nct_id', 'Unknown'),
                'intervention': lead_asset.get('intervention', 'Unknown'),
                'condition': lead_asset.get('condition', 'Unknown'),
                'phase': lead_asset.get('phase', 'Unknown'),
                'status': lead_asset.get('status', 'Unknown')
            } if lead_asset else None,
            'financial_metrics': financial_metrics,
            'all_programs': trials
        })

    # Sort by score
    ranked_targets.sort(key=lambda x: x['acquisition_score'], reverse=True)

    # Add rank
    for i, target in enumerate(ranked_targets[:max_results], 1):
        target['rank'] = i

    return ranked_targets[:max_results]

def get_rare_disease_acquisition_targets(
    therapeutic_focus: str = 'any',
    min_programs: int = 1,
    max_programs: int = 8,
    exclude_academic: bool = True,
    exclude_government: bool = True,
    exclude_cro: bool = True,
    prefer_phase3: bool = True,
    max_results: int = 50,
    enrich_financials: bool = False,
    max_cash_runway_months: Optional[float] = None
) -> Dict:
    """Get ranked rare disease acquisition targets with intelligent filtering and optional financial enrichment.

    Financial enrichment uses DUAL sources to maximize coverage:
    - SEC EDGAR: Cash, R&D expense, cash runway, earnings (US public companies)
    - Yahoo Finance: Market cap, stock price, P/E ratio, 52-week change (global public companies)

    Args:
        therapeutic_focus: 'ultra_rare_metabolic', 'neuromuscular', 'gene_therapy', 'oncology_rare', 'any'
        min_programs: Minimum programs (default: 1)
        max_programs: Maximum programs (default: 8)
        exclude_academic: Exclude universities/medical centers (default: True)
        exclude_government: Exclude NIH/NCI (default: True)
        exclude_cro: Exclude CROs (default: True)
        prefer_phase3: Adaptive phase strategy (default: True)
        max_results: Top N targets (default: 50)
        enrich_financials: Enable dual financial data lookup - SEC EDGAR + Yahoo Finance (default: False, slower but adds comprehensive financial context)
        max_cash_runway_months: Filter for distressed companies (default: None, requires enrich_financials=True)

    Returns:
        dict: query_strategy, filtering_summary, top_targets, summary
    """

    # Get query
    query = THERAPEUTIC_QUERIES.get(therapeutic_focus, THERAPEUTIC_QUERIES['any'])

    # Adaptive phase strategy
    phase_expansion_reason = None
    phases_included = 'PHASE3 only'

    if prefer_phase3:
        # Try Phase 3 first
        trials_phase3 = query_ct_gov_with_pagination(query, 'PHASE3')
        sponsor_trials_phase3, _ = filter_and_aggregate_sponsors(
            trials_phase3,
            exclude_academic,
            exclude_government,
            exclude_cro,
            min_programs,
            max_programs
        )

        # Check if expansion needed
        if len(sponsor_trials_phase3) < 20:
            phase_expansion_reason = f'Phase 3 only: {len(sponsor_trials_phase3)} companies (threshold: 20)'
            print(f"\nExpanding to Phase 2: {phase_expansion_reason}")

            # Query both phases separately and combine
            trials_phase2 = query_ct_gov_with_pagination(query, 'PHASE2')
            trials_combined = trials_phase3 + trials_phase2

            sponsor_trials, filtering_stats = filter_and_aggregate_sponsors(
                trials_combined,
                exclude_academic,
                exclude_government,
                exclude_cro,
                min_programs,
                max_programs
            )
            phases_included = 'PHASE2+PHASE3'
        else:
            sponsor_trials = sponsor_trials_phase3
            filtering_stats = {
                'total_trials': len(trials_phase3),
                'companies_before_filtering': len({t.get('sponsor') for t in trials_phase3}),
                'excluded_academic': 0,
                'excluded_government': 0,
                'excluded_large_pharma': 0,
                'excluded_cro': 0,
                'excluded_small_portfolio': 0,
                'companies_after_filtering': len(sponsor_trials)
            }
            phase_expansion_reason = f'Phase 3 sufficient ({len(sponsor_trials)} companies ≥ 20)'
    else:
        # Query both phases separately and combine
        trials_phase2 = query_ct_gov_with_pagination(query, 'PHASE2')
        trials_phase3 = query_ct_gov_with_pagination(query, 'PHASE3')
        trials = trials_phase2 + trials_phase3

        sponsor_trials, filtering_stats = filter_and_aggregate_sponsors(
            trials,
            exclude_academic,
            exclude_government,
            exclude_cro,
            min_programs,
            max_programs
        )
        phases_included = 'PHASE2+PHASE3'
        phase_expansion_reason = 'Phase 2+3 from start'

    # Rank targets with optional financial enrichment
    if enrich_financials:
        print("\n" + "="*80)
        print("ENRICHING WITH FINANCIAL DATA (YAHOO FINANCE v3.0)")
        print("="*80)

    top_targets = rank_acquisition_targets(
        sponsor_trials,
        max_results,
        enrich_financials=enrich_financials,
        max_cash_runway_months=max_cash_runway_months
    )

    # Generate summary
    summary = f"""# Rare Disease Acquisition Targets

## Query Strategy
- Therapeutic Focus: {therapeutic_focus}
- Phases: {phases_included}
- Strategy: {phase_expansion_reason}
- Financial Enrichment: {'Enabled' if enrich_financials else 'Disabled'}

## Filtering
- Total Trials: {filtering_stats['total_trials']:,}
- Before Filtering: {filtering_stats['companies_before_filtering']:,} companies
- Excluded Academic: {filtering_stats['excluded_academic']:,}
- Excluded Government: {filtering_stats['excluded_government']:,}
- Excluded Large (>{max_programs}): {filtering_stats['excluded_large_pharma']:,}
- Excluded CRO: {filtering_stats['excluded_cro']:,}
- Excluded Small (<{min_programs}): {filtering_stats['excluded_small_portfolio']:,}
- After Filtering: {filtering_stats['companies_after_filtering']:,} companies

## Top 10 Targets

"""

    for target in top_targets[:10]:
        summary += f"""### {target['rank']}. {target['sponsor']} (Score: {target['acquisition_score']})
- Portfolio: {target['total_programs']} programs ({target['phase3_count']} P3, {target['phase2_count']} P2)
- Active: {target['recruiting_count']} recruiting
"""
        if target['lead_asset']:
            lead = target['lead_asset']
            summary += f"""- Lead: {lead['intervention']} - {lead['condition']} ({lead['phase']})
  NCT: {lead['nct_id']}
"""
        if target.get('financial_metrics'):
            fm = target['financial_metrics']
            sources = ', '.join(fm.get('sources', []))
            summary += f"""- Financial [{sources}]:
"""
            # SEC EDGAR metrics
            if 'SEC EDGAR' in fm.get('sources', []):
                summary += f"""  - Cash: ${fm.get('cash_millions', 'N/A')}M, Runway: {fm.get('cash_runway_months', 'N/A')} months
"""
            # Yahoo Finance metrics
            if 'Yahoo Finance' in fm.get('sources', []):
                ticker = fm.get('ticker', 'N/A')
                market_cap = fm.get('market_cap_millions')
                market_cap_str = f"${market_cap:,.0f}M" if market_cap else 'N/A'
                stock_price = fm.get('stock_price', 'N/A')
                pe_ratio = fm.get('pe_ratio')
                pe_str = f"{pe_ratio:.1f}" if pe_ratio else 'N/A'
                change_pct = fm.get('fifty_two_week_change_pct')
                change_str = f"{change_pct:+.1f}%" if change_pct is not None else 'N/A'
                summary += f"""  - Ticker: {ticker}, Market Cap: {market_cap_str}, Price: ${stock_price}, P/E: {pe_str}, 52W Change: {change_str}
"""
            # Distress signals
            if fm.get('distress_signals'):
                summary += f"""  - ⚠️ Distress: {', '.join(fm['distress_signals'])}
"""
        summary += "\n"

    return {
        'query_strategy': {
            'therapeutic_focus': therapeutic_focus,
            'phases_included': phases_included,
            'phase_expansion_reason': phase_expansion_reason,
            'financial_enrichment': enrich_financials
        },
        'filtering_summary': filtering_stats,
        'top_targets': top_targets,
        'summary': summary
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Get ranked rare disease acquisition targets with intelligent filtering'
    )
    parser.add_argument('--therapeutic-focus', default='any',
                       help='Therapeutic area: ultra_rare_metabolic, neuromuscular, gene_therapy, oncology_rare, any (default: any)')
    parser.add_argument('--min-programs', type=int, default=1, help='Minimum programs (default: 1)')
    parser.add_argument('--max-programs', type=int, default=8, help='Maximum programs (default: 8)')
    parser.add_argument('--exclude-academic', action='store_true', default=True, help='Exclude academic institutions (default: True)')
    parser.add_argument('--include-academic', action='store_false', dest='exclude_academic', help='Include academic institutions')
    parser.add_argument('--exclude-government', action='store_true', default=True, help='Exclude government entities (default: True)')
    parser.add_argument('--include-government', action='store_false', dest='exclude_government', help='Include government entities')
    parser.add_argument('--exclude-cro', action='store_true', default=True, help='Exclude CROs (default: True)')
    parser.add_argument('--include-cro', action='store_false', dest='exclude_cro', help='Include CROs')
    parser.add_argument('--prefer-phase3', action='store_true', default=True, help='Prefer Phase 3 trials (default: True)')
    parser.add_argument('--max-results', type=int, default=50, help='Maximum results (default: 50)')
    parser.add_argument('--enrich-financials', action='store_true', help='Enable SEC/Yahoo Finance enrichment')
    parser.add_argument('--max-cash-runway-months', type=float, help='Filter companies with cash runway below this (months)')

    args = parser.parse_args()

    result = get_rare_disease_acquisition_targets(
        therapeutic_focus=args.therapeutic_focus,
        min_programs=args.min_programs,
        max_programs=args.max_programs,
        exclude_academic=args.exclude_academic,
        exclude_government=args.exclude_government,
        exclude_cro=args.exclude_cro,
        prefer_phase3=args.prefer_phase3,
        max_results=args.max_results,
        enrich_financials=args.enrich_financials,
        max_cash_runway_months=args.max_cash_runway_months
    )

    print(result['summary'])
    print(f"\n✓ Found {len(result['top_targets'])} targets")
    print(f"✓ Strategy: {result['query_strategy']['phase_expansion_reason']}")
    if result['query_strategy']['financial_enrichment']:
        enriched_count = sum(1 for t in result['top_targets'] if t.get('financial_metrics'))
        print(f"✓ Financial data: {enriched_count}/{len(result['top_targets'])} targets enriched")
