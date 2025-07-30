import cv2


class FrameNumberDrawer:
    def __init__(self):
        pass

    def draw(self, frames):
        # Write the frame number on the top left corner of the frame
        output_frames = []
        for i in range(len(frames)):
            frame = frames[i].copy()
            cv2.putText(
                frame, str(i), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )
            output_frames.append(frame)
        return output_frames
