from django.core.management.base import BaseCommand, CommandError
from products.models import ComplianceScan
from products.rule_engine import run_compliance_checks


class Command(BaseCommand):
    help = "Run compliance rule checks on a ComplianceScan by its ID"

    def add_arguments(self, parser):
        parser.add_argument('scan_id', type=int, help="ID of the ComplianceScan to check")

    def handle(self, *args, **options):
        scan_id = options['scan_id']

        try:
            scan = ComplianceScan.objects.get(id=scan_id)
        except ComplianceScan.DoesNotExist:
            raise CommandError(f"No ComplianceScan found with id {scan_id}")

        extracted_fields = scan.extracted_fields
        if not extracted_fields:
            raise CommandError(
                f"ComplianceScan #{scan_id} has no extracted fields. "
                "Please run 'python manage.py run_ocr {}' first.".format(scan_id)
            )

        self.stdout.write(f"Running compliance checks for Scan #{scan.id} "
                           f"(product: {scan.product.name})...")

        status, violations = run_compliance_checks(extracted_fields)

        scan.compliance_status = status
        scan.violations = violations
        scan.save()

        if status == "COMPLIANT":
            self.stdout.write(self.style.SUCCESS(f"Result: {status} - All rules passed!"))
        else:
            self.stdout.write(self.style.ERROR(f"Result: {status}"))
            self.stdout.write("\nViolations found:")
            for i, v in enumerate(violations, 1):
                self.stdout.write(f"  {i}. {v}")