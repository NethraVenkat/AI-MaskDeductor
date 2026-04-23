import cv2
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import os


class MaskDetector:
    def __init__(self):
        self.face_detector = None
        self.mask_detector = None
        self.load_models()

    def load_models(self):
        try:
            prototxt_path = "detector/models/deploy.prototxt"
            weights_path = "detector/models/res10_300x300_ssd_iter_140000.caffemodel"

            if os.path.exists(prototxt_path) and os.path.exists(weights_path):
                self.face_detector = cv2.dnn.readNet(prototxt_path, weights_path)
            else:
                self.face_detector = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )

            mask_model_path = "detector/models/mask_detector.model"
            if os.path.exists(mask_model_path):
                self.mask_detector = load_model(mask_model_path)
        except Exception as e:
            print(f"Error loading models: {e}")
            self.face_detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

    def detect_faces_dnn(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        self.face_detector.setInput(blob)
        detections = self.face_detector.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                faces.append((startX, startY, endX - startX, endY - startY))
        return faces

    def detect_faces_cascade(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces

    def predict_mask(self, face_img):
        if self.mask_detector is None:
            return self.simple_mask_detection(face_img)

        try:
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            face_img = cv2.resize(face_img, (224, 224))
            face_img = img_to_array(face_img)
            face_img = preprocess_input(face_img)
            face_img = np.expand_dims(face_img, axis=0)

            prediction = self.mask_detector.predict(face_img)[0]
            return ("Mask", prediction[0]) if prediction[0] > prediction[1] else ("No Mask", prediction[1])
        except Exception:
            return self.simple_mask_detection(face_img)

    def simple_mask_detection(self, face_img):
        lower_half = face_img[face_img.shape[0]//2:, :]

        hsv = cv2.cvtColor(lower_half, cv2.COLOR_BGR2HSV)

        mask_colors = [
            (np.array([0, 0, 100]), np.array([180, 50, 255])),
            (np.array([90, 50, 50]), np.array([130, 255, 255])),
        ]

        total_pixels = lower_half.shape[0] * lower_half.shape[1]
        covered_pixels = 0

        for lower, upper in mask_colors:
            mask = cv2.inRange(hsv, lower, upper)
            covered_pixels += cv2.countNonZero(mask)

        coverage_ratio = covered_pixels / total_pixels

        if coverage_ratio > 0.3:
            return ("Mask", coverage_ratio)
        else:
            return ("No Mask", 1 - coverage_ratio)

    def detect_and_predict(self, frame):
        if isinstance(self.face_detector, cv2.dnn_Net):
            faces = self.detect_faces_dnn(frame)
        else:
            faces = self.detect_faces_cascade(frame)

        results = []
        for (x, y, w, h) in faces:
            x, y = max(0, x), max(0, y)
            w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)

            face_img = frame[y:y+h, x:x+w]
            if face_img.size == 0:
                continue

            label, confidence = self.predict_mask(face_img)
            results.append({
                'box': (x, y, w, h),
                'label': label,
                'confidence': float(confidence)
            })

        return results

    def draw_predictions(self, frame, predictions):
        masked_count = 0
        unmasked_count = 0

        for pred in predictions:
            x, y, w, h = pred['box']
            label = pred['label']
            confidence = pred['confidence']

            if label == "Mask":
                color = (0, 255, 0)
                masked_count += 1
            else:
                color = (0, 0, 255)
                unmasked_count += 1

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            text = f"{label}: {confidence:.2f}"
            cv2.putText(frame, text, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        info_text = f"Total: {len(predictions)} | Masked: {masked_count} | No Mask: {unmasked_count}"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame, masked_count, unmasked_count
