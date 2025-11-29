import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_semaglutide_adverse_events():
    """Get adverse event reports for semaglutide from FDA FAERS.

    Returns:
        dict: Contains total_count, top_reactions, demographics, and severity data
    """

    # FDA adverse_events with count parameter returns aggregated counts only
    # Response structure: result['data']['results'] = [{"term": "NAUSEA", "count": 11180}, ...]
    result = lookup_drug(
        search_term='semaglutide',
        search_type='adverse_events',
        count='patient.reaction.reactionmeddrapt.exact',
        limit=100  # Maximum allowed by FDA API
    )

    if not result or 'data' not in result:
        return {
            'total_count': 0,
            'summary': 'No adverse event data found for semaglutide'
        }

    # Extract results from nested structure
    data = result.get('data', {})
    reaction_counts = data.get('results', [])

    if not reaction_counts:
        return {
            'total_count': 0,
            'summary': 'No adverse event data found for semaglutide'
        }

    # Calculate total reports across all reactions
    total_reports = sum(item.get('count', 0) for item in reaction_counts)

    # Build reactions dictionary from aggregated counts
    reactions = {}
    key_concerns = {
        'muscle_loss': 0,
        'gallbladder': 0,
        'pancreatitis': 0,
        'nausea': 0,
        'vomiting': 0,
        'diarrhea': 0
    }

    for item in reaction_counts:
        reaction_term = item.get('term', '').lower()
        count = item.get('count', 0)

        if reaction_term:
            reactions[reaction_term] = count

            # Track key safety concerns
            if 'muscle' in reaction_term or 'sarcopenia' in reaction_term or 'atrophy' in reaction_term:
                key_concerns['muscle_loss'] += count
            if 'gallbladder' in reaction_term or 'cholelithiasis' in reaction_term or 'cholecystitis' in reaction_term:
                key_concerns['gallbladder'] += count
            if 'pancreatitis' in reaction_term or 'pancrea' in reaction_term:
                key_concerns['pancreatitis'] += count
            if 'nausea' in reaction_term:
                key_concerns['nausea'] += count
            if 'vomiting' in reaction_term:
                key_concerns['vomiting'] += count
            if 'diarrhea' in reaction_term or 'diarrhoea' in reaction_term:
                key_concerns['diarrhea'] += count

    top_reactions = sorted(reactions.items(), key=lambda x: x[1], reverse=True)[:20]

    summary = f"""
SEMAGLUTIDE ADVERSE EVENTS ANALYSIS
====================================

Total Adverse Event Reports: {total_reports:,}

TOP 20 REPORTED ADVERSE EVENTS:
"""
    for i, (reaction, count) in enumerate(top_reactions, 1):
        pct = (count / total_reports) * 100
        summary += f"{i:2d}. {reaction.title():40s} {count:,} ({pct:5.1f}%)\n"

    summary += f"""
KEY SAFETY CONCERNS:
- Muscle Mass Loss:        {key_concerns['muscle_loss']:,} reports
- Gallbladder Issues:      {key_concerns['gallbladder']:,} reports
- Pancreatitis:            {key_concerns['pancreatitis']:,} reports
- Nausea:                  {key_concerns['nausea']:,} reports
- Vomiting:                {key_concerns['vomiting']:,} reports
- Diarrhea:                {key_concerns['diarrhea']:,} reports

INTERPRETATION:
- Data represents aggregated FDA FAERS adverse event counts
- Count-based aggregation provides reaction frequency without individual patient details
- Reporting bias exists (more likely to report serious/unusual events)
- Data represents post-market surveillance reports (not incidence rates)
- Consider temporal trends and comparator data for full risk assessment

NOTE: Demographics and serious outcome details not available in count-based aggregation.
For detailed patient-level data, additional queries would be needed.
"""

    return {
        'total_count': total_reports,
        'top_reactions': top_reactions,
        'key_concerns': key_concerns,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_semaglutide_adverse_events()
    print(result['summary'])
