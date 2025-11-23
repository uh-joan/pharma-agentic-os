import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_adc_fda_drugs():
    """Get all FDA approved antibody-drug conjugate (ADC) drugs."""

    # Known ADC drug names (brand and generic)
    adc_terms = [
        "trastuzumab emtansine", "Kadcyla",
        "trastuzumab deruxtecan", "Enhertu",
        "brentuximab vedotin", "Adcetris",
        "polatuzumab vedotin", "Polivy",
        "enfortumab vedotin", "Padcev",
        "sacituzumab govitecan", "Trodelvy",
        "inotuzumab ozogamicin", "Besponsa",
        "gemtuzumab ozogamicin", "Mylotarg",
        "moxetumomab pasudotox", "Lumoxiti",
        "belantamab mafodotin", "Blenrep",
        "tisotumab vedotin", "Tivdak",
        "loncastuximab tesirine", "Zynlonta",
        "mirvetuximab soravtansine", "Elahere"
    ]
    all_results = []

    for term in adc_terms:
        try:
            result = lookup_drug(search_term=term, search_type="general", limit=10, count='openfda.brand_name.exact')
            if result and 'results' in result:
                all_results.extend(result['results'])
        except Exception as e:
            print(f"Warning: Could not fetch data for {term}: {e}")
            continue
    
    # Deduplicate by generic name
    unique_drugs = {}
    for drug in all_results:
        openfda = drug.get('openfda', {})
        generic_name = openfda.get('generic_name', [])
        
        if generic_name:
            key = generic_name[0].lower()
            if key not in unique_drugs:
                unique_drugs[key] = {
                    'generic_name': generic_name[0],
                    'brand_name': openfda.get('brand_name', [''])[0],
                    'manufacturer': openfda.get('manufacturer_name', [''])[0],
                    'approval_date': drug.get('effective_time', 'Unknown')
                }
    
    drugs_list = list(unique_drugs.values())
    
    return {
        'total_count': len(drugs_list),
        'adc_drugs': drugs_list
    }

if __name__ == "__main__":
    result = get_adc_fda_drugs()
    print(f"ADC approved drugs: {result['total_count']} unique drugs")
    for drug in result['adc_drugs']:
        print(f"  {drug['brand_name']} ({drug['generic_name']}) - {drug['manufacturer']}")
