import cv2
import pickle
from drawers.court_key_points_drawer import CourtKeypointDrawer
from utils.video_utils import read_video


def test_court_drawer_on_real_data():
    """
    Testa il metodo 'draw_frame' di CourtKeypointDrawer usando
    un frame reale e i dati reali dei keypoints.
    """
    # --- Configurazione del Test ---
    VIDEO_PATH = "input_videos/video_2.mp4"
    FRAME_TO_TEST = 50
    COURT_KEYPOINTS_STUB = "stubs/court_key_points_stub.pkl"

    # --- Caricamento Dati ---
    video_frames = read_video(VIDEO_PATH)
    frame = video_frames[FRAME_TO_TEST]

    with open(COURT_KEYPOINTS_STUB, "rb") as f:
        all_keypoints = pickle.load(f)

    keypoints_for_frame = all_keypoints[FRAME_TO_TEST]

    # --- Esecuzione del Test ---
    drawer = CourtKeypointDrawer()
    output_frame = drawer.draw_frame(frame, keypoints_for_frame)

    # --- Verifica del Risultato ---
    output_image_path = "test_court_drawer_output.jpg"
    cv2.imwrite(output_image_path, output_frame)

    print(f"✅ Test completato per CourtKeypointDrawer.")
    print(f"Controlla l'immagine salvata in: '{output_image_path}'")
    print(
        "Dovresti vedere dei punti rossi con dei numeri bianchi disegnati sui punti chiave del campo (linee, angoli, ecc.)."
    )


if __name__ == "__main__":
    test_court_drawer_on_real_data()
