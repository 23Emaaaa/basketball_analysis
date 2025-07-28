import cv2

class ShotVisualizer:
    def __init__(self):
        pass

    def draw_shot(self, frame, shot_event, player_position):
        if shot_event['shot_event'] == 'shot_started':
            # Draw a circle at the player's position
            cv2.circle(frame, player_position, 10, (0, 0, 255), -1)
        elif shot_event['shot_event'] == 'shot_ended':
            # Draw a text indicating the shot outcome
            if shot_event['successful']:
                cv2.putText(frame, "Goal!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Miss!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return frame
