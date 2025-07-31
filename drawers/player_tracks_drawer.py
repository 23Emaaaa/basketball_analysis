from .utils import draw_ellipse, draw_traingle


class PlayerTracksDrawer:
    def __init__(self, team_1_color=[255, 245, 238], team_2_color=[128, 0, 0]):
        self.default_player_team_id = 1
        self.team_1_color = team_1_color
        self.team_2_color = team_2_color

    def draw_frame(
        self,
        frame,
        player_tracks_for_frame,
        player_assignment_for_frame,
        player_with_ball_id,
    ):
        """
        Disegna i tracciati dei giocatori, l'assegnazione alla squadra e l'indicatore di possesso palla
        su un SINGOLO frame.

        Args:
            frame (np.array): Il frame su cui disegnare.
            player_tracks_for_frame (dict): Dizionario con le informazioni di tracciamento dei giocatori per questo frame.
            player_assignment_for_frame (dict): Dizionario che mappa track_id a team_id.
            player_with_ball_id (int): L'ID del giocatore che ha la palla.

        Returns:
            np.array: Il frame con gli elementi disegnati.
        """
        output_frame = frame.copy()

        # Disegna il box per ogni giocatore
        for track_id, player in player_tracks_for_frame.items():
            team_id = player_assignment_for_frame.get(
                track_id, self.default_player_team_id
            )
            color = self.team_1_color if team_id == 1 else self.team_2_color

            # Disegna l'ellisse per il giocatore
            output_frame = draw_ellipse(output_frame, player["bbox"], color, track_id)

            # Se questo giocatore ha la palla, disegna un triangolo sopra di lui
            if track_id == player_with_ball_id:
                output_frame = draw_traingle(output_frame, player["bbox"], (0, 0, 255))

        return output_frame

    def draw(self, video_frames, tracks, player_assignment, ball_aquisition):
        """
        Metodo originale che ora utilizza 'draw_frame' in un ciclo.
        Disegna i tracciati su una lista completa di frame.
        """
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            # Prendi i dati per il frame corrente
            player_tracks_for_frame = tracks.get(frame_num, {})
            player_assignment_for_frame = player_assignment.get(frame_num, {})
            player_with_ball_id = ball_aquisition.get(
                frame_num, -1
            )  # -1 se nessuno ha la palla

            # Usa il nuovo metodo per disegnare sul singolo frame
            drawn_frame = self.draw_frame(
                frame,
                player_tracks_for_frame,
                player_assignment_for_frame,
                player_with_ball_id,
            )
            output_video_frames.append(drawn_frame)

        return output_video_frames
