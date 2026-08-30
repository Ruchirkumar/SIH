from django.contrib import admin
from .models import Product, ComplianceScan

class ComplianceScanInline(admin.TabularInline):
    model = ComplianceScan
    extra = 0
    fields = ('image', 'compliance_status', 'scanned_at')
    readonly_fields = ('scanned_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer_name', 'category', 'created_at')
    search_fields = ('name', 'manufacturer_name')
    inlines = [ComplianceScanInline]

@admin.register(ComplianceScan)
class ComplianceScanAdmin(admin.ModelAdmin):
    list_display = ('product', 'compliance_status', 'scanned_by', 'scanned_at')
    list_filter = ('compliance_status', 'scanned_at')
    search_fields = ('product__name', 'extracted_text')
    readonly_fields = ('scanned_at',)
