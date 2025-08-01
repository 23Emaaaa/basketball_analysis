import cv2
from utils.bbox_utils import get_center_of_bbox


class ShotVisualizer:
    def __init__(self):
        self.trajectory_color = (0, 255, 0)
        self.success_color = (0, 255, 0)
        self.failure_color = (0, 0, 255)

    def draw(self, frame, shot_detector, shot_outcome_text=None):
        """
        Disegna tutti gli elementi visivi: la traiettoria e l'esito persistente del tiro.

        Args:
            frame (numpy.ndarray): Il frame video su cui disegnare.
            shot_detector (ShotDetector): L'istanza del rilevatore per disegnare la traiettoria.
            shot_outcome_text (str, optional): Il testo da disegnare ("Bucket!" o "Miss!"). Defaults to None.
        """
        output_frame = frame.copy()

        # 1. Disegna la traiettoria se un tiro è in corso
        if shot_detector.shot_in_progress:
            self._draw_trajectory(output_frame, shot_detector.ball_positions_in_shot)

        # 2. Disegna l'esito del tiro se è fornito
        if shot_outcome_text:
            color = (
                self.success_color
                if shot_outcome_text == "Bucket!"
                else self.failure_color
            )
            self._draw_shot_outcome(output_frame, shot_outcome_text, color)

        return output_frame

    def _draw_trajectory(self, frame, trajectory):
        for i in range(len(trajectory) - 1):
            if not trajectory[i] or not trajectory[i + 1]:
                continue
            p1 = get_center_of_bbox(trajectory[i])
            p2 = get_center_of_bbox(trajectory[i + 1])
            cv2.line(frame, p1, p2, self.trajectory_color, 2)

    def _draw_shot_outcome(self, frame, text, color):
        cv2.putText(frame, text, (150, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
