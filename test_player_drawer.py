import cv2
import pickle
from drawers.player_tracks_drawer import PlayerTracksDrawer
from utils.video_utils import read_video


def test_player_drawer_on_real_data():
    """
    Testa il metodo 'draw_frame' di PlayerTracksDrawer usando un frame
    reale e i dati di tracciamento reali dagli stub.
    """
    # --- Configurazione del Test ---
    VIDEO_PATH = "input_videos/video_2.mp4"  # IMPORTANTE: Assicurati che il nome del video sia corretto
    FRAME_TO_TEST = 50  # Scegliamo un frame a caso nel video

    # Percorsi ai file stub necessari
    PLAYER_TRACKS_STUB = "stubs/player_track_stubs.pkl"
    PLAYER_ASSIGNMENT_STUB = "stubs/player_assignment_stub.pkl"
    BALL_ACQUISITION_STUB = "stubs/ball_acquisition.pkl"

    # --- Caricamento Dati ---

    # Carica il frame specifico dal video
    video_frames = read_video(VIDEO_PATH)
    frame = video_frames[FRAME_TO_TEST]

    # Carica i dati di tracciamento dagli stub
    with open(PLAYER_TRACKS_STUB, "rb") as f:
        player_tracks = pickle.load(f)
    with open(PLAYER_ASSIGNMENT_STUB, "rb") as f:
        player_assignments = pickle.load(f)
    with open(BALL_ACQUISITION_STUB, "rb") as f:
        ball_acquisition = pickle.load(f)

    # Estrai i dati solo per il frame che stiamo testando
    player_tracks_for_frame = player_tracks[FRAME_TO_TEST]
    player_assignment_for_frame = player_assignments[FRAME_TO_TEST]
    player_with_ball_id = ball_acquisition[FRAME_TO_TEST]

    # --- Esecuzione del Test ---

    # Crea un'istanza del drawer
    drawer = PlayerTracksDrawer()

    # Chiama il NUOVO metodo 'draw_frame' con i dati reali
    output_frame = drawer.draw_frame(
        frame, player_tracks_for_frame, player_assignment_for_frame, player_with_ball_id
    )

    # --- Verifica del Risultato ---
    output_image_path = "test_player_drawer_output.jpg"
    cv2.imwrite(output_image_path, output_frame)

    print(f"✅ Test completato per PlayerTracksDrawer.")
    print(f"Controlla l'immagine salvata in: '{output_image_path}'")
    print(
        f"Dovresti vedere il frame {FRAME_TO_TEST} del tuo video con i box dei giocatori e i loro ID disegnati sopra."
    )
    print(
        "Se un giocatore ha la palla, dovresti vedere anche un triangolo rosso sopra di lui."
    )


if __name__ == "__main__":
    test_player_drawer_on_real_data()
