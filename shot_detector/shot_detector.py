import numpy as np


class ShotDetector:
    def __init__(self, basket_area, basket_radius=20):
        self.basket_area = basket_area
        self.basket_radius = basket_radius
        self.shot_in_progress = False
        self.shot_start_frame = 0
        self.ball_positions_in_shot = []

    def detect(self, ball_positions_this_frame, player_track, frame_num):
        if not self.shot_in_progress:
            # ball_positions_this_frame is a dict like {ball_id: {'bbox': [x,y,w,h]}}
            if not ball_positions_this_frame:
                self.ball_positions_in_shot = []  # Clear history if ball is lost
                return None

            # Get the bbox of the first available ball
            ball_bbox = list(ball_positions_this_frame.values())[0].get("bbox")
            if not ball_bbox:
                return None

            self.ball_positions_in_shot.append(ball_bbox)

            if len(self.ball_positions_in_shot) < 3:
                return None

            p1 = self.ball_positions_in_shot[-3]
            p2 = self.ball_positions_in_shot[-2]
            p3 = self.ball_positions_in_shot[-1]

            # Check for a parabolic trajectory using the y-coordinate of the bbox center
            y1_center = (p1[1] + p1[3]) / 2
            y2_center = (p2[1] + p2[3]) / 2
            y3_center = (p3[1] + p3[3]) / 2

            if y2_center < y1_center and y3_center > y2_center:
                self.shot_in_progress = True
                self.shot_start_frame = frame_num
                return {"shot_event": "shot_started", "frame": frame_num}

            if len(self.ball_positions_in_shot) > 10:
                self.ball_positions_in_shot.pop(0)

        else:  # Shot is in progress
            if ball_positions_this_frame:
                ball_bbox = list(ball_positions_this_frame.values())[0].get("bbox")
                if ball_bbox:
                    self.ball_positions_in_shot.append(ball_bbox)

            if frame_num - self.shot_start_frame > 15:
                self.shot_in_progress = False

                successful = False
                if (
                    self.basket_area is not None
                    and len(self.ball_positions_in_shot) > 0
                ):
                    for bbox in self.ball_positions_in_shot:
                        ball_center = np.array(
                            [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
                        )
                        distance = np.linalg.norm(
                            ball_center - np.array(self.basket_area)
                        )
                        if distance < self.basket_radius:
                            successful = True
                            break

                self.ball_positions_in_shot = []
                return {
                    "shot_event": "shot_ended",
                    "frame": frame_num,
                    "successful": successful,
                }

        return None
