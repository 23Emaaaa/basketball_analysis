import cv2
import supervision as sv


class CourtKeypointDrawer:
    """
    Classe responsabile per disegnare i punti chiave del campo sui frame.
    """

    def __init__(self):
        self.keypoint_color = "#ff2c2c"
        self.text_color = (255, 255, 255)  # Bianco per il testo
        # Usiamo solo l'annotator che funziona correttamente
        self.vertex_annotator = sv.VertexAnnotator(
            color=sv.Color.from_hex(self.keypoint_color), radius=5
        )

    def draw_frame(self, frame, keypoints_for_frame):
        """
        Disegna i punti chiave del campo su un SINGOLO frame.
        - Disegna i punti rossi con la libreria supervision.
        - Disegna le etichette numeriche manualmente con OpenCV per bypassare i bug.
        """
        annotated_frame = frame.copy()

        # Se non ci sono keypoints per questo frame, restituisci il frame originale
        if keypoints_for_frame is None or keypoints_for_frame.xy.numel() == 0:
            return annotated_frame

        # 1. Disegna i punti (pallini rossi) - Questa parte funziona
        annotated_frame = self.vertex_annotator.annotate(
            scene=annotated_frame, key_points=keypoints_for_frame
        )

        # 2. Disegna le etichette (numeri) manualmente con OpenCV
        # Estraiamo le coordinate dei punti come un array NumPy
        keypoints_xy = keypoints_for_frame.xy.cpu().numpy()[0]

        # Cicliamo su ogni punto per disegnarne l'etichetta
        for i, (x, y) in enumerate(keypoints_xy):
            # Convertiamo le coordinate in interi per il disegno
            text_position = (
                int(x) + 5,
                int(y) - 5,
            )  # Leggero offset per la leggibilità

            cv2.putText(
                img=annotated_frame,
                text=str(i),
                org=text_position,
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.4,
                color=self.text_color,
                thickness=1,
            )

        return annotated_frame

    def draw(self, frames, court_keypoints):
        """
        Metodo originale che ora utilizza 'draw_frame' in un ciclo.
        """
        output_frames = []
        for index, frame in enumerate(frames):
            keypoints_for_frame = court_keypoints[index]
            drawn_frame = self.draw_frame(frame, keypoints_for_frame)
            output_frames.append(drawn_frame)

        return output_frames
