import sys
sys.path.insert(0, ".claude")

from mcp.servers.who_mcp import search_indicators, get_country_data
from mcp.servers.datacommons_mcp import search_indicators as dc_search_indicators, get_observations

# ISO3 to full country name mapping for Data Commons
COUNTRY_NAME_MAP = {
    'USA': 'United States',
    'IND': 'India',
    'CHN': 'China',
    'BRA': 'Brazil',
    'GBR': 'United Kingdom',
    'DEU': 'Germany',
    'FRA': 'France',
    'ITA': 'Italy',
    'ESP': 'Spain',
    'CAN': 'Canada',
    'AUS': 'Australia',
    'JPN': 'Japan',
    'MEX': 'Mexico',
    'RUS': 'Russia',
    'ZAF': 'South Africa',
    'KOR': 'South Korea',
    'IDN': 'Indonesia',
    'TUR': 'Turkey',
    'SAU': 'Saudi Arabia',
    'NGA': 'Nigeria',
    'EGY': 'Egypt',
    'PAK': 'Pakistan',
    'BGD': 'Bangladesh',
    'VNM': 'Vietnam',
    'THA': 'Thailand',
    'PHL': 'Philippines',
    'POL': 'Poland',
    'ARG': 'Argentina',
    'NLD': 'Netherlands',
    'BEL': 'Belgium',
    'SWE': 'Sweden',
    'CHE': 'Switzerland'
}

def get_population_data(country_code):
    """Get population data for a country using Data Commons.

    Args:
        country_code: ISO3 country code (e.g., 'USA', 'IND', 'BRA')

    Returns:
        int: Population value or None if not found
    """
    country_name = COUNTRY_NAME_MAP.get(country_code)
    if not country_name:
        print(f"    [WARNING] Unknown country code: {country_code}, cannot fetch population")
        return None

    try:
        # Step 1: Search for population indicator
        search_result = dc_search_indicators(
            query="population",
            places=[country_name],
            include_topics=False,
            per_search_limit=1
        )

        variables = search_result.get('variables', [])
        if not variables:
            return None

        variable_dcid = variables[0]['dcid']
        places_with_data = variables[0].get('places_with_data', [])
        if not places_with_data:
            return None

        place_dcid = places_with_data[0]

        # Step 2: Get latest observation
        obs_result = get_observations(
            variable_dcid=variable_dcid,
            place_dcid=place_dcid,
            date="latest"
        )

        place_observations = obs_result.get('place_observations', [])
        if not place_observations:
            return None

        time_series = place_observations[0].get('time_series', [])
        if not time_series:
            return None

        _, population = time_series[0]
        return int(population) if population else None

    except Exception as e:
        print(f"    [DC ERROR] {str(e)}")
        return None


