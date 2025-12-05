import sys
sys.path.insert(0, ".claude")
from mcp.servers.datacommons_mcp import search_indicators, get_observations

def get_cdc_obesity_prevalence():
    """Get CDC obesity prevalence data for the United States from Data Commons.

    Returns:
        dict: Contains adult obesity, young adult obesity, state-level, and time series data

    Example:
        result = get_cdc_obesity_prevalence()
        print(f"Adult obesity: {result['adult_obesity']['latest_value']}%")
    """

    results = {
        'adult_obesity': {},
        'young_adult_obesity': {},
        'state_level': [],
        'time_series': []
    }

    print("Fetching CDC obesity prevalence data from Data Commons...\n")

    # 1. Get adult obesity prevalence (national level)
    print("1. Fetching adult obesity prevalence (national)...")
    try:
        adult_search = search_indicators(
            query="obesity prevalence",
            places=["United States"],
            per_search_limit=5
        )

        # Extract variable DCID for adult obesity
        adult_var = None
        if 'candidates' in adult_search:
            for candidate in adult_search['candidates']:
                if 'Percent_Person_Obesity' in candidate.get('variable_dcid', ''):
                    adult_var = candidate['variable_dcid']
                    break

        if not adult_var:
            adult_var = "Percent_Person_Obesity"  # Fallback to known variable

        # Get observations
        adult_obs = get_observations(
            variable_dcid=adult_var,
            place_dcid="country/USA",
            date="latest"
        )

        if adult_obs and 'observations' in adult_obs:
            obs_list = adult_obs['observations']
            if obs_list and len(obs_list) > 0:
                latest = obs_list[-1]  # Most recent
                results['adult_obesity'] = {
                    'latest_value': latest.get('value'),
                    'latest_year': latest.get('date'),
                    'variable_dcid': adult_var
                }
                print(f"   ✓ Adult obesity: {latest.get('value')}% ({latest.get('date')})")

    except Exception as e:
        print(f"   ⚠️  Error fetching adult obesity: {str(e)}")

    # 2. Get young adult (18-24) obesity prevalence
    print("\n2. Fetching young adult (18-24) obesity prevalence...")
    try:
        young_var = "Percent_Person_18To24Years_Obesity"

        young_obs = get_observations(
            variable_dcid=young_var,
            place_dcid="country/USA",
            date="latest"
        )

        if young_obs and 'observations' in young_obs:
            obs_list = young_obs['observations']
            if obs_list and len(obs_list) > 0:
                latest = obs_list[-1]
                results['young_adult_obesity'] = {
                    'latest_value': latest.get('value'),
                    'latest_year': latest.get('date'),
                    'variable_dcid': young_var
                }
                print(f"   ✓ Young adult obesity: {latest.get('value')}% ({latest.get('date')})")

    except Exception as e:
        print(f"   ⚠️  Error fetching young adult obesity: {str(e)}")

    # 3. Get state-level data for top 5 states by population
    print("\n3. Fetching state-level obesity data...")
    states = [
        ("California", "geoId/06"),
        ("Texas", "geoId/48"),
        ("Florida", "geoId/12"),
        ("New York", "geoId/36"),
        ("Pennsylvania", "geoId/42")
    ]

    for state_name, state_dcid in states:
        try:
            state_obs = get_observations(
                variable_dcid="Percent_Person_Obesity",
                place_dcid=state_dcid,
                date="latest"
            )

            if state_obs and 'observations' in state_obs:
                obs_list = state_obs['observations']
                if obs_list and len(obs_list) > 0:
                    latest = obs_list[-1]
                    results['state_level'].append({
                        'state': state_name,
                        'value': latest.get('value'),
                        'year': latest.get('date')
                    })
                    print(f"   ✓ {state_name}: {latest.get('value')}% ({latest.get('date')})")
        except Exception as e:
            print(f"   ⚠️  Error fetching {state_name}: {str(e)}")

    # 4. Get time series for trend analysis (last 10 years)
    print("\n4. Fetching time series data (2015-2024)...")
    try:
        time_series_obs = get_observations(
            variable_dcid="Percent_Person_Obesity",
            place_dcid="country/USA",
            date="range",
            date_range_start="2015",
            date_range_end="2024"
        )

        if time_series_obs and 'observations' in time_series_obs:
            results['time_series'] = [
                {
                    'year': obs.get('date'),
                    'value': obs.get('value')
                }
                for obs in time_series_obs['observations']
            ]
            print(f"   ✓ Retrieved {len(results['time_series'])} years of data")
    except Exception as e:
        print(f"   ⚠️  Error fetching time series: {str(e)}")

    # Generate summary
    summary_parts = []
    if results['adult_obesity']:
        summary_parts.append(
            f"Adult obesity prevalence: {results['adult_obesity']['latest_value']}% "
            f"({results['adult_obesity']['latest_year']})"
        )
    if results['young_adult_obesity']:
        summary_parts.append(
            f"Young adult (18-24) obesity: {results['young_adult_obesity']['latest_value']}% "
            f"({results['young_adult_obesity']['latest_year']})"
        )

    results['summary'] = " | ".join(summary_parts)

    return results

if __name__ == "__main__":
    result = get_cdc_obesity_prevalence()

    print("\n" + "="*80)
    print("CDC OBESITY PREVALENCE DATA")
    print("="*80)

    if result['adult_obesity']:
        print(f"\nAdult obesity prevalence: {result['adult_obesity']['latest_value']}% "
              f"({result['adult_obesity']['latest_year']})")

    if result['young_adult_obesity']:
        print(f"Young adult (18-24) obesity: {result['young_adult_obesity']['latest_value']}% "
              f"({result['young_adult_obesity']['latest_year']})")

    if result['state_level']:
        print(f"\nState-level data ({result['state_level'][0]['year']}):")
        for state in result['state_level']:
            print(f"  - {state['state']}: {state['value']}%")

    if result['time_series']:
        print(f"\nTime series trends ({len(result['time_series'])} years):")
        for entry in result['time_series']:
            print(f"  - {entry['year']}: {entry['value']}%")

    print("\n" + "="*80)
