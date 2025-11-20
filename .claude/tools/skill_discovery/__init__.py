"""
Skill Discovery Module for Index-Based Verification

This module provides intelligent skill discovery and verification using the skills
index as the source of truth. It implements a four-level verification system:

Level 1: Index-Based Discovery (Fast)
    - Query index for skill metadata
    - Filter by server, category, pattern

Level 2: Skill Health Check (Medium)
    - Verify files exist and are executable
    - Syntax validation
    - Structure validation

Level 3: Semantic Matching (Smart)
    - Find skills that match intent, not just exact names
    - Score-based matching algorithm

Level 4: Strategy Decision Tree
    - Decide whether to REUSE, ADAPT, or CREATE skill
    - Provide actionable execution plan

Reference:
    - Implementation Plan: .claude/.context/implementation-plans/index-based-skill-discovery.md
    - Skills Index: .claude/skills/index.json
"""

__version__ = "1.0.0"
__all__ = [
    "find_skill_in_index",
    "query_skills_by_criteria",
    "verify_skill_health",
    "batch_health_check",
    "find_matching_skill",
    "determine_skill_strategy",
    "add_skill_to_index",
    "update_skill_health",
    "validate_and_sync_index",
]
