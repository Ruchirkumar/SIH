from django import forms
from .models import Product, ComplianceScan


class ScanUploadForm(forms.Form):
    """
    Single form that creates both a Product and its first ComplianceScan.
    Kept as a plain Form (not ModelForm) since it spans two models.
    """
    product_name = forms.CharField(
        max_length=255,
        label="Product Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Reliclear Eye Drops'})
    )
    manufacturer_name = forms.CharField(
        max_length=255,
        required=False,
        label="Manufacturer (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    category = forms.CharField(
        max_length=100,
        required=False,
        label="Category (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. food, pharma, cosmetics'})
    )
    image = forms.ImageField(
        label="Product Label Image",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
