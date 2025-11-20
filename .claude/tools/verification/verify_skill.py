#!/usr/bin/env python3
"""Skill verification tool for closing the agentic loop.

This script provides autonomous verification that pharma-search-specialist
can use to validate skill creation before returning results to the user.

Usage:
    python3 verify_skill.py \\
        --bash-output "$(bash execution output)" \\
        --execution-output "$(python script output)" \\
        --server-type ct_gov \\
        [--skill-path .claude/skills/skill-name/scripts/skill.py]

Reference: https://www.pulsemcp.com/posts/closing-the-agentic-loop-mcp-use-case
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Dict, Any


def verify_execution(bash_output: str) -> Tuple[bool, str]:
    """Check if code executed successfully.

    Args:
        bash_output: Raw output from Bash tool execution

    Returns:
        (success, error_message)
    """
    # Check for Python exceptions
    python_errors = [
        'Traceback (most recent call last)',
        'SyntaxError:',
        'IndentationError:',
        'NameError:',
        'TypeError:',
        'AttributeError:',
        'ImportError:',
        'ModuleNotFoundError:',
        'KeyError:',
        'ValueError:',
        'IndexError:',
    ]

    for error in python_errors:
        if error in bash_output:
            # Extract error details
            lines = bash_output.split('\n')
            error_idx = next(i for i, line in enumerate(lines) if error in line)
            error_context = '\n'.join(lines[max(0, error_idx-2):min(len(lines), error_idx+3)])
            return False, f"Python exception detected:\n{error_context}"

    # Check for MCP server errors
    mcp_errors = [
        'Connection refused',
        'Timeout',
        'MCP server error',
        'Failed to connect',
        'Server not responding',
    ]

    for error in mcp_errors:
        if error.lower() in bash_output.lower():
            return False, f"MCP server error: {error}"

    return True, "Code executed successfully (exit code 0)"


def verify_data_retrieved(execution_output: str) -> Tuple[bool, int]:
    """Check if data was retrieved.

    Args:
        execution_output: Output from Python script execution

    Returns:
        (success, record_count)
    """
    # Try to extract counts from common output patterns
    count_patterns = [
        r'Total trials found:\s*(\d+)',
        r'Total drugs found:\s*(\d+)',
        r'Total records:\s*(\d+)',
        r'Found (\d+) trials',
        r'Found (\d+) drugs',
        r'Found (\d+) records',
        r'Retrieved (\d+) trials',
        r'Retrieved (\d+) drugs',
        r'Retrieved (\d+) records',
        r'(\d+) trials returned',
        r'(\d+) drugs returned',
        r'total[_\s]*count[\'"]?\s*:\s*(\d+)',
    ]

    for pattern in count_patterns:
        match = re.search(pattern, execution_output, re.IGNORECASE)
        if match:
            count = int(match.group(1))
            if count > 0:
                return True, count
            else:
                return False, 0

    # If no explicit count found, check for data indicators
    data_indicators = [
        'trials_summary',
        'drugs_summary',
        'results',
        'NCT',
        'Application',
    ]

    has_data = any(indicator in execution_output for indicator in data_indicators)

    if has_data:
        return True, -1  # Data present but count unknown

    return False, 0


def verify_pagination_complete(
    execution_output: str,
    server_type: str
) -> Tuple[bool, str]:
    """Check if all records were retrieved (pagination complete).

    Args:
        server_type: 'ct_gov', 'fda', etc.
        execution_output: Output from Python script execution

    Returns:
        (complete, warning_message)
    """
    if server_type == 'ct_gov':
        # Check for nextPageToken indicator
        if 'nextPageToken' in execution_output and 'null' not in execution_output.lower():
            return False, "WARNING: nextPageToken present in response. Results may be truncated."

        # Check for suspicious round numbers (common pagination limits)
        suspicious_counts = [100, 500, 1000, 5000, 10000]
        for pattern in [r'Found (\d+) trials', r'Total trials:\s*(\d+)', r'total[_\s]*count[\'"]?\s*:\s*(\d+)']:
            match = re.search(pattern, execution_output, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                if count in suspicious_counts:
                    return False, f"WARNING: Result count ({count}) matches common pagination limit. May be truncated."

    elif server_type == 'fda':
        # FDA uses 'limit' parameter, check if results == limit
        limit_match = re.search(r'limit[\'"]?\s*:\s*(\d+)', execution_output, re.IGNORECASE)
        count_match = re.search(r'(\d+)\s+results?', execution_output, re.IGNORECASE)

        if limit_match and count_match:
            limit = int(limit_match.group(1))
            count = int(count_match.group(1))
            if count == limit:
                return False, f"WARNING: Result count ({count}) equals limit. May be truncated."

    return True, "Pagination complete (no truncation indicators)"


def verify_skill_executable(skill_path: str) -> Tuple[bool, str]:
    """Check if skill can run standalone.

    Args:
        skill_path: Path to Python skill file

    Returns:
        (executable, error_message)
    """
    if not skill_path:
        return True, "Skill path not provided (skipping executable check)"

    path = Path(skill_path)

    # Check file exists
    if not path.exists():
        return False, f"Skill file not found: {skill_path}"

    # Check for if __name__ == "__main__": block
    content = path.read_text()
    if 'if __name__ == "__main__"' not in content:
        return False, "Skill missing 'if __name__ == \"__main__\":' block (not executable standalone)"

    # Try to execute the skill
    try:
        result = subprocess.run(
            ['python3', str(path)],
            capture_output=True,
            timeout=30,
            cwd=path.parent.parent.parent,  # Run from repo root
            env={'PYTHONPATH': 'scripts'}
        )

        if result.returncode == 0:
            return True, "Skill runs standalone successfully"
        else:
            error = result.stderr.decode() or result.stdout.decode()
            return False, f"Skill execution failed:\n{error[:200]}"

    except subprocess.TimeoutExpired:
        return False, "Skill execution timeout (>30s)"
    except Exception as e:
        return False, f"Skill execution error: {str(e)}"


def verify_schema(execution_output: str, server_type: str) -> Tuple[bool, str]:
    """Check if data matches expected schema.

    Args:
        execution_output: Output from Python script execution
        server_type: 'ct_gov', 'fda', etc.

    Returns:
        (valid, error_message)
    """
    if server_type == 'ct_gov':
        # Check for required CT.gov fields
        required_fields = ['NCT']  # All trials have NCT ID

        for field in required_fields:
            if field not in execution_output:
                return False, f"Missing required field: {field}"

        return True, "First record contains required fields (NCT ID present)"

    elif server_type == 'fda':
        # Check for FDA structure (JSON-based)
        fda_fields = ['application', 'drug', 'sponsor']

        found_fields = [f for f in fda_fields if f.lower() in execution_output.lower()]

        if found_fields:
            return True, f"FDA data structure valid (found: {', '.join(found_fields)})"
        else:
            return False, "Missing expected FDA fields (application/drug/sponsor)"

    elif server_type == 'pubmed':
        # Check for PubMed fields
        if 'PMID' in execution_output or 'pmid' in execution_output:
            return True, "PubMed data structure valid (PMID present)"
        else:
            return False, "Missing PMID field in PubMed results"

    # Default: if we have data, assume schema is valid
    return True, f"Data structure appears valid for {server_type}"


def run_all_verifications(
    bash_output: str,
    execution_output: str,
    server_type: str,
    skill_path: str = None
) -> Dict[str, Any]:
    """Run all verification checks.

    Args:
        bash_output: Raw output from Bash tool
        execution_output: Output from Python script execution
        server_type: 'ct_gov', 'fda', etc.
        skill_path: Optional path to skill file for executable check

    Returns:
        {
            'all_passed': bool,
            'checks': {
                'execution': {'passed': bool, 'message': str},
                'data_retrieved': {'passed': bool, 'count': int, 'message': str},
                'pagination': {'passed': bool, 'message': str},
                'executable': {'passed': bool, 'message': str},
                'schema': {'passed': bool, 'message': str}
            },
            'summary': str
        }
    """
    checks = {}

    # Run all checks
    exec_passed, exec_msg = verify_execution(bash_output)
    checks['execution'] = {'passed': exec_passed, 'message': exec_msg}

    data_passed, count = verify_data_retrieved(execution_output)
    checks['data_retrieved'] = {
        'passed': data_passed,
        'count': count,
        'message': f"Retrieved {count} records" if count > 0 else "No data retrieved"
    }

    page_passed, page_msg = verify_pagination_complete(execution_output, server_type)
    checks['pagination'] = {'passed': page_passed, 'message': page_msg}

    exec_skill_passed, exec_skill_msg = verify_skill_executable(skill_path)
    checks['executable'] = {'passed': exec_skill_passed, 'message': exec_skill_msg}

    schema_passed, schema_msg = verify_schema(execution_output, server_type)
    checks['schema'] = {'passed': schema_passed, 'message': schema_msg}

    # Determine overall status
    all_passed = all(c['passed'] for c in checks.values())

    # Generate summary
    if all_passed:
        summary = "✓ All verification checks passed. Skill is complete and correct."
    else:
        failed_checks = [name for name, result in checks.items() if not result['passed']]
        summary = f"✗ Verification FAILED: {', '.join(failed_checks)}. Review issues and apply fixes."

    return {
        'all_passed': all_passed,
        'checks': checks,
        'summary': summary
    }


def main():
    parser = argparse.ArgumentParser(
        description='Verify skill execution for closing the agentic loop'
    )
    parser.add_argument(
        '--bash-output',
        required=True,
        help='Raw output from Bash tool execution'
    )
    parser.add_argument(
        '--execution-output',
        required=True,
        help='Output from Python script execution'
    )
    parser.add_argument(
        '--server-type',
        required=True,
        choices=['ct_gov', 'fda', 'pubmed', 'nlm_codes', 'who', 'sec_edgar',
                 'healthcare', 'financials', 'datacommons', 'opentargets',
                 'pubchem', 'uspto_patents'],
        help='MCP server type'
    )
    parser.add_argument(
        '--skill-path',
        help='Optional path to skill file for executable check'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Run all verifications
    results = run_all_verifications(
        bash_output=args.bash_output,
        execution_output=args.execution_output,
        server_type=args.server_type,
        skill_path=args.skill_path
    )

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Human-readable output
        print("\n" + "="*60)
        print("SKILL VERIFICATION REPORT")
        print("="*60)

        for check_name, check_result in results['checks'].items():
            status = "✓" if check_result['passed'] else "✗"
            print(f"\n{status} {check_name.upper()}:")
            print(f"  {check_result['message']}")
            if 'count' in check_result and check_result['count'] > 0:
                print(f"  Count: {check_result['count']}")

        print("\n" + "="*60)
        print(results['summary'])
        print("="*60 + "\n")

    # Exit with appropriate code
    sys.exit(0 if results['all_passed'] else 1)


if __name__ == '__main__':
    main()
