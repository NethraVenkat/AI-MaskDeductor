from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/overview/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/insights/', views.dashboard_insights, name='dashboard_insights'),
    path('planner/compliance/', views.compliance_planner, name='compliance_planner'),
    path('replay/incidents/', views.incident_replay, name='incident_replay'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('api/start_camera/', views.start_camera, name='start_camera'),
    path('api/stop_camera/', views.stop_camera, name='stop_camera'),
    path('api/stats/', views.get_stats, name='get_stats'),
    path('api/alerts/', views.get_alerts, name='get_alerts'),
    path('api/detections/', views.get_detections, name='get_detections'),
    path('api/crowd_analytics/', views.get_crowd_analytics, name='get_crowd_analytics'),
    path('api/detect_image/', views.detect_from_image, name='detect_image'),
]
