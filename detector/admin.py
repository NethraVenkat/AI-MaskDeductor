from django.contrib import admin
from .models import Detection, Alert, CrowdAnalytics


@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'camera_id', 'location', 'total_faces', 'masked_count', 'unmasked_count', 'risk_level']
    list_filter = ['risk_level', 'camera_id', 'location']
    search_fields = ['camera_id', 'location']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'camera_id', 'location', 'alert_type', 'severity', 'resolved']
    list_filter = ['severity', 'alert_type', 'resolved']
    search_fields = ['camera_id', 'location', 'message']


@admin.register(CrowdAnalytics)
class CrowdAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'camera_id', 'location', 'crowd_count', 'safe_limit', 'density_level']
    list_filter = ['density_level', 'camera_id']
    search_fields = ['camera_id', 'location']
