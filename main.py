import os
from utils import read_video, save_video, save_stub
from trackers import PlayerTracker, BallTracker
from court_keypoint_detector import CourtKeypointDetector
from team_assigner import TeamAssigner
from ball_aquisition import BallAquisitionDetector
from shot_detector import ShotDetector  # <-- 1. IMPORT CORRETTO
from shot_visualizer import ShotVisualizer
from drawers import (
    PlayerTracksDrawer,
    BallTracksDrawer,
    CourtKeypointDrawer,
)
from configs import (
    PLAYER_DETECTOR_PATH,
    BALL_DETECTOR_PATH,
    COURT_KEYPOINT_DETECTOR_PATH,
)


def main(input_video_path, read_stubs=False):
    """
    Funzione principale per eseguire l'analisi completa del video di basket.
    """
    video_frames = read_video(input_video_path)

    # --- Analisi (uguale a prima) ---
    stubs_dir = "stubs"
    # ... (tutta la parte di generazione/lettura stubs rimane invariata)
    player_tracks_stub = os.path.join(stubs_dir, "player_track_stubs.pkl")
    ball_tracks_stub = os.path.join(stubs_dir, "ball_track_stubs.pkl")
    court_keypoints_stub = os.path.join(stubs_dir, "court_key_points_stub.pkl")
    player_assignment_stub = os.path.join(stubs_dir, "player_assignment_stub.pkl")
    ball_aquisition_stub = os.path.join(stubs_dir, "ball_aquisition.pkl")

    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    player_tracks = player_tracker.get_object_tracks(
        video_frames, read_from_stub=read_stubs, stub_path=player_tracks_stub
    )

    ball_tracker = BallTracker(BALL_DETECTOR_PATH)
    ball_tracks = ball_tracker.get_object_tracks(
        video_frames, read_from_stub=read_stubs, stub_path=ball_tracks_stub
    )
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    court_keypoint_detector = CourtKeypointDetector(COURT_KEYPOINT_DETECTOR_PATH)
    court_keypoints = court_keypoint_detector.get_court_keypoints(
        video_frames, read_from_stub=read_stubs, stub_path=court_keypoints_stub
    )

    team_assigner = TeamAssigner()
    player_assignments = team_assigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=read_stubs,
        stub_path=player_assignment_stub,
    )

    ball_aquisition_detector = BallAquisitionDetector()
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(
        player_tracks, ball_tracks
    )
    if not read_stubs:
        save_stub(ball_aquisition_stub, ball_aquisition)

    # --- Inizializzazione Drawer e Detector ---
    player_drawer = PlayerTracksDrawer()
    ball_drawer = BallTracksDrawer()
    court_drawer = CourtKeypointDrawer()
    shot_detector = ShotDetector(basket_area=None)
    shot_visualizer = ShotVisualizer()

    output_frames = []
    print("Inizio elaborazione e disegno frame per frame...")

    # --- CICLO PRINCIPALE DI ELABORAZIONE E DISEGNO ---
    for frame_num, frame in enumerate(video_frames):

        # --- 2. ACCESSO AI DATI CORRETTO ---
        # Usa l'indicizzazione da lista [frame_num] invece del .get() da dizionario
        player_tracks_for_frame = player_tracks[frame_num]
        ball_tracks_for_frame = ball_tracks[frame_num]
        court_keypoints_for_frame = court_keypoints[frame_num]
        player_assignments_for_frame = player_assignments[frame_num]
        player_with_ball_id = ball_aquisition[frame_num]

        shot_event = shot_detector.detect(
            ball_tracks_for_frame, player_tracks_for_frame, frame_num
        )

        # --- PIPELINE DI DISEGNO ---
        annotated_frame = frame.copy()

        annotated_frame = court_drawer.draw_frame(
            annotated_frame, court_keypoints_for_frame
        )
        annotated_frame = player_drawer.draw_frame(
            annotated_frame,
            player_tracks_for_frame,
            player_assignments_for_frame,
            player_with_ball_id,
        )
        annotated_frame = ball_drawer.draw_frame(annotated_frame, ball_tracks_for_frame)
        annotated_frame = shot_visualizer.draw_events(
            annotated_frame, shot_event, shot_detector
        )

        output_frames.append(annotated_frame)

    print("Elaborazione completata. Salvataggio del video...")

    output_video_path = "output_videos/output_video.mp4"
    os.makedirs("output_videos", exist_ok=True)
    save_video(output_frames, output_video_path)

    print(f"✅ Video finale salvato in '{output_video_path}'")


if __name__ == "__main__":
    main(input_video_path="input_videos/video_2.mp4", read_stubs=True)
