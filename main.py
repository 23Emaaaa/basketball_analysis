import os
import argparse
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from team_assigner import TeamAssigner
from court_keypoint_detector import CourtKeypointDetector
from ball_aquisition import BallAquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from tactical_view_converter import TacticalViewConverter
from speed_and_distance_calculator import SpeedAndDistanceCalculator
from shot_detector import ShotDetector
from shot_classifier import ShotClassifier
from shot_visualizer import ShotVisualizer
from drawers import (
    PlayerTracksDrawer,
    BallTracksDrawer,
    CourtKeypointDrawer,
    TeamBallControlDrawer,
    FrameNumberDrawer,
    PassInterceptionDrawer,
    TacticalViewDrawer,
    SpeedAndDistanceDrawer,
)
from configs import (
    STUBS_DEFAULT_PATH,
    PLAYER_DETECTOR_PATH,
    BALL_DETECTOR_PATH,
    COURT_KEYPOINT_DETECTOR_PATH,
    OUTPUT_VIDEO_PATH,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Basketball Video Analysis")
    parser.add_argument("input_video", type=str, help="Path to input video file")
    parser.add_argument(
        "--output_video",
        type=str,
        default=OUTPUT_VIDEO_PATH,
        help="Path to output video file",
    )
    parser.add_argument(
        "--stub_path",
        type=str,
        default=STUBS_DEFAULT_PATH,
        help="Path to stub directory",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Read Video
    video_frames = read_video(args.input_video)

    ## Initialize Tracker
    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    ball_tracker = BallTracker(BALL_DETECTOR_PATH)

    ## Initialize Keypoint Detector
    court_keypoint_detector = CourtKeypointDetector(COURT_KEYPOINT_DETECTOR_PATH)

    # Initialize Shot Modules
    shot_detector = ShotDetector(basket_area=None)  # We will update this in the loop
    shot_classifier = ShotClassifier(
        court_dimensions=None
    )  # TODO: Define court dimensions
    shot_visualizer = ShotVisualizer()

    # Run Detectors
    player_tracks = player_tracker.get_object_tracks(
        video_frames,
        read_from_stub=True,
        stub_path=os.path.join(args.stub_path, "player_track_stubs.pkl"),
    )

    ball_tracks = ball_tracker.get_object_tracks(
        video_frames,
        read_from_stub=True,
        stub_path=os.path.join(args.stub_path, "ball_track_stubs.pkl"),
    )
    ## Run KeyPoint Extractor
    court_keypoints_per_frame = court_keypoint_detector.get_court_keypoints(
        video_frames,
        read_from_stub=True,
        stub_path=os.path.join(args.stub_path, "court_key_points_stub.pkl"),
    )

    # Remove Wrong Ball Detections
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)
    # Interpolate Ball Tracks
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # Assign Player Teams
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames,
        player_tracks,
        read_from_stub=True,
        stub_path=os.path.join(args.stub_path, "player_assignment_stub.pkl"),
    )

    # Ball Acquisition
    ball_aquisition_detector = BallAquisitionDetector()
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(
        player_tracks, ball_tracks
    )

    # Detect Passes
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(
        ball_aquisition, player_assignment
    )
    interceptions = pass_and_interception_detector.detect_interceptions(
        ball_aquisition, player_assignment
    )

    # Tactical View
    tactical_view_converter = TacticalViewConverter(
        court_image_path="./images/basketball_court.png"
    )

    court_keypoints_per_frame = tactical_view_converter.validate_keypoints(
        court_keypoints_per_frame
    )
    tactical_player_positions = (
        tactical_view_converter.transform_players_to_tactical_view(
            court_keypoints_per_frame, player_tracks
        )
    )

    # Speed and Distance Calculator
    speed_and_distance_calculator = SpeedAndDistanceCalculator(
        tactical_view_converter.width,
        tactical_view_converter.height,
        tactical_view_converter.actual_width_in_meters,
        tactical_view_converter.actual_height_in_meters,
    )
    player_distances_per_frame = speed_and_distance_calculator.calculate_distance(
        tactical_player_positions
    )
    player_speed_per_frame = speed_and_distance_calculator.calculate_speed(
        player_distances_per_frame
    )

    # Draw output
    # Initialize Drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    court_keypoint_drawer = CourtKeypointDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    frame_number_drawer = FrameNumberDrawer()
    pass_and_interceptions_drawer = PassInterceptionDrawer()
    tactical_view_drawer = TacticalViewDrawer()
    speed_and_distance_drawer = SpeedAndDistanceDrawer()

    output_video_frames = video_frames.copy()

    for frame_num, frame in enumerate(output_video_frames):
        # Get basket 2d coordinates
        basket_2d_coords = (
            tactical_view_converter.transform_3d_to_2d(
                tactical_view_converter.basket_3d_coordinates[0],
                court_keypoints_per_frame[frame_num],
            )
            if court_keypoints_per_frame[frame_num] is not None
            else None
        )
        shot_detector.basket_area = basket_2d_coords

        # Shot Detection
        ball_positions_this_frame = ball_tracks[frame_num]
        player_positions_this_frame = player_tracks[frame_num]
        shot_event = shot_detector.detect(
            ball_positions_this_frame, player_positions_this_frame, frame_num
        )

        if shot_event:
            player_in_possession_info = ball_aquisition[frame_num]
            player_in_possession_id = player_in_possession_info

            if player_in_possession_id:
                player_bbox = (
                    player_tracks[frame_num]
                    .get(player_in_possession_id, {})
                    .get("bbox")
                )
                if player_bbox:
                    shot_classification = shot_classifier.classify(
                        shot_event, player_bbox
                    )
                    frame = shot_visualizer.draw_shot(frame, shot_event, player_bbox)

    ## Draw object Tracks
    output_video_frames = player_tracks_drawer.draw(
        output_video_frames, player_tracks, player_assignment, ball_aquisition
    )
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)

    ## Draw KeyPoints
    output_video_frames = court_keypoint_drawer.draw(
        output_video_frames, court_keypoints_per_frame
    )

    ## Draw Frame Number
    output_video_frames = frame_number_drawer.draw(output_video_frames)

    # Draw Team Ball Control
    output_video_frames = team_ball_control_drawer.draw(
        output_video_frames, player_assignment, ball_aquisition
    )

    # Draw Passes and Interceptions
    output_video_frames = pass_and_interceptions_drawer.draw(
        output_video_frames, passes, interceptions
    )

    # Speed and Distance Drawer
    output_video_frames = speed_and_distance_drawer.draw(
        output_video_frames,
        player_tracks,
        player_distances_per_frame,
        player_speed_per_frame,
    )

    ## Draw Tactical View
    output_video_frames = tactical_view_drawer.draw(
        output_video_frames,
        tactical_view_converter.court_image_path,
        tactical_view_converter.width,
        tactical_view_converter.height,
        tactical_view_converter.key_points,
        tactical_player_positions,
        player_assignment,
        ball_aquisition,
    )

    # Save video
    save_video(output_video_frames, args.output_video)


if __name__ == "__main__":
    main()
