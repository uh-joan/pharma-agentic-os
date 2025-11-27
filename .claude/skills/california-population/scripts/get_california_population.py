import sys
sys.path.insert(0, ".claude")
from mcp.servers.datacommons_mcp import search_indicators, get_observations

def get_california_population():
    """Get latest population statistics for California from Data Commons.

    This skill demonstrates querying the Data Commons knowledge graph
    for demographic statistics using the proper two-step workflow.

    Returns:
        dict: Contains summary and data with the following structure:
            {
                'summary': str (human-readable summary),
                'population': int (latest population value),
                'year': str (year of the data),
                'source': str (data source name)
            }

    Example:
        >>> result = get_california_population()
        >>> print(result['summary'])
        California Population (2024): 39,538,223
        Source: USCensusPEP_Annual_Population
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
        return {
            'summary': 'No population variable found for California',
            'population': None,
            'year': None,
            'source': None
        }

    variable_dcid = variables[0]['dcid']
    places_with_data = variables[0].get('places_with_data', [])
    if not places_with_data:
        return {
            'summary': 'No place data available',
            'population': None,
            'year': None,
            'source': None
        }

    place_dcid = places_with_data[0]

    # Step 2: Get latest observation
    obs_result = get_observations(
        variable_dcid=variable_dcid,
        place_dcid=place_dcid,
        date="latest"
    )

    # Extract latest value
    place_observations = obs_result.get('place_observations', [])
    if not place_observations:
        return {
            'summary': 'No observations found',
            'population': None,
            'year': None,
            'source': None
        }

    time_series = place_observations[0].get('time_series', [])
    if not time_series:
        return {
            'summary': 'No time series data',
            'population': None,
            'year': None,
            'source': None
        }

    # Get latest data point
    year, population = time_series[0]
    source = obs_result.get('source_metadata', {}).get('import_name', 'Data Commons')

    summary_text = f"California Population ({year}): {int(population):,}\nSource: {source}"

    return {
        'summary': summary_text,
        'population': int(population),
        'year': year,
        'source': source
    }

if __name__ == "__main__":
    result = get_california_population()
    print(result['summary'])
