import sys
sys.path.insert(0, ".claude")
from mcp.servers.healthcare_mcp import search_providers

def get_texas_cardiologists():
    """Get cardiologists practicing in Texas using CMS Medicare provider data.

    Returns:
        dict: Contains total_count, providers list, and summary
    """
    # Search for cardiologists in Texas
    result = search_providers(
        specialty="Cardiology",
        state="TX",
        limit=100
    )

    providers = result.get('providers', [])
    total_count = len(providers)

    # Aggregate data
    cities = {}
    organization_types = {}

    for provider in providers:
        # Count by city
        city = provider.get('city', 'Unknown')
        cities[city] = cities.get(city, 0) + 1

        # Count by organization type
        org_type = provider.get('organization_type', 'Individual')
        organization_types[org_type] = organization_types.get(org_type, 0) + 1

    # Sort cities by count
    top_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]

    # Build summary
    summary = f"""Texas Cardiologists Summary
========================

Total Providers: {total_count}

Top 10 Cities:
"""

    for city, count in top_cities:
        summary += f"  • {city}: {count} providers\n"

    summary += f"\nOrganization Types:\n"
    for org_type, count in sorted(organization_types.items(), key=lambda x: x[1], reverse=True):
        summary += f"  • {org_type}: {count} providers\n"

    return {
        'total_count': total_count,
        'providers': providers,
        'cities': dict(top_cities),
        'organization_types': organization_types,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_texas_cardiologists()
    print(result['summary'])
