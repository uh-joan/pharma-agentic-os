"""
Index Update Mechanisms

Keeps skills index synchronized with filesystem reality. Provides functions
for adding/updating skills, health status, and validating consistency.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    from .health_check import HealthStatus
except ImportError:
    # Running as script
    sys.path.insert(0, str(Path(__file__).parent))
    from health_check import HealthStatus


def add_skill_to_index(
    skill_name: str,
    folder_name: str,
    script_path: str,
    skill_md_path: str,
    metadata: dict
) -> None:
    """Add newly created skill to index.

    Args:
        skill_name: Function name (e.g., 'get_kras_trials')
        folder_name: Folder name (e.g., 'kras-trials')
        script_path: Path to Python script (relative to .claude/skills/)
        skill_md_path: Path to SKILL.md (relative to .claude/skills/)
        metadata: {
            'description': str,
            'servers_used': list[str],
            'patterns_demonstrated': list[str],
            'category': str,
            'complexity': str,
            'function_signature': str (optional)
        }
    """
    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    # Create new skill entry
    new_skill = {
        'name': skill_name,
        'structure': 'folder',
        'folder': folder_name,
        'skill_md': skill_md_path,
        'script': script_path,
        'has_frontmatter': True,
        'description': metadata.get('description', ''),
        'function_signature': metadata.get('function_signature', f"{skill_name}() -> dict"),
        'servers_used': metadata.get('servers_used', []),
        'patterns_demonstrated': metadata.get('patterns_demonstrated', []),
        'category': metadata.get('category', 'clinical-trials'),
        'complexity': metadata.get('complexity', 'simple')
    }

    # Check if skill already exists (update instead of add)
    existing_idx = None
    for idx, skill in enumerate(index['skills']):
        if skill['name'] == skill_name:
            existing_idx = idx
            break

    if existing_idx is not None:
        # Update existing entry
        index['skills'][existing_idx] = new_skill
        action = "Updated"
    else:
        # Add new entry
        index['skills'].append(new_skill)
        action = "Added"

    # Update metadata
    index['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    index['migration_status']['folder_skills_count'] = len([
        s for s in index['skills'] if s['structure'] == 'folder'
    ])

    # Save updated index
    index_path.write_text(json.dumps(index, indent=2))

    print(f"✓ Index updated: {action} '{skill_name}' to skills library")


def update_skill_health(
    skill_name: str,
    health_status: HealthStatus,
    issues: list[str]
) -> None:
    """Update skill health status in index.

    Adds health metadata to track skill quality over time.

    Args:
        skill_name: Skill name to update
        health_status: Health status enum value
        issues: List of issues detected
    """
    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    for skill in index['skills']:
        if skill['name'] == skill_name:
            skill['health'] = {
                'status': health_status.value,
                'last_checked': datetime.now().isoformat(),
                'issues': issues
            }
            break

    index['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    index_path.write_text(json.dumps(index, indent=2))

    print(f"⚠ Index updated: '{skill_name}' marked as {health_status.value}")


def mark_skill_migrated(skill_name: str, new_folder: str) -> None:
    """Mark skill as migrated to folder structure.

    Args:
        skill_name: Skill name
        new_folder: New folder name
    """
    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    for skill in index['skills']:
        if skill['name'] == skill_name:
            skill['structure'] = 'folder'
            skill['folder'] = new_folder
            skill['skill_md'] = f"{new_folder}/SKILL.md"
            skill['script'] = f"{new_folder}/scripts/{skill_name}.py"
            skill['has_frontmatter'] = True

            # Move deprecated info
            if 'deprecated_flat_files' not in skill:
                skill['deprecated_flat_files'] = {
                    'py': f"{skill_name}.py",
                    'md': f"{skill_name}.md",
                    'status': 'deprecated',
                    'removal_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                }
            break

    index['migration_status']['folder_skills_count'] += 1
    index['migration_status']['flat_skills_count'] -= 1
    index['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    index_path.write_text(json.dumps(index, indent=2))

    print(f"✓ Index updated: '{skill_name}' migrated to folder structure")


def validate_and_sync_index() -> dict:
    """Validate index matches filesystem reality.

    Checks:
        - All indexed skills exist on filesystem
        - All skill folders have index entries
        - Health status is current

    Returns:
        {
            'valid': bool,
            'issues': list[str],
            'fixed': list[str]
        }
    """
    index_path = Path('.claude/skills/index.json')
    index = json.loads(index_path.read_text())

    issues = []
    fixed = []

    # Check 1: Index → Filesystem (orphaned entries)
    for skill in index['skills']:
        script_path = Path(f".claude/skills/{skill['script']}")
        if not script_path.exists():
            issues.append(f"Indexed skill missing: {skill['name']} ({skill['script']})")

    # Check 2: Filesystem → Index (unindexed skills)
    skills_dir = Path('.claude/skills')
    if skills_dir.exists():
        for folder in skills_dir.iterdir():
            if folder.is_dir() and folder.name not in ['scripts', '__pycache__']:
                skill_md = folder / 'SKILL.md'
                if skill_md.exists():
                    # Check if indexed
                    indexed = any(s.get('folder') == folder.name for s in index['skills'])
                    if not indexed:
                        issues.append(f"Unindexed skill found: {folder.name}")
                        # Auto-fix could parse SKILL.md frontmatter here

    # Check 3: Health status current (< 7 days old)
    for skill in index['skills']:
        if 'health' in skill:
            try:
                last_checked = datetime.fromisoformat(skill['health']['last_checked'])
                age_days = (datetime.now() - last_checked).days
                if age_days > 7:
                    issues.append(f"Stale health check: {skill['name']} ({age_days} days old)")
            except (ValueError, KeyError):
                issues.append(f"Invalid health timestamp: {skill['name']}")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'fixed': fixed
    }


def main():
    """CLI interface for index maintenance."""
    import argparse

    parser = argparse.ArgumentParser(description='Maintain skills index')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add skill
    add_parser = subparsers.add_parser('add', help='Add skill to index')
    add_parser.add_argument('--name', required=True, help='Skill name')
    add_parser.add_argument('--folder', required=True, help='Folder name')
    add_parser.add_argument('--description', default='', help='Description')
    add_parser.add_argument('--servers', required=True, help='Comma-separated servers')
    add_parser.add_argument('--patterns', default='', help='Comma-separated patterns')
    add_parser.add_argument('--category', default='clinical-trials', help='Category')
    add_parser.add_argument('--complexity', default='simple', help='Complexity')

    # Update health
    health_parser = subparsers.add_parser('health', help='Update health status')
    health_parser.add_argument('--skill', required=True, help='Skill name')
    health_parser.add_argument('--status', required=True, choices=['healthy', 'degraded', 'broken'])
    health_parser.add_argument('--issues', default='', help='Comma-separated issues')

    # Validate
    subparsers.add_parser('validate', help='Validate index consistency')

    # Sync
    subparsers.add_parser('sync', help='Sync index with filesystem')

    args = parser.parse_args()

    if args.command == 'add':
        metadata = {
            'description': args.description,
            'servers_used': args.servers.split(','),
            'patterns_demonstrated': args.patterns.split(',') if args.patterns else [],
            'category': args.category,
            'complexity': args.complexity
        }

        add_skill_to_index(
            skill_name=args.name,
            folder_name=args.folder,
            script_path=f"{args.folder}/scripts/{args.name}.py",
            skill_md_path=f"{args.folder}/SKILL.md",
            metadata=metadata
        )
        return 0

    elif args.command == 'health':
        status_map = {
            'healthy': HealthStatus.HEALTHY,
            'degraded': HealthStatus.DEGRADED,
            'broken': HealthStatus.BROKEN
        }
        issues = args.issues.split(',') if args.issues else []

        update_skill_health(
            skill_name=args.skill,
            health_status=status_map[args.status],
            issues=issues
        )
        return 0

    elif args.command == 'validate':
        result = validate_and_sync_index()

        print("Index Validation Results:")
        print(f"  Valid: {result['valid']}")

        if result['issues']:
            print(f"\nIssues found ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"  - {issue}")

        if result['fixed']:
            print(f"\nAuto-fixed ({len(result['fixed'])}):")
            for fix in result['fixed']:
                print(f"  - {fix}")

        return 0 if result['valid'] else 1

    elif args.command == 'sync':
        result = validate_and_sync_index()
        # Would implement auto-fix logic here
        print("Sync not yet implemented - use validate to see issues")
        return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
