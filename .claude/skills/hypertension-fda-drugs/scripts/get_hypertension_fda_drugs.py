import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_hypertension_fda_drugs():
    """Get FDA approved drugs for hypertension.

    Returns:
        dict: Contains summary and detailed drug information
    """
    # Query FDA for hypertension drugs using label search
    # Search in indications_and_usage field for hypertension
    result = lookup_drug(
        search_term="indications_and_usage:hypertension",
        search_type="label",
        limit=100  # Get comprehensive results
    )

    if not result or 'data' not in result:
        return {
            'total_count': 0,
            'drugs': [],
            'summary': "No hypertension drugs found in FDA database."
        }

    # Extract drug data from label results
    drugs_data = result['data'].get('results', [])
    if not drugs_data:
        return {
            'total_count': 0,
            'drugs': [],
            'summary': "No hypertension drugs found in FDA database."
        }

    # Extract unique drugs by brand name
    unique_drugs = {}
    for item in drugs_data:
        openfda = item.get('openfda', {})

        # Get brand names (can be a list)
        brand_names = openfda.get('brand_name', ['Unknown'])
        brand_name = brand_names[0] if brand_names else 'Unknown'

        # Skip if already processed
        if brand_name in unique_drugs:
            continue

        # Get other details
        generic_names = openfda.get('generic_name', ['N/A'])
        generic_name = generic_names[0] if generic_names else 'N/A'

        manufacturers = openfda.get('manufacturer_name', ['N/A'])
        manufacturer = manufacturers[0] if manufacturers else 'N/A'

        product_types = openfda.get('product_type', ['N/A'])
        product_type = product_types[0] if product_types else 'N/A'

        routes = openfda.get('route', [])
        route = ', '.join(routes) if routes else 'N/A'

        unique_drugs[brand_name] = {
            'brand_name': brand_name,
            'generic_name': generic_name,
            'manufacturer': manufacturer,
            'product_type': product_type,
            'route': route
        }

    # Convert to list and sort by brand name
    drugs_list = sorted(list(unique_drugs.values()), key=lambda x: x['brand_name'])

    # Group by product type
    product_type_counts = {}
    for drug in drugs_list:
        ptype = drug['product_type']
        product_type_counts[ptype] = product_type_counts.get(ptype, 0) + 1

    # Create summary
    summary = f"""FDA Approved Hypertension Drugs Summary:

Total unique drugs: {len(drugs_list)}

Product Type Distribution:
"""
    for ptype, count in sorted(product_type_counts.items(), key=lambda x: x[1], reverse=True):
        summary += f"  - {ptype}: {count}\n"

    summary += f"\nTop 20 Drugs by Brand Name:\n"
    for i, drug in enumerate(drugs_list[:20], 1):
        summary += f"  {i}. {drug['brand_name']}\n"
        summary += f"      Generic: {drug['generic_name']}\n"
        summary += f"      Manufacturer: {drug['manufacturer']}\n"
        summary += f"      Route: {drug['route']}\n\n"

    return {
        'total_count': len(drugs_list),
        'drugs': drugs_list,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_hypertension_fda_drugs()
    print(result['summary'])
