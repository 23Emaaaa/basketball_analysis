import cv2
import numpy as np
from shot_visualizer import ShotVisualizer  # Importiamo la nostra nuova classe
from shot_detector import ShotDetector


def test_shot_visualizer():
    """
    Script di test per verificare il corretto funzionamento di ShotVisualizer.
    Questo test verifica due scenari:
    1. Il disegno della traiettoria durante un tiro.
    2. Il disegno del risultato ("Bucket!") alla fine di un tiro.
    """
    # --- Preparazione dei Dati di Test (Mock Data) ---

    # 1. Crea un'istanza del nostro visualizer
    visualizer = ShotVisualizer()

    # 2. Crea un frame finto (un'immagine nera) su cui disegnare
    # Dimensioni simili a un frame video tipico (es. 1280x720)
    mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    # 3. Simula lo stato di un ShotDetector durante un tiro
    mock_shot_detector = ShotDetector(basket_area=None)
    mock_shot_detector.shot_in_progress = True
    # Creiamo una finta traiettoria (una semplice linea diagonale)
    mock_shot_detector.ball_positions_in_shot = [
        [100, 200, 110, 210],  # Bbox 1
        [120, 220, 130, 230],  # Bbox 2
        [140, 240, 150, 250],  # Bbox 3
    ]

    # 4. Crea un finto evento di "tiro terminato con successo"
    mock_shot_event = {"shot_event": "shot_ended", "successful": True}

    # --- Esecuzione del Test ---

    # Chiama la funzione che vogliamo testare, passandogli i dati finti.
    # In questo caso, simuliamo sia un tiro in corso SIA la sua conclusione
    # per avere tutti gli elementi visivi in un'unica immagine.
    output_frame = visualizer.draw_events(
        frame=mock_frame, shot_event=mock_shot_event, shot_detector=mock_shot_detector
    )

    # --- Verifica del Risultato ---

    # Salva l'immagine risultante su disco.
    output_image_path = "test_shot_visualizer_output.jpg"
    cv2.imwrite(output_image_path, output_frame)

    print(f"✅ Test completato. Controlla l'immagine salvata in: '{output_image_path}'")
    print(
        "Dovresti vedere una linea verde (la traiettoria) e la scritta 'Bucket!' in verde."
    )


if __name__ == "__main__":
    test_shot_visualizer()
