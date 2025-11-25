import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import device_510k, device_pma, device_registration
from datetime import datetime

def get_company_fda_device_approvals(
    company_name,
    start_year=2020,
    end_year=None,
    device_types=None
):
    """Get FDA device approvals for a medical device company.

    Args:
        company_name (str): Company name (e.g., "Boston Scientific", "Medtronic")
        start_year (int): Start year for filtering (default: 2020)
        end_year (int): End year for filtering (default: current year)
        device_types (list): Device types to search - "pma", "510k", "registration"
                            Default: all types

    Returns:
        dict: Contains company, time_period, total_approvals, approvals_by_type,
              approvals list, and summary
    """
    if end_year is None:
        end_year = datetime.now().year

    if device_types is None:
        device_types = ["pma", "510k", "registration"]

    all_approvals = []
    seen_identifiers = set()  # For deduplication

    print(f"Searching FDA device approvals for {company_name} ({start_year}-{end_year})...")

    # Search 510(k) clearances
    if "510k" in device_types:
        print("  Searching 510(k) clearances...")
        try:
            result_510k = device_510k(search=company_name, limit=100)

            if result_510k and isinstance(result_510k, dict):
                results = result_510k.get('results', [])
                print(f"  Found {len(results)} 510(k) records")

                for device in results:
                    # Extract and parse date
                    date_received = device.get('date_received', '')
                    if date_received:
                        try:
                            year = int(date_received[:4])
                            if start_year <= year <= end_year:
                                k_number = device.get('k_number', '')

                                # Deduplicate by k_number
                                if k_number and k_number not in seen_identifiers:
                                    seen_identifiers.add(k_number)

                                    all_approvals.append({
                                        'device_name': device.get('device_name', 'N/A'),
                                        'approval_type': '510k',
                                        'approval_date': date_received,
                                        'product_code': device.get('product_code', 'N/A'),
                                        'device_class': device.get('device_class', 'N/A'),
                                        'medical_specialty': device.get('medical_specialty_description', 'N/A'),
                                        'k_number': k_number,
                                        'pma_number': None,
                                        'applicant': device.get('applicant', 'N/A')
                                    })
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            print(f"  Warning: 510(k) search failed - {e}")

    # Search PMA approvals
    if "pma" in device_types:
        print("  Searching PMA approvals...")
        try:
            result_pma = device_pma(search=company_name, limit=100)

            if result_pma and isinstance(result_pma, dict):
                results = result_pma.get('results', [])
                print(f"  Found {len(results)} PMA records")

                for device in results:
                    # Extract and parse date
                    date_received = device.get('date_received', '')
                    if date_received:
                        try:
                            year = int(date_received[:4])
                            if start_year <= year <= end_year:
                                pma_number = device.get('pma_number', '')

                                # Deduplicate by pma_number
                                if pma_number and pma_number not in seen_identifiers:
                                    seen_identifiers.add(pma_number)

                                    all_approvals.append({
                                        'device_name': device.get('generic_name', 'N/A'),
                                        'approval_type': 'PMA',
                                        'approval_date': date_received,
                                        'product_code': device.get('product_code', 'N/A'),
                                        'device_class': 'III',  # PMA devices are Class III
                                        'medical_specialty': device.get('medical_specialty_description', 'N/A'),
                                        'k_number': None,
                                        'pma_number': pma_number,
                                        'applicant': device.get('applicant_name', 'N/A')
                                    })
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            print(f"  Warning: PMA search failed - {e}")

    # Search device registrations
    if "registration" in device_types:
        print("  Searching device registrations...")
        try:
            result_reg = device_registration(search=company_name, limit=100)

            if result_reg and isinstance(result_reg, dict):
                results = result_reg.get('results', [])
                print(f"  Found {len(results)} registration records")

                for device in results:
                    # Note: Registration listings may not have approval dates
                    # We'll use registration_number for deduplication
                    reg_number = device.get('registration_number', '')

                    if reg_number and reg_number not in seen_identifiers:
                        seen_identifiers.add(reg_number)

                        all_approvals.append({
                            'device_name': device.get('proprietary_name', 'N/A'),
                            'approval_type': 'registration',
                            'approval_date': device.get('registration_date', 'N/A'),
                            'product_code': device.get('product_code', 'N/A'),
                            'device_class': device.get('device_class', 'N/A'),
                            'medical_specialty': 'N/A',
                            'k_number': None,
                            'pma_number': None,
                            'applicant': device.get('owner_operator_name', 'N/A')
                        })
        except Exception as e:
            print(f"  Warning: Registration search failed - {e}")

    # Sort by approval date (newest first)
    all_approvals.sort(key=lambda x: x['approval_date'], reverse=True)

    # Calculate statistics
    approvals_by_type = {
        'PMA': sum(1 for a in all_approvals if a['approval_type'] == 'PMA'),
        '510k': sum(1 for a in all_approvals if a['approval_type'] == '510k'),
        'registration': sum(1 for a in all_approvals if a['approval_type'] == 'registration')
    }

    # Generate summary
    summary_parts = [
        f"{company_name} FDA Device Approvals ({start_year}-{end_year})",
        f"Total: {len(all_approvals)} approvals"
    ]

    if approvals_by_type['PMA'] > 0:
        summary_parts.append(f"  - PMA: {approvals_by_type['PMA']}")
    if approvals_by_type['510k'] > 0:
        summary_parts.append(f"  - 510(k): {approvals_by_type['510k']}")
    if approvals_by_type['registration'] > 0:
        summary_parts.append(f"  - Registrations: {approvals_by_type['registration']}")

    # Add device class breakdown
    class_counts = {}
    for approval in all_approvals:
        device_class = approval['device_class']
        class_counts[device_class] = class_counts.get(device_class, 0) + 1

    if class_counts:
        summary_parts.append("\nBy Device Class:")
        for device_class, count in sorted(class_counts.items()):
            summary_parts.append(f"  - Class {device_class}: {count}")

    summary = "\n".join(summary_parts)

    return {
        'company': company_name,
        'time_period': f"{start_year}-{end_year}",
        'total_approvals': len(all_approvals),
        'approvals_by_type': approvals_by_type,
        'approvals': all_approvals,
        'summary': summary
    }

if __name__ == "__main__":
    # Example usage
    import sys

    company = sys.argv[1] if len(sys.argv) > 1 else "Medtronic"
    start_year = int(sys.argv[2]) if len(sys.argv) > 2 else 2020
    end_year = int(sys.argv[3]) if len(sys.argv) > 3 else None

    result = get_company_fda_device_approvals(
        company_name=company,
        start_year=start_year,
        end_year=end_year
    )

    print("\n" + "="*80)
    print(result['summary'])
    print("="*80)

    # Show top 10 recent approvals
    print("\nTop 10 Recent Approvals:")
    for i, approval in enumerate(result['approvals'][:10], 1):
        print(f"\n{i}. {approval['device_name']}")
        print(f"   Type: {approval['approval_type']} | Date: {approval['approval_date']}")
        print(f"   Class: {approval['device_class']} | Code: {approval['product_code']}")
        if approval['k_number']:
            print(f"   K-Number: {approval['k_number']}")
        if approval['pma_number']:
            print(f"   PMA Number: {approval['pma_number']}")
