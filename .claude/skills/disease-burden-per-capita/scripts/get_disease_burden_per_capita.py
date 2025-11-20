import sys
sys.path.insert(0, ".claude")

from mcp.servers.who_mcp import get_health_indicators
from mcp.servers.datacommons_mcp import get_statistics

def get_disease_burden_per_capita(country="USA", disease_indicator="deaths_tuberculosis"):
    """Compare WHO disease burden with Data Commons population for per-capita analysis.

    Args:
        country: ISO3 country code (e.g., 'USA', 'IND', 'BRA')
        disease_indicator: WHO indicator code

    Returns:
        dict: Contains disease data, population data, per-capita metrics
    """

    print(f"\n=== Analyzing {disease_indicator} burden in {country} ===\n")

    # Step 1: Get WHO disease burden data
    print("Step 1: Fetching WHO disease burden data...")
    who_result = get_health_indicators(
        country=country,
        indicator=disease_indicator,
        year="latest"
    )

    if not who_result or 'error' in who_result:
        return {'success': False, 'error': 'WHO data fetch failed'}

    disease_data = who_result.get('value', {})
    disease_count = disease_data.get('numeric', 0)
    disease_year = disease_data.get('year', 'Unknown')

    print(f"✓ WHO Data: {disease_count:,.0f} {disease_indicator} in {disease_year}")

    # Step 2: Get Data Commons population
    print("\nStep 2: Fetching Data Commons population data...")

    country_mapping = {
        'USA': 'country/USA',
        'IND': 'country/IND',
        'BRA': 'country/BRA',
        'CHN': 'country/CHN'
    }

    dc_place = country_mapping.get(country, f'country/{country}')

    dc_result = get_statistics(
        place=dc_place,
        stat_var="Count_Person",
        date="latest"
    )

    if not dc_result or 'error' in dc_result:
        return {'success': False, 'error': 'Data Commons fetch failed'}

    population = dc_result.get('value', 0)
    pop_year = dc_result.get('date', 'Unknown')

    print(f"✓ Data Commons: {population:,.0f} population in {pop_year}")

    # Step 3: Calculate per-capita
    print("\nStep 3: Calculating per-capita metrics...")

    if population > 0:
        per_100k = (disease_count / population) * 100000
        per_million = (disease_count / population) * 1000000
    else:
        per_100k = 0
        per_million = 0

    summary = f"""
=== Disease Burden Per-Capita Analysis: {country} ===

Disease Indicator: {disease_indicator}
Analysis Period: {disease_year} (disease), {pop_year} (population)

ABSOLUTE NUMBERS:
  Total Cases: {disease_count:,.0f}
  Population: {population:,.0f}

PER-CAPITA METRICS:
  Per 100,000 population: {per_100k:.2f}
  Per 1,000,000 population: {per_million:.2f}
"""

    return {
        'success': True,
        'country': country,
        'disease_data': {'count': disease_count, 'year': disease_year},
        'population_data': {'count': population, 'year': pop_year},
        'per_capita_metrics': {'per_100k': per_100k, 'per_million': per_million},
        'summary': summary.strip()
    }

if __name__ == "__main__":
    result = get_disease_burden_per_capita(country="USA", disease_indicator="deaths_tuberculosis")
    if result['success']:
        print(result['summary'])
    else:
        print(f"Error: {result['error']}")
