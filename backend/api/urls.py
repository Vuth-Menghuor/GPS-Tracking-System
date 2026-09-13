from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('devices/', views.get_device_data, name='get_device_data'),
    path('fetch-tracking/', views.fetch_tracking_data, name='fetch_tracking_data'),
    path('tracking-status/', views.get_tracking_status, name='get_tracking_status'),
    path('load-database/', views.load_to_database, name='load_to_database'),
    path('import-status/', views.get_import_status, name='get_import_status'),
    path('export-csv/', views.export_to_csv, name='export_to_csv'),
    path('stats/', views.get_stats, name='get_stats'),
    path('logs/', views.get_recent_logs, name='get_recent_logs'),
]
