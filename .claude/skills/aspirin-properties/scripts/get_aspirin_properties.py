import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubchem_mcp import get_compound_by_name

def get_aspirin_properties():
    """Get chemical properties for aspirin from PubChem.

    Returns:
        dict: Contains compound properties and summary
    """
    # Query PubChem for aspirin
    result = get_compound_by_name(name="aspirin")

    if not result or 'error' in result:
        return {
            'success': False,
            'error': result.get('error', 'Unknown error'),
            'summary': 'Failed to retrieve aspirin properties'
        }

    # Extract key properties
    properties = {
        'name': result.get('IUPACName', 'N/A'),
        'molecular_formula': result.get('MolecularFormula', 'N/A'),
        'molecular_weight': result.get('MolecularWeight', 'N/A'),
        'canonical_smiles': result.get('CanonicalSMILES', 'N/A'),
        'isomeric_smiles': result.get('IsomericSMILES', 'N/A'),
        'inchi': result.get('InChI', 'N/A'),
        'inchi_key': result.get('InChIKey', 'N/A'),
        'cid': result.get('CID', 'N/A')
    }

    # Build summary
    summary = f"""
Aspirin Chemical Properties:
═══════════════════════════════════════

Basic Information:
  • PubChem CID: {properties['cid']}
  • IUPAC Name: {properties['name']}
  • Molecular Formula: {properties['molecular_formula']}
  • Molecular Weight: {properties['molecular_weight']} g/mol

Structure Identifiers:
  • Canonical SMILES: {properties['canonical_smiles']}
  • Isomeric SMILES: {properties['isomeric_smiles']}
  • InChI Key: {properties['inchi_key']}

Full InChI:
  {properties['inchi']}
"""

    return {
        'success': True,
        'properties': properties,
        'raw_data': result,
        'summary': summary.strip()
    }

if __name__ == "__main__":
    result = get_aspirin_properties()
    if result['success']:
        print(result['summary'])
    else:
        print(f"Error: {result['error']}")
