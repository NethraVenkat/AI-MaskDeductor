from djongo import models
from datetime import datetime


class Detection(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    camera_id = models.CharField(max_length=100, default='Camera-1')
    location = models.CharField(max_length=200, default='Main Entrance')
    total_faces = models.IntegerField(default=0)
    masked_count = models.IntegerField(default=0)
    unmasked_count = models.IntegerField(default=0)
    compliance_rate = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20, default='Low')
    image_path = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'detections'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Detection at {self.timestamp} - {self.camera_id}"


class Alert(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    camera_id = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    message = models.TextField()
    resolved = models.BooleanField(default=False)

    class Meta:
        db_table = 'alerts'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Alert: {self.alert_type} at {self.location}"


class CrowdAnalytics(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    camera_id = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    crowd_count = models.IntegerField(default=0)
    safe_limit = models.IntegerField(default=20)
    density_level = models.CharField(max_length=20)

    class Meta:
        db_table = 'crowd_analytics'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Crowd: {self.crowd_count} at {self.location}"
