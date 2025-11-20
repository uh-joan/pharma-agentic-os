"""
Level 1: Index-Based Discovery (Fast)

Fast skill discovery using index.json as the source of truth.
Provides immediate access to skill metadata without filesystem scanning.
"""

import json
from pathlib import Path
from typing import Optional


def find_skill_in_index(skill_name: str) -> Optional[dict]:
    """Check if skill exists in index with full metadata.

    Args:
        skill_name: Skill function name (e.g., 'get_glp1_trials')

    Returns:
        Skill metadata dict or None if not found
        {
            'name': 'get_glp1_trials',
            'structure': 'folder',
            'folder': 'glp1-trials',
            'script': 'glp1-trials/scripts/get_glp1_trials.py',
            'servers_used': ['ct_gov_mcp'],
            'patterns_demonstrated': ['pagination', 'markdown_parsing'],
            'category': 'clinical-trials',
            'complexity': 'medium'
        }
    """
    index_path = Path('.claude/skills/index.json')
    if not index_path.exists():
        return None

    index = json.loads(index_path.read_text())

    for skill in index.get('skills', []):
        if skill['name'] == skill_name:
            return skill

    return None


def query_skills_by_criteria(
    server: Optional[str] = None,
    category: Optional[str] = None,
    pattern: Optional[str] = None,
    complexity: Optional[str] = None
) -> list[dict]:
    """Find skills matching criteria.

    Examples:
        >>> query_skills_by_criteria(server='ct_gov_mcp')
        >>> query_skills_by_criteria(pattern='pagination')
        >>> query_skills_by_criteria(category='clinical-trials', complexity='simple')

    Args:
        server: Filter by MCP server (e.g., 'ct_gov_mcp')
        category: Filter by category (e.g., 'clinical-trials', 'drug-discovery')
        pattern: Filter by pattern (e.g., 'pagination', 'markdown_parsing')
        complexity: Filter by complexity (e.g., 'simple', 'medium', 'complex')

    Returns:
        List of skill metadata dicts matching criteria
    """
    index_path = Path('.claude/skills/index.json')
    if not index_path.exists():
        return []

    index = json.loads(index_path.read_text())
    results = []

    for skill in index.get('skills', []):
        matches = True

        if server and server not in skill.get('servers_used', []):
            matches = False
        if category and category != skill.get('category'):
            matches = False
        if pattern and pattern not in skill.get('patterns_demonstrated', []):
            matches = False
        if complexity and complexity != skill.get('complexity'):
            matches = False

        if matches:
            results.append(skill)

    return results


def main():
    """CLI interface for index queries."""
    import argparse

    parser = argparse.ArgumentParser(description='Query skills index')
    parser.add_argument('--name', help='Skill name to find')
    parser.add_argument('--server', help='Filter by server (e.g., ct_gov_mcp)')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--pattern', help='Filter by pattern')
    parser.add_argument('--complexity', help='Filter by complexity')
    parser.add_argument('--json', action='store_true', help='Output JSON')

    args = parser.parse_args()

    if args.name:
        result = find_skill_in_index(args.name)
        if args.json:
            print(json.dumps(result, indent=2))
        elif result:
            print(f"Found skill: {result['name']}")
            print(f"  Structure: {result.get('structure', 'unknown')}")
            print(f"  Script: {result.get('script', 'unknown')}")
            print(f"  Servers: {', '.join(result.get('servers_used', []))}")
            print(f"  Patterns: {', '.join(result.get('patterns_demonstrated', []))}")
        else:
            print(f"Skill '{args.name}' not found in index")
            return 1
    else:
        results = query_skills_by_criteria(
            server=args.server,
            category=args.category,
            pattern=args.pattern,
            complexity=args.complexity
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Found {len(results)} matching skills:")
            for skill in results:
                print(f"  - {skill['name']} ({skill.get('category', 'unknown')})")

    return 0


if __name__ == "__main__":
    exit(main())
