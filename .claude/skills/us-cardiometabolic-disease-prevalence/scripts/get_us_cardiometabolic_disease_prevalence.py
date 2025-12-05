import sys
sys.path.insert(0, ".claude")
from mcp.servers.datacommons_mcp import search_statvar, get_stat_series

def get_us_cardiometabolic_disease_prevalence():
    """Get US data for cardiovascular and metabolic comorbidities.

    Attempts to fetch prevalence data for:
    - NASH/MASH (Non-alcoholic steatohepatitis / Metabolic dysfunction-associated steatohepatitis)
    - HFpEF (Heart failure with preserved ejection fraction)
    - CKD (Chronic kidney disease)

    Note: Data Commons may not have direct prevalence data for all conditions.
    The function returns available epidemiological data (mortality, incidence, etc.)
    and clearly indicates when prevalence data is not available.

    Returns:
        dict: Contains available data and summary with data availability notes
    """
    results = {}
    summary_lines = []

    # Disease queries prioritizing prevalence data
    disease_configs = {
        'CKD': {
            'full_name': 'Chronic Kidney Disease',
            'search_terms': [
                'chronic kidney disease prevalence',
                'kidney disease prevalence adults',
                'chronic kidney disease',
                'kidney disease'
            ]
        },
        'HFpEF': {
            'full_name': 'Heart Failure with Preserved Ejection Fraction',
            'search_terms': [
                'heart failure prevalence',
                'heart failure cases',
                'heart failure',
                'cardiovascular disease prevalence'
            ]
        },
        'NASH/MASH': {
            'full_name': 'Non-Alcoholic Steatohepatitis / Metabolic Dysfunction-Associated Steatohepatitis',
            'search_terms': [
                'fatty liver disease prevalence',
                'liver disease prevalence',
                'non-alcoholic fatty liver',
                'liver disease'
            ]
        }
    }

    for disease_code, config in disease_configs.items():
        print(f"\n{'='*70}")
        print(f"Searching for {config['full_name']} ({disease_code})")
        print('='*70)

        disease_data = None
        best_stat_type = None  # Track what type of statistic we found

        for search_term in config['search_terms']:
            print(f"\nQuery: '{search_term}'")

            try:
                search_result = search_statvar(search_term)

                if not search_result or 'statVars' not in search_result or not search_result['statVars']:
                    print("  No statistical variables found")
                    continue

                stat_vars = search_result['statVars']
                print(f"  Found {len(stat_vars)} statistical variables")

                # Prioritize different types of statistics
                stat_priorities = [
                    ('prevalence', ['prevalence', 'percent of population']),
                    ('incidence', ['incidence', 'new cases']),
                    ('count', ['count', 'number of people', 'cases']),
                    ('mortality', ['death', 'mortality', 'deaths'])
                ]

                for priority_name, priority_keywords in stat_priorities:
                    if disease_data and best_stat_type in ['prevalence', 'incidence', 'count']:
                        break  # Already found good data

                    for stat_var in stat_vars[:20]:  # Check top 20 results
                        name = stat_var.get('name', '').lower()
                        dcid = stat_var.get('dcid', '')

                        if not any(keyword in name for keyword in priority_keywords):
                            continue

                        print(f"  Checking [{priority_name}]: {stat_var.get('name', 'Unknown')[:60]}...")

                        try:
                            # Get time series data
                            stat_series = get_stat_series(
                                place='country/USA',
                                stat_var=dcid
                            )

                            if stat_series and 'series' in stat_series and stat_series['series']:
                                series_data = stat_series['series']
                                dates = sorted(series_data.keys(), reverse=True)

                                if dates:
                                    latest_date = dates[0]
                                    value = series_data[latest_date]

                                    if value and value > 0:
                                        disease_data = {
                                            'disease_code': disease_code,
                                            'disease_name': config['full_name'],
                                            'search_term': search_term,
                                            'stat_var_name': stat_var.get('name', 'Unknown'),
                                            'stat_var_dcid': dcid,
                                            'stat_type': priority_name,
                                            'value': value,
                                            'date': latest_date
                                        }
                                        best_stat_type = priority_name
                                        print(f"  ✓ Found {priority_name} data: {value:,.0f} ({latest_date})")
                                        break
                        except Exception as e:
                            continue

                    if disease_data and best_stat_type == priority_name:
                        break

                if disease_data and best_stat_type in ['prevalence', 'incidence', 'count']:
                    break  # Found good data, stop searching

            except Exception as e:
                print(f"  Error: {e}")
                continue

        # Store result and create summary
        if disease_data:
            results[disease_code] = disease_data

            # Format the summary based on data type
            if disease_data['stat_type'] == 'mortality':
                summary_lines.append(
                    f"⚠️  {disease_code}: Only mortality data available - {disease_data['value']:,.0f} deaths/year ({disease_data['date']}). "
                    f"Prevalence data not found in Data Commons."
                )
            else:
                summary_lines.append(
                    f"✓ {disease_code}: {disease_data['value']:,.0f} ({disease_data['stat_type']}, {disease_data['date']})"
                )
        else:
            results[disease_code] = None
            summary_lines.append(
                f"✗ {disease_code}: No data found in Data Commons"
            )

    # Create summary with data availability note
    data_found = sum(1 for v in results.values() if v is not None)
    prevalence_found = sum(1 for v in results.values() if v and v['stat_type'] == 'prevalence')

    summary = {
        'total_diseases_queried': len(disease_configs),
        'diseases_with_any_data': data_found,
        'diseases_with_prevalence': prevalence_found,
        'data_completeness': f"{data_found}/{len(disease_configs)} diseases have data",
        'prevalence_completeness': f"{prevalence_found}/{len(disease_configs)} diseases have prevalence data",
        'note': (
            "Data Commons has limited prevalence data for specific disease subtypes. "
            "Claims in competitive landscape report requiring prevalence data may need "
            "alternative sources (e.g., published literature, disease registries, CDC reports)."
        ),
        'details': '\n'.join(summary_lines)
    }

    return {
        'results': results,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_us_cardiometabolic_disease_prevalence()

    print("\n" + "="*80)
    print("US CARDIOMETABOLIC DISEASE DATA SEARCH")
    print("="*80)

    print(f"\nData Completeness:")
    print(f"  Any data: {result['summary']['data_completeness']}")
    print(f"  Prevalence data: {result['summary']['prevalence_completeness']}")

    print(f"\n{result['summary']['details']}")

    print(f"\n{result['summary']['note']}")

    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)

    for disease_code, data in result['results'].items():
        if data:
            print(f"\n{disease_code} ({data['disease_name']}):")
            print(f"  Data Type: {data['stat_type'].upper()}")
            print(f"  Statistical Variable: {data['stat_var_name']}")
            print(f"  Value: {data['value']:,.0f}")
            print(f"  Year: {data['date']}")
            print(f"  DCID: {data['stat_var_dcid']}")

            if data['stat_type'] == 'mortality':
                print(f"  ⚠️  NOTE: This is mortality data, not prevalence. Direct prevalence not available.")
        else:
            print(f"\n{disease_code}: No data found in Data Commons")

    print("\n" + "="*80)
    print("RECOMMENDATION FOR REPORT CITATIONS")
    print("="*80)
    print("\nFor the competitive landscape report, these prevalence claims need alternative sources:")
    print("1. NASH/MASH prevalence (3-5% US population) - Consider AASLD/EASL literature")
    print("2. HFpEF prevalence (3-5M US patients) - Consider AHA/ACC heart failure reports")
    print("3. CKD prevalence (15% US adults) - Consider NIDDK/USRDS reports")
    print("\nData Commons focuses on broad population health statistics rather than")
    print("specific disease prevalence for rare/emerging conditions.")
