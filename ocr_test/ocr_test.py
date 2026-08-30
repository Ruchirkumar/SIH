import easyocr

# Create the reader (English only for now). This downloads model 
# weights on first run - may take a minute or two.
reader = easyocr.Reader(['en'])

# Run OCR on the test image
results = reader.readtext('ocr_test/test_label.jpeg')

# results is a list of (bounding_box, text, confidence) tuples
print(f"\n{'='*50}")
print(f"Found {len(results)} text regions\n")

for i, (bbox, text, confidence) in enumerate(results):
    print(f"[{i}] Text: '{text}'")
    print(f"    Confidence: {confidence:.2f}")
    print(f"    Bounding box: {bbox}")
    print()