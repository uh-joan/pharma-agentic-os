import sys
sys.path.insert(0, ".claude")

from mcp.servers.who_mcp import search_indicators, get_indicator_data
from mcp.servers.datacommons_mcp import search_stat_vars, get_stat_value

def get_global_diabetes_prevalence():
    """Fetch global diabetes prevalence from WHO and Data Commons.

    Returns:
        dict: Contains summary and detailed data from both sources
            {
                'who_data': {indicator_code: {indicator_name, data}},
                'datacommons_data': {stat_var_id: {stat_var_name, data}},
                'summary': {
                    'who': {indicator_code, indicator_name, value, year, unit},
                    'datacommons': {stat_var_id, stat_var_name, value, value_millions, date}
                },
                'summary_text': str
            }
    """
    results = {
        'who_data': {},
        'datacommons_data': {},
        'summary': {}
    }

    # WHO Data Collection
    print("=== WHO Global Diabetes Data ===\n")
    try:
        # Search for diabetes prevalence indicators
        indicators = search_indicators(keywords="diabetes prevalence adults")

        if indicators and len(indicators) > 0:
            # Try multiple relevant indicators
            for indicator in indicators[:3]:
                ind_code = indicator.get('code')
                ind_name = indicator.get('name', 'Unknown')

                print(f"Trying indicator: [{ind_code}] {ind_name}")

                # Get global data
                data = get_indicator_data(
                    indicator_code=ind_code,
                    country_code="GLOBAL"
                )

                if data:
                    results['who_data'][ind_code] = {
                        'indicator_name': ind_name,
                        'data': data
                    }

                    # Extract key info
                    if isinstance(data, dict):
                        value = data.get('value')
                        year = data.get('year')
                        unit = data.get('unit', '')

                        if value:
                            print(f"  ✓ {year}: {value}{unit}")

                            # Store in summary if this is good data
                            if 'who' not in results['summary'] or not results['summary']['who'].get('value'):
                                results['summary']['who'] = {
                                    'indicator_code': ind_code,
                                    'indicator_name': ind_name,
                                    'value': value,
                                    'year': year,
                                    'unit': unit
                                }
                    elif isinstance(data, list) and len(data) > 0:
                        # Time series data - get latest
                        latest = max(data, key=lambda x: x.get('year', 0))
                        value = latest.get('value')
                        year = latest.get('year')
                        unit = latest.get('unit', '')

                        if value:
                            print(f"  ✓ {year}: {value}{unit}")

                            if 'who' not in results['summary'] or not results['summary']['who'].get('value'):
                                results['summary']['who'] = {
                                    'indicator_code': ind_code,
                                    'indicator_name': ind_name,
                                    'value': value,
                                    'year': year,
                                    'unit': unit
                                }
                else:
                    print(f"  - No data available")
                print()

        if 'who' not in results['summary']:
            results['summary']['who'] = {'error': 'No usable data found'}

    except Exception as e:
        print(f"✗ WHO error: {e}\n")
        results['summary']['who'] = {'error': str(e)}

    # Data Commons Collection
    print("=== Data Commons Global Diabetes Data ===\n")
    try:
        # Search for diabetes count/prevalence variables
        stat_vars = search_stat_vars(query="diabetes count adults global")

        if stat_vars and len(stat_vars) > 0:
            # Try multiple relevant stat vars
            for var in stat_vars[:5]:
                var_id = var.get('dcid')
                var_name = var.get('name', 'Unknown')

                print(f"Trying stat var: [{var_id}] {var_name}")

                # Get global data (Earth = World)
                data = get_stat_value(
                    place="Earth",
                    stat_var=var_id
                )

                if data and isinstance(data, dict):
                    value = data.get('value')
                    date = data.get('date')

                    if value:
                        results['datacommons_data'][var_id] = {
                            'stat_var_name': var_name,
                            'data': data
                        }

                        # Format large numbers
                        if value > 1_000_000:
                            value_millions = value / 1_000_000
                            print(f"  ✓ {date}: {value_millions:.1f}M people ({value:,})")
                        else:
                            print(f"  ✓ {date}: {value:,}")

                        # Store in summary if this looks like total count
                        if 'datacommons' not in results['summary'] or not results['summary']['datacommons'].get('value'):
                            results['summary']['datacommons'] = {
                                'stat_var_id': var_id,
                                'stat_var_name': var_name,
                                'value': value,
                                'value_millions': round(value / 1_000_000, 1) if value > 1_000_000 else value,
                                'date': date
                            }
                    else:
                        print(f"  - No value in data")
                else:
                    print(f"  - No data available")
                print()

        if 'datacommons' not in results['summary']:
            results['summary']['datacommons'] = {'error': 'No usable data found'}

    except Exception as e:
        print(f"✗ Data Commons error: {e}\n")
        results['summary']['datacommons'] = {'error': str(e)}

    # Generate summary text
    print("=" * 60)
    print("GLOBAL DIABETES PREVALENCE - AUTHORITATIVE DATA")
    print("=" * 60 + "\n")

    summary_lines = []

    # WHO summary
    if 'who' in results['summary'] and 'error' not in results['summary']['who']:
        who = results['summary']['who']
        summary_lines.append(f"WHO ({who['year']}):")
        summary_lines.append(f"  • {who['indicator_name']}")
        summary_lines.append(f"  • Prevalence: {who['value']}{who['unit']}")
        summary_lines.append(f"  • Source: WHO Indicator {who['indicator_code']}")
    else:
        summary_lines.append("WHO: " + results['summary'].get('who', {}).get('error', 'No data'))

    summary_lines.append("")

    # Data Commons summary
    if 'datacommons' in results['summary'] and 'error' not in results['summary']['datacommons']:
        dc = results['summary']['datacommons']
        summary_lines.append(f"Data Commons ({dc['date']}):")
        summary_lines.append(f"  • {dc['stat_var_name']}")
        if dc['value'] > 1_000_000:
            summary_lines.append(f"  • Total: {dc['value_millions']}M people ({dc['value']:,})")
        else:
            summary_lines.append(f"  • Total: {dc['value']:,}")
        summary_lines.append(f"  • Source: {dc['stat_var_id']}")
    else:
        summary_lines.append("Data Commons: " + results['summary'].get('datacommons', {}).get('error', 'No data'))

    summary_lines.append("")
    summary_lines.append("Note: Both sources provide authoritative global health statistics")
    summary_lines.append("suitable for citation in research and reports.")

    results['summary_text'] = "\n".join(summary_lines)
    print(results['summary_text'])

    return results

if __name__ == "__main__":
    result = get_global_diabetes_prevalence()

    # Show data collection success
    print("\n" + "=" * 60)
    who_success = 'who' in result['summary'] and 'error' not in result['summary']['who']
    dc_success = 'datacommons' in result['summary'] and 'error' not in result['summary']['datacommons']

    print(f"Data Collection Status:")
    print(f"  • WHO: {'✓ Success' if who_success else '✗ Failed'}")
    print(f"  • Data Commons: {'✓ Success' if dc_success else '✗ Failed'}")
    print("=" * 60)
