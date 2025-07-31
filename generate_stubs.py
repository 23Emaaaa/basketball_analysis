import os
from utils import read_video, save_stub
from trackers import PlayerTracker, BallTracker
from team_assigner import TeamAssigner
from court_keypoint_detector import CourtKeypointDetector
from ball_aquisition import BallAquisitionDetector
from configs import (
    PLAYER_DETECTOR_PATH,
    BALL_DETECTOR_PATH,
    COURT_KEYPOINT_DETECTOR_PATH,
)


def generate_all_stubs(video_path):
    """
    Genera tutti i file stub necessari per un dato video,
    eseguendo l'intera pipeline di analisi e salvando ogni passaggio.
    """
    # Assicurati che la cartella stubs esista
    stubs_dir = "stubs"
    os.makedirs(stubs_dir, exist_ok=True)

    # Definisci i percorsi per tutti i file stub che creeremo
    player_tracks_stub_path = os.path.join(stubs_dir, "player_track_stubs.pkl")
    ball_tracks_stub_path = os.path.join(stubs_dir, "ball_track_stubs.pkl")
    court_keypoints_stub_path = os.path.join(stubs_dir, "court_key_points_stub.pkl")
    player_assignment_stub_path = os.path.join(stubs_dir, "player_assignment_stub.pkl")
    ball_aquisition_stub_path = os.path.join(stubs_dir, "ball_aquisition.pkl")

    print(f"Inizio la generazione degli stub per il video: {video_path}")
    video_frames = read_video(video_path)

    # --- Esecuzione della Pipeline di Analisi ---

    # 1. Tracciamento Giocatori
    print("Passaggio 1/5: Tracciamento dei giocatori...")
    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    player_tracks = player_tracker.get_object_tracks(
        video_frames, read_from_stub=False, stub_path=player_tracks_stub_path
    )

    # 2. Tracciamento Palla
    print("Passaggio 2/5: Tracciamento della palla...")
    ball_tracker = BallTracker(BALL_DETECTOR_PATH)
    ball_tracks = ball_tracker.get_object_tracks(
        video_frames, read_from_stub=False, stub_path=ball_tracks_stub_path
    )
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # 3. Rilevamento Keypoints del Campo
    print("Passaggio 3/5: Rilevamento dei keypoints del campo...")
    court_keypoint_detector = CourtKeypointDetector(COURT_KEYPOINT_DETECTOR_PATH)
    court_keypoints_per_frame = court_keypoint_detector.get_court_keypoints(
        video_frames, read_from_stub=False, stub_path=court_keypoints_stub_path
    )

    # 4. Assegnazione Squadre
    print("Passaggio 4/5: Assegnazione delle squadre ai giocatori...")
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=False,
        stub_path=player_assignment_stub_path,
    )

    # 5. Rilevamento Possesso Palla
    print("Passaggio 5/5: Rilevamento del possesso palla...")
    ball_aquisition_detector = BallAquisitionDetector()
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(
        player_tracks, ball_tracks
    )
    save_stub(ball_aquisition_stub_path, ball_aquisition)

    print(
        "\n✅ Tutti i file stub sono stati rigenerati con successo per il nuovo video!"
    )
    print("Ora puoi eseguire di nuovo 'test_player_drawer.py'.")


if __name__ == "__main__":
    # IMPORTANTE: Assicurati che questo percorso punti al tuo nuovo video
    NEW_VIDEO_PATH = "input_videos/video_2.mp4"
    generate_all_stubs(video_path=NEW_VIDEO_PATH)
