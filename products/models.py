from django.db import models
from django.conf import settings

class Product(models.Model):
    """
    Represents a product to be compliance-scanned.
    """
    name = models.CharField(max_length=255)
    manufacturer_name = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True, help_text="e.g. food, cosmetics, electronics")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ComplianceScan(models.Model):
    """
    Represents a single compliance scan instance for a product.
    Allows for scan history over time.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLIANT = 'COMPLIANT', 'Compliant'
        NON_COMPLIANT = 'NON_COMPLIANT', 'Non-Compliant'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='scans'
    )
    image = models.ImageField(upload_to='scans/%Y/%m/%d/')
    extracted_text = models.TextField(blank=True, help_text="Raw OCR output")
    extracted_fields = models.JSONField(
        blank=True,
        null=True,
        help_text="Structured fields like MRP, net_quantity, mfg_date"
    )
    compliance_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    violations = models.JSONField(
        blank=True,
        null=True,
        help_text="List of rule violations found"
    )
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='scans_performed'
    )
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan {self.id} for {self.product.name} - {self.get_compliance_status_display()}"
