import cv2
import pickle
from drawers.ball_tracks_drawer import BallTracksDrawer
from utils.video_utils import read_video


def test_ball_drawer_on_real_data():
    """
    Testa il metodo 'draw_frame' di BallTracksDrawer usando un frame
    reale e i dati di tracciamento della palla reali dallo stub.
    """
    # --- Configurazione del Test ---
    VIDEO_PATH = "input_videos/video_2.mp4"
    FRAME_TO_TEST = 50  # Usiamo lo stesso frame di prima per coerenza
    BALL_TRACKS_STUB = "stubs/ball_track_stubs.pkl"

    # --- Caricamento Dati ---
    video_frames = read_video(VIDEO_PATH)
    frame = video_frames[FRAME_TO_TEST]

    with open(BALL_TRACKS_STUB, "rb") as f:
        ball_tracks = pickle.load(f)

    ball_tracks_for_frame = ball_tracks[FRAME_TO_TEST]

    # --- Esecuzione del Test ---
    drawer = BallTracksDrawer()
    output_frame = drawer.draw_frame(frame, ball_tracks_for_frame)

    # --- Verifica del Risultato ---
    output_image_path = "test_ball_drawer_output.jpg"
    cv2.imwrite(output_image_path, output_frame)

    print(f"✅ Test completato per BallTracksDrawer.")
    print(f"Controlla l'immagine salvata in: '{output_image_path}'")
    print(
        f"Dovresti vedere il frame {FRAME_TO_TEST} del video con un triangolo verde disegnato sulla palla."
    )


if __name__ == "__main__":
    test_ball_drawer_on_real_data()
