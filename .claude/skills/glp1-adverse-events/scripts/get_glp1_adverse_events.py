import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug
import re

def get_glp1_adverse_events():
    """Extract adverse event rates from FDA drug labels for GLP-1 drugs.

    Queries FDA labels for major GLP-1 drugs and extracts common adverse event
    rates (nausea, vomiting, diarrhea, constipation, discontinuation).

    Returns:
        dict: Contains total_drugs_analyzed, adverse_events by drug, and summary
    """

    # GLP-1 drugs to analyze
    drugs = {
        'semaglutide': ['semaglutide', 'ozempic', 'wegovy'],
        'tirzepatide': ['tirzepatide', 'mounjaro', 'zepbound'],
        'liraglutide': ['liraglutide', 'victoza', 'saxenda'],
        'dulaglutide': ['dulaglutide', 'trulicity'],
        'exenatide': ['exenatide', 'byetta', 'bydureon'],
        'oral_semaglutide': ['rybelsus']
    }

    adverse_events = {}
    drugs_analyzed = 0

    # Common adverse events to extract
    ae_patterns = {
        'nausea': r'nausea[^\d]*(\d+(?:\.\d+)?)\s*%',
        'vomiting': r'vomit(?:ing)?[^\d]*(\d+(?:\.\d+)?)\s*%',
        'diarrhea': r'diarrhea[^\d]*(\d+(?:\.\d+)?)\s*%',
        'constipation': r'constipation[^\d]*(\d+(?:\.\d+)?)\s*%',
        'discontinued': r'discontinu(?:ed|ation)[^\d]*(\d+(?:\.\d+)?)\s*%'
    }

    for drug_key, search_terms in drugs.items():
        print(f"Analyzing {drug_key}...")

        # Try each search term until we get a result
        label_text = None
        for term in search_terms:
            try:
                result = lookup_drug(term, search_type='label')

                # FDA MCP returns nested structure: result['data']['results']
                if result and 'data' in result and 'results' in result['data'] and len(result['data']['results']) > 0:
                    # Extract label text
                    label_data = result['data']['results'][0]

                    # Look for adverse reactions in various sections
                    sections = []
                    if 'adverse_reactions' in label_data:
                        sections.append(label_data['adverse_reactions'])
                    if 'openfda' in label_data:
                        if 'adverse_reactions' in label_data['openfda']:
                            sections.extend(label_data['openfda']['adverse_reactions'])
                    if 'boxed_warning' in label_data:
                        sections.append(label_data['boxed_warning'])
                    if 'warnings_and_cautions' in label_data:
                        sections.append(label_data['warnings_and_cautions'])

                    # Combine all relevant sections
                    label_text = ' '.join(str(s) for s in sections if s)

                    if label_text and len(label_text) > 100:
                        break

            except Exception as e:
                print(f"  Error querying {term}: {e}")
                continue

        if not label_text:
            print(f"  No label data found for {drug_key}")
            adverse_events[drug_key] = {'error': 'No label data found'}
            continue

        # Extract adverse event rates
        drug_ae = {}
        label_lower = label_text.lower()

        for ae_name, pattern in ae_patterns.items():
            matches = re.findall(pattern, label_lower, re.IGNORECASE)
            if matches:
                # Take the first match (usually the most prominent rate)
                try:
                    rate = float(matches[0])
                    drug_ae[ae_name] = rate
                except ValueError:
                    continue

        if drug_ae:
            adverse_events[drug_key] = drug_ae
            drugs_analyzed += 1
            print(f"  ✓ Found {len(drug_ae)} adverse event rates")
        else:
            adverse_events[drug_key] = {'note': 'No rates extracted (manual review needed)'}
            print(f"  ⚠ Label found but rates not extracted (text format may vary)")

    # Generate summary
    summary_lines = [
        f"FDA Drug Label Adverse Events Analysis - GLP-1 Drugs",
        f"=" * 60,
        f"Total drugs analyzed: {drugs_analyzed}/6",
        "",
        "Adverse Event Rates by Drug:"
    ]

    for drug, events in adverse_events.items():
        if 'error' in events or 'note' in events:
            summary_lines.append(f"\n{drug.upper()}: {events.get('error') or events.get('note')}")
        else:
            summary_lines.append(f"\n{drug.upper()}:")
            for event, rate in sorted(events.items()):
                summary_lines.append(f"  - {event.capitalize()}: {rate}%")

    summary_lines.extend([
        "",
        "Note: Rates extracted via regex patterns from FDA labels.",
        "Label text formats vary - some rates may require manual extraction.",
        "Data represents most common adverse events reported in clinical trials."
    ])

    return {
        'total_drugs_analyzed': drugs_analyzed,
        'adverse_events': adverse_events,
        'summary': '\n'.join(summary_lines)
    }

if __name__ == "__main__":
    result = get_glp1_adverse_events()
    print(result['summary'])
