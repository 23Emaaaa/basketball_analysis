from .utils import draw_traingle


class BallTracksDrawer:
    """
    Classe responsabile per disegnare il tracciamento della palla sui frame del video.
    """

    def __init__(self):
        self.ball_pointer_color = (
            0,
            255,
            0,
        )  # Colore verde per il puntatore della palla

    def draw_frame(self, frame, ball_tracks_for_frame):
        """
        Disegna il puntatore della palla su un SINGOLO frame.

        Args:
            frame (np.array): Il frame su cui disegnare.
            ball_tracks_for_frame (dict): Dizionario con le informazioni di tracciamento della palla.

        Returns:
            np.array: Il frame con il puntatore disegnato.
        """
        output_frame = frame.copy()

        # Disegna il puntatore per la palla (di solito ha ID 1)
        for _, ball_data in ball_tracks_for_frame.items():
            if ball_data.get("bbox"):
                output_frame = draw_traingle(
                    output_frame, ball_data["bbox"], self.ball_pointer_color
                )

        return output_frame

    def draw(self, video_frames, tracks):
        """
        Metodo originale che ora utilizza 'draw_frame' in un ciclo.
        Disegna i puntatori della palla su una lista di frame.
        """
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            ball_tracks_for_frame = tracks[frame_num]
            drawn_frame = self.draw_frame(frame, ball_tracks_for_frame)
            output_video_frames.append(drawn_frame)

        return output_video_frames
