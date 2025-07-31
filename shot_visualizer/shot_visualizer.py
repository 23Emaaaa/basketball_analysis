import cv2
from utils.bbox_utils import get_center_of_bbox


class ShotVisualizer:
    def __init__(self):
        """
        Inizializza il visualizzatore con i colori per il disegno.
        """
        self.trajectory_color = (0, 255, 0)  # Verde per la traiettoria
        self.success_color = (0, 255, 0)  # Verde per "Bucket!"
        self.failure_color = (0, 0, 255)  # Rosso per "Miss!"

    def draw_events(self, frame, shot_event, shot_detector):
        """
        Disegna tutti gli elementi visivi legati al tiro su un singolo frame.
        Questo metodo funge da punto di ingresso principale per il disegno degli eventi di tiro.

        Args:
            frame (numpy.ndarray): Il frame video su cui disegnare.
            shot_event (dict): L'evento di tiro rilevato (inizio/fine).
            shot_detector (ShotDetector): L'istanza del rilevatore per accedere al suo stato.

        Returns:
            numpy.ndarray: Il frame con gli elementi visivi disegnati.
        """
        output_frame = frame.copy()

        # 1. Disegna la traiettoria della palla (solo per debug, quando un tiro è in corso)
        if shot_detector.shot_in_progress:
            self._draw_trajectory(output_frame, shot_detector.ball_positions_in_shot)

        # 2. Disegna l'esito del tiro ("Bucket!" o "Miss!") quando il tiro termina
        if shot_event and shot_event["shot_event"] == "shot_ended":
            self._draw_shot_outcome(output_frame, shot_event["successful"])

        return output_frame

    def _draw_trajectory(self, frame, trajectory):
        """
        Disegna una linea che rappresenta la traiettoria della palla.
        Funzione interna chiamata da draw_events.
        """
        # Disegna una linea che collega i centri delle bbox della palla
        for i in range(len(trajectory) - 1):
            # Assicurati che le bbox siano valide prima di processarle
            if not trajectory[i] or not trajectory[i + 1]:
                continue

            p1 = get_center_of_bbox(trajectory[i])
            p2 = get_center_of_bbox(trajectory[i + 1])
            cv2.line(frame, p1, p2, self.trajectory_color, 2)

    def _draw_shot_outcome(self, frame, successful):
        """
        Scrive "Bucket!" o "Miss!" sul frame.
        Funzione interna chiamata da draw_events.
        """
        text = "Bucket!" if successful else "Miss!"
        color = self.success_color if successful else self.failure_color

        # Posiziona il testo in un punto ben visibile (es. in alto a sinistra)
        cv2.putText(
            frame,
            text,
            (150, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,  # Dimensione del font
            color,
            3,  # Spessore del font
        )
