import sys
import re
sys.path.insert(0, ".claude")
from mcp.servers.financials_mcp import financial_intelligence

def extract_value(text, pattern, default=None):
    """Extract numeric value from markdown text using regex."""
    match = re.search(pattern, text)
    if match:
        value_str = match.group(1).strip()

        # Handle N/A values
        if 'N/A' in value_str or value_str == '-':
            return default

        # Remove commas and convert to float
        value_str = value_str.replace(',', '')
        # Handle percentages
        value_str = value_str.replace('%', '')

        # Handle B (billions) and M (millions) suffixes
        if 'B' in value_str:
            return float(value_str.replace('B', '').replace('USD', '').strip()) * 1e9
        elif 'M' in value_str:
            return float(value_str.replace('M', '').strip()) * 1e6

        # Remove currency symbols
        value_str = value_str.replace('$', '').replace('USD', '').strip()

        try:
            return float(value_str)
        except ValueError:
            return default
    return default

def get_pharma_company_stock_data(companies=None):
    """Get stock data for pharmaceutical companies.

    Args:
        companies: List of ticker symbols (e.g., ['PFE', 'MRK', 'JNJ'])

    Returns:
        dict: Contains total_count and companies list with stock data
    """
    if companies is None:
        companies = ['PFE', 'MRK', 'JNJ']

    results = []
    for ticker in companies:
        try:
            # Get comprehensive stock data using financial_intelligence
            pricing_response = financial_intelligence(method='stock_pricing', symbol=ticker) or {}
            summary_response = financial_intelligence(method='stock_summary', symbol=ticker) or {}

            # Extract markdown text from responses
            pricing_text = pricing_response.get('text', '')
            summary_text = summary_response.get('text', '')

            # Parse pricing data from markdown
            price = extract_value(pricing_text, r'\*\*Current Price:\*\*\s*\$?([\d,.]+)', None)
            change = extract_value(pricing_text, r'\*\*Daily Change:\*\*\s*\$?([-\d,.]+)', None)
            change_percent = extract_value(pricing_text, r'\*\*Daily Change:\*\*\s*\$?[-\d,.]+\s*\(([-+\d,.]+)%\)', None)
            volume = extract_value(pricing_text, r"\*\*Today's Volume:\*\*\s*([\d,.]+[MB]?)", None)
            week_52_high = extract_value(pricing_text, r'\*\*52-Week High:\*\*\s*\$?([\d,.]+)', None)
            week_52_low = extract_value(pricing_text, r'\*\*52-Week Low:\*\*\s*\$?([\d,.]+)', None)

            # Parse summary data from markdown
            # Try market cap first, fallback to enterprise value if N/A
            market_cap = extract_value(summary_text, r'\*\*Market Cap:\*\*\s*([\d,.NABMK]+)\s*(?:USD)?', None)
            if market_cap is None:
                market_cap = extract_value(summary_text, r'\*\*Enterprise Value:\*\*\s*([\d,.NABMK]+)\s*(?:USD)?', None)

            pe_ratio = extract_value(summary_text, r'\*\*Trailing P/E:\*\*\s*([\d,.NA]+)', None)
            if pe_ratio is None:
                # Try forward P/E as fallback
                pe_ratio = extract_value(summary_text, r'\*\*Forward P/E:\*\*\s*([\d,.NA]+)', None)

            beta = extract_value(summary_text, r'\*\*Beta:\*\*\s*([\d,.]+)', None)

            # Dividend yield would need stock_estimates or stock_dividends method
            # For now, set to None as it's not in stock_summary
            dividend_yield = None

            stock_data = {
                'ticker': ticker,
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield,
                'beta': beta,
                '52_week_high': week_52_high,
                '52_week_low': week_52_low,
                'error': None
            }
            results.append(stock_data)
        except Exception as e:
            # If ticker fails, include error but continue
            results.append({
                'ticker': ticker,
                'error': str(e),
                'price': None,
                'change': None,
                'change_percent': None,
                'volume': None,
                'market_cap': None,
                'pe_ratio': None,
                'dividend_yield': None,
                'beta': None,
                '52_week_high': None,
                '52_week_low': None
            })

    return {'total_count': len(results), 'companies': results}

if __name__ == "__main__":
    # Accept command-line arguments (ticker symbols) or use defaults
    if len(sys.argv) > 1:
        companies = sys.argv[1:]  # All arguments after script name are ticker symbols
    else:
        # Default example
        companies = ['PFE', 'MRK', 'JNJ']
        print("Usage: python get_pharma_company_stock_data.py <TICKER1> <TICKER2> ...")
        print(f"Running default example with: {', '.join(companies)}\n")

    result = get_pharma_company_stock_data(companies=companies)

    print(f"\n{'='*80}")
    print(f"PHARMA STOCK DATA - {result['total_count']} Companies")
    print(f"{'='*80}\n")

    for stock in result['companies']:
        ticker = stock['ticker']
        error = stock.get('error')

        print(f"{ticker}:")

        if error:
            print(f"  ❌ Error: {error}")
        else:
            price = stock.get('price')
            change = stock.get('change')
            change_pct = stock.get('change_percent')
            market_cap = stock.get('market_cap')
            pe = stock.get('pe_ratio')
            div_yield = stock.get('dividend_yield')
            beta = stock.get('beta')

            if price:
                sign = '+' if change and change >= 0 else ''
                print(f"  Price: ${price:.2f} ({sign}{change:.2f}, {sign}{change_pct:.2f}%)")
            if market_cap:
                print(f"  Market Cap: ${market_cap/1e9:.2f}B")
            if pe:
                print(f"  P/E Ratio: {pe:.2f}")
            if div_yield:
                print(f"  Dividend Yield: {div_yield:.2f}%")
            if beta:
                print(f"  Beta: {beta:.2f}")

            if not any([price, market_cap, pe, div_yield, beta]):
                print(f"  ⚠️  No data available")

        print()
