from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import cv2
import json
import base64
import numpy as np
from datetime import datetime, timedelta
from .models import Detection, Alert, CrowdAnalytics
from .mask_detector import MaskDetector
import threading

detector = MaskDetector()
camera = None
camera_lock = threading.Lock()


def build_live_snapshot():
    all_detections = Detection.objects.all()

    total_detections = all_detections.count()
    total_faces = sum(d.total_faces for d in all_detections)
    total_masked = sum(d.masked_count for d in all_detections)
    total_unmasked = sum(d.unmasked_count for d in all_detections)

    avg_compliance = (total_masked / total_faces * 100) if total_faces > 0 else 0
    all_alerts = Alert.objects.all()
    active_alerts_count = sum(1 for alert in all_alerts if not bool(alert.resolved))

    high_risk_count = all_detections.filter(risk_level='High').count()
    medium_risk_count = all_detections.filter(risk_level='Medium').count()
    low_risk_count = all_detections.filter(risk_level='Low').count()

    latest_detection = all_detections.order_by('-timestamp').first()

    return {
        'total_detections': total_detections,
        'total_faces': total_faces,
        'masked_count': total_masked,
        'unmasked_count': total_unmasked,
        'compliance_rate': round(avg_compliance, 2),
        'active_alerts': active_alerts_count,
        'risk_distribution': {
            'high': high_risk_count,
            'medium': medium_risk_count,
            'low': low_risk_count
        },
        'last_capture': latest_detection.timestamp.strftime('%Y-%m-%d %H:%M:%S') if latest_detection else 'Waiting for the live camera feed'
    }


def index(request):
    return render(request, 'index.html', {'live_snapshot': build_live_snapshot()})


def dashboard_overview(request):
    return render(request, 'dashboard_overview.html', {'live_snapshot': build_live_snapshot()})


def dashboard_insights(request):
    return render(request, 'dashboard_insights.html', {'live_snapshot': build_live_snapshot()})


def compliance_planner(request):
    return render(request, 'compliance_planner.html', {'live_snapshot': build_live_snapshot()})


def incident_replay(request):
    return render(request, 'incident_replay.html', {'live_snapshot': build_live_snapshot()})


