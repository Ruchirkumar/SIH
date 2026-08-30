from django.core.management.base import BaseCommand, CommandError
from products.models import ComplianceScan
from products.ocr_utils import run_ocr, clean_fragments


class Command(BaseCommand):
    help = "Print raw OCR fragments for a scan, for debugging extraction issues"

    def add_arguments(self, parser):
        parser.add_argument('scan_id', type=int)

    def handle(self, *args, **options):
        scan = ComplianceScan.objects.get(id=options['scan_id'])
        raw = run_ocr(scan.image.path)
        clean = clean_fragments(raw)

        self.stdout.write(f"\nTotal fragments: {len(raw)}, kept after confidence filter: {len(clean)}\n")
        for text, conf in clean:
            self.stdout.write(f"  '{text}'  (confidence: {conf:.2f})")