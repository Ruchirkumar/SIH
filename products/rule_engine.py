from datetime import datetime


def parse_date(date_str):
    """Parses an MM/YYYY string into a datetime. Returns None on bad format."""
    try:
        return datetime.strptime(date_str, "%m/%Y")
    except (ValueError, TypeError):
        return None


def check_mrp_present(extracted_fields):
    if not extracted_fields.get("mrp"):
        return "MRP declaration is missing [Rule 6(1)(e), LM(PC) Rules 2011]"
    return None


def check_mfg_date_present(extracted_fields):
    dates = extracted_fields.get("dates", [])
    if not any(d.get("label") == "mfg_date" for d in dates):
        return "Month and year of manufacture is missing [Rule 6(1)(d), LM(PC) Rules 2011]"
    return None


def check_expiry_date_present(extracted_fields):
    dates = extracted_fields.get("dates", [])
    if not any(d.get("label") == "expiry_date" for d in dates):
        return ("Expiry date is missing (not explicitly mandated by Rule 6 for all "
                "commodities, but required under sector-specific rules e.g. Drugs Rules "
                "for pharmaceuticals)")
    return None


def check_expiry_after_mfg(extracted_fields):
    dates = extracted_fields.get("dates", [])
    mfg_entry = next((d for d in dates if d.get("label") == "mfg_date"), None)
    exp_entry = next((d for d in dates if d.get("label") == "expiry_date"), None)

    if mfg_entry and exp_entry:
        mfg_dt = parse_date(mfg_entry.get("value"))
        exp_dt = parse_date(exp_entry.get("value"))
        if mfg_dt and exp_dt:
            if exp_dt <= mfg_dt:
                return (
                    f"Expiry date ({exp_entry.get('value')}) must be after "
                    f"manufacturing date ({mfg_entry.get('value')})"
                )
        else:
            return "Manufacturing or expiry date has an invalid format (expected MM/YYYY)"
    return None


def check_license_present(extracted_fields):
    if not extracted_fields.get("license_no"):
        # Note: manufacturing license numbers (e.g. FSSAI, Drug License) are required
        # under sector-specific laws (FSS Act 2006, Drugs & Cosmetics Rules 1945),
        # not directly by LM(PC) Rules 2011 itself - flagged here as good practice.
        return "Manufacturing/product license number is missing or not detected"
    return None


def check_manufacturer_present(extracted_fields):
    if not extracted_fields.get("manufacturer"):
        return ("Name and complete address of manufacturer/packer/importer is missing "
                "[Rule 6(1)(a), LM(PC) Rules 2011]")
    return None


def run_compliance_checks(extracted_fields):
    """
    Runs all compliance rules against the extracted fields.
    Returns a tuple: (status, violations)
      status: "COMPLIANT" or "NON_COMPLIANT"
      violations: list of human-readable violation strings
    """
    if not extracted_fields:
        return "NON_COMPLIANT", ["No extracted fields available for compliance check"]

    rules = [
        check_mrp_present,
        check_mfg_date_present,
        check_expiry_date_present,
        check_expiry_after_mfg,
        check_license_present,
        check_manufacturer_present,
    ]

    violations = []
    for rule in rules:
        result = rule(extracted_fields)
        if result:
            violations.append(result)

    status = "COMPLIANT" if not violations else "NON_COMPLIANT"
    return status, violations