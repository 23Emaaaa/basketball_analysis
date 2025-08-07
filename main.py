import os
import argparse
import pandas as pd
from utils import read_video, save_video, save_stub
from trackers import PlayerTracker, BallTracker

# ... (altri import come prima)
from court_keypoint_detector import CourtKeypointDetector
from team_assigner import TeamAssigner
from ball_acquisition import BallAcquisitionDetector
from shot_detector import ShotDetector
from tactical_view import TacticalViewConverter
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


def main(input_video_path, output_video_path, read_stubs=False):
    video_frames = read_video(input_video_path)

    # --- Analisi dei Giocatori e del Campo (invariata) ---
    stubs_dir = "stubs"
    os.makedirs(stubs_dir, exist_ok=True)
    player_tracks_stub = os.path.join(stubs_dir, "player_track_stubs.pkl")
    court_keypoints_stub = os.path.join(stubs_dir, "court_key_points_stub.pkl")
    # ... (il resto della definizione dei percorsi stub è invariato)
    player_assignment_stub = os.path.join(stubs_dir, "player_assignment_stub.pkl")
    ball_acquisition_stub = os.path.join(stubs_dir, "ball_acquisition.pkl")

    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    player_tracks = player_tracker.get_object_tracks(
        video_frames, read_from_stub=read_stubs, stub_path=player_tracks_stub
    )

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

    # --- Rilevamento della Palla (con il nuovo metodo pulito) ---
    ball_tracker = BallTracker(BALL_DETECTOR_PATH)
    # MODIFICA: Chiamiamo il nuovo metodo 'track_frames' se non leggiamo da stub
    if read_stubs:
        with open(os.path.join(stubs_dir, "ball_track_stubs.pkl"), "rb") as f:
            ball_tracks = pd.read_pickle(f)
    else:
        ball_tracks = ball_tracker.track_frames(video_frames)
        save_stub(os.path.join(stubs_dir, "ball_track_stubs.pkl"), ball_tracks)

    # --- Rilevamento Possesso Palla (invariato) ---
    ball_acquisition_detector = BallAcquisitionDetector()
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(
        player_tracks, ball_tracks
    )
    if not read_stubs:
        save_stub(ball_acquisition_stub, ball_acquisition)

    # --- Inizializzazione (invariata) ---
    # ... (il codice da qui è identico a prima fino alla fine)
    player_drawer = PlayerTracksDrawer()
    ball_drawer = BallTracksDrawer()
    court_drawer = CourtKeypointDrawer()
    shot_detector = ShotDetector(basket_area=None)
    shot_visualizer = ShotVisualizer()
    tactical_converter = TacticalViewConverter()
    shot_outcome_info = {"text": "", "display_frames": 0}
    output_frames = []
    print("Inizio elaborazione e disegno frame per frame...")
    for frame_num, frame in enumerate(video_frames):
        player_tracks_for_frame = player_tracks[frame_num]
        ball_tracks_for_frame = ball_tracks[frame_num]
        court_keypoints_for_frame = court_keypoints[frame_num]
        player_assignments_for_frame = player_assignments[frame_num]
        player_with_ball_id = ball_acquisition[frame_num]
        basket_2d_coords = tactical_converter.transform_3d_to_2d(
            tactical_converter.basket_3d_coordinates, court_keypoints_for_frame
        )
        if basket_2d_coords is not None:
            shot_detector.basket_area = basket_2d_coords[0]
        shot_event = shot_detector.detect(
            ball_tracks_for_frame,
            player_tracks_for_frame,
            player_with_ball_id,
            frame_num,
        )
        if shot_event and shot_event["shot_event"] == "shot_ended":
            shot_outcome_info["text"] = (
                "Bucket!" if shot_event["successful"] else "Miss!"
            )
            shot_outcome_info["display_frames"] = 60
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
        outcome_text_to_draw = None
        if shot_outcome_info["display_frames"] > 0:
            outcome_text_to_draw = shot_outcome_info["text"]
            shot_outcome_info["display_frames"] -= 1
        annotated_frame = shot_visualizer.draw(
            annotated_frame, shot_detector, outcome_text_to_draw
        )
        output_frames.append(annotated_frame)
    print("Elaborazione completata. Salvataggio del video...")
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    save_video(output_frames, output_video_path)
    print(f"✅ Video finale salvato in '{output_video_path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esegue l'analisi video di una partita di basket."
    )
    parser.add_argument(
        "--input_video", type=str, required=True, help="Percorso del video di input."
    )
    parser.add_argument(
        "--output_video",
        type=str,
        required=True,
        help="Percorso dove salvare il video analizzato.",
    )
    parser.add_argument(
        "--no_stubs",
        action="store_true",
        help="Forza la ri-analisi ignorando i file stub.",
    )
    args = parser.parse_args()
    main(
        input_video_path=args.input_video,
        output_video_path=args.output_video,
        read_stubs=not args.no_stubs,
    )
