"""
⚠️ DEPRECATED WRAPPER (2025-11-28)

This skill has been superseded by the generic 'safety-stopped-trials' skill.
This file now serves as a thin compatibility wrapper.

Recommendation: Migrate to the generic skill:
  from skills.safety_stopped_trials.scripts.get_safety_stopped_trials import get_safety_stopped_trials
  result = get_safety_stopped_trials("diabetes", condition_subtypes={...})
"""

import sys
import warnings
import os

# Add .claude directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, ".claude")

# Import the generic skill (direct import from file path)
# Note: This import works because we added .claude/skills/ parent to path
import importlib.util
spec = importlib.util.spec_from_file_location(
    "get_safety_stopped_trials",
    os.path.join(os.path.dirname(__file__), "../../safety-stopped-trials/scripts/get_safety_stopped_trials.py")
)
safety_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety_module)
get_safety_stopped_trials = safety_module.get_safety_stopped_trials


def get_diabetes_drugs_stopped_safety():
    """Get diabetes clinical trials stopped due to safety concerns.

    ⚠️ DEPRECATED: This function wraps the generic safety-stopped-trials skill.
    Please use get_safety_stopped_trials("diabetes") directly in new code.

    Returns:
        dict: Contains total_count, trials, categorizations, notable_drugs, summary
    """

    # Emit deprecation warning
    warnings.warn(
        "get_diabetes_drugs_stopped_safety() is deprecated. "
        "Use get_safety_stopped_trials('diabetes', condition_subtypes={...}) instead.",
        DeprecationWarning,
        stacklevel=2
    )

    # Diabetes-specific condition subtypes (preserves legacy behavior)
    condition_subtypes = {
        'Type 1 Diabetes': ['type 1', 'type i', 't1d'],
        'Type 2 Diabetes': ['type 2', 'type ii', 't2d'],
        'Gestational Diabetes': ['gestational', 'gdm']
    }

    # Call the generic skill with diabetes parameters
    return get_safety_stopped_trials(
        indication="diabetes",
        condition_subtypes=condition_subtypes
    )


if __name__ == "__main__":
    # Print deprecation notice
    print("=" * 80)
    print("⚠️  DEPRECATION NOTICE")
    print("=" * 80)
    print()
    print("This skill (diabetes-drugs-stopped-safety) is deprecated as of 2025-11-28.")
    print()
    print("Replacement: safety-stopped-trials (generic, works for any indication)")
    print()
    print("Migration:")
    print("  Old: python get_diabetes_drugs_stopped_safety.py")
    print('  New: python get_safety_stopped_trials.py "diabetes"')
    print()
    print("This wrapper maintains backward compatibility by calling the generic skill.")
    print("=" * 80)
    print()

    # Execute the wrapped function
    result = get_diabetes_drugs_stopped_safety()
    print("\n" + result['summary'])
