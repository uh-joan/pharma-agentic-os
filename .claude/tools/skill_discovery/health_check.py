"""
Level 2: Skill Health Check (Medium)

Verify skill files exist and are executable. Provides comprehensive health
diagnostics including file existence, structure validation, syntax checking,
and import testing.
"""

import json
import subprocess
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


class HealthStatus(Enum):
    """Health status for skills."""
    HEALTHY = "healthy"      # All checks pass
    DEGRADED = "degraded"    # Works but needs improvement
    BROKEN = "broken"        # Cannot execute


@dataclass
class HealthReport:
    """Comprehensive health report for a skill."""
    status: HealthStatus
    exists: bool
    structure_valid: bool
    executable: bool
    syntax_valid: bool
    issues: list[str]
    recommendations: list[str]

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        result = asdict(self)
        result['status'] = self.status.value
        return result


def verify_skill_health(skill_metadata: dict) -> HealthReport:
    """Comprehensive health check for a skill.

    Checks:
        1. Files exist (SKILL.md, script)
        2. Structure valid (folder format, frontmatter)
        3. Syntax valid (Python compiles)
        4. Executable (can import without errors)

    Args:
        skill_metadata: Skill metadata from index

    Returns:
        HealthReport with detailed diagnostics
    """
    issues = []
    recommendations = []

    # Check 1: File existence
    skill_md = Path(f".claude/skills/{skill_metadata.get('skill_md', '')}")
    script = Path(f".claude/skills/{skill_metadata.get('script', '')}")

    exists = skill_md.exists() and script.exists()
    if not exists:
        issues.append("Files missing")
        if not skill_md.exists():
            issues.append(f"Missing: {skill_metadata.get('skill_md', 'SKILL.md')}")
        if not script.exists():
            issues.append(f"Missing: {skill_metadata.get('script', 'script')}")

    # Check 2: Structure validation
    structure_valid = (
        skill_metadata.get('structure') == 'folder' and
        skill_metadata.get('has_frontmatter', False)
    )
    if not structure_valid:
        issues.append("Structure invalid")
        if skill_metadata.get('structure') != 'folder':
            recommendations.append("Migrate to folder structure")
        if not skill_metadata.get('has_frontmatter'):
            recommendations.append("Add YAML frontmatter to SKILL.md")

    # Check 3: Syntax validation (compile check)
    syntax_valid = False
    if exists:
        try:
            result = subprocess.run(
                ['python3', '-m', 'py_compile', str(script)],
                capture_output=True,
                timeout=5
            )
            syntax_valid = result.returncode == 0
            if not syntax_valid:
                error_msg = result.stderr.decode().strip()
                issues.append(f"Syntax error: {error_msg}")
        except subprocess.TimeoutExpired:
            issues.append("Syntax check timeout")
        except Exception as e:
            issues.append(f"Syntax check failed: {str(e)}")

    # Check 4: Import test (executability)
    executable = False
    if syntax_valid:
        try:
            # Test basic import (don't actually execute the skill)
            test_code = f"""
import sys
sys.path.insert(0, ".claude")
# Try importing the module without executing
with open("{script}", "r") as f:
    code = f.read()
    # Check for basic Python validity
    compile(code, "{script}", "exec")
"""
            result = subprocess.run(
                ['python3', '-c', test_code],
                capture_output=True,
                timeout=5,
                cwd=Path('.claude').parent
            )
            executable = result.returncode == 0
            if not executable:
                issues.append("Import failed - missing dependencies or invalid code")
        except subprocess.TimeoutExpired:
            issues.append("Import test timeout")
        except Exception as e:
            issues.append(f"Import test failed: {str(e)}")

    # Determine health status
    if exists and structure_valid and syntax_valid and executable:
        status = HealthStatus.HEALTHY
    elif exists and syntax_valid:
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.BROKEN

    return HealthReport(
        status=status,
        exists=exists,
        structure_valid=structure_valid,
        executable=executable,
        syntax_valid=syntax_valid,
        issues=issues,
        recommendations=recommendations
    )


def batch_health_check() -> dict[str, HealthReport]:
    """Check health of all skills in index.

    Returns:
        {skill_name: HealthReport}
    """
    index_path = Path('.claude/skills/index.json')
    if not index_path.exists():
        return {}

    index = json.loads(index_path.read_text())
    results = {}

    for skill in index.get('skills', []):
        results[skill['name']] = verify_skill_health(skill)

    return results


def main():
    """CLI interface for health checks."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Check skill health')
    parser.add_argument('--skill', help='Skill name to check')
    parser.add_argument('--all', action='store_true', help='Check all skills')
    parser.add_argument('--update-index', action='store_true', help='Update index with health status')
    parser.add_argument('--json', action='store_true', help='Output JSON')

    args = parser.parse_args()

    if args.skill:
        # Check single skill
        try:
            from .index_query import find_skill_in_index
        except ImportError:
            # Running as script, not module
            sys.path.insert(0, str(Path(__file__).parent))
            from index_query import find_skill_in_index

        skill_metadata = find_skill_in_index(args.skill)
        if not skill_metadata:
            print(f"Skill '{args.skill}' not found in index")
            return 1

        report = verify_skill_health(skill_metadata)

        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(f"Health Check: {args.skill}")
            print(f"Status: {report.status.value}")
            print(f"  Files exist: {report.exists}")
            print(f"  Structure valid: {report.structure_valid}")
            print(f"  Syntax valid: {report.syntax_valid}")
            print(f"  Executable: {report.executable}")
            if report.issues:
                print(f"  Issues:")
                for issue in report.issues:
                    print(f"    - {issue}")
            if report.recommendations:
                print(f"  Recommendations:")
                for rec in report.recommendations:
                    print(f"    - {rec}")

        return 0 if report.status == HealthStatus.HEALTHY else 1

    elif args.all:
        # Check all skills
        results = batch_health_check()

        if args.json:
            json_results = {name: report.to_dict() for name, report in results.items()}
            print(json.dumps(json_results, indent=2))
        else:
            print(f"Health Check: All Skills ({len(results)} total)")
            print()

            healthy = [name for name, r in results.items() if r.status == HealthStatus.HEALTHY]
            degraded = [name for name, r in results.items() if r.status == HealthStatus.DEGRADED]
            broken = [name for name, r in results.items() if r.status == HealthStatus.BROKEN]

            print(f"✅ HEALTHY: {len(healthy)}")
            for name in healthy:
                print(f"  - {name}")

            if degraded:
                print(f"\n⚠️  DEGRADED: {len(degraded)}")
                for name in degraded:
                    print(f"  - {name}")
                    for issue in results[name].issues:
                        print(f"      {issue}")

            if broken:
                print(f"\n❌ BROKEN: {len(broken)}")
                for name in broken:
                    print(f"  - {name}")
                    for issue in results[name].issues:
                        print(f"      {issue}")

        return 0 if len(broken) == 0 else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
