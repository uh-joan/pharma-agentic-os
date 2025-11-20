import sys
sys.path.insert(0, ".claude")
from mcp.servers.nlm_codes_mcp import search_icd10

def get_diabetes_icd10_codes():
    """Search for diabetes-related ICD-10 codes using NLM Clinical Tables API.

    Returns:
        dict: Contains total_count, codes list, and formatted summary
    """
    # Search for diabetes ICD-10 codes
    result = search_icd10(term="diabetes", maxList=50)

    # Parse the results
    codes = []
    if isinstance(result, list) and len(result) >= 4:
        # NLM API returns: [total_count, [codes], [display_names], [additional_info]]
        total_count = result[0]
        code_list = result[1] if len(result) > 1 else []
        display_names = result[2] if len(result) > 2 else []

        # Combine codes with their descriptions
        for i in range(min(len(code_list), len(display_names))):
            codes.append({
                'code': code_list[i],
                'description': display_names[i]
            })

    # Create summary
    summary = {
        'total_count': len(codes),
        'codes': codes,
        'categories': {}
    }

    # Group by code prefix for better organization
    for code_entry in codes:
        code = code_entry['code']
        prefix = code[:3]  # First 3 characters (e.g., E10, E11)

        if prefix not in summary['categories']:
            summary['categories'][prefix] = []
        summary['categories'][prefix].append(code_entry)

    return summary

if __name__ == "__main__":
    result = get_diabetes_icd10_codes()

    print(f"\n=== Diabetes ICD-10 Codes ===")
    print(f"Total codes found: {result['total_count']}")
    print(f"\nCodes by category:")

    for prefix, codes in sorted(result['categories'].items()):
        print(f"\n{prefix} ({len(codes)} codes):")
        for code_entry in codes[:5]:  # Show first 5 per category
            print(f"  {code_entry['code']}: {code_entry['description']}")
        if len(codes) > 5:
            print(f"  ... and {len(codes) - 5} more")
