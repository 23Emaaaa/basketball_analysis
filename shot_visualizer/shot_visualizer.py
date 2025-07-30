import cv2


class ShotVisualizer:
    def __init__(self):
        pass

    def draw_shot(self, frame, shot_event, player_bbox):
        if shot_event["shot_event"] == "shot_started":
            # player_bbox is [x1, y1, x2, y2]
            # Calculate the center of the bounding box
            x_center = int((player_bbox[0] + player_bbox[2]) / 2)
            y_center = int((player_bbox[1] + player_bbox[3]) / 2)
            center_point = (x_center, y_center)

            # Draw a circle at the player's center
            cv2.circle(frame, center_point, 10, (0, 0, 255), -1)
        elif shot_event["shot_event"] == "shot_ended":
            # Draw a text indicating the shot outcome
            if shot_event["successful"]:
                cv2.putText(
                    frame,
                    "Bucket!",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    frame,
                    "Miss!",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

        return frame
