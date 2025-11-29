#!/usr/bin/env python3
"""
Step 2: Filter Academic Institutions

Removes universities, hospitals, government organizations, and individual PIs
from sponsor list to focus on investable companies.
"""

import sys
import re
from typing import List, Dict

sys.path.insert(0, ".claude")


# Academic institution keywords (comprehensive list)
ACADEMIC_KEYWORDS = [
    # Universities
    'university', 'universit', 'universi',
    'college', 'school of medicine', 'school of pharmacy',

    # Hospitals & Medical Centers
    'hospital', 'medical center', 'medical centre', 'health center',
    'health centre', 'clinic', 'clinique', 'klinik',
    'cancer center', 'cancer centre',  # Research cancer centers
    'sloan kettering', 'md anderson', 'm.d. anderson',  # Specific major centers
    'general hospital',  # MGH, etc.

    # Research Institutes
    'institute', 'institut', 'centro', 'centre',

    # Government & Public Health
    'va ', 'veterans administration', 'veterans affairs',
    'nhs ', 'national health service',
    'ministry of health', 'department of health',
    'public health', 'government',
    'national cancer institute', 'nci',

    # Academic Organizations
    'academic', 'academisch', 'academy',
    'research foundation', 'research group',
    'cooperative group', 'children\'s oncology group',

    # Country-specific
    'inserm', 'cnrs',  # French research
    'chu ', 'chru ',  # French university hospitals
    'azienda ospedaliera', 'a.o.u.',  # Italian hospitals
    'karolinska',  # Swedish research
]

# Additional patterns for individual researchers
INDIVIDUAL_PATTERNS = [
    r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # FirstName LastName
    r'^Dr\.\s+',  # Dr. Name
    r'^Prof\.\s+',  # Prof. Name
    r'MD$', r'PhD$', r'MD,', r'PhD,',  # Academic titles
]


def is_academic_institution(sponsor_name: str) -> bool:
    """Check if sponsor is an academic institution or individual researcher.

    Args:
        sponsor_name: Sponsor name from ClinicalTrials.gov

    Returns:
        bool: True if academic/non-commercial, False if likely a company
    """
    sponsor_lower = sponsor_name.lower()

    # Check academic keywords
    for keyword in ACADEMIC_KEYWORDS:
        if keyword in sponsor_lower:
            return True

    # Check individual researcher patterns
    for pattern in INDIVIDUAL_PATTERNS:
        if re.search(pattern, sponsor_name):
            return True

    return False


def is_likely_company(sponsor_name: str) -> bool:
    """Check if sponsor has company indicators.

    Args:
        sponsor_name: Sponsor name from ClinicalTrials.gov

    Returns:
        bool: True if likely a company, False otherwise
    """
    # Company suffixes
    company_indicators = [
        'inc.', 'inc', 'llc', 'ltd.', 'ltd', 'limited',
        'corporation', 'corp.', 'corp',
        'gmbh', 's.a.', 'sa', 'plc', 'pty',
        'pharmaceuticals', 'pharma', 'therapeutics',
        'biosciences', 'biotechnology', 'biotech',
        'ag ', ' ag', 'se ', ' se',  # European company types
    ]

    sponsor_lower = sponsor_name.lower()

    for indicator in company_indicators:
        if indicator in sponsor_lower:
            return True

    return False


def filter_academic_institutions(sponsors: List[str]) -> Dict[str, any]:
    """Filter sponsor list to remove academic institutions.

    Args:
        sponsors: List of sponsor names from ClinicalTrials.gov

    Returns:
        dict: {
            'total_input': 1049,
            'companies_found': 312,
            'academic_filtered': 737,
            'companies': ['AbbVie Inc.', 'Amgen Inc.', ...],
            'academic_examples': ['Harvard University', 'Mayo Clinic', ...]
        }
    """
    companies = []
    academic = []

    for sponsor in sponsors:
        # First check if it's clearly a company
        if is_likely_company(sponsor):
            companies.append(sponsor)
        # Then check if it's academic
        elif is_academic_institution(sponsor):
            academic.append(sponsor)
        else:
            # Ambiguous - err on side of inclusion
            # Will be filtered later by SEC EDGAR validation
            companies.append(sponsor)

    return {
        'total_input': len(sponsors),
        'companies_found': len(companies),
        'academic_filtered': len(academic),
        'companies': sorted(companies),
        'academic_examples': sorted(academic)[:20]  # First 20 for review
    }


# Make script executable
if __name__ == "__main__":
    # Test with sample data
    test_sponsors = [
        "AbbVie Inc.",
        "Harvard University",
        "Mayo Clinic",
        "Amgen Inc",
        "M.D. Anderson Cancer Center",
        "Pfizer",
        "Johns Hopkins University",
        "Memorial Sloan Kettering Cancer Center",
        "Merck Sharp & Dohme LLC",
        "University of Texas",
        "Bristol-Myers Squibb",
        "National Cancer Institute (NCI)",
        "Genentech, Inc.",
        "Massachusetts General Hospital",
        "Eli Lilly and Company",
        "Arcellx, Inc.",
        "Disc Medicine, Inc.",
        "THERABIONIC GmbH",
        "A.O.U. Città della Salute e della Scienza",
        "ADC Therapeutics S.A."
    ]

    print("="*60)
    print("Testing Academic Institution Filter")
    print("="*60)
    print(f"\nInput: {len(test_sponsors)} sponsors\n")

    result = filter_academic_institutions(test_sponsors)

    print(f"\nResults:")
    print(f"  Total input: {result['total_input']}")
    print(f"  Companies found: {result['companies_found']}")
    print(f"  Academic filtered: {result['academic_filtered']}")
    print(f"  Accuracy: {result['companies_found'] / result['total_input'] * 100:.1f}% identified as companies")

    print(f"\n\nCompanies ({len(result['companies'])}):")
    for i, company in enumerate(result['companies'], 1):
        print(f"  {i}. {company}")

    print(f"\n\nAcademic Institutions Filtered ({len(result['academic_examples'])}):")
    for i, academic in enumerate(result['academic_examples'], 1):
        print(f"  {i}. {academic}")

    print("\n" + "="*60)
    print("✓ Filter test complete")
    print("="*60)
