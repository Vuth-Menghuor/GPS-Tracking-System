from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.core.management import call_command
from django.conf import settings
import json
import csv
import os
import subprocess
import threading
from datetime import datetime
from django.db import close_old_connections
from django.db.models import Count
from .models import DeviceData
from datetime import timezone, timedelta
import math


import_job_lock = threading.Lock()
import_job_status = {
    'running': False,
    'success': None,
    'error': None,
    'total_records': 0,
}
tracking_job_lock = threading.Lock()
tracking_job_status = {
    'running': False,
    'success': None,
    'error': None,
    'json_file': None,
    'folder': None,
}

def get_relative_short_label(unix_timestamp):
    if not unix_timestamp or str(unix_timestamp) in ['', '0', 'None', 'null']:
        return ''
    try:
        ts = int(unix_timestamp)
        ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        mins = int((datetime.now(timezone.utc) - ts_dt).total_seconds() // 60)
        mins_in_year = 365 * 24 * 60
        mins_in_month = 30 * 24 * 60
        mins_in_day = 24 * 60
        if mins >= mins_in_year:
            return f"{mins // mins_in_year}y ago"
        if mins >= mins_in_month:
            return f"{mins // mins_in_month}m ago"
        if mins >= mins_in_day:
            return f"{mins // mins_in_day}d ago"
        if mins >= 60:
            return f"{mins // 60}h ago"
        return f"{mins}min ago"
    except Exception:
        return ''
from datetime import timezone, timedelta


@csrf_exempt
@require_http_methods(["GET"])
def get_device_data(request):
    """Get paginated device data"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
        # Get all device data ordered by ranking_id
        devices = DeviceData.objects.all().order_by('ranking_id')
        
        # Paginate
        paginator = Paginator(devices, per_page)
        page_obj = paginator.get_page(page)
        
        # Helper to format time since using hearttime_unix
        def format_time_since(unix_timestamp):
            if not unix_timestamp or unix_timestamp in ["", "0", 0, None]:
                return ""
            try:
                ts_dt = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
                now = datetime.now(timezone.utc)
                delta = now - ts_dt
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                return f"{days}d{hours}h{minutes}min"
            except Exception:
                return ""

        # Convert to list of dictionaries
        data = []
        for device in page_obj:
            data.append({
                'ranking_id': device.ranking_id,
                'imei': device.imei,
                'latitude': float(device.latitude),
                'longitude': float(device.longitude),
                'coordinates': device.coordinates,
                'datastatus': device.datastatus,
                'datastatus_description': device.datastatus_description,
                'hearttime_date': device.hearttime_date.strftime('%Y-%m-%d') if device.hearttime_date else '',
                'hearttime_time': device.hearttime_time.strftime('%H:%M:%S') if device.hearttime_time else '',
                'hearttime_unix': device.hearttime_unix,
                # New field: TimeSinceUpdate (detailed) and TimeAgo (compact)
                'TimeSinceUpdate': format_time_since(device.hearttime_unix) or '',
                'TimeAgo': get_relative_short_label(device.hearttime_unix) or '',
                'status': device.status,
                'created_at': device.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': device.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_records': paginator.count,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def fetch_tracking_data(request):
    """Start GPS collection without blocking the HTTP worker."""
    try:
        with tracking_job_lock:
            if tracking_job_status['running']:
                return JsonResponse({
                    'success': False,
                    'error': 'GPS data collection is already in progress.',
                }, status=409)

            tracking_job_status.update({
                'running': True,
                'success': None,
                'error': None,
                'json_file': None,
                'folder': None,
            })
            threading.Thread(target=_run_tracking_fetch, daemon=True).start()

        return JsonResponse({
            'success': True,
            'message': 'GPS data collection started. The dashboard will update when it finishes.',
        }, status=202)
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return JsonResponse({'success': False, 'error': error_details}, status=500)


def _run_tracking_fetch():
    """Collect ProTrack data in a background thread."""
    try:
        call_command('fetch_tracking_data')
        response_logs_dir = os.path.join(settings.BASE_DIR, 'response_logs')
        folders = [folder for folder in os.listdir(response_logs_dir)
                   if folder.startswith('tracking_run_')]
        if not folders:
            raise RuntimeError('GPS collection completed but no data file was created.')
        folder = sorted(folders)[-1]
        json_file = os.path.join(response_logs_dir, folder, 'all_records.json')
        if not os.path.exists(json_file):
            raise RuntimeError('GPS collection completed but its JSON data file is missing.')
        tracking_job_status.update({
            'success': True,
            'error': None,
            'json_file': json_file,
            'folder': folder,
        })
    except Exception as error:
        tracking_job_status.update({'success': False, 'error': str(error)})
    finally:
        tracking_job_status['running'] = False


@require_http_methods(["GET"])
def get_tracking_status(request):
    """Return the state of the current or most recently completed GPS fetch."""
    return JsonResponse({'success': True, **tracking_job_status})


@csrf_exempt
@require_http_methods(["POST"])
def load_to_database(request):
    """Start a device-data import without blocking the HTTP worker."""
    try:
        data = json.loads(request.body)
        json_file = data.get('json_file')
        clear_existing = data.get('clear_existing', False)
        
        if not json_file or not os.path.exists(json_file):
            return JsonResponse({'success': False, 'error': 'JSON file not found'}, status=400)
        
        with import_job_lock:
            if import_job_status['running']:
                return JsonResponse({
                    'success': False,
                    'error': 'A data import is already in progress.',
                }, status=409)

            import_job_status.update({
                'running': True,
                'success': None,
                'error': None,
                'total_records': DeviceData.objects.count(),
            })
            worker = threading.Thread(
                target=_run_device_import,
                args=(json_file, clear_existing),
                daemon=True,
            )
            worker.start()

        return JsonResponse({
            'success': True,
            'message': 'Data import started. The dashboard will update when it finishes.',
        }, status=202)
        
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return JsonResponse({'success': False, 'error': error_details}, status=500)


def _run_device_import(json_file, clear_existing):
    """Run the long-lived import in a worker thread with its own DB connection."""
    close_old_connections()
    try:
        cmd_args = ['load_device_data', json_file]
        if clear_existing:
            cmd_args.append('--clear-existing')
        call_command(*cmd_args)
        import_job_status.update({
            'success': True,
            'error': None,
            'total_records': DeviceData.objects.count(),
        })
    except Exception as error:
        import_job_status.update({
            'success': False,
            'error': str(error),
        })
    finally:
        import_job_status['running'] = False
        close_old_connections()


@require_http_methods(["GET"])
def get_import_status(request):
    """Return the state of the current or most recently completed import."""
    return JsonResponse({'success': True, **import_job_status})


@csrf_exempt
@require_http_methods(["GET"])
def export_to_csv(request):
    """Export all device data to CSV"""
    try:
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="gps_tracking_data_{timestamp}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Helpers to format relative/detailed strings from hearttime_unix
        def format_time_since(unix_timestamp):
            if not unix_timestamp or str(unix_timestamp) in ['', '0', 'None', 'null']:
                return ''
            try:
                ts = int(unix_timestamp)
                ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                delta = now - ts_dt
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                return f"{days}d{hours}h{minutes}min"
            except Exception:
                return ''

        def get_relative_short_label(unix_timestamp):
            if not unix_timestamp or str(unix_timestamp) in ['', '0', 'None', 'null']:
                return ''
            try:
                mins = None
                ts = int(unix_timestamp)
                ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                mins = int((now - ts_dt).total_seconds() // 60)
                mins_in_year = 365 * 24 * 60
                mins_in_month = 30 * 24 * 60
                mins_in_day = 24 * 60
                if mins >= mins_in_year:
                    return f"{mins // mins_in_year}y ago"
                if mins >= mins_in_month:
                    return f"{mins // mins_in_month}m ago"
                if mins >= mins_in_day:
                    return f"{mins // mins_in_day}d ago"
                if mins >= 60:
                    return f"{mins // 60}h ago"
                return f"{mins}min ago"
            except Exception:
                return ''

        # Write header (added TimeSinceUpdate and TimeAgo)
        writer.writerow([
            'Ranking ID', 'IMEI', 'Latitude', 'Longitude', 'Coordinates',
            'Data Status Code', 'Data Status', 'Heart Date', 'Heart Time',
            'Heart Unix', 'TimeSinceUpdate', 'TimeAgo', 'Status', 'Created At', 'Updated At'
        ])
        
        # Write data
        devices = DeviceData.objects.all().order_by('ranking_id')
        for device in devices:
            relative_detailed = format_time_since(device.hearttime_unix)
            relative_short = get_relative_short_label(device.hearttime_unix)
            writer.writerow([
                device.ranking_id,
                device.imei,
                device.latitude,
                device.longitude,
                device.coordinates,
                device.datastatus,
                device.datastatus_description,
                device.hearttime_date.strftime('%Y-%m-%d') if device.hearttime_date else '',
                device.hearttime_time.strftime('%H:%M:%S') if device.hearttime_time else '',
                device.hearttime_unix,
                relative_detailed,
                relative_short,
                device.status,
                device.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                device.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_stats(request):
    """Get dashboard statistics"""
    try:
        total_devices = DeviceData.objects.count()
        
        # Get all status totals in one grouped query rather than one query per
        # status. This keeps the dashboard responsive on the hosted database.
        status_counts = {
            row['datastatus_description']: row['count']
            for row in DeviceData.objects.values('datastatus_description').annotate(count=Count('imei'))
        }
        
        # GPS coordinates availability
        with_coordinates = DeviceData.objects.exclude(latitude=0, longitude=0).count()
        without_coordinates = total_devices - with_coordinates
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_devices': total_devices,
                'with_coordinates': with_coordinates,
                'without_coordinates': without_coordinates,
                'status_counts': status_counts
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_recent_logs(request):
    """Get list of recent tracking runs"""
    try:
        response_logs_dir = os.path.join(settings.BASE_DIR, 'response_logs')
        logs = []
        
        if os.path.exists(response_logs_dir):
            folders = [f for f in os.listdir(response_logs_dir) if f.startswith('tracking_run_')]
            folders.sort(reverse=True)  # Most recent first
            
            for folder in folders[:10]:  # Get last 10 runs
                folder_path = os.path.join(response_logs_dir, folder)
                json_file = os.path.join(folder_path, 'all_records.json')
                
                if os.path.exists(json_file):
                    # Get file size and modification time
                    stat = os.stat(json_file)
                    size_mb = round(stat.st_size / (1024 * 1024), 2)
                    mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    logs.append({
                        'folder': folder,
                        'json_file': json_file,
                        'size_mb': size_mb,
                        'modified': mod_time
                    })
        
        return JsonResponse({
            'success': True,
            'logs': logs
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
