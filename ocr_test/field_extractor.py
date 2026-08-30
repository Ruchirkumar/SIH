import re

# --- Step 1: Paste your real OCR results here as (text, confidence) tuples ---
# In the real pipeline this will come directly from easyocr's reader.readtext() output.
# For now we hardcode your actual test run so we can build and test extraction logic
# without re-running OCR every time.

ocr_results = [
    ("Composition:", 1.00),
    ("Sodium Carboxymethyl", 0.87),
    ("MRP ?", 0.93),
    ("(Incl  of all laxes)", 0.56),
    ("cellulose IP", 1.00),
    ("0.5% wlv", 0.72),
    ("Stabilized Oxychloro", 1.00),
    ("Complex", 1.00),
    ("0.005% wlv", 1.00),
    ("(As preservative)", 0.98),
    ("Sterile aqueous vehicle", 1.00),
    ("Application:", 1.00),
    ("As directed by the Physician:", 0.89),
    ("137.00", 0.92),
    ("Storage:", 1.00),
    ("Store below 308C. Protect from", 0.93),
    ("B,No.: AHKO2FZA", 0.32),
    ("light & moisture: Do not freeze:", 0.70),
    ("WARNING", 1.00),
    ("Mfg: Date =", 0.96),
    ("04/2025", 0.96),
    ("Expiry Date: 03/2027", 0.95),
    ("Mfg: Lic: No:: 51/UAISCIP-2013", 0.47),
    ("Manufactured by : Pure & Cure Heallhcare", 0.81),
    ("Pvt: Ltd: (A subsidiary of Akums Drugs &", 0.65),
    ("Pharmaceuticals Ltd ) Plot No. 264,27-30,", 0.65),
    ("Seclor-8A, II.E , SIDCUL, Ranipur;", 0.42),
    ("Haridwar-249 403, Uttarakhand", 0.96),
]

CONFIDENCE_THRESHOLD = 0.40


def clean_fragments(results):
    """Drop low-confidence junk before we even try to parse it."""
    return [(text, conf) for text, conf in results if conf >= CONFIDENCE_THRESHOLD]


def extract_mrp(fragments):
    """
    Look for a price pattern: digits, optional comma, decimal point, 2 digits.
    e.g. '137.00', '1,299.50'
    We don't rely on it being next to the word 'MRP' - we search all fragments.
    """
    pattern = re.compile(r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b')
    for text, conf in fragments:
        match = pattern.search(text)
        if match:
            return {"value": match.group(), "confidence": conf, "source_text": text}
    return None


def extract_dates(fragments):
    """
    Look for MM/YYYY style dates (common for mfg/expiry on packaging).
    If the date's own fragment has no keyword, check the PREVIOUS fragment too -
    OCR often splits "Mfg: Date =" and "04/2025" into separate boxes.
    """
    date_pattern = re.compile(r'\b(0[1-9]|1[0-2])/(\d{4})\b')
    found = []
    for i, (text, conf) in enumerate(fragments):
        match = date_pattern.search(text)
        if match:
            label = "unknown"
            lower = text.lower()
            if "mfg" in lower or "manufactur" in lower:
                label = "mfg_date"
            elif "exp" in lower:
                label = "expiry_date"
            else:
                # look back one fragment for a keyword since OCR often splits
                # "Mfg: Date =" and "04/2025" into separate boxes
                if i > 0:
                    prev_text = fragments[i - 1][0].lower()
                    if "mfg" in prev_text or "manufactur" in prev_text:
                        label = "mfg_date"
                    elif "exp" in prev_text:
                        label = "expiry_date"
            found.append({
                "value": match.group(),
                "label": label,
                "confidence": conf,
                "source_text": text
            })
    return found


def extract_license_no(fragments):
    """
    License numbers are alphanumeric with slashes/hyphens, following 'Lic' or 'License'.
    Word boundaries (\\b) are critical here - without them, 'lic' matches inside
    unrelated words like 'Application' (App-LIC-ation).
    """
    pattern = re.compile(r'\b(lic|licence|license)\b[^\d]{0,15}([A-Z0-9/\-]{5,})', re.IGNORECASE)
    for text, conf in fragments:
        match = pattern.search(text)
        if match:
            return {"value": match.group(2), "confidence": conf, "source_text": text}
    return None


def extract_manufacturer_block(fragments):
    """
    Manufacturer info is usually multiple consecutive fragments starting with
    'Manufactured by' - we grab that line plus the next few as one block.
    """
    block = []
    capturing = False
    for text, conf in fragments:
        if "manufactur" in text.lower():
            capturing = True
        if capturing:
            block.append(text)
        # crude stop condition: pincode-like pattern signals end of address
        if capturing and re.search(r'\b\d{6}\b', text):
            break
    return " ".join(block) if block else None


if __name__ == "__main__":
    clean = clean_fragments(ocr_results)

    print(f"Kept {len(clean)} of {len(ocr_results)} fragments after confidence filtering\n")

    mrp = extract_mrp(clean)
    dates = extract_dates(clean)
    license_no = extract_license_no(clean)
    manufacturer = extract_manufacturer_block(clean)

    print("=== EXTRACTED FIELDS ===")
    print(f"MRP: {mrp}")
    print(f"Dates found: {dates}")
    print(f"License No: {license_no}")
    print(f"Manufacturer block: {manufacturer}")