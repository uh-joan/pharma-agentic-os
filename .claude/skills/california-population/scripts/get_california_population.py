import sys
sys.path.insert(0, ".claude")
from mcp.servers.datacommons_mcp import query

def get_california_population():
    """Get population statistics for California from Data Commons.

    This skill demonstrates querying the Data Commons knowledge graph
    for demographic statistics using geographic entity codes and
    statistical variables.

    Returns:
        dict: Contains summary and data with the following structure:
            {
                'summary': str (human-readable summary),
                'data': dict (full Data Commons response with nested structure)
            }

    Example:
        >>> result = get_california_population()
        >>> print(result['summary'])
        California Population Data Retrieved
        Source: Data Commons
        Population (2022): 39,029,342
    """
    # Query population data for California using FIPS code
    result = query(
        entities=["geoId/06"],  # California geographic identifier
        variables=["Count_Person"]  # Total population variable
    )

    # Extract and format the data
    if result and isinstance(result, dict):
        summary_text = "California Population Data Retrieved\nSource: Data Commons\n"

        # Try to extract population value if available in response
        if 'data' in result and isinstance(result['data'], dict):
            if 'geoId/06' in result['data']:
                ca_data = result['data']['geoId/06']
                if 'Count_Person' in ca_data and ca_data['Count_Person']:
                    # Extract most recent population value
                    pop_entries = ca_data['Count_Person']
                    if pop_entries and len(pop_entries) > 0:
                        latest = pop_entries[0]
                        if 'value' in latest:
                            pop_value = f"{latest['value']:,}"
                            year = latest.get('date', 'Latest')
                            summary_text += f"Population ({year}): {pop_value}\n"

        summary_text += f"Full Response: {result}"

        return {
            'summary': summary_text,
            'data': result
        }
    else:
        return {
            'summary': 'No data retrieved from Data Commons',
            'data': None
        }

if __name__ == "__main__":
    result = get_california_population()
    print(result['summary'])