def generate_frames():
    global camera
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)

    while True:
        with camera_lock:
            if camera is None or not camera.isOpened():
                break

            success, frame = camera.read()
            if not success:
                break

            predictions = detector.detect_and_predict(frame)
            frame, masked_count, unmasked_count = detector.draw_predictions(frame, predictions)

            total_faces = len(predictions)
            compliance_rate = (masked_count / total_faces * 100) if total_faces > 0 else 100

            if total_faces > 0:
                risk_level = 'Low' if compliance_rate >= 80 else 'Medium' if compliance_rate >= 50 else 'High'

                Detection.objects.create(
                    camera_id='Camera-1',
                    location='Main Entrance',
                    total_faces=total_faces,
                    masked_count=masked_count,
                    unmasked_count=unmasked_count,
                    compliance_rate=compliance_rate,
                    risk_level=risk_level
                )

                if unmasked_count > 0 and compliance_rate < 80:
                    Alert.objects.create(
                        camera_id='Camera-1',
                        location='Main Entrance',
                        alert_type='Mask Violation',
                        severity='High' if compliance_rate < 50 else 'Medium',
                        message=f'{unmasked_count} person(s) without mask detected'
                    )

                CrowdAnalytics.objects.create(
                    camera_id='Camera-1',
                    location='Main Entrance',
                    crowd_count=total_faces,
                    safe_limit=20,
                    density_level='High' if total_faces > 20 else 'Medium' if total_faces > 10 else 'Low'
                )

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def video_feed(request):
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@csrf_exempt
@require_http_methods(["POST"])
def start_camera(request):
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            if camera.isOpened():
                return JsonResponse({'status': 'success', 'message': 'Camera started'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to start camera'}, status=500)
        return JsonResponse({'status': 'success', 'message': 'Camera already running'})


@csrf_exempt
@require_http_methods(["POST"])
def stop_camera(request):
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
            return JsonResponse({'status': 'success', 'message': 'Camera stopped'})
        return JsonResponse({'status': 'success', 'message': 'Camera already stopped'})


@require_http_methods(["GET"])
def get_stats(request):
    return JsonResponse(build_live_snapshot())


@require_http_methods(["GET"])
def get_alerts(request):
    alerts = Alert.objects.all().order_by('-timestamp')

    alerts_data = [{
        'id': str(alert.id),
        'timestamp': alert.timestamp.isoformat(),
        'camera_id': alert.camera_id,
        'location': alert.location,
        'alert_type': alert.alert_type,
        'severity': alert.severity,
        'message': alert.message
    } for alert in alerts]

    return JsonResponse({'alerts': alerts_data})


@require_http_methods(["GET"])
def get_detections(request):
    detections = Detection.objects.all().order_by('-timestamp')

    detections_data = [{
        'id': str(detection.id),
        'timestamp': detection.timestamp.isoformat(),
        'camera_id': detection.camera_id,
        'location': detection.location,
        'total_faces': detection.total_faces,
        'masked_count': detection.masked_count,
        'unmasked_count': detection.unmasked_count,
        'compliance_rate': detection.compliance_rate,
        'risk_level': detection.risk_level
    } for detection in detections]

    return JsonResponse({'detections': detections_data})


@require_http_methods(["GET"])
def get_crowd_analytics(request):
    analytics = CrowdAnalytics.objects.all().order_by('-timestamp')

    analytics_data = [{
        'id': str(analytic.id),
        'timestamp': analytic.timestamp.isoformat(),
        'camera_id': analytic.camera_id,
        'location': analytic.location,
        'crowd_count': analytic.crowd_count,
        'safe_limit': analytic.safe_limit,
        'density_level': analytic.density_level
    } for analytic in analytics]

    return JsonResponse({'analytics': analytics_data})


@csrf_exempt
@require_http_methods(["POST"])
def detect_from_image(request):
    try:
        data = json.loads(request.body)
        image_data = data.get('image', '')

        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        predictions = detector.detect_and_predict(frame)
        frame, masked_count, unmasked_count = detector.draw_predictions(frame, predictions)

        ret, buffer = cv2.imencode('.jpg', frame)
        img_str = base64.b64encode(buffer).decode()

        total_faces = len(predictions)
        compliance_rate = (masked_count / total_faces * 100) if total_faces > 0 else 0

        if total_faces > 0:
            risk_level = 'Low' if compliance_rate >= 80 else 'Medium' if compliance_rate >= 50 else 'High'

            Detection.objects.create(
                camera_id='Image-Upload',
                location='Manual Capture',
                total_faces=total_faces,
                masked_count=masked_count,
                unmasked_count=unmasked_count,
                compliance_rate=compliance_rate,
                risk_level=risk_level
            )

            if unmasked_count > 0 and compliance_rate < 80:
                Alert.objects.create(
                    camera_id='Image-Upload',
                    location='Manual Capture',
                    alert_type='Mask Violation',
                    severity='High' if compliance_rate < 50 else 'Medium',
                    message=f'{unmasked_count} person(s) without mask detected'
                )

            CrowdAnalytics.objects.create(
                camera_id='Image-Upload',
                location='Manual Capture',
                crowd_count=total_faces,
                safe_limit=20,
                density_level='High' if total_faces > 20 else 'Medium' if total_faces > 10 else 'Low'
            )

        return JsonResponse({
            'status': 'success',
            'image': f'data:image/jpeg;base64,{img_str}',
            'total_faces': total_faces,
            'masked_count': masked_count,
            'unmasked_count': unmasked_count,
            'compliance_rate': round(compliance_rate, 2)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
