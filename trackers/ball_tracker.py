import pandas as pd
from ultralytics import YOLO
from utils.bbox_utils import get_center_of_bbox
from utils.kalman_filter import KalmanFilter


class BallTracker:
    def __init__(self, model):
        self.model = model
        self.kalman_filter = KalmanFilter()
        self.filter_initialized = False

    def track_frames(self, frames):
        """
        Metodo principale che rileva la palla e applica il filtro di Kalman
        per ottenere una traiettoria pulita e completa.
        """
        raw_detections = self._detect_frames_raw(frames)
        return self._get_kalman_filtered_tracks(raw_detections)

    def _get_kalman_filtered_tracks(self, detections):
        tracks = []

        for frame_num, detection_bbox in enumerate(detections):
            frame_tracks = {}
            predicted_position = self.kalman_filter.predict()

            if detection_bbox:  # Se il detector ha trovato la palla
                center_point = get_center_of_bbox(detection_bbox)

                if not self.filter_initialized:
                    self.kalman_filter.initialize_state(center_point)
                    self.filter_initialized = True

                corrected_position = self.kalman_filter.correct(center_point)
                corrected_bbox = self._create_bbox_from_center(
                    corrected_position, detection_bbox
                )
                frame_tracks[1] = {"bbox": corrected_bbox}

            elif self.filter_initialized:
                predicted_bbox = self._create_bbox_from_center(predicted_position)
                frame_tracks[1] = {"bbox": predicted_bbox}

            tracks.append(frame_tracks)

        return tracks

    def _create_bbox_from_center(self, center, reference_bbox=None):
        width = reference_bbox[2] - reference_bbox[0] if reference_bbox else 20
        height = reference_bbox[3] - reference_bbox[1] if reference_bbox else 20
        x1 = center[0] - width / 2
        y1 = center[1] - height / 2
        x2 = center[0] + width / 2
        y2 = center[1] + height / 2
        return [x1, y1, x2, y2]

    def _detect_frames_raw(self, frames):
        """
        Esegue il rilevamento YOLO e restituisce solo il BBox della palla con la confidenza più alta per ogni frame.
        """
        batch_size = 20
        raw_detections = []
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i : i + batch_size], conf=0.2)
            for detection in detections_batch:
                ball_bbox = None
                max_confidence = 0

                # Cerca dinamicamente l'ID della classe "Ball"
                try:
                    ball_class_id = [
                        k for k, v in detection.names.items() if v == "Ball"
                    ][0]
                except IndexError:
                    # Se il modello non ha la classe 'Ball', non possiamo fare nulla
                    raw_detections.append(ball_bbox)
                    continue

                for box in detection.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    if class_id == ball_class_id:
                        if confidence > max_confidence:
                            ball_bbox = box.xyxy[0].tolist()
                            max_confidence = confidence

                raw_detections.append(ball_bbox)
        return raw_detections
