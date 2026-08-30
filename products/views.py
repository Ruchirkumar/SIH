from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ScanUploadForm
from .models import Product, ComplianceScan
from .ocr_utils import extract_fields
from .rule_engine import run_compliance_checks


def upload_scan(request):
    if request.method == 'POST':
        form = ScanUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the Product
            product = Product.objects.create(
                name=form.cleaned_data['product_name'],
                manufacturer_name=form.cleaned_data.get('manufacturer_name', ''),
                category=form.cleaned_data.get('category', ''),
                created_by=request.user if request.user.is_authenticated else None,
            )

            # Create the scan with the uploaded image
            scan = ComplianceScan.objects.create(
                product=product,
                image=form.cleaned_data['image'],
                scanned_by=request.user if request.user.is_authenticated else None,
            )

            # Run OCR + rule engine immediately (synchronous - fine for demo scale)
            try:
                raw_text, fields = extract_fields(scan.image.path)
                scan.extracted_text = raw_text
                scan.extracted_fields = fields

                status, violations = run_compliance_checks(fields)
                scan.compliance_status = status
                scan.violations = violations
                scan.save()
            except Exception as e:
                messages.error(request, f"Processing failed: {e}")
                return redirect('scan_result', scan_id=scan.id)

            return redirect('scan_result', scan_id=scan.id)
    else:
        form = ScanUploadForm()

    return render(request, 'products/upload.html', {'form': form})


def scan_result(request, scan_id):
    scan = get_object_or_404(ComplianceScan, id=scan_id)
    return render(request, 'products/result.html', {'scan': scan})


def scan_list(request):
    scans = ComplianceScan.objects.select_related('product').order_by('-scanned_at')

    status_filter = request.GET.get('status')
    if status_filter in ('COMPLIANT', 'NON_COMPLIANT', 'PENDING'):
        scans = scans.filter(compliance_status=status_filter)

    total = ComplianceScan.objects.count()
    compliant_count = ComplianceScan.objects.filter(compliance_status='COMPLIANT').count()
    non_compliant_count = ComplianceScan.objects.filter(compliance_status='NON_COMPLIANT').count()

    context = {
        'scans': scans,
        'total': total,
        'compliant_count': compliant_count,
        'non_compliant_count': non_compliant_count,
        'current_filter': status_filter,
    }
    return render(request, 'products/scan_list.html', context)
