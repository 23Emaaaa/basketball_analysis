import numpy as np
from utils.bbox_utils import get_center_of_bbox


class ShotDetector:
    def __init__(
        self,
        basket_area,
        basket_radius=30,
        vertical_velocity_threshold=5,
        min_frames_in_shot=5,
    ):
        self.basket_area = basket_area
        self.basket_radius = basket_radius
        self.vertical_velocity_threshold = vertical_velocity_threshold
        self.min_frames_in_shot = min_frames_in_shot

        self.shot_in_progress = False
        self.shot_start_frame = 0
        self.ball_positions_in_shot = []
        self.last_ball_pos = None

    def detect(
        self,
        ball_tracks_for_frame,
        player_tracks_for_frame,
        ball_acquisition,
        frame_num,
    ):
        ball_pos = self._get_ball_position(ball_tracks_for_frame)

        # Se non c'è la palla in questo frame, non facciamo nulla
        if ball_pos is None:
            self.last_ball_pos = None
            return None

        # Rilevamento dell'inizio di un tiro
        if not self.shot_in_progress:
            if self.last_ball_pos is not None:
                vertical_velocity = (
                    self.last_ball_pos[1] - ball_pos[1]
                )  # Y cresce verso il basso, quindi una velocità positiva è verso l'alto

                # CONDIZIONE DI TRIGGER: la palla sale velocemente E nessuno la possiede
                if (
                    vertical_velocity > self.vertical_velocity_threshold
                    and ball_acquisition == -1
                ):
                    self.shot_in_progress = True
                    self.shot_start_frame = frame_num
                    self.ball_positions_in_shot = [self.last_ball_pos, ball_pos]

            self.last_ball_pos = ball_pos
            return None

        # Se un tiro è già in corso
        else:
            self.ball_positions_in_shot.append(ball_pos)

            # CONDIZIONE DI FINE TIRO: la palla scende sotto l'altezza del canestro
            if self.basket_area is not None and ball_pos[1] > self.basket_area[1]:
                self.shot_in_progress = False

                # Analizza la traiettoria solo se è abbastanza lunga
                if len(self.ball_positions_in_shot) < self.min_frames_in_shot:
                    return None

                # Verifica se è stato canestro
                successful = self._classify_shot()

                # Resetta e restituisci l'evento
                event = {
                    "shot_event": "shot_ended",
                    "frame": frame_num,
                    "successful": successful,
                }
                self.ball_positions_in_shot = []
                self.last_ball_pos = None
                return event

        self.last_ball_pos = ball_pos
        return None

    def _classify_shot(self):
        """
        Analizza l'intera traiettoria registrata per determinare se il tiro è andato a segno.
        """
        if not self.ball_positions_in_shot or self.basket_area is None:
            return False

        # Converti le posizioni in un array numpy per calcoli più semplici
        trajectory = np.array(self.ball_positions_in_shot)
        basket_pos = np.array(self.basket_area)

        # Calcola la distanza orizzontale di ogni punto della traiettoria dal canestro
        horizontal_distances = np.abs(trajectory[:, 0] - basket_pos[0])

        # Trova l'indice del punto della traiettoria più vicino orizzontalmente al canestro
        closest_point_idx = np.argmin(horizontal_distances)
        closest_point = trajectory[closest_point_idx]

        # Calcola la distanza 2D tra quel punto e il canestro
        distance_to_basket = np.linalg.norm(closest_point - basket_pos)

        # Se il punto più vicino è entro il raggio del canestro, è canestro.
        return distance_to_basket < self.basket_radius

    def _get_ball_position(self, ball_tracks):
        """Estrae la posizione centrale della palla dal dizionario di tracciamento."""
        if 1 in ball_tracks and ball_tracks[1].get("bbox"):
            return get_center_of_bbox(ball_tracks[1]["bbox"])
        return None
