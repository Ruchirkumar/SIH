from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_scan, name='upload_scan'),
    path('scan/<int:scan_id>/', views.scan_result, name='scan_result'),
    path('scans/', views.scan_list, name='scan_list'),
]
