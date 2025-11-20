import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import search_drug_label
from mcp.servers.pubchem_mcp import get_compound_by_name

def get_anticoagulant_chemical_properties():
    """Get FDA approved anticoagulants and their PubChem chemical properties.

    Returns:
        dict: Contains total count, drug list with properties, and summary
    """

    print("Step 1: Querying FDA for anticoagulant drugs...")

    fda_result = search_drug_label(search="anticoagulant", limit=100)

    if not fda_result or 'results' not in fda_result:
        return {'total_count': 0, 'drugs': [], 'summary': 'No FDA data found'}

    # Extract unique drug names
    drug_names = set()
    for result in fda_result['results']:
        if 'openfda' in result:
            for brand in result['openfda'].get('brand_name', []):
                drug_names.add(brand)
            for generic in result['openfda'].get('generic_name', []):
                drug_names.add(generic)

    print(f"Found {len(drug_names)} unique anticoagulant drug names")

    # Query PubChem for properties
    print("\nStep 2: Querying PubChem for chemical properties...")

    drugs_with_properties = []
    success = failed = 0

    for drug_name in sorted(drug_names)[:20]:  # Limit to 20
        try:
            result = get_compound_by_name(compound_name=drug_name)

            if result and 'PropertyTable' in result:
                props = result['PropertyTable'].get('Properties', [])
                if props:
                    p = props[0]
                    drugs_with_properties.append({
                        'drug_name': drug_name,
                        'cid': p.get('CID'),
                        'molecular_formula': p.get('MolecularFormula'),
                        'molecular_weight': p.get('MolecularWeight'),
                        'tpsa': p.get('TPSA'),
                        'xlogp': p.get('XLogP')
                    })
                    success += 1
                else:
                    failed += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    summary = {
        'total_fda_drugs': len(drug_names),
        'pubchem_success': success,
        'pubchem_failed': failed,
        'integration_rate': f"{(success/(success+failed)*100):.1f}%" if (success+failed) > 0 else "0%"
    }

    print(f"\n{'='*70}")
    print("MULTI-SERVER INTEGRATION SUMMARY")
    print(f"{'='*70}")
    print(f"FDA Drugs: {summary['total_fda_drugs']}")
    print(f"PubChem Success: {summary['pubchem_success']}")
    print(f"Integration Rate: {summary['integration_rate']}")
    print(f"{'='*70}")

    return {'total_count': len(drugs_with_properties), 'drugs': drugs_with_properties, 'summary': summary}

if __name__ == "__main__":
    result = get_anticoagulant_chemical_properties()
    print(f"\n✓ Integrated data for {result['total_count']} drugs")
