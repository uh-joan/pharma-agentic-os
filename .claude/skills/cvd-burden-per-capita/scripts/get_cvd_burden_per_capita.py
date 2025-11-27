import sys
sys.path.insert(0, ".claude")
from mcp.servers.who_mcp import search_indicators as who_search, get_health_data
from mcp.servers.datacommons_mcp import search_indicators, get_observations

def get_population_data(country_name):
    """Get population data for a country using Data Commons proper API.

    Args:
        country_name: Human-readable country name (e.g., "United States", "Brazil")

    Returns:
        int: Population value or None if not found
    """
    try:
        # Step 1: Search for population indicator
        search_result = search_indicators(
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
        print(f"Data Commons error for {country_name}: {str(e)}")
        return None


def get_cvd_burden_per_capita():
    """Calculate CVD burden per capita by combining WHO and Data Commons data."""

    countries = [
        "United States", "United Kingdom", "Germany", "France", "Italy",
        "Spain", "Canada", "Australia", "Japan", "China",
        "India", "Brazil", "Mexico", "Russia", "South Africa"
    ]

    cvd_burden = []
    data_availability = {'total_countries': len(countries), 'who_success': 0,
                        'dc_success': 0, 'both_success': 0, 'details': []}

    for country in countries:
        country_status = {'country': country, 'who_available': False,
                         'dc_available': False, 'cvd_deaths': None, 'population': None}

        # Map country names to ISO 3-letter codes
        country_code_map = {
            "United States": "USA", "United Kingdom": "GBR", "Germany": "DEU",
            "France": "FRA", "Italy": "ITA", "Spain": "ESP", "Canada": "CAN",
            "Australia": "AUS", "Japan": "JPN", "China": "CHN",
            "India": "IND", "Brazil": "BRA", "Mexico": "MEX",
            "Russia": "RUS", "South Africa": "ZAF"
        }

        try:
            country_code = country_code_map.get(country)
            if not country_code:
                continue

            # Use WHO Health Data API with CVD mortality indicator
            # WHOSIS_000015 is the CVD mortality rate indicator
            who_result = get_health_data(
                indicator_code="WHOSIS_000015",
                filter=f"SpatialDim eq '{country_code}'",
                top=1
            )

            cvd_deaths = None
            if who_result and 'value' in who_result:
                records = who_result['value']
                if records:
                    # Get most recent value
                    records_sorted = sorted(records,
                                          key=lambda x: x.get('TimeDim', 0),
                                          reverse=True)
                    if records_sorted:
                        cvd_deaths = records_sorted[0].get('NumericValue')
                        if cvd_deaths:
                            country_status['who_available'] = True

            country_status['cvd_deaths'] = cvd_deaths
            if cvd_deaths:
                data_availability['who_success'] += 1
        except Exception as e:
            print(f"WHO error for {country}: {str(e)}")

        # Use new Data Commons API
        population = get_population_data(country)

        if population:
            country_status['dc_available'] = True
            country_status['population'] = population
            data_availability['dc_success'] += 1
        
        if cvd_deaths and population and cvd_deaths > 0 and population > 0:
            deaths_per_100k = (cvd_deaths / population) * 100000
            cvd_burden.append({
                'country': country,
                'cvd_deaths': int(cvd_deaths),
                'population': int(population),
                'deaths_per_100k': round(deaths_per_100k, 2)
            })
            data_availability['both_success'] += 1
        
        data_availability['details'].append(country_status)
    
    cvd_burden.sort(key=lambda x: x['deaths_per_100k'], reverse=True)
    
    if cvd_burden:
        avg_burden = sum(c['deaths_per_100k'] for c in cvd_burden) / len(cvd_burden)
        summary = {
            'countries_with_complete_data': len(cvd_burden),
            'average_burden_per_100k': round(avg_burden, 2),
            'highest_burden': {'country': cvd_burden[0]['country'], 'rate': cvd_burden[0]['deaths_per_100k']},
            'lowest_burden': {'country': cvd_burden[-1]['country'], 'rate': cvd_burden[-1]['deaths_per_100k']}
        }
    else:
        summary = {'countries_with_complete_data': 0, 
                  'note': 'No countries had both WHO and Data Commons data'}
    
    return {'cvd_burden_data': cvd_burden, 'summary': summary, 'data_availability': data_availability}

if __name__ == "__main__":
    result = get_cvd_burden_per_capita()
    print(f"\nCVD Burden Analysis: {result['data_availability']['total_countries']} countries")
    print(f"Complete data: {result['data_availability']['both_success']} countries")
