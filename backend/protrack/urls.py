"""
URL configuration for protrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "message": "GPS Tracking API",
        "version": "1.0",
        "endpoints": {
            "stats": "/api/stats/",
            "devices": "/api/devices/",
            "fetch_tracking": "/api/fetch-tracking/",
            "load_database": "/api/load-database/",
            "export_csv": "/api/export-csv/",
            "logs": "/api/logs/",
            "admin": "/admin/"
        }
    })


def health_check(request):
    """Minimal endpoint for Render; deliberately does not query the database."""
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('', api_root, name='api_root'),
    path('healthz/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
