import re
import easyocr

# Reader is expensive to initialize (loads model weights), so create it once
# at module load time, not per-call. This gets reused across scans.
_reader = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader


CONFIDENCE_THRESHOLD = 0.40


def run_ocr(image_path):
    """
    Runs EasyOCR on the given image path.
    Returns a list of (text, confidence) tuples, sorted top-to-bottom
    by their vertical position (helps keep related fragments near each other).
    """
    reader = get_reader()
    raw_results = reader.readtext(image_path)

    # raw_results is [(bbox, text, confidence), ...]
    # sort by the y-coordinate of the top-left corner of each box
    raw_results.sort(key=lambda r: r[0][0][1])

    return [(text, float(conf)) for (_, text, conf) in raw_results]


def clean_fragments(results, threshold=CONFIDENCE_THRESHOLD):
    return [(text, conf) for text, conf in results if conf >= threshold]


def extract_mrp(fragments):
    pattern = re.compile(r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b')
    for text, conf in fragments:
        match = pattern.search(text)
        if match:
            return {"value": match.group(), "confidence": conf, "source_text": text}
    return None


def extract_dates(fragments):
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
    pattern = re.compile(r'\b(lic|licence|license)\b[^\d]{0,15}([A-Z0-9/\-]{5,})', re.IGNORECASE)
    for text, conf in fragments:
        match = pattern.search(text)
        if match:
            return {"value": match.group(2), "confidence": conf, "source_text": text}
    return None


def extract_manufacturer_block(fragments):
    block = []
    capturing = False
    for text, conf in fragments:
        if "manufactur" in text.lower():
            capturing = True
        if capturing:
            block.append(text)
        if capturing and re.search(r'\b\d{6}\b', text):
            break
    return " ".join(block) if block else None


def extract_fields(image_path):
    """
    Main entry point: runs OCR on an image and returns a dict of
    structured fields plus the raw extracted text, ready to save
    onto a ComplianceScan instance.
    """
    raw_results = run_ocr(image_path)
    clean = clean_fragments(raw_results)

    fields = {
        "mrp": extract_mrp(clean),
        "dates": extract_dates(clean),
        "license_no": extract_license_no(clean),
        "manufacturer": extract_manufacturer_block(clean),
    }

    raw_text = "\n".join(text for text, conf in raw_results)

    return raw_text, fields