from django.core.management.base import BaseCommand, CommandError
from products.models import ComplianceScan
from products.ocr_utils import extract_fields


class Command(BaseCommand):
    help = "Run OCR + field extraction on a ComplianceScan by its ID"

    def add_arguments(self, parser):
        parser.add_argument('scan_id', type=int, help="ID of the ComplianceScan to process")

    def handle(self, *args, **options):
        scan_id = options['scan_id']

        try:
            scan = ComplianceScan.objects.get(id=scan_id)
        except ComplianceScan.DoesNotExist:
            raise CommandError(f"No ComplianceScan found with id {scan_id}")

        self.stdout.write(f"Running OCR on scan #{scan.id} (product: {scan.product.name})...")

        image_path = scan.image.path

        try:
            raw_text, fields = extract_fields(image_path)
        except Exception as e:
            raise CommandError(f"OCR failed: {e}")

        scan.extracted_text = raw_text
        scan.extracted_fields = fields
        scan.save()

        self.stdout.write(self.style.SUCCESS(f"Done. Extracted fields:"))
        self.stdout.write(str(fields))