def get_disease_burden_per_capita(country="USA", disease_indicator="life expectancy"):
    """Calculate disease burden per capita by combining WHO and Data Commons data.

    Demonstrates multi-server integration:
    1. WHO MCP: Get disease/health indicator data
    2. Data Commons MCP: Get population data
    3. Calculate true per-capita rates

    Args:
        country: ISO3 country code (e.g., 'USA', 'IND', 'BRA')
        disease_indicator: WHO indicator keywords (e.g., 'diabetes', 'tuberculosis', 'maternal mortality')

    Returns:
        dict: Contains indicator data, population, and per-capita calculations
    """

    print(f"\n=== Analyzing {disease_indicator} burden in {country} ===\n")

    # Step 1: Search for WHO indicator and get disease burden data
    print("Step 1: Searching for WHO indicator...")
    who_indicators = search_indicators(keywords=disease_indicator)

    if not who_indicators.get('indicators'):
        return {'success': False, 'error': f'No WHO indicator found for: {disease_indicator}'}

    # Filter for disease burden indicators (prioritize DALYs, deaths, prevalence)
    burden_keywords = ['daly', 'death', 'mortality', 'prevalence', 'incidence', 'rate']
    exclude_keywords = ['approval', 'regulation', 'policy', 'legislation', 'training', 'education', 'awareness']

    best_indicator = None
    for indicator in who_indicators['indicators']:
        indicator_name_lower = indicator.get('name', '').lower()

        # Skip regulatory/policy indicators
        if any(exclude in indicator_name_lower for exclude in exclude_keywords):
            continue

        # Prioritize disease burden indicators
        if any(burden in indicator_name_lower for burden in burden_keywords):
            best_indicator = indicator
            break

    # Fallback to first indicator if no burden indicator found
    if not best_indicator:
        best_indicator = who_indicators['indicators'][0]

    indicator_code = best_indicator.get('code')
    indicator_name = best_indicator.get('name')
    print(f"✓ Found indicator: {indicator_name} ({indicator_code})")

    # Step 2: Get WHO data for country
    print(f"\nStep 2: Fetching WHO data for {country}...")
    who_data = get_country_data(
        indicator_code=indicator_code,
        country_code=country
    )

    if not who_data or not who_data.get('data'):
        return {'success': False, 'error': f'WHO data fetch failed for {country}'}

    # Extract latest disease burden value (get the most recent year)
    # Prefer "both sexes" data, fallback to any available
    disease_records = [r for r in who_data['data'] if r.get('dim1') in ['SEX_BTSX', '', None]]

    if not disease_records:
        # If no "both sexes" data, use any available record
        disease_records = who_data['data']

    if not disease_records:
        return {'success': False, 'error': 'No data records found'}

    # Get the most recent record (sort by time_dim)
    disease_records.sort(key=lambda x: x.get('time_dim', 0))
    disease_record = disease_records[-1]  # Last record is most recent

    disease_value = disease_record.get('numeric_value')
    disease_year = disease_record.get('time_dim', 'Unknown')

    # Handle None values gracefully
    if disease_value is None:
        return {'success': False, 'error': 'No numeric value found in WHO data'}

    print(f"✓ WHO Data: {disease_value:,.2f} (year: {disease_year})")

    # Step 3: Get population data from Data Commons
    print(f"\nStep 3: Fetching population data from Data Commons...")
    population = get_population_data(country)

    if population:
        print(f"✓ Population: {population:,}")

        # Step 4: Calculate per-capita rate
        # Check if the indicator is already a rate (per 100k, per capita, etc.)
        indicator_lower = indicator_name.lower()
        is_already_rate = any(term in indicator_lower for term in ['per 100', 'per capita', 'rate per', '/ 100'])

        if is_already_rate:
            per_capita_value = disease_value
            calculation_note = "Indicator already expressed as per-capita rate"
        else:
            # Calculate per 100,000 population
            per_capita_value = (disease_value / population) * 100000
            calculation_note = f"Calculated as ({disease_value:,.0f} / {population:,}) × 100,000"

        # Format summary
        summary = f"""
=== Disease Burden Per Capita Analysis: {country} ===

Indicator: {indicator_name}
Code: {indicator_code}
Year: {disease_year}

Raw Value: {disease_value:,.2f}
Population: {population:,}
Per 100,000 Population: {per_capita_value:,.2f}

Calculation: {calculation_note}

Data Sources:
  - Disease/Health Data: WHO (World Health Organization)
  - Population Data: Data Commons (via Google/US Census)
"""

        return {
            'success': True,
            'country': country,
            'indicator_name': indicator_name,
            'indicator_code': indicator_code,
            'raw_value': disease_value,
            'year': disease_year,
            'population': population,
            'per_100k_population': round(per_capita_value, 2),
            'is_already_rate': is_already_rate,
            'summary': summary.strip()
        }
    else:
        # Population data unavailable - return WHO data only
        print(f"⚠ Population data unavailable, returning raw WHO values only")

        summary = f"""
=== WHO Health Indicator Data: {country} ===

Indicator: {indicator_name}
Code: {indicator_code}
Year: {disease_year}

VALUE: {disease_value:,.2f}

Note: Population data unavailable for {country} ({COUNTRY_NAME_MAP.get(country, 'unknown')}).
Per-capita calculation not possible. Showing raw WHO indicator value.
"""

        return {
            'success': True,
            'country': country,
            'indicator_name': indicator_name,
            'indicator_code': indicator_code,
            'value': disease_value,
            'year': disease_year,
            'population': None,
            'per_100k_population': None,
            'summary': summary.strip()
        }

if __name__ == "__main__":
    # Accept command-line arguments or use defaults
    if len(sys.argv) >= 3:
        country = sys.argv[1]
        disease_indicator = sys.argv[2]
    else:
        # Default example
        country = "USA"
        disease_indicator = "diabetes"
        print("Usage: python get_disease_burden_per_capita.py <country_code> <disease_indicator>")
        print(f"Example: python get_disease_burden_per_capita.py USA 'diabetes'")
        print(f"         python get_disease_burden_per_capita.py IND 'tuberculosis'")
        print(f"\nRunning default example: {country}, '{disease_indicator}'\n")

    result = get_disease_burden_per_capita(country=country, disease_indicator=disease_indicator)
    if result['success']:
        print(result['summary'])
    else:
        print(f"Error: {result['error']}")
