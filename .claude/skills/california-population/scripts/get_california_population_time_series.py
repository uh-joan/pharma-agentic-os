import sys
sys.path.insert(0, ".claude")
from mcp.servers.datacommons_mcp import search_indicators, get_observations

def get_california_population_time_series():
    """Get California population time series data.

    Returns:
        dict: Population data with time series and summary statistics
    """
    # Step 1: Search for population indicator
    search_result = search_indicators(
        query="population",
        places=["California, USA"],
        include_topics=False,
        per_search_limit=1
    )

    # Extract variable and place DCIDs
    variables = search_result.get('variables', [])
    if not variables:
        return {'error': 'No population variable found for California'}

    variable_dcid = variables[0]['dcid']
    places_with_data = variables[0].get('places_with_data', [])
    if not places_with_data:
        return {'error': 'No place data available'}

    place_dcid = places_with_data[0]

    # Step 2: Get observations (all historical data)
    obs_result = get_observations(
        variable_dcid=variable_dcid,
        place_dcid=place_dcid,
        date="all"
    )

    # Process results
    place_observations = obs_result.get('place_observations', [])
    if not place_observations:
        return {'error': 'No observations found'}

    time_series = place_observations[0].get('time_series', [])
    if not time_series:
        return {'error': 'No time series data'}

    # Convert to list of dicts and sort by date
    observations = [
        {'date': date, 'population': int(value)}
        for date, value in time_series
    ]
    observations.sort(key=lambda x: x['date'])

    # Calculate growth rates
    for i in range(1, len(observations)):
        prev_pop = observations[i-1]['population']
        curr_pop = observations[i]['population']
        growth_rate = ((curr_pop - prev_pop) / prev_pop) * 100
        observations[i]['growth_rate'] = round(growth_rate, 2)

    return {
        'summary': {
            'total_years': len(observations),
            'earliest_year': observations[0]['date'] if observations else None,
            'latest_year': observations[-1]['date'] if observations else None,
            'earliest_population': observations[0]['population'] if observations else None,
            'latest_population': observations[-1]['population'] if observations else None
        },
        'observations': observations,
        'source': obs_result.get('source_metadata', {}).get('import_name', 'Data Commons')
    }

if __name__ == "__main__":
    result = get_california_population_time_series()
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        summary = result['summary']
        print(f"California Population Time Series")
        print(f"  Years: {summary['total_years']} ({summary['earliest_year']} - {summary['latest_year']})")
        print(f"  Population: {summary['earliest_population']:,} → {summary['latest_population']:,}")
        print(f"  Source: {result['source']}")
        print(f"\nShowing last 5 years:")
        for obs in result['observations'][-5:]:
            growth = f" (+{obs['growth_rate']}%)" if 'growth_rate' in obs else ""
            print(f"  {obs['date']}: {obs['population']:,}{growth}")